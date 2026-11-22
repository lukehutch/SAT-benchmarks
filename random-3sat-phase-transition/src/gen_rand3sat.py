#!/usr/bin/env python3
"""
Generator for Critical Phase-Transition Uniform Random 3-SAT Benchmarks (m/n = 4.26).

Reproduces `rand3sat_n200_sat.cnf` (Python Random seed 200000) and
`rand3sat_n200_unsat.cnf` (seed 200005), plus their Binary AIGER 1.9 conversions
in `../aig-version/`.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent
AIG_DIR = SUITE_DIR / "aig-version"

INSTANCES = [
    ("rand3sat_n200_sat", 200, 852, 200000, "SAT"),
    ("rand3sat_n200_unsat", 200, 852, 200005, "UNSAT"),
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
    with open(path, "w") as f:
        f.write(f"c Uniform Random 3-SAT at phase transition m/n={len(clauses)/n:.2f}, seed={seed}, expected={ans}\n")
        f.write(f"p cnf {n} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")


def main() -> None:
    sys.path.insert(0, str(SUITE_DIR.parent / "sat-competition-2024-2026-main-track" / "src"))
    from cnf2aig import cnf_to_aiger

    AIG_DIR.mkdir(parents=True, exist_ok=True)
    for name, n, m, seed, ans in INSTANCES:
        cnf_path = SUITE_DIR / f"{name}.cnf"
        aig_path = AIG_DIR / f"{name}.aig"
        clauses = gen_uniform_3sat(n, m, seed)
        write_dimacs(cnf_path, n, clauses, seed, ans)
        _, _, ands = cnf_to_aiger(
            cnf_path, aig_path, comment=f"benchmark={name}\nseed={seed}\nexpected={ans}\norigin=CNF"
        )
        print(f"Generated {cnf_path.name} ({n} vars, {m} clauses) & aig-version/{aig_path.name} ({ands} ANDs)")


if __name__ == "__main__":
    main()
