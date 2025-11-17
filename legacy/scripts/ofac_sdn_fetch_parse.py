"""
OFAC SDN XML fetcher & parser
 - Downloads https://www.treasury.gov/ofac/downloads/sdn.xml
 - Extracts Digital Currency Address entries (e.g., ETH/BTC/BNB/USDT addresses)
 - Writes dataset/sdn_addresses.json (lowercased where applicable)

Usage:
  python scripts/ofac_sdn_fetch_parse.py --output dataset/sdn_addresses.json
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

SDN_XML_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"

# Basic patterns for ETH-like addresses; other chains may appear in SDN too
HEX_ADDR_RE = re.compile(r"0x[a-fA-F0-9]{20,64}")


def fetch_xml(url: str) -> bytes:
    with urlopen(url) as resp:
        return resp.read()


def extract_digital_currency_addresses(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    ns = {}  # SDN XML usually not namespace heavy for the fields we need
    addrs: set[str] = set()
    # The structure includes <sdnEntry><idList><id><idType>Digital Currency Address</idType><idNumber>...</idNumber>
    for id_elem in root.findall(".//idList/id", ns):
        id_type = (id_elem.findtext("idType") or "").strip()
        if id_type.lower() != "digital currency address":
            continue
        raw = (id_elem.findtext("idNumber") or "").strip()
        if not raw:
            continue
        # Collect hex-like addresses; keep raw too for non-hex cases
        matches = HEX_ADDR_RE.findall(raw)
        if matches:
            for m in matches:
                addrs.add(m.lower())
        else:
            addrs.add(raw.strip().lower())
    return sorted(addrs)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch & parse OFAC SDN XML to JSON address list.")
    ap.add_argument("--url", default=SDN_XML_URL, help="SDN XML URL")
    ap.add_argument("--output", default="dataset/sdn_addresses.json", help="Output JSON path")
    args = ap.parse_args()

    xml_bytes = fetch_xml(args.url)
    addrs = extract_digital_currency_addresses(xml_bytes)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(addrs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(addrs)} SDN digital currency addresses to {out}")


if __name__ == "__main__":
    main()


