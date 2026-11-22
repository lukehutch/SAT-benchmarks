#!/usr/bin/env python3
"""
Fetch the 14 curated SAT Competition 2023/2024 flat DIMACS CNFs from the Global
Benchmark Database (GBD: https://benchmark-database.de/file/<gbd_hash>) and
convert each `.cnf` into Binary AIGER 1.9 inside `../aig-version/`.
"""
from __future__ import annotations

import json
import lzma
import sys
import urllib.request
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SUITE_DIR = SRC_DIR.parent
AIG_DIR = SUITE_DIR / "aig-version"
MANIFEST = SRC_DIR / "sc23_24_manifest.json"


def main() -> None:
    sys.path.insert(0, str(SUITE_DIR.parent / "sat-competition-2024-2026-main-track" / "src"))
    from cnf2aig import cnf_to_aiger

    data = json.loads(MANIFEST.read_text())
    AIG_DIR.mkdir(parents=True, exist_ok=True)
    for item in data["sat_competition_flat_cnfs"]:
        name = item["name"]
        h = item["gbd_hash"]
        cnf_path = SUITE_DIR / f"{name}.cnf"
        aig_path = AIG_DIR / f"{name}.aig"
        if not cnf_path.exists():
            url = f"https://benchmark-database.de/file/{h}"
            print(f"Downloading {name} ({h}) from {url} ...")
            raw = urllib.request.urlopen(url, timeout=60).read()
            if raw[:6] == b"\xfd7zXZ\x00":
                raw = lzma.decompress(raw)
            cnf_path.write_bytes(raw)
        nv, nc, ands = cnf_to_aiger(
            cnf_path,
            aig_path,
            comment=f"benchmark={name}\ngbd_hash={h}\nexpected={item['ans']}\norigin=CNF",
        )
        print(f"  {name}: vars={nv} clauses={nc} -> aig-version/{aig_path.name} ({ands} ANDs)")


if __name__ == "__main__":
    main()
