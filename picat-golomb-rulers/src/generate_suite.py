#!/usr/bin/env python3
"""Reproducible generator for `picat-golomb-rulers` (Optimal Golomb Rulers).

Uses Picat 3.9#12 native SAT compiler (`import sat.` + `solve([$dump(...)], Vars)`)
implementing Hakan Kjellerstrand & Neng-Fa Zhou's `golomb_ruler.pi` (MIT) across
tight optimal SAT (L*) and tight infeasible UNSAT (L*-1) brackets for M = 6..10 marks.
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

# OEIS A003022 optimal Golomb ruler lengths L*(M):
# M=6 -> 17, M=7 -> 25, M=8 -> 34, M=9 -> 44, M=10 -> 55.
INSTANCES: list[tuple[int, int, str]] = [
    (6, 16, "UNSAT"),
    (6, 17, "SAT"),
    (7, 24, "UNSAT"),
    (7, 25, "SAT"),
    (8, 33, "UNSAT"),
    (8, 34, "SAT"),
    (9, 43, "UNSAT"),
    (9, 44, "SAT"),
    (10, 54, "UNSAT"),
    (10, 55, "SAT"),
]


def make_picat_source(m: int, length: int, out_cnf: Path) -> str:
    return f"""/* Auto-generated Picat-SAT Golomb Ruler decision instance (M={m}, L={length}) */
import sat.

main =>
    N = {m},
    L = {length},
    Xs = new_list(N),
    Xs :: 0..L,
    Xs[1] #= 0,
    Xs[N] #= L,
    foreach(I in 2..N)
        Xs[I-1] #< Xs[I]
    end,
    Diffs = [D : I in 1..N-1, J in I+1..N, D #= Xs[J] - Xs[I]],
    Diffs :: 1..L,
    all_different(Diffs),
    % Reflection symmetry breaking (golomb_ruler.pi / MiniZinc golomb.mzn)
    Xs[2] - Xs[1] #< Xs[N] - Xs[N-1],
    solve([$dump("{out_cnf}")], Xs ++ Diffs).
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
    cnf2aig.cnf_to_aiger(raw_cnf, tmp_aig, comment=f"picat-golomb-rulers/{stem} (Picat 3.9#12 SAT)")
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
    with tempfile.TemporaryDirectory(prefix="picat_golomb_") as td:
        td_path = Path(td)
        for m, length, verdict in INSTANCES:
            stem = f"golomb_m{m}_l{length}"
            pi_file = td_path / f"{stem}.pi"
            raw_cnf = td_path / f"{stem}.cnf"
            pi_file.write_text(make_picat_source(m, length, raw_cnf), encoding="utf-8")
            subprocess.run([args.picat, str(pi_file)], check=True)
            convert_all_formats(raw_cnf, stem)
            expected_rows.append((f"{stem}.cnf", verdict))
            print(f"[picat-golomb-rulers] generated {stem} ({verdict})")

    expected_rows.sort(key=lambda r: r[0])
    (SUITE_DIR / "expected.tsv").write_text(
        "".join(f"{inst}\t{v}\n" for inst, v in expected_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
