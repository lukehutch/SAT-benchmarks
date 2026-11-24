#!/usr/bin/env python3
"""Reproducible generator for `picat-mapf` (Multi-Agent Path Finding — Makespan).

Uses Picat 3.9#12 native SAT compiler (`import sat.` + `solve([$dump(...)], B)`)
faithfully implementing Roman Bartak & Neng-Fa Zhou's ICTAI'17 `mapf_makespan.pi`
(https://picat-lang.org/sat/mapf_makespan.pi, MPL-2.0): spacetime reachability pruning,
EO vertex occupancy per agent, Chen 2-product vertex-collision AMO, and adjacency
transitions across:
  - 2 tight bottleneck doorway makespan UNSAT (M*-1) / SAT (M*) brackets (`9x9` K=12, `11x11` K=18)
  - 3 upstream ICTAI'17 / MiniZinc `16x16` obstacle grids (`p10_a10`, `p20_a20`, `p20_a40`)
  - 1 verbatim built-in `mapf_makespan.pi` `32x32` 30-agent obstacle grid (`M=43`, 188k vars)
"""
from __future__ import annotations

import argparse
import lzma
import os
import re
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


def parse_dzn(path: Path) -> tuple[int, list[tuple[int, int]], list[list[int]]]:
    txt = path.read_text(encoding="utf-8")
    as_len = int(re.search(r"as_len\s*=\s*(\d+)", txt).group(1))
    m_as = re.search(r"as\s*=\s*array2d\([^,]+,[^,]+,\s*\[(.*?)\]\s*\)", txt, re.S)
    nums = [int(x) for x in re.findall(r"\d+", m_as.group(1))]
    agents = [(nums[2 * i], nums[2 * i + 1]) for i in range(as_len)]
    rel_len = int(re.search(r"rel_len\s*=\s*(\d+)", txt).group(1))
    m_rel = re.search(r"rel\s*=\s*\[(.*?)\]\s*;", txt, re.S)
    sets = re.findall(r"\{([^}]*)\}", m_rel.group(1))
    neibs = [[int(x) for x in re.findall(r"\d+", s)] for s in sets]
    assert len(neibs) == rel_len
    return rel_len, agents, neibs


def make_grid_graph(grid_lines: list[str]):
    rows, cols = len(grid_lines), len(grid_lines[0])
    vid: dict[tuple[int, int], int] = {}
    cnt = 0
    for r in range(rows):
        for c in range(cols):
            if grid_lines[r][c] == ".":
                cnt += 1
                vid[(r, c)] = cnt
    neibs: list[list[int]] = [[] for _ in range(cnt)]
    for (r, c), u in vid.items():
        nb = [u]
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            if (r + dr, c + dc) in vid:
                nb.append(vid[(r + dr, c + dc)])
        neibs[u - 1] = nb
    return cnt, vid, neibs


def make_graph_mapf_picat(n: int, agents: list[tuple[int, int]], neibs: list[list[int]], horizon: int, out_cnf: Path) -> str:
    rel_facts = ", ".join(f"$neibs({u + 1}, {neibs[u]})" for u in range(n))
    as_str = "[" + ",".join(f"({s},{g})" for s, g in agents) + "]"
    return f"""/* Auto-generated Picat-SAT MAPF makespan instance (N={n}, K={len(agents)}, M={horizon}) */
import sat.

main =>
    cl_facts([{rel_facts}], [$neibs(+,-)]),
    N = {n},
    As = to_array({as_str}),
    K = len(As),
    M = {horizon},
    M1 = M + 1,
    B = new_array(M1, K, N),
    foreach(A in 1..K)
        (V, FV) = As[A],
        B[1,A,V] = 1,
        B[M1,A,FV] = 1,
        DF = bfs_dist(N, V),
        DB = bfs_dist(N, FV),
        foreach(U in 1..N)
            D1 = DF[U],
            if D1 < 0 then
                foreach(T in 1..M1) B[T,A,U] = 0 end
            elseif D1 > 0 then
                foreach(T in 1..min(D1, M1)) B[T,A,U] = 0 end
            end,
            D2 = DB[U],
            if D2 < 0 then
                foreach(T in 1..M1) B[T,A,U] = 0 end
            elseif D2 > 0 then
                foreach(T in max(1, M1-D2+1)..M1) B[T,A,U] = 0 end
            end
        end
    end,
    B :: 0..1,
    foreach(T in 1..M1, A in 1..K)
        sum([B[T,A,V] : V in 1..N]) #= 1
    end,
    foreach(T in 1..M1, V in 1..N)
        sum([B[T,A,V] : A in 1..K]) #=< 1
    end,
    foreach(T in 1..M, A in 1..K, V in 1..N)
        if B[T,A,V] !== 0 then
            neibs(V, Neibs),
            B[T,A,V] #=> sum([B[T+1,A,U] : U in Neibs]) #>= 1
        end
    end,
    solve([$dump("{out_cnf}")], B).

bfs_dist(N, Src) = Dist =>
    Dist = new_array(N),
    foreach(I in 1..N) Dist[I] = -1 end,
    Dist[Src] := 0,
    Q = new_array(N),
    Q[1] := Src,
    Head = 1, Tail = 1,
    while (Head <= Tail)
        U = Q[Head], Head := Head + 1,
        D = Dist[U] + 1,
        neibs(U, Neibs),
        foreach(W in Neibs)
            if Dist[W] == -1 then
                Dist[W] := D,
                Tail := Tail + 1,
                Q[Tail] := W
            end
        end
    end.
"""


def make_builtin_32x32_picat(out_cnf: Path) -> str:
    orig = (UPSTREAM_DIR / "mapf_makespan.pi").read_text(encoding="utf-8")
    gen_rel_blk = orig[orig.index("gen_rel(M) =>") : orig.index("path(N,As) =>")]
    tail_blk = orig[orig.index("preprocess_forward(A,V,MaxT,N,B) =>") :]
    return f"""/* Verbatim built-in 32x32 30-agent instance from mapf_makespan.pi (M=LB=43) */
import sat.

main =>
    ins(M, As),
    gen_rel(M),
    N = max([max(Row) : Row in M]),
    AsArr = to_array(As),
    K = len(AsArr),
    lower_upper_bounds(As, LB, _UB),
    Hor = LB,
    M1 = Hor + 1,
    B = new_array(M1, K, N),
    foreach(A in 1..K)
        (V, FV) = AsArr[A],
        B[1,A,V] = 1,
        preprocess_forward(A, V, M1, N, B),
        B[M1,A,FV] = 1,
        preprocess_backward(A, FV, M1, N, B)
    end,
    B :: 0..1,
    foreach(T in 1..M1, A in 1..K)
        sum([B[T,A,V] : V in 1..N]) #= 1
    end,
    foreach(T in 1..M1, V in 1..N)
        sum([B[T,A,V] : A in 1..K]) #=< 1
    end,
    foreach(T in 1..Hor, A in 1..K, V in 1..N)
        neibs(V, Neibs),
        B[T,A,V] #=> sum([B[T+1,A,U] : U in Neibs]) #>= 1
    end,
    solve([$dump("{out_cnf}")], B).

{gen_rel_blk}
{tail_blk}
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
    cnf2aig.cnf_to_aiger(raw_cnf, tmp_aig, comment=f"picat-mapf/{stem} (Picat 3.9#12 SAT)")
    with tmp_aig.open("rb") as fin, lzma.open(aig_xz, "wb", preset=6) as fout:
        shutil.copyfileobj(fin, fout)
    tmp_aig.unlink()

    cnf2xcnf.cnf_to_xcnf(raw_cnf, xcnf_xz)
    subprocess.run([sys.executable, str(TO_ANF), str(xcnf_xz), str(anf_xz)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--picat", default=os.environ.get("PICAT_BIN", "picat"))
    args = ap.parse_args()

    # 1. Two-room 9x9 single-cell doorway bottleneck (N=73, K=12, LB=16, M*=19)
    g9 = [
        "....#....",
        "....#....",
        "....#....",
        "....#....",
        ".........",
        "....#....",
        "....#....",
        "....#....",
        "....#....",
    ]
    cnt9, vid9, nb9 = make_grid_graph(g9)
    agents9 = [
        (vid9[(0, 0)], vid9[(0, 8)]), (vid9[(0, 8)], vid9[(0, 0)]),
        (vid9[(2, 1)], vid9[(2, 7)]), (vid9[(2, 7)], vid9[(2, 1)]),
        (vid9[(4, 1)], vid9[(4, 7)]), (vid9[(4, 7)], vid9[(4, 1)]),
        (vid9[(6, 1)], vid9[(6, 7)]), (vid9[(6, 7)], vid9[(6, 1)]),
        (vid9[(8, 0)], vid9[(8, 8)]), (vid9[(8, 8)], vid9[(8, 0)]),
        (vid9[(4, 2)], vid9[(4, 6)]), (vid9[(4, 6)], vid9[(4, 2)]),
    ]

    # 2. Two-room 11x11 single-cell doorway bottleneck (N=111, K=18, LB=20, M*=25)
    g11 = [
        ".....#.....",
        ".....#.....",
        ".....#.....",
        ".....#.....",
        ".....#.....",
        "...........",
        ".....#.....",
        ".....#.....",
        ".....#.....",
        ".....#.....",
        ".....#.....",
    ]
    cnt11, vid11, nb11 = make_grid_graph(g11)
    agents11 = [
        (vid11[(0, 0)], vid11[(0, 10)]),   (vid11[(0, 10)], vid11[(0, 0)]),
        (vid11[(1, 1)], vid11[(1, 9)]),    (vid11[(1, 9)], vid11[(1, 1)]),
        (vid11[(3, 0)], vid11[(3, 10)]),   (vid11[(3, 10)], vid11[(3, 0)]),
        (vid11[(4, 2)], vid11[(4, 8)]),    (vid11[(4, 8)], vid11[(4, 2)]),
        (vid11[(5, 1)], vid11[(5, 9)]),    (vid11[(5, 9)], vid11[(5, 1)]),
        (vid11[(6, 2)], vid11[(6, 8)]),    (vid11[(6, 8)], vid11[(6, 2)]),
        (vid11[(7, 0)], vid11[(7, 10)]),   (vid11[(7, 10)], vid11[(7, 0)]),
        (vid11[(9, 1)], vid11[(9, 9)]),    (vid11[(9, 9)], vid11[(9, 1)]),
        (vid11[(10, 0)], vid11[(10, 10)]), (vid11[(10, 10)], vid11[(10, 0)]),
    ]

    jobs: list[tuple[str, str, str]] = []  # (stem, verdict, picat_code)
    with tempfile.TemporaryDirectory(prefix="picat_mapf_") as td:
        td_path = Path(td)

        # Tight bottleneck UNSAT/SAT brackets
        for stem, n, ag, nb, hor, verdict in [
            ("mapf_bn9x9_k12_m18", cnt9, agents9, nb9, 18, "UNSAT"),
            ("mapf_bn9x9_k12_m19", cnt9, agents9, nb9, 19, "SAT"),
            ("mapf_bn11x11_k18_m24", cnt11, agents11, nb11, 24, "UNSAT"),
            ("mapf_bn11x11_k18_m25", cnt11, agents11, nb11, 25, "SAT"),
        ]:
            raw_cnf = td_path / f"{stem}.cnf"
            jobs.append((stem, verdict, make_graph_mapf_picat(n, ag, nb, hor, raw_cnf)))

        # Upstream ICTAI'17 / MiniZinc 16x16 obstacle grids
        for dzn_name, stem, hor, verdict in [
            ("ins_g16_p10_a10.dzn", "mapf_g16_p10_a10_m19", 19, "SAT"),
            ("ins_g16_p20_a20.dzn", "mapf_g16_p20_a20_m23", 23, "SAT"),
            ("ins_g16_p20_a40.dzn", "mapf_g16_p20_a40_m22", 22, "SAT"),
        ]:
            n, ag, nb = parse_dzn(UPSTREAM_DIR / dzn_name)
            raw_cnf = td_path / f"{stem}.cnf"
            jobs.append((stem, verdict, make_graph_mapf_picat(n, ag, nb, hor, raw_cnf)))

        # Verbatim built-in 32x32 30-agent instance from mapf_makespan.pi
        stem32 = "mapf_32x32_k30_m43"
        jobs.append((stem32, "SAT", make_builtin_32x32_picat(td_path / f"{stem32}.cnf")))

        expected_rows: list[tuple[str, str]] = []
        for stem, verdict, code in jobs:
            pi_file = td_path / f"{stem}.pi"
            raw_cnf = td_path / f"{stem}.cnf"
            pi_file.write_text(code, encoding="utf-8")
            subprocess.run([args.picat, str(pi_file)], check=True)
            convert_all_formats(raw_cnf, stem)
            expected_rows.append((f"{stem}.cnf", verdict))
            print(f"[picat-mapf] generated {stem} ({verdict})")

    expected_rows.sort(key=lambda r: r[0])
    (SUITE_DIR / "expected.tsv").write_text(
        "".join(f"{inst}\t{v}\n" for inst, v in expected_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
