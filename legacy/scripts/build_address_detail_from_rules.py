"""
Build rule-based address detail JSON from run_rules.py outputs.

Inputs:
  - --rules-output result/tracex_rules_output.json
  - --rules-yaml rules/tracex_rules.yaml (for rule names/severity)
  - --address 0x...
  - optional SDN/mixer/hop lists under dataset/

Output:
  - web_demo/result/address_detail_{address}.json
"""
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_rules_output(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def load_rules_yaml(path: str) -> Dict[str, Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        y = yaml.safe_load(f)
    idx = {}
    for r in y.get("rules", []):
        idx[r["id"]] = {"name": r.get("name", r["id"]), "severity": r.get("severity", "LOW")}
    return idx


def load_set(path: Path) -> set:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return set(str(x).lower() for x in data)
    return set()


def build_detail(address: str, rows: List[Dict[str, Any]], rules_idx: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    addr = address.lower()
    addr_rows = [r for r in rows if str(r.get("address", "")).lower() == addr]
    total = sum(float(r.get("total_risk_score") or 0.0) for r in addr_rows)
    c = sum(float(r.get("compliance_score") or 0.0) for r in addr_rows)
    e = sum(float(r.get("exposure_score") or 0.0) for r in addr_rows)
    b = sum(float(r.get("behavior_score") or 0.0) for r in addr_rows)

    # Aggregate rules by max score contribution across txs
    rule_scores: Dict[str, float] = {}
    for r in addr_rows:
        sd = r.get("score_detail") or {}
        for rid, sc in sd.items():
            rule_scores[rid] = max(rule_scores.get(rid, 0.0), float(sc or 0.0))

    rules = []
    for rid, sc in sorted(rule_scores.items(), key=lambda x: -x[1]):
        meta = rules_idx.get(rid, {"name": rid, "severity": "LOW"})
        rules.append({"id": rid, "name": meta["name"], "severity": meta["severity"], "score": sc, "reason": ""})

    # tx_recent (up to 10, prefer those with any rules)
    def score_of_tx(r):
        return sum((r.get("score_detail") or {}).values()) if isinstance(r.get("score_detail"), dict) else 0.0
    sorted_rows = sorted(addr_rows, key=score_of_tx, reverse=True)[:10]

    tx_recent = []
    for r in sorted_rows:
        tx_recent.append({
            "tx_hash": r.get("tx_hash"),
            "ts": r.get("timestamp") or r.get("ts"),
            "usd_value": r.get("usd_value") or 0.0,
            "dir": r.get("direction") or "-",
            "rules": list((r.get("score_detail") or {}).keys()),
        })

    # Evidence via datasets
    sdn = load_set(Path("dataset/sdn_addresses.json"))
    hop1 = load_set(Path("dataset/sdn_hop1.json"))
    hop2 = load_set(Path("dataset/sdn_hop2.json"))
    evidence = {"sdn": addr in sdn, "hop": 1 if addr in hop1 else (2 if addr in hop2 else None), "mixer": False, "cex_internal": False}

    return {
        "address": address,
        "chain": "ethereum",
        "analyzed_at": rows and rows[0].get("analyzed_at") or "",
        "scores": {"total": total, "C": c, "E": e, "B": b},
        "rules": rules,
        "evidence": evidence,
        "tx_recent": tx_recent,
    }


def main():
    ap = argparse.ArgumentParser(description="Build rule-based address detail JSON.")
    ap.add_argument("--rules-output", default="result/tracex_rules_output.json")
    ap.add_argument("--rules-yaml", default="rules/tracex_rules.yaml")
    ap.add_argument("--address", required=True)
    ap.add_argument("--output", default=None, help="Output JSON path; default web_demo/result/address_detail_{address}.json")
    args = ap.parse_args()

    rows = load_rules_output(args.rules_output)
    rules_idx = load_rules_yaml(args.rules_yaml)
    detail = build_detail(args.address, rows, rules_idx)

    out = args.output or f"web_demo/result/address_detail_{args.address}.json"
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(detail, f, ensure_ascii=False, indent=2)
    print(f"Saved address detail to {out_path}")


if __name__ == "__main__":
    main()


