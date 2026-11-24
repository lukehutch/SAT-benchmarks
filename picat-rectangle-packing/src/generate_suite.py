#!/usr/bin/env python3
"""Reproducible generator for `picat-rectangle-packing` (2D Square/Rectangle Packing).

Uses Picat 3.9#12 native SAT compiler (`import sat.` + `solve([$dump(...)], Vars)`)
implementing 2D non-overlapping consecutive-square packing (`1x1..nxn` into a fixed
`H x W` bounding box) via Picat's native `diffn` + redundant `cumulative` constraints
and centroid symmetry breaking, combining `hakank/picat/perfect_square_placement.pi`
and MiniZinc `rectangle-packing/rect_packing.mzn` (MIT).
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

# Tight area-sufficient UNSAT (W*H >= sum i^2 yet geometrically unpackable) vs optimal/tight SAT pairs:
#   n=8  (sum=204):  13x16=208 UNSAT vs 14x15=210 SAT (optimal)
#   n=10 (sum=385):  20x20=400 UNSAT vs 15x27=405 SAT (optimal)
#   n=12 (sum=650):  25x26=650 UNSAT vs 23x29=667 SAT (optimal)
#   n=14 (sum=1015): 31x33=1023 UNSAT vs 23x45=1035 SAT (optimal)
#   n=17 (sum=1785): 40x45=1800 UNSAT vs 41x44=1804 SAT (tight feasible)
INSTANCES: list[tuple[int, int, int, str]] = [
    (8, 13, 16, "UNSAT"),
    (8, 14, 15, "SAT"),
    (10, 20, 20, "UNSAT"),
    (10, 15, 27, "SAT"),
    (12, 25, 26, "UNSAT"),
    (12, 23, 29, "SAT"),
    (14, 31, 33, "UNSAT"),
    (14, 23, 45, "SAT"),
    (17, 40, 45, "UNSAT"),
    (17, 41, 44, "SAT"),
]


def make_picat_source(n: int, h: int, w: int, out_cnf: Path) -> str:
    return f"""/* Auto-generated Picat-SAT 2D Rectangle Packing instance (1..{n} squares in {h}x{w}) */
import sat.

main =>
    N = {n},
    H = {h},
    W = {w},
    S = [I : I in 1..N],
    X = new_list(N),
    Y = new_list(N),
    foreach(I in 1..N)
        X[I] :: 0..(W - I),
        Y[I] :: 0..(H - I)
    end,
    Rects = [[X[I], Y[I], I, I] : I in 1..N],
    diffn(Rects),
    cumulative(X, S, S, H),
    cumulative(Y, S, S, W),
    % MiniZinc rect_packing.mzn reflection symmetry breaking on largest square N
    2 * X[N] #=< W - N,
    2 * Y[N] #=< H - N,
    solve([$dump("{out_cnf}")], X ++ Y).
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
    cnf2aig.cnf_to_aiger(raw_cnf, tmp_aig, comment=f"picat-rectangle-packing/{stem} (Picat 3.9#12 SAT)")
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
    with tempfile.TemporaryDirectory(prefix="picat_rpack_") as td:
        td_path = Path(td)
        for n, h, w, verdict in INSTANCES:
            stem = f"rpack_n{n}_{h}x{w}"
            pi_file = td_path / f"{stem}.pi"
            raw_cnf = td_path / f"{stem}.cnf"
            pi_file.write_text(make_picat_source(n, h, w, raw_cnf), encoding="utf-8")
            subprocess.run([args.picat, str(pi_file)], check=True)
            convert_all_formats(raw_cnf, stem)
            expected_rows.append((f"{stem}.cnf", verdict))
            print(f"[picat-rectangle-packing] generated {stem} ({verdict})")

    expected_rows.sort(key=lambda r: r[0])
    (SUITE_DIR / "expected.tsv").write_text(
        "".join(f"{inst}\t{v}\n" for inst, v in expected_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
