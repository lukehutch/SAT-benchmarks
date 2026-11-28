#!/usr/bin/env python3
"""Reproducible generator for `picat-costas-arrays` (Costas Arrays).

Uses Picat 3.9#12 native SAT compiler (`import sat.` + `solve([$dump(...)], Vars)`)
faithfully implementing Hakan Kjellerstrand's `costas_array.pi` (based on Barry
O'Sullivan's MiniZinc `CostasArray.mzn`, MIT) across the SAT scaling ladder N = 8..16.
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

# Pure SAT scaling ladder N = 8..16 (all proven SAT; OEIS A008404 counts > 0 for all N <= 31).
INSTANCES: list[tuple[int, str]] = [(n, "SAT") for n in range(8, 17)]


def make_picat_source(n: int, out_cnf: Path) -> str:
    return f"""/* Auto-generated Picat-SAT Costas Array instance (N={n}) */
import sat.

main =>
    N = {n},
    Costas = new_list(N),
    Costas :: 1..N,
    Differences = new_array(N, N),
    DiffVars = vars(Differences),
    DiffVars :: -N+1..N-1,
    foreach(I in 1..N, J in 1..I)
        Differences[I,J] #= -N+1
    end,
    all_different(Costas),
    foreach(I in 1..N, J in I+1..N)
        Differences[I,J] #= Costas[J] - Costas[J-I]
    end,
    foreach(I in 1..N-1)
        all_different([Differences[I,J] : J in I+1..N])
    end,
    foreach(I in 1..N, J in I+1..N)
        Differences[I,J] #!= 0
    end,
    foreach(K in 3..N, L in K+1..N)
        Differences[K-2,L-1] + Differences[K,L] #= Differences[K-1,L-1] + Differences[K-1,L]
    end,
    % Standard MiniZinc reflection symmetry breaking
    Costas[1] #< Costas[N],
    solve([$dump("{out_cnf}")], Costas ++ DiffVars).
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
    cnf2aig.cnf_to_aiger(raw_cnf, tmp_aig, comment=f"picat-costas-arrays/{stem} (Picat 3.9#12 SAT)")
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
    with tempfile.TemporaryDirectory(prefix="picat_costas_") as td:
        td_path = Path(td)
        for n, verdict in INSTANCES:
            stem = f"costas_n{n}"
            pi_file = td_path / f"{stem}.pi"
            raw_cnf = td_path / f"{stem}.cnf"
            pi_file.write_text(make_picat_source(n, raw_cnf), encoding="utf-8")
            subprocess.run([args.picat, str(pi_file)], check=True)
            convert_all_formats(raw_cnf, stem)
            expected_rows.append((f"{stem}.cnf", verdict))
            print(f"[picat-costas-arrays] generated {stem} ({verdict})")

    expected_rows.sort(key=lambda r: r[0])
    (SUITE_DIR / "expected.tsv").write_text(
        "".join(f"{inst}\t{v}\n" for inst, v in expected_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
