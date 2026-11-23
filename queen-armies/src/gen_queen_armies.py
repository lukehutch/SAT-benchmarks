#!/usr/bin/env python3
"""
Standalone DIMACS CNF generator and witness verifier for the Peaceable Queen Armies problem.

Inspired by:
  - Christopher Wolfram, "Chess Queen Armies With SAT Solvers" (September 2022),
    https://christopherwolfram.com/projects/queen-armies/
  - Rosetta Code, "Peaceful Chess Queen Armies"
  - OEIS A250000 (2 armies), A277433 (3 armies), A277434 (4 armies)
  - Robert A. Bosch, "Peaceably Coexisting Armies of Queens" (Optima, 1999)
  - Barbara M. Smith, Karen E. Petrie, and Ian P. Gent, "Models and Symmetry Breaking
    for 'Peaceably Coexisting Armies of Queens'" (CPAIOR 2004)

Problem definition:
  Place A armies of at least k queens each on an R x C chessboard such that no queen
  from army a attacks any queen from a different army b != a along any row, column, or
  diagonal (same-army queens are allowed to attack one another).

CNF encoding:
  - Queen variables q(r, c, a) = 1 + a*(R*C) + r*C + c for 0 <= r < R, 0 <= c < C, 0 <= a < A.
  - Line-occupancy variables L(line) (for A = 2: single polarity variable per row/col/diag so
    q(r,c,0) => L and q(r,c,1) => !L; for A >= 3: L(line, a) with pairwise mutual exclusion
    !L(line, a) | !L(line, b) across distinct armies a < b).
  - Cardinality constraints sum_{r,c} q(r, c, a) >= k encoded via Sinz (2005) monotone
    sequential counters.

License: MIT
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Curated 8-instance balanced suite (4 SAT / 4 UNSAT) across A in {2, 3, 4} armies,
# calibrated to take Frobenius 1C ~5-15s without timing out across repeated runs.
CURATED_SUITE: list[tuple[str, int, int, int, int, str]] = [
    # (filename, num_armies, rows, cols, k, expected_status)
    ("queen_armies_a3_13x16_k14_sat.cnf", 3, 13, 16, 14, "SAT"),
    ("queen_armies_a4_14x16_k9_sat.cnf", 4, 14, 16, 9, "SAT"),
    ("queen_armies_a2_15x16_k33_sat.cnf", 2, 15, 16, 33, "SAT"),
    ("queen_armies_a3_15x16_k16_sat.cnf", 3, 15, 16, 16, "SAT"),
    ("queen_armies_a3_7x8_k5_unsat.cnf", 3, 7, 8, 5, "UNSAT"),
    ("queen_armies_a3_6x10_k5_unsat.cnf", 3, 6, 10, 5, "UNSAT"),
    ("queen_armies_a3_6x11_k6_unsat.cnf", 3, 6, 11, 6, "UNSAT"),
    ("queen_armies_a2_7x10_k12_unsat.cnf", 2, 7, 10, 12, "UNSAT"),
]


def _add_sinz_at_least(
    lits: list[int], k: int, next_var: int, clauses: list[list[int]]
) -> int:
    """Sinz (2005) sequential counter enforcing sum(lits) >= k."""
    n = len(lits)
    if k <= 0:
        return next_var
    if k > n:
        clauses.append([])
        return next_var

    s: dict[tuple[int, int], int] = {}
    for i in range(n):
        hi = min(i + 1, k)
        for j in range(hi):
            s[(i, j)] = next_var
            next_var += 1

    clauses.append([-s[(0, 0)], lits[0]])
    for i in range(1, n):
        hi = min(i + 1, k)
        prev_hi = min(i, k)
        clauses.append([-s[(i, 0)], lits[i], s[(i - 1, 0)]])
        for j in range(1, hi):
            if j < prev_hi:
                clauses.append([-s[(i, j)], s[(i - 1, j)], lits[i]])
                clauses.append([-s[(i, j)], s[(i - 1, j - 1)]])
            else:
                clauses.append([-s[(i, j)], lits[i]])
                clauses.append([-s[(i, j)], s[(i - 1, j - 1)]])

    clauses.append([s[(n - 1, k - 1)]])
    return next_var


def encode_queen_armies(
    rows: int, cols: int, k: int, num_armies: int = 2
) -> tuple[int, list[list[int]]]:
    """Encode Peaceable Queen Armies as DIMACS CNF. Returns (num_vars, clauses)."""
    n_sq = rows * cols
    next_var = n_sq * num_armies + 1
    clauses: list[list[int]] = []

    def qvar(r: int, c: int, a: int) -> int:
        return 1 + a * n_sq + r * cols + c

    lines: list[list[tuple[int, int]]] = []
    for r in range(rows):
        lines.append([(r, c) for c in range(cols)])
    for c in range(cols):
        lines.append([(r, c) for r in range(rows)])
    for d in range(-(cols - 1), rows):
        sq = [(r, r - d) for r in range(rows) if 0 <= r - d < cols]
        if len(sq) >= 2:
            lines.append(sq)
    for diag in range(rows + cols - 1):
        sq = [(r, diag - r) for r in range(rows) if 0 <= diag - r < cols]
        if len(sq) >= 2:
            lines.append(sq)

    if num_armies == 2:
        for sq in lines:
            lvar = next_var
            next_var += 1
            for r, c in sq:
                clauses.append([-qvar(r, c, 0), lvar])
                clauses.append([-qvar(r, c, 1), -lvar])
    else:
        for sq in lines:
            lvars = list(range(next_var, next_var + num_armies))
            next_var += num_armies
            for a in range(num_armies):
                for r, c in sq:
                    clauses.append([-qvar(r, c, a), lvars[a]])
            for a in range(num_armies):
                for b in range(a + 1, num_armies):
                    clauses.append([-lvars[a], -lvars[b]])

    for a in range(num_armies):
        lits = [qvar(r, c, a) for r in range(rows) for c in range(cols)]
        next_var = _add_sinz_at_least(lits, k, next_var, clauses)

    return next_var - 1, clauses


def write_cnf(
    out_path: Path,
    rows: int,
    cols: int,
    k: int,
    num_armies: int,
    status_hint: str | None = None,
) -> tuple[int, int]:
    nv, clauses = encode_queen_armies(rows, cols, k, num_armies)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(
            f"c Peaceable Queen Armies: {num_armies} armies of k={k} queens on a {rows}x{cols} board\n"
        )
        f.write(
            "c Encoding: line-occupancy non-attacking constraints + Sinz (2005) sequential counter (>= k)\n"
        )
        f.write("c Reference: https://christopherwolfram.com/projects/queen-armies/\n")
        if status_hint:
            f.write(f"c Expected status: {status_hint}\n")
        f.write(f"p cnf {nv} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")
    return nv, len(clauses)


def verify_model(
    rows: int, cols: int, k: int, num_armies: int, model: dict[int, bool]
) -> tuple[bool, str]:
    """Independently verify that a DIMACS assignment encodes a valid Peaceable Queen Armies placement."""
    n_sq = rows * cols
    armies: list[list[tuple[int, int]]] = [[] for _ in range(num_armies)]
    for a in range(num_armies):
        for r in range(rows):
            for c in range(cols):
                var = 1 + a * n_sq + r * cols + c
                if model.get(var, False):
                    armies[a].append((r, c))
        if len(armies[a]) < k:
            return False, f"army {a} has {len(armies[a])} queens (< {k})"
    for a in range(num_armies):
        for b in range(a + 1, num_armies):
            for r1, c1 in armies[a]:
                for r2, c2 in armies[b]:
                    if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                        return (
                            False,
                            f"attack between army {a} at ({r1},{c1}) and army {b} at ({r2},{c2})",
                        )
    return True, "OK"


def main() -> None:
    ap = argparse.ArgumentParser(description="Peaceable Queen Armies DIMACS CNF generator")
    ap.add_argument("--armies", type=int, default=2, help="Number of opposing queen armies (A >= 2)")
    ap.add_argument("--rows", type=int, default=8, help="Board rows (R)")
    ap.add_argument("--cols", type=int, default=8, help="Board columns (C)")
    ap.add_argument("--size", type=int, default=9, help="Queens per army (k)")
    ap.add_argument("-o", "--output", type=Path, help="Output .cnf path")
    ap.add_argument(
        "--generate-suite",
        type=Path,
        help="Generate the full curated 8-instance suite (CNF + AIG + XCNF) into directory",
    )
    args = ap.parse_args()

    if args.generate_suite:
        from cnf2aig import cnf_to_aiger
        from cnf2xcnf import cnf_to_xcnf

        suite_dir = args.generate_suite
        for fname, A, rows, cols, k, status in CURATED_SUITE:
            cnf_path = suite_dir / fname
            nv, nc = write_cnf(cnf_path, rows, cols, k, A, status)
            stem = cnf_path.stem
            aig_path = suite_dir / "aig-version" / f"{stem}.aig"
            xcnf_path = suite_dir / "xcnf-version" / f"{stem}.xcnf"
            _, _, na = cnf_to_aiger(
                cnf_path,
                aig_path,
                comment=f"Peaceable Queen Armies: A={A}, {rows}x{cols}, k={k} ({status})",
            )
            _, _, rem_c, nx = cnf_to_xcnf(cnf_path, xcnf_path)
            print(
                f"  {fname:<36} vars={nv:5d} cls={nc:5d} aig_ands={na:6d} xors={nx} [{status}]"
            )
        return

    out = args.output or Path(f"queen_armies_a{args.armies}_{args.rows}x{args.cols}_k{args.size}.cnf")
    nv, nc = write_cnf(out, args.rows, args.cols, args.size, args.armies)
    print(f"Wrote {out}: vars={nv}, clauses={nc}")


if __name__ == "__main__":
    main()
