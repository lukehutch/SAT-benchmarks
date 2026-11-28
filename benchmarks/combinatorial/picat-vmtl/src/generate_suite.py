#!/usr/bin/env python3
"""Reproducible generator for `picat-vmtl` (Vertex Magic Total Labeling on K_n).

Uses Picat 3.9#12 native SAT compiler (`import sat.` + `solve([$dump(...)], Vars)`)
faithfully implementing Neng-Fa Zhou's `vmtl.pi` (https://picat-lang.org/sat/vmtl.pi,
MPL-2.0), fixing the magic constant K across tight SAT/UNSAT brackets for N = 4..10.

Produces all 4 lossless `.xz` formats:
  - `cnf-orig/*.cnf.xz`       (native Picat-SAT DIMACS CNF)
  - `aig-converted/*.aig.xz`  (Binary AIGER 1.9 via `cnf2aig.py`)
  - `xcnf-converted/*.xcnf.xz`(CryptoMiniSat XCNF via `cnf2xcnf.py`)
  - `anf-converted/*.anf.xz`  (DIMACS-ANF via `../../src/to_anf.py`)
"""
from __future__ import annotations

import argparse
import lzma
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = SUITE_DIR / "src"
REPO_ROOT = SUITE_DIR.parent

sys.path.insert(0, str(SRC_DIR))
import cnf2aig
import cnf2xcnf

TO_ANF = REPO_ROOT / "src" / "to_anf.py"

# Exact curated ladder across K_4..K_10:
# For K_n, M = n(n+1)/2 labels in 1..M satisfy n*K + sum(V_i) = M(M+1), giving the exact
# arithmetic feasibility range K_min(n) = ceil(n(n^2+3)/4) .. K_max(n) = floor(n(n+1)^2/4).
# Any K < K_min(n) or K > K_max(n) is mathematically UNSAT; for K_4, K=19 is also UNSAT
# (feasible K in {20, 21, 23}).
INSTANCES: list[tuple[int, int, str]] = [
    (4, 19, "UNSAT"),
    (5, 34, "UNSAT"),
    (5, 35, "SAT"),
    (6, 58, "UNSAT"),
    (6, 59, "SAT"),
    (7, 111, "SAT"),
    (8, 148, "SAT"),
    (9, 207, "SAT"),
    (10, 257, "UNSAT"),
    (10, 280, "SAT"),
]


def make_picat_source(n: int, k: int, out_cnf: Path) -> str:
    return f"""/* Auto-generated wrapper for Neng-Fa Zhou's vmtl.pi (K_{n}, K={k}) */
import sat.

main =>
    NV = {n},
    VVars = new_array(NV),
    EVars = new_array(NV, NV),
    foreach(I in 1..NV) EVars[I,I] = 0 end,
    foreach(I in 1..NV-1, J in I+1..NV) EVars[I,J] = EVars[J,I] end,
    Vars = vars((VVars, EVars)),
    NE = NV*(NV-1) div 2,
    Vars :: 1..(NV+NE),
    K = {k},
    all_different(Vars),
    foreach(I in 1..NV)
        VVars[I] + sum([EVars[I,J] : J in 1..NV]) #= K
    end,
    solve([$dump("{out_cnf}")], Vars).
"""


def convert_all_formats(raw_cnf: Path, stem: str) -> None:
    cnf_xz = SUITE_DIR / "cnf-orig" / f"{stem}.cnf.xz"
    aig_xz = SUITE_DIR / "aig-converted" / f"{stem}.aig.xz"
    xcnf_xz = SUITE_DIR / "xcnf-converted" / f"{stem}.xcnf.xz"
    anf_xz = SUITE_DIR / "anf-converted" / f"{stem}.anf.xz"
    for d in (cnf_xz.parent, aig_xz.parent, xcnf_xz.parent, anf_xz.parent):
        d.mkdir(parents=True, exist_ok=True)

    with raw_cnf.open("rb") as fin, lzma.open(cnf_xz, "wb", preset=6) as fout:
        shutil.copyfileobj(fin, fout)

    tmp_aig = raw_cnf.with_suffix(".aig")
    cnf2aig.cnf_to_aiger(raw_cnf, tmp_aig, comment=f"picat-vmtl/{stem} (Picat 3.9#12 SAT)")
    with tmp_aig.open("rb") as fin, lzma.open(aig_xz, "wb", preset=6) as fout:
        shutil.copyfileobj(fin, fout)
    tmp_aig.unlink()

    cnf2xcnf.cnf_to_xcnf(raw_cnf, xcnf_xz)
    subprocess.run([sys.executable, str(TO_ANF), str(xcnf_xz), str(anf_xz)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--picat", default=os.environ.get("PICAT_BIN", "picat"))
    args = ap.parse_args()

    expected_rows: list[tuple[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="picat_vmtl_") as td:
        td_path = Path(td)
        for n, k, verdict in INSTANCES:
            stem = f"vmtl_n{n}_k{k}"
            pi_file = td_path / f"{stem}.pi"
            raw_cnf = td_path / f"{stem}.cnf"
            pi_file.write_text(make_picat_source(n, k, raw_cnf), encoding="utf-8")
            subprocess.run([args.picat, str(pi_file)], check=True)
            convert_all_formats(raw_cnf, stem)
            expected_rows.append((f"{stem}.cnf", verdict))
            print(f"[picat-vmtl] generated {stem} ({verdict})")

    expected_rows.sort(key=lambda r: r[0])
    (SUITE_DIR / "expected.tsv").write_text(
        "".join(f"{inst}\t{v}\n" for inst, v in expected_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
