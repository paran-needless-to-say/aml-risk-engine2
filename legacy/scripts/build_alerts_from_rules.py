"""
Aggregate run_rules.py output into today's Top-N risky addresses.

Input:
  - result JSON(s) produced by run_rules.py (default: result/tracex_rules_output.json)
Output:
  - web_demo/result/alerts_today.json with fields:
      [{ "address": "...", "score": 67.5, "C": 0, "E": 30, "B": 37.5 }]

Usage:
  python scripts/build_alerts_from_rules.py \
    --inputs result/tracex_rules_output.json \
    --topk 5 \
    --output web_demo/result/alerts_today.json
"""
import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path


def load_results(paths):
  rows = []
  for p in paths:
    try:
      with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
          rows.extend(data)
    except Exception:
      continue
  return rows


def aggregate(rows):
  agg = defaultdict(lambda: {"total": 0.0, "C": 0.0, "E": 0.0, "B": 0.0})
  for r in rows:
    addr = (r.get("address") or "").lower()
    if not addr:
      continue
    agg[addr]["total"] += float(r.get("total_risk_score") or 0.0)
    agg[addr]["C"] += float(r.get("compliance_score") or 0.0)
    agg[addr]["E"] += float(r.get("exposure_score") or 0.0)
    agg[addr]["B"] += float(r.get("behavior_score") or 0.0)
  out = [
    {"address": a, "score": v["total"], "C": v["C"], "E": v["E"], "B": v["B"]}
    for a, v in agg.items()
  ]
  out.sort(key=lambda x: x["score"], reverse=True)
  return out


def main():
  ap = argparse.ArgumentParser(description="Build alerts_today.json from rules outputs.")
  ap.add_argument("--inputs", nargs="+", default=["result/tracex_rules_output.json"], help="Input JSON files or globs")
  ap.add_argument("--topk", type=int, default=5, help="Top K addresses")
  ap.add_argument("--output", default="web_demo/result/alerts_today.json", help="Output JSON path")
  args = ap.parse_args()

  files = []
  for inp in args.inputs:
    files.extend(glob.glob(inp))
  rows = load_results(files)
  agg = aggregate(rows)[: args.topk]

  out_path = Path(args.output)
  out_path.parent.mkdir(parents=True, exist_ok=True)
  with out_path.open("w", encoding="utf-8") as f:
    json.dump(agg, f, ensure_ascii=False, indent=2)
  print(f"Saved {len(agg)} alerts to {out_path}")


if __name__ == "__main__":
  main()


