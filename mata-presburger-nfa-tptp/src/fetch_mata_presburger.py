#!/usr/bin/env python3
"""Fetch and extract the MATA Presburger explicit-complement NFA benchmark set.

Upstream repositories:
  - Benchmarks: https://github.com/VeriFIT/nfa-bench (nfa_bench/presburger-explicit/complement/)
  - Input list: bench-single-presburger-explicit-complement.input (169 entries; 174 .mata files in directory)
  - Automata library: https://github.com/VeriFIT/mata (MIT License)
"""
from __future__ import annotations

import lzma
import pathlib
import subprocess
import sys
import tempfile

REPO_URL = "https://github.com/VeriFIT/nfa-bench.git"


def main() -> int:
    suite_dir = pathlib.Path(__file__).resolve().parent.parent
    mata_dir = suite_dir / "mata-orig"
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, tmp], check=True)
        src_root = pathlib.Path(tmp) / "benchmarks" / "nfa" / "presburger-explicit" / "complement" / "tptp"
        if not src_root.exists():
            matches = [p for p in pathlib.Path(tmp).rglob("tptp") if p.is_dir() and "complement" in p.parts]
            if not matches:
                print("Could not locate presburger complement/tptp directory", file=sys.stderr)
                return 1
            src_root = matches[0]
        count = 0
        mata_dir.mkdir(parents=True, exist_ok=True)
        for mata in sorted(src_root.glob("*.mata")):
            dst = mata_dir / (mata.name + ".xz")
            dst.write_bytes(lzma.compress(mata.read_bytes(), preset=6))
            count += 1
        print(f"Packed {count} .mata.xz files into {mata_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
