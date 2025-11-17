"""
CLI runner for TRACE-X rules.

Example:
  python run_rules.py --chain ethereum --address 0xabc... \
      --transactions-dir data/address_transactions \
      --rules rules/tracex_rules.yaml \
      --output result/tracex_rules_output.json
"""
import argparse
import json
from pathlib import Path

from rules_engine import load_and_evaluate


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="TRACE-X rules runner (per address CSV).")
    p.add_argument("--chain", required=True, choices=["bsc", "ethereum", "polygon"], help="Chain name")
    p.add_argument("--address", required=True, help="Target address")
    p.add_argument("--transactions-dir", default="data/address_transactions", help="Directory containing CSVs")
    p.add_argument("--rules", default="rules/tracex_rules.yaml", help="Rules YAML path")
    p.add_argument("--output", default="result/tracex_rules_output.json", help="Output JSON path")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    csv_path = Path(args.transactions_dir) / args.chain / f"{args.address}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Transaction file not found: {csv_path}")

    results = load_and_evaluate(str(csv_path), args.rules)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved rule evaluation to: {out_path}")


if __name__ == "__main__":
    main()


