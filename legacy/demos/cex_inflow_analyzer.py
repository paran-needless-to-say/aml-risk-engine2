"""
Rule-based analyzer focused on addresses receiving funds from CEX deposit/withdrawal wallets.

Usage:
  python cex_inflow_analyzer.py --chain <bsc|ethereum|polygon> --address <address> \
      [--transactions-dir data/address_transactions] [--output result/cex_inflow_report.json]

Input:
  - Loads CSV: {transactions_dir}/{chain}/{address}.csv
  - Required columns: from, to
  - Optional columns: value, timestamp

Aux data:
  - Known CEX wallets: dataset/cex_addresses.json
  - Known bridge contracts: dataset/bridge_contracts.json (optional, improves R5)
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd


# -------------------------------
# Configuration / Thresholds
# -------------------------------
DEFAULT_THRESHOLDS = {
    "min_cex_inflow_count": 2,         # R1: number of CEX-sourced inflow txs
    "min_cex_inflow_total": 0.0,       # R1: total amount threshold (set >0 if value exists)
    "fanout_unique_out_addrs": 5,      # R2: number of unique outs after CEX inflow
    "fanout_time_window_sec": 24 * 3600,
    "velocity_min_out_txs": 10,        # R3: number of outgoing txs within window
    "velocity_time_window_sec": 6 * 3600,
    "mixing_unique_out_addrs": 20,     # R4: many small outs → mixing-like
    "bridge_follow_time_sec": 24 * 3600,  # R5: bridge usage soon after CEX inflow
}


@dataclass
class RuleFinding:
    id: str
    name: str
    severity: str
    confidence: float
    reason: str


@dataclass
class AnalysisReport:
    chain: str
    address: str
    analyzed_at: str
    risk_score: float
    risk_level: str
    findings: List[RuleFinding]
    stats: Dict[str, float]


def _risk_level(score: float) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _load_known_cex_addresses() -> Dict[str, Dict[str, List[str]]]:
    path = Path("dataset/cex_addresses.json")
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_bridge_contracts() -> Dict[str, List[str]]:
    path = Path("dataset/bridge_contracts.json")
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize to lists of addresses per chain
    norm: Dict[str, List[str]] = {}
    for chain, addrs in data.items():
        if isinstance(addrs, list):
            norm[chain.lower()] = [a.lower() for a in addrs]
    return norm


def _load_address_txs(chain: str, address: str, transactions_dir: str) -> pd.DataFrame:
    tx_path = Path(transactions_dir) / chain / f"{address}.csv"
    if not tx_path.exists():
        raise FileNotFoundError(f"Transaction file not found: {tx_path}")
    df = pd.read_csv(tx_path)
    required = ["from", "to"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns {missing} in {tx_path}")
    # Normalize
    df["from"] = df["from"].astype(str).str.lower()
    df["to"] = df["to"].astype(str).str.lower()
    if "timestamp" in df.columns:
        # Accept int/float/str timestamps; store as int seconds if possible
        try:
            df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce").astype("Int64")
        except Exception:
            pass
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def _build_cex_set(known: Dict[str, Dict[str, List[str]]], chain: str) -> Set[str]:
    by_chain = known.get(chain.lower(), {})
    s: Set[str] = set()
    for _, addrs in by_chain.items():
        for a in addrs:
            s.add(a.lower())
    return s


def _compute_basic_stats(df: pd.DataFrame, target: str) -> Dict[str, float]:
    inflow = df[df["to"] == target]
    outflow = df[df["from"] == target]
    stats = {
        "inflow_txs": float(len(inflow)),
        "outflow_txs": float(len(outflow)),
        "unique_senders": float(inflow["from"].nunique()),
        "unique_receivers": float(outflow["to"].nunique()),
    }
    if "value" in df.columns:
        stats["inflow_total"] = float(inflow["value"].fillna(0).sum())
        stats["outflow_total"] = float(outflow["value"].fillna(0).sum())
    return stats


def _evaluate_rules(
    chain: str,
    address: str,
    df: pd.DataFrame,
    cex_addrs: Set[str],
    bridge_map: Dict[str, List[str]],
    thresholds: Dict[str, float],
) -> Tuple[List[RuleFinding], float]:
    findings: List[RuleFinding] = []
    risk_points = 0.0

    inflow = df[df["to"] == address]
    outflow = df[df["from"] == address]

    # R1: Significant inflow from known CEX addresses
    cex_inflow = inflow[inflow["from"].isin(cex_addrs)]
    cex_inflow_count = len(cex_inflow)
    cex_inflow_total = float(cex_inflow["value"].fillna(0).sum()) if "value" in cex_inflow.columns else 0.0
    if cex_inflow_count >= thresholds["min_cex_inflow_count"] and cex_inflow_total >= thresholds["min_cex_inflow_total"]:
        conf = min(100.0, 50.0 + 5.0 * (cex_inflow_count - thresholds["min_cex_inflow_count"]))
        findings.append(
            RuleFinding(
                id="R1_CEX_INFLOW",
                name="CEX-sourced inflow",
                severity="HIGH",
                confidence=conf,
                reason=f"Detected {cex_inflow_count} inflows from known CEX addresses (total {cex_inflow_total:.4f}).",
            )
        )
        risk_points += 35.0

    # Time-indexed helpers
    has_time = "timestamp" in df.columns and df["timestamp"].notna().any()
    bridge_addrs = set(a.lower() for a in bridge_map.get(chain.lower(), []))

    # R2: Fan-out after CEX inflow within a time window
    if has_time and not cex_inflow.empty:
        earliest_cex_in = int(cex_inflow["timestamp"].dropna().min())
        window_end = earliest_cex_in + int(thresholds["fanout_time_window_sec"])
        fanout_slice = outflow[
            (outflow["timestamp"].notna())
            & (outflow["timestamp"] >= earliest_cex_in)
            & (outflow["timestamp"] <= window_end)
        ]
        unique_outs = fanout_slice["to"].nunique()
        if unique_outs >= thresholds["fanout_unique_out_addrs"]:
            findings.append(
                RuleFinding(
                    id="R2_FANOUT",
                    name="Fan-out after CEX inflow",
                    severity="HIGH",
                    confidence=min(100.0, 50.0 + 5.0 * (unique_outs - thresholds["fanout_unique_out_addrs"])),
                    reason=f"{unique_outs} unique outgoing addresses within {thresholds['fanout_time_window_sec']/3600:.0f}h after first CEX inflow.",
                )
            )
            risk_points += 25.0

    # R3: High velocity of outgoing transfers after CEX inflow
    if has_time and not cex_inflow.empty:
        earliest_cex_in = int(cex_inflow["timestamp"].dropna().min())
        vel_end = earliest_cex_in + int(thresholds["velocity_time_window_sec"])
        velocity_slice = outflow[
            (outflow["timestamp"].notna())
            & (outflow["timestamp"] >= earliest_cex_in)
            & (outflow["timestamp"] <= vel_end)
        ]
        out_txs = len(velocity_slice)
        if out_txs >= thresholds["velocity_min_out_txs"]:
            findings.append(
                RuleFinding(
                    id="R3_VELOCITY",
                    name="High velocity after CEX inflow",
                    severity="MEDIUM",
                    confidence=min(100.0, 50.0 + 3.0 * (out_txs - thresholds["velocity_min_out_txs"])),
                    reason=f"{out_txs} outgoing txs within {thresholds['velocity_time_window_sec']/3600:.0f}h after first CEX inflow.",
                )
            )
            risk_points += 15.0

    # R4: Mixing-like distribution (many unique outs; small amounts if value available)
    if not outflow.empty:
        unique_outs_total = outflow["to"].nunique()
        mixing_hit = unique_outs_total >= thresholds["mixing_unique_out_addrs"]
        if "value" in outflow.columns and outflow["value"].notna().any():
            median_out = float(outflow["value"].median(skipna=True))
            mixing_hit = mixing_hit or (unique_outs_total >= thresholds["mixing_unique_out_addrs"] // 2 and median_out > 0 and median_out < 1e-3)
        if mixing_hit:
            findings.append(
                RuleFinding(
                    id="R4_MIXING_LIKE",
                    name="Mixing-like distribution",
                    severity="MEDIUM",
                    confidence=65.0,
                    reason=f"Many unique outgoing recipients ({unique_outs_total}); potential mixing/peel chain behavior.",
                )
            )
            risk_points += 10.0

    # R5: Bridge transfer soon after CEX inflow
    if has_time and not cex_inflow.empty and len(bridge_addrs) > 0:
        earliest_cex_in = int(cex_inflow["timestamp"].dropna().min())
        bridge_window_end = earliest_cex_in + int(thresholds["bridge_follow_time_sec"])
        to_bridge = outflow[
            (outflow["timestamp"].notna())
            & (outflow["timestamp"] >= earliest_cex_in)
            & (outflow["timestamp"] <= bridge_window_end)
            & (outflow["to"].isin(bridge_addrs))
        ]
        if len(to_bridge) > 0:
            findings.append(
                RuleFinding(
                    id="R5_BRIDGE_AFTER_CEX",
                    name="Bridge usage after CEX inflow",
                    severity="HIGH",
                    confidence=80.0,
                    reason=f"Detected {len(to_bridge)} transfers to bridge addresses within 24h after first CEX inflow.",
                )
            )
            risk_points += 20.0

    # Risk scoring: cap at 100
    risk_score = min(100.0, risk_points)
    return findings, risk_score


def analyze_cex_inflow(
    chain: str,
    address: str,
    transactions_dir: str,
    thresholds: Optional[Dict[str, float]] = None,
) -> AnalysisReport:
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    address = address.lower()
    chain = chain.lower()

    df = _load_address_txs(chain, address, transactions_dir)
    stats = _compute_basic_stats(df, address)
    known_cex = _load_known_cex_addresses()
    bridge_map = _load_bridge_contracts()

    cex_set = _build_cex_set(known_cex, chain)
    findings, risk_score = _evaluate_rules(chain, address, df, cex_set, bridge_map, thresholds)

    return AnalysisReport(
        chain=chain,
        address=address,
        analyzed_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        findings=findings,
        stats=stats,
    )


def _print_human(report: AnalysisReport) -> None:
    print("=" * 70)
    print("🏦 CEX Inflow Rule-based AML Report")
    print("=" * 70)
    print(f"- Chain   : {report.chain}")
    print(f"- Address : {report.address}")
    print(f"- Time    : {report.analyzed_at}")
    print("")
    print(f"Risk Score : {report.risk_score:.1f}/100  ({report.risk_level})")
    print("")
    if report.findings:
        print(f"Findings ({len(report.findings)}):")
        for i, f in enumerate(report.findings, 1):
            print(f"  [{i}] {f.name} ({f.severity}) — {f.confidence:.0f}%")
            print(f"      {f.reason}")
    else:
        print("No rule triggers detected.")
    print("")
    print("Stats:")
    for k, v in report.stats.items():
        print(f"  - {k}: {v}")
    print("")
    if report.risk_score >= 75:
        print("Recommendations:")
        print("  - Immediate enhanced monitoring")
        print("  - Identify downstream recipients; consider freezing pending investigation")
        print("  - Prepare SAR if policy mandates for CRITICAL")
    elif report.risk_score >= 50:
        print("Recommendations:")
        print("  - 72h enhanced monitoring")
        print("  - Investigate bridge/mixing involvement")
    elif report.risk_score >= 30:
        print("Recommendations:")
        print("  - Add to watchlist; re-evaluate weekly")
    else:
        print("Recommendations:")
        print("  - Standard monitoring")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rule-based CEX inflow AML analyzer (address-focused).")
    p.add_argument("--chain", required=True, choices=["bsc", "ethereum", "polygon"], help="Chain name")
    p.add_argument("--address", required=True, help="Target address (lower/anycase accepted)")
    p.add_argument(
        "--transactions-dir",
        default="data/address_transactions",
        help="Directory containing {chain}/{address}.csv",
    )
    p.add_argument(
        "--output",
        default="result/cex_inflow_report.json",
        help="Path to write JSON report (will be created/overwritten).",
    )
    return p


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    report = analyze_cex_inflow(args.chain, args.address, args.transactions_dir)

    # Human-readable
    _print_human(report)

    # JSON output
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                **asdict(report),
                "findings": [asdict(f) for f in report.findings],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nSaved JSON report to: {out_path}")


if __name__ == "__main__":
    main()


