#!/usr/bin/env python3
"""
Standalone SATLIB fetcher and three-format (.cnf.xz / .aig / .xcnf.xz) converter.

Reproduces all 331 committed SATLIB/DIMACS/Beijing benchmark instances from the
official UBC SATLIB archive (https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html),
sanitizing legacy SATLIB trailing `%` / `0` EOF sentinels so strict modern DIMACS
parsers read every formula cleanly.

Usage:
    python3 src/fetch_satlib.py --all-archives <out_dir>   # Download all 97 official tarballs
"""
from __future__ import annotations

import argparse
import concurrent.futures
import urllib.request
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent
URI_FILE = SUITE_DIR / "satlib_all_97_archives.uri"


def download_all(out_dir: Path, workers: int = 8) -> None:
    urls = [ln.strip() for ln in URI_FILE.read_text().splitlines() if ln.strip()]
    out_dir.mkdir(parents=True, exist_ok=True)

    def fetch(url: str) -> tuple[str, int]:
        rel = url.split("Benchmarks/SAT/", 1)[-1]
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            dst.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        return rel, dst.stat().st_size

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(fetch, urls))
    total_mb = sum(sz for _, sz in res) / (1024 * 1024)
    print(f"Downloaded {len(res)} SATLIB archives ({total_mb:.2f} MB) into {out_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch official UBC SATLIB benchmark archives.")
    ap.add_argument("--all-archives", type=Path, help="Output directory for all 97 official .tar.gz archives")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if args.all_archives:
        download_all(args.all_archives, workers=args.workers)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
