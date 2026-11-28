#!/usr/bin/env python3
"""Reproducible 4-format benchmark generator for `brewbaker-golomb-rulers`.

Invokes verbatim upstream `sat_challenges.py` (Chad Brewbaker, gist 6f055336fda6009d1e67e0da8c843d19)
to build all DIMACS CNF instances (`cnf-orig/*.cnf.xz`), then derives and verifies lossless:
  - CryptoMiniSat XCNF (`xcnf-converted/*.xcnf.xz`) via `cnf2xcnf.py`
  - Binary AIGER 1.9 (`aig-converted/*.aig.xz`) via `cnf2aig.py` (verified with `abc` if installed)
  - Linear-size DIMACS-ANF (`anf-converted/*.anf.xz`) via `../../src/to_anf.py --verify`
and writes the exact sorted 2-column `expected.tsv` manifest.

Usage:
    python3 src/generate_suite.py
"""
from __future__ import annotations

import lzma
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SUITE_DIR = SRC_DIR.parent
REPO_ROOT = SUITE_DIR.parent
SAT_CHALLENGES = SRC_DIR / "sat_challenges.py"
TO_ANF = REPO_ROOT / "src" / "to_anf.py"

sys.path.insert(0, str(SRC_DIR))
from cnf2aig import cnf_to_aiger
from cnf2xcnf import cnf_to_xcnf

INSTANCES: list[tuple[str, list[str], str]] = [('golomb_m5_l10', ['golomb', '5', '10'], 'UNSAT'), ('golomb_m5_l11', ['golomb', '5', '11'], 'SAT'), ('golomb_m6_l16', ['golomb', '6', '16'], 'UNSAT'), ('golomb_m6_l17', ['golomb', '6', '17'], 'SAT'), ('golomb_m7_l24', ['golomb', '7', '24'], 'UNSAT'), ('golomb_m7_l25', ['golomb', '7', '25'], 'SAT'), ('golomb_m8_l33', ['golomb', '8', '33'], 'UNSAT'), ('golomb_m8_l34', ['golomb', '8', '34'], 'SAT'), ('golomb_m9_l43', ['golomb', '9', '43'], 'UNSAT'), ('golomb_m9_l44', ['golomb', '9', '44'], 'SAT'), ('golomb_m10_l54', ['golomb', '10', '54'], 'UNSAT'), ('golomb_m10_l55', ['golomb', '10', '55'], 'SAT')]


def main() -> None:
    cnf_dir = SUITE_DIR / "cnf-orig"
    aig_dir = SUITE_DIR / "aig-converted"
    xcnf_dir = SUITE_DIR / "xcnf-converted"
    anf_dir = SUITE_DIR / "anf-converted"
    for d in (cnf_dir, aig_dir, xcnf_dir, anf_dir):
        d.mkdir(parents=True, exist_ok=True)

    has_abc = shutil.which("abc") is not None
    expected_rows: list[tuple[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="brewbaker_gen_") as td:
        tmp = Path(td)
        for stem, cli_args, verdict in INSTANCES:
            raw_cnf = subprocess.check_output([sys.executable, str(SAT_CHALLENGES), *cli_args])
            cnf_xz = cnf_dir / f"{stem}.cnf.xz"
            with lzma.open(cnf_xz, "wb", preset=6) as f:
                f.write(raw_cnf)

            xcnf_xz = xcnf_dir / f"{stem}.xcnf.xz"
            nv, orig_c, rem_c, nx = cnf_to_xcnf(cnf_xz, xcnf_xz)

            aig_raw = tmp / f"{stem}.aig"
            a_nv, a_nc, a_ands = cnf_to_aiger(
                cnf_xz, aig_raw, comment=f"Converted from {stem}.cnf by cnf2aig.py"
            )
            if has_abc:
                proc = subprocess.run(
                    ["abc", "-c", f"read {aig_raw}; print_stats"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                assert "i/o =" in proc.stdout, f"ABC failed to parse {stem}.aig: {proc.stdout}"
            aig_xz = aig_dir / f"{stem}.aig.xz"
            with lzma.open(aig_xz, "wb", preset=6) as f:
                f.write(aig_raw.read_bytes())
            aig_raw.unlink()

            anf_xz = anf_dir / f"{stem}.anf.xz"
            subprocess.run(
                [sys.executable, str(TO_ANF), str(xcnf_xz), str(anf_xz), "--preset", "6", "--verify"],
                check=True,
            )

            expected_rows.append((f"{stem}.cnf", verdict))
            print(
                f"  [ok] {stem}: vars={nv:,} cls={orig_c:,} xors={nx:,} ands={a_ands:,} "
                f"| cnf={cnf_xz.stat().st_size/1024:.1f}KB aig={aig_xz.stat().st_size/1024:.1f}KB "
                f"xcnf={xcnf_xz.stat().st_size/1024:.1f}KB anf={anf_xz.stat().st_size/1024:.1f}KB",
                flush=True,
            )

    expected_rows.sort(key=lambda r: r[0])
    tsv_text = "\n".join(f"{name}\t{v}" for name, v in expected_rows) + "\n"
    (SUITE_DIR / "expected.tsv").write_text(tsv_text, encoding="utf-8", newline="\n")
    print(f"Wrote {SUITE_DIR / 'expected.tsv'} ({len(expected_rows)} rows).")


if __name__ == "__main__":
    main()
