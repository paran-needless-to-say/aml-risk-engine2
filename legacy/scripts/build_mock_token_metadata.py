#!/usr/bin/env python3
"""
Quick-and-dirty helper to generate a contract → {name, symbol} mapping
for the web demo.

⚠️ This is a temporary script built while the full preprocessing/API
pipeline is still under construction.  It reads the per-chain feature CSV
files that already exist in `data/features/` and enriches them with a small
set of manually curated token labels.  Everything else gets a deterministic
placeholder so that the React demo can show “realistic” names without
misleading anyone that the numbers are production-ready.

Output: `web_demo/mock_token_metadata.json`
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIR = REPO_ROOT / "data" / "features"
OUTPUT_PATH = REPO_ROOT / "web_demo" / "mock_token_metadata.json"

# Minimal hand-curated mapping for well-known contracts we often mention
# during demos.  Extend this list as you validate more tokens.
MANUAL_LABELS: Dict[str, Dict[str, str]] = {
    # Ethereum
    "ethereum:0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {
        "name": "USD Coin",
        "symbol": "USDC",
    },
    "ethereum:0xdac17f958d2ee523a2206206994597c13d831ec7": {
        "name": "Tether USD",
        "symbol": "USDT",
    },
    "ethereum:0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": {
        "name": "Wrapped BTC",
        "symbol": "WBTC",
    },
    "ethereum:0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
        "name": "Wrapped Ether",
        "symbol": "WETH",
    },
    # Polygon
    "polygon:0x2791bca1f2de4661ed88a30c99a7a9449aa84174": {
        "name": "USD Coin (Polygon)",
        "symbol": "USDC.e",
    },
    "polygon:0x7ceb23fd6bc0add59e62ac25578270cff1b9f619": {
        "name": "Wrapped Ether (Polygon)",
        "symbol": "WETH",
    },
    "polygon:0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270": {
        "name": "Wrapped Matic",
        "symbol": "WMATIC",
    },
    # BSC
    "bsc:0x55d398326f99059ff775485246999027b3197955": {
        "name": "Tether USD (BSC)",
        "symbol": "USDT",
    },
    "bsc:0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": {
        "name": "USD Coin (BSC)",
        "symbol": "USDC",
    },
}

# Helper ---------------------------------------------------------------


def iter_feature_rows(feature_path: Path) -> Iterable[Dict[str, str]]:
    with feature_path.open() as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            yield row


def build_mapping() -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    placeholder_counters: Dict[str, int] = {}

    for feature_file in FEATURE_DIR.glob("*_basic_metrics_processed.csv"):
        chain = feature_file.stem.split("_")[0]  # ethereum_basic_metrics_processed -> ethereum
        placeholder_counters.setdefault(chain, 1)

        for row in iter_feature_rows(feature_file):
            contract = row["Contract"].strip().lower()
            key = f"{chain}:{contract}"

            if key in mapping:
                continue

            if key in MANUAL_LABELS:
                mapping[key] = MANUAL_LABELS[key]
                continue

            idx = placeholder_counters[chain]
            mapping[key] = {
                "name": f"{chain.upper()} Token {idx:04d}",
                "symbol": f"{chain[:2].upper()}-{idx:04d}",
            }
            placeholder_counters[chain] += 1

    return mapping


def render_sample(mapping: Dict[str, Dict[str, str]], limit: int = 8) -> List[str]:
    samples: List[str] = []
    for key in sorted(mapping.keys())[:limit]:
        chain, contract = key.split(":", 1)
        label = mapping[key]
        samples.append(
            f"{chain.upper()} | {contract} → {label['symbol']} ({label['name']})"
        )
    return samples


def main() -> None:
    mapping = build_mapping()

    OUTPUT_PATH.write_text(json.dumps(mapping, indent=2, sort_keys=True))
    print(f"[ok] wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} with {len(mapping)} entries")

    print("\nSample tokens:")
    for line in render_sample(mapping):
        print("  •", line)


if __name__ == "__main__":
    main()

