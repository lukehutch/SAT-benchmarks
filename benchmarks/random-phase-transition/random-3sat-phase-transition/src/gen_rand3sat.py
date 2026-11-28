#!/usr/bin/env python3
"""
Generator for Uniform Random 3-SAT Phase-Transition Benchmarks (n = 200).

Generates 8 instances (4 SAT / 4 UNSAT) spanning the classic easy-hard-easy
curve around the critical clause-to-variable phase transition alpha_c ~= 4.26:
  - Under-constrained (SAT side):  alpha in {3.80, 4.00, 4.10}
  - Critical threshold:            alpha = 4.26 (1 SAT + 1 UNSAT)
  - Over-constrained (UNSAT side): alpha in {4.45, 4.65, 5.00}

Also writes native CNFs to `../cnf-orig/`, Binary AIGER 1.9 conversions to
`../aig-converted/`, and CryptoMiniSat `.xcnf` conversions to `../xcnf-converted/`.
"""
from __future__ import annotations

import lzma
import random
import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent
CNF_DIR = SUITE_DIR / "cnf-orig"
AIG_DIR = SUITE_DIR / "aig-converted"
XCNF_DIR = SUITE_DIR / "xcnf-converted"

INSTANCES = [
    ("rand3sat_n200_r380_sat",   200,  760, 203800, "SAT"),
    ("rand3sat_n200_r400_sat",   200,  800, 204000, "SAT"),
    ("rand3sat_n200_r410_sat",   200,  820, 204100, "SAT"),
    ("rand3sat_n200_sat",        200,  852, 200000, "SAT"),
    ("rand3sat_n200_unsat",      200,  852, 200005, "UNSAT"),
    ("rand3sat_n200_r445_unsat", 200,  890, 204450, "UNSAT"),
    ("rand3sat_n200_r465_unsat", 200,  930, 204650, "UNSAT"),
    ("rand3sat_n200_r500_unsat", 200, 1000, 205000, "UNSAT"),
]


def gen_uniform_3sat(n: int, m: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    clauses: list[list[int]] = []
    vars_pool = list(range(1, n + 1))
    for _ in range(m):
        vs = rng.sample(vars_pool, 3)
        clauses.append([v if rng.getrandbits(1) else -v for v in vs])
    return clauses


def write_dimacs(path: Path, n: int, clauses: list[list[int]], seed: int, ans: str) -> None:
    opener = (lambda p: lzma.open(p, "wt", preset=6)) if path.suffix == ".xz" else (lambda p: open(p, "w"))
    with opener(path) as f:
        f.write(f"c Uniform Random 3-SAT at m/n={len(clauses)/n:.2f}, seed={seed}, expected={ans}\n")
        f.write(f"p cnf {n} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")


def main() -> None:
    sys.path.insert(0, str(SUITE_DIR / "src"))
    sys.path.insert(0, str(SUITE_DIR.parent / "sat-competition-2024-2026-main-track" / "src"))
    from cnf2aig import cnf_to_aiger
    from cnf2xcnf import cnf_to_xcnf

    CNF_DIR.mkdir(parents=True, exist_ok=True)
    AIG_DIR.mkdir(parents=True, exist_ok=True)
    XCNF_DIR.mkdir(parents=True, exist_ok=True)
    for name, n, m, seed, ans in INSTANCES:
        cnf_path = CNF_DIR / f"{name}.cnf.xz"
        aig_path = AIG_DIR / f"{name}.aig.xz"
        xcnf_path = XCNF_DIR / f"{name}.xcnf.xz"
        if not cnf_path.exists():
            clauses = gen_uniform_3sat(n, m, seed)
            write_dimacs(cnf_path, n, clauses, seed, ans)
        if not aig_path.exists():
            _, _, ands = cnf_to_aiger(
                cnf_path, aig_path, comment=f"benchmark={name}\nseed={seed}\nexpected={ans}\norigin=CNF"
            )
            print(f"Generated cnf-orig/{cnf_path.name} ({n} vars, {m} clauses) & aig-converted/{aig_path.name} ({ands} ANDs)")
        if not xcnf_path.exists():
            cnf_to_xcnf(cnf_path, xcnf_path)
            print(f"Generated xcnf-converted/{xcnf_path.name}")


if __name__ == "__main__":
    main()
