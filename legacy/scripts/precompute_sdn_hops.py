"""
Precompute SDN hop1/hop2 sets from address-level transaction CSVs.

Inputs:
  - dataset/sdn_addresses.json (list)
  - data/address_transactions/{chain}/*.csv with columns: from, to [, usd_value, timestamp]

Outputs:
  - dataset/sdn_hop1.json
  - dataset/sdn_hop2.json

Usage:
  python scripts/precompute_sdn_hops.py --transactions-dir data/address_transactions --chain ethereum
"""
import argparse
import json
from pathlib import Path
from typing import Set

import pandas as pd


def load_sdn(path: Path) -> Set[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing SDN addresses: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return set([str(x).lower() for x in data])


def precompute_hops(tx_dir: Path, chain: str, sdn: Set[str]) -> tuple[Set[str], Set[str]]:
    chain_dir = tx_dir / chain
    if not chain_dir.exists():
        raise FileNotFoundError(f"Transactions directory not found: {chain_dir}")
    hop1: Set[str] = set()
    hop2: Set[str] = set()

    # First pass: find hop1 neighbors of SDN (either direction)
    for csv_file in chain_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file, usecols=["from", "to"])
        except Exception:
            continue
        df["from"] = df["from"].astype(str).str.lower()
        df["to"] = df["to"].astype(str).str.lower()
        # SDN → X or X → SDN
        hop1 |= set(df.loc[df["from"].isin(sdn), "to"].tolist())
        hop1 |= set(df.loc[df["to"].isin(sdn), "from"].tolist())

    # Remove SDN itself
    hop1 -= sdn

    # Second pass: find neighbors of hop1 (to build hop2), excluding SDN
    for csv_file in chain_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file, usecols=["from", "to"])
        except Exception:
            continue
        df["from"] = df["from"].astype(str).str.lower()
        df["to"] = df["to"].astype(str).str.lower()

        # hop1 → Y or Y → hop1
        hop2 |= set(df.loc[df["from"].isin(hop1), "to"].tolist())
        hop2 |= set(df.loc[df["to"].isin(hop1), "from"].tolist())

    hop2 -= sdn
    hop2 -= hop1
    return hop1, hop2


def main() -> None:
    ap = argparse.ArgumentParser(description="Precompute SDN hop1/hop2 from address-level CSVs.")
    ap.add_argument("--transactions-dir", default="data/address_transactions", help="Root dir with chain subfolders")
    ap.add_argument("--chain", required=True, choices=["bsc", "ethereum", "polygon"], help="Chain to process")
    ap.add_argument("--sdn", default="dataset/sdn_addresses.json", help="SDN address list JSON")
    ap.add_argument("--out-hop1", default="dataset/sdn_hop1.json", help="Output JSON for hop1 set")
    ap.add_argument("--out-hop2", default="dataset/sdn_hop2.json", help="Output JSON for hop2 set")
    args = ap.parse_args()

    sdn = load_sdn(Path(args.sdn))
    hop1, hop2 = precompute_hops(Path(args.transactions_dir), args.chain, sdn)

    out1 = Path(args.out_hop1); out1.parent.mkdir(parents=True, exist_ok=True)
    out2 = Path(args.out_hop2); out2.parent.mkdir(parents=True, exist_ok=True)

    with out1.open("w", encoding="utf-8") as f:
        json.dump(sorted(list(hop1)), f, ensure_ascii=False, indent=2)
    with out2.open("w", encoding="utf-8") as f:
        json.dump(sorted(list(hop2)), f, ensure_ascii=False, indent=2)
    print(f"Saved hop1={len(hop1)} to {out1}")
    print(f"Saved hop2={len(hop2)} to {out2}")


if __name__ == "__main__":
    main()


