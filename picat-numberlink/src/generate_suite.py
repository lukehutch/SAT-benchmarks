#!/usr/bin/env python3
"""Reproducible generator for `picat-numberlink` (Planar Numberlink Disjoint Paths).

Uses Picat 3.9#12 native SAT compiler (`import sat.` + `solve([$dump(...)], M)`)
faithfully implementing Neng-Fa Zhou's `numberlink_b.pi` Espresso-minimized Boolean
degree-PB formulation (`https://picat-lang.org/sat/numberlink_b.pi`, MPL-2.0) across
authentic upstream Numberlink grids (5x5 up to 42x25) plus 3 topological-crossing
endpoint-swap UNSAT counterparts (10x10, 12x12, 15x15).
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
UPSTREAM_DIR = SRC_DIR / "upstream"
REPO_ROOT = SUITE_DIR.parent

sys.path.insert(0, str(SRC_DIR))
import cnf2aig
import cnf2xcnf

TO_ANF = REPO_ROOT / "src" / "to_anf.py"

# (stem, INo in upstream hakank_numberlink.pi / numberlink_b.pi, optional terminal swap, expected verdict)
INSTANCES: list[tuple[str, int, str, str]] = [
    ("numberlink_5x5_p4", 2, "", "SAT"),
    ("numberlink_7x7_p5", 7, "", "SAT"),
    ("numberlink_10x10_p8", 1, "", "SAT"),
    ("numberlink_10x10_p8_swap", 1, "InputM[3,3] := 1, InputM[3,5] := 5,", "UNSAT"),
    ("numberlink_12x12_p10", 6, "", "SAT"),
    ("numberlink_12x12_p10_swap", 6, "InputM[3,3] := 5, InputM[3,10] := 1,", "UNSAT"),
    ("numberlink_15x15_p12", 3, "", "SAT"),
    ("numberlink_15x15_p12_swap", 3, "InputM[1,4] := 11, InputM[1,11] := 10,", "UNSAT"),
    ("numberlink_42x25_p62", 4, "", "SAT"),
]


def make_picat_source(ino: int, swap_stmt: str, out_cnf: Path, input_block: str) -> str:
    return f"""/* Auto-generated Picat-SAT Numberlink instance (numberlink_b.pi formulation, INo={ino}) */
import sat.

main =>
    inputM({ino}, NP, InputM),
    {swap_stmt}
    NR = InputM.length,
    NC = InputM[1].length,
    M = new_array(NP, NR, NC),
    M :: 0..1,
    foreach(R in 1..NR, C in 1..NC)
        sum([M[P,R,C] : P in 1..NP]) #= 1
    end,
    foreach(P in 1..NP, R in 1..NR, C in 1..NC)
        Neibs = [M[P,R1,C1] : (R1,C1) in [(R-1,C),(R+1,C),(R,C-1),(R,C+1)], (R1>=1, C1>=1, R1=<NR, C1=<NC)],
        (InputM[R,C]==P ->
            M[P,R,C] #= 1, sum(Neibs) #= 1
        ;
            M[P,R,C] #=> (sum(Neibs) #= 2)
        )
    end,
    solve([$dump("{out_cnf}")], M).

{input_block}
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
    cnf2aig.cnf_to_aiger(raw_cnf, tmp_aig, comment=f"picat-numberlink/{stem} (Picat 3.9#12 SAT)")
    with tmp_aig.open("rb") as fin, lzma.open(aig_xz, "wb", preset=6) as fout:
        shutil.copyfileobj(fin, fout)
    tmp_aig.unlink()

    cnf2xcnf.cnf_to_xcnf(raw_cnf, xcnf_xz)
    subprocess.run([sys.executable, str(TO_ANF), str(xcnf_xz), str(anf_xz)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--picat", default=os.environ.get("PICAT_BIN", "picat"))
    args = ap.parse_args()

    hak_nl = (UPSTREAM_DIR / "hakank_numberlink.pi").read_text(encoding="utf-8")
    input_block = hak_nl[hak_nl.index("inputM(INo,NP,M) ?=>") :]

    expected_rows: list[tuple[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="picat_nl_") as td:
        td_path = Path(td)
        for stem, ino, swap_stmt, verdict in INSTANCES:
            pi_file = td_path / f"{stem}.pi"
            raw_cnf = td_path / f"{stem}.cnf"
            pi_file.write_text(make_picat_source(ino, swap_stmt, raw_cnf, input_block), encoding="utf-8")
            subprocess.run([args.picat, str(pi_file)], check=True)
            convert_all_formats(raw_cnf, stem)
            expected_rows.append((f"{stem}.cnf", verdict))
            print(f"[picat-numberlink] generated {stem} ({verdict})")

    expected_rows.sort(key=lambda r: r[0])
    (SUITE_DIR / "expected.tsv").write_text(
        "".join(f"{inst}\t{v}\n" for inst, v in expected_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
