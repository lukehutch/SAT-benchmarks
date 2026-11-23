#!/usr/bin/env python3
"""
Standalone DIMACS CNF generator and cycle verifier for Obstacle Knight's Tour
(Hamiltonian Cycle on Chessboards with Random Obstacle Pieces).

Problem definition:
  Given an R x C chessboard where a random subset B of squares is occupied by
  blocking obstacle pieces (sampled independently with probability d via Python's
  deterministic Mersenne Twister `random.Random(seed)`), decide whether the knight's
  graph on the unoccupied squares V = (R x C) \\ B contains a closed knight's tour
  (a Hamiltonian cycle visiting every unoccupied square exactly once).

CNF encoding (Directed 1-Factor + Strict Binary-Order MTZ Subtour Elimination):
  - Arc variables 1..=|A| correspond to directed knight moves (u -> v) between
    unoccupied squares in row-major order.
  - Exact-One out-arc and Exact-One in-arc at every unoccupied vertex (pairwise AMO
    for deg <= 6, Sinz sequential counter for deg in {7, 8}).
  - No 2-cycles: (-a_{u->v} | -a_{v->u}) for every undirected edge {u, v}.
  - Cycle reversal symmetry breaking at vertex 0: succ(0) < pred(0).
  - Strict binary-order Miller-Tucker-Zemlin (MTZ) rank constraints:
    a_{u->v} => rank(u) < rank(v) for all u, v != 0 using b = ceil(log2(|V|)) bits.

License: MIT
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

KNIGHT_MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

# Curated 10-instance balanced suite (5 SAT / 5 UNSAT), calibrated to take Frobenius 1C
# ~5-15s without timing out across repeated runs. Every board is 2-vertex-connected,
# color-balanced (|W| == |B|), and admits a spanning 2-factor (cycle cover), so every
# UNSAT instance fails strictly via global subtour entanglement.
CURATED_SUITE: list[tuple[str, int, int, float, int, str]] = [
    # (filename, rows, cols, density, seed, expected_status)
    ("knights_12x12_d15_obs16_s12150144_sat.cnf", 12, 12, 0.15, 12150144, "SAT"),
    ("knights_14x14_d26_obs52_s34280941_sat.cnf", 14, 14, 0.26, 34280941, "SAT"),
    ("knights_14x14_d20_obs34_s14203078_sat.cnf", 14, 14, 0.20, 14203078, "SAT"),
    ("knights_15x15_d24_obs55_s35244162_sat.cnf", 15, 15, 0.24, 35244162, "SAT"),
    ("knights_16x16_d25_obs66_s365029087_sat.cnf", 16, 16, 0.25, 365029087, "SAT"),
    ("knights_15x15_d22_obs41_s956712163_unsat.cnf", 15, 15, 0.22, 956712163, "UNSAT"),
    ("knights_15x15_d22_obs51_s756748105_unsat.cnf", 15, 15, 0.22, 756748105, "UNSAT"),
    ("knights_15x15_d21_obs55_s956405106_unsat.cnf", 15, 15, 0.21, 956405106, "UNSAT"),
    ("knights_15x15_d22_obs53_s756776522_unsat.cnf", 15, 15, 0.22, 756776522, "UNSAT"),
    ("knights_15x15_d21_obs51_s556324743_unsat.cnf", 15, 15, 0.21, 556324743, "UNSAT"),
]


def sample_obstacles(rows: int, cols: int, density: float, seed: int) -> set[tuple[int, int]]:
    rng = random.Random(seed)
    return {(r, c) for r in range(rows) for c in range(cols) if rng.random() < density}


def build_knight_graph(
    rows: int, cols: int, obstacles: set[tuple[int, int]]
) -> tuple[list[tuple[int, int]], list[list[int]]]:
    free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in obstacles]
    idx = {sq: i for i, sq in enumerate(free)}
    n = len(free)
    adj: list[list[int]] = [[] for _ in range(n)]
    for i, (r, c) in enumerate(free):
        for dr, dc in KNIGHT_MOVES:
            j = idx.get((r + dr, c + dc))
            if j is not None:
                adj[i].append(j)
    return free, adj


def encode_hamiltonian_cycle_cnf(
    n: int, adj: list[list[int]]
) -> tuple[int, list[list[int]], list[tuple[int, int]]]:
    """Encode undirected Hamiltonian cycle as DIMACS CNF. Returns (num_vars, clauses, arcs)."""
    arcs: list[tuple[int, int]] = []
    arc_var: dict[tuple[int, int], int] = {}
    out_arcs: list[list[int]] = [[] for _ in range(n)]
    in_arcs: list[list[int]] = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            var = len(arcs) + 1
            arcs.append((u, v))
            arc_var[(u, v)] = var
            out_arcs[u].append(var)
            in_arcs[v].append(var)

    next_var = len(arcs) + 1
    clauses: list[list[int]] = []

    def add_eo(lits: list[int]) -> None:
        nonlocal next_var
        clauses.append(list(lits))
        k = len(lits)
        if k <= 6:
            for i in range(k):
                for j in range(i + 1, k):
                    clauses.append([-lits[i], -lits[j]])
        else:
            s_base = next_var
            next_var += k - 1
            clauses.append([-lits[0], s_base])
            for i in range(1, k - 1):
                sp, sc = s_base + i - 1, s_base + i
                clauses.append([-lits[i], sc])
                clauses.append([-sp, sc])
                clauses.append([-lits[i], -sp])
            clauses.append([-lits[k - 1], -(s_base + k - 2)])

    for v in range(n):
        add_eo(out_arcs[v])
        add_eo(in_arcs[v])

    # Forbid 2-cycles
    for u, v in arcs:
        if u < v and (v, u) in arc_var:
            clauses.append([-arc_var[(u, v)], -arc_var[(v, u)]])

    # Break cycle reversal symmetry at root vertex 0: succ(0) < pred(0)
    nbrs0 = sorted(adj[0])
    for i in range(len(nbrs0)):
        for j in range(i):
            clauses.append([-arc_var[(0, nbrs0[i])], -arc_var[(nbrs0[j], 0)]])

    # Strict binary-order MTZ subtour elimination: a_{u->v} => rank(u) < rank(v) for u, v != 0
    bits = max(1, (n - 1).bit_length())
    r_var: list[list[int]] = [[] for _ in range(n)]
    for v in range(1, n):
        r_var[v] = list(range(next_var, next_var + bits))
        next_var += bits

    for a, (u, v) in enumerate(arcs, start=1):
        if u == 0 or v == 0:
            continue
        if bits == 1:
            clauses.append([-a, -r_var[u][0]])
            clauses.append([-a, r_var[v][0]])
            continue
        prev = a
        for b in range(bits - 1, 0, -1):
            ru, rv = r_var[u][b], r_var[v][b]
            clauses.append([-prev, -ru, rv])
            eq_b = next_var
            next_var += 1
            clauses.append([-prev, -ru, -rv, eq_b])
            clauses.append([-prev, ru, rv, eq_b])
            prev = eq_b
        clauses.append([-prev, -r_var[u][0]])
        clauses.append([-prev, r_var[v][0]])

    return next_var - 1, clauses, arcs


def write_cnf(
    out_path: Path,
    rows: int,
    cols: int,
    density: float,
    seed: int,
    status_hint: str | None = None,
) -> tuple[int, int, int, int]:
    obstacles = sample_obstacles(rows, cols, density, seed)
    free, adj = build_knight_graph(rows, cols, obstacles)
    nv, clauses, arcs = encode_hamiltonian_cycle_cnf(len(free), adj)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(
            f"c Obstacle Knight's Tour (Hamiltonian Cycle): {rows}x{cols} board, "
            f"density={density:.2f}, seed={seed}, obstacles={len(obstacles)}, free={len(free)}, arcs={len(arcs)}\n"
        )
        f.write(
            "c Encoding: directed 1-factor + no-2-cycles + root orientation + strict binary-order MTZ\n"
        )
        if status_hint:
            f.write(f"c Expected status: {status_hint}\n")
        # Compact ASCII board preview in comments ('#' = obstacle, '.' = free square)
        for r in range(rows):
            row_s = "".join("#" if (r, c) in obstacles else "." for c in range(cols))
            f.write(f"c board {r:02d}: {row_s}\n")
        f.write(f"p cnf {nv} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")
    return nv, len(clauses), len(obstacles), len(free)


def verify_tour_model(
    rows: int, cols: int, density: float, seed: int, model: dict[int, bool]
) -> tuple[bool, str]:
    """Decode and independently verify a closed knight's tour from a SAT assignment."""
    obstacles = sample_obstacles(rows, cols, density, seed)
    free, adj = build_knight_graph(rows, cols, obstacles)
    n = len(free)
    arcs = [(u, v) for u in range(n) for v in adj[u]]
    succ: dict[int, int] = {}
    for var, (u, v) in enumerate(arcs, start=1):
        if model.get(var, False):
            if u in succ:
                return False, f"vertex {u} has multiple outgoing arcs"
            succ[u] = v
    if len(succ) != n:
        return False, f"expected {n} active arcs, found {len(succ)}"
    visited: set[int] = set()
    cur = 0
    for _ in range(n):
        if cur in visited:
            return False, "disjoint subtour detected"
        visited.add(cur)
        nxt = succ[cur]
        r1, c1 = free[cur]
        r2, c2 = free[nxt]
        if sorted((abs(r1 - r2), abs(c1 - c2))) != [1, 2]:
            return False, f"illegal knight move {(r1, c1)} -> {(r2, c2)}"
        cur = nxt
    if cur != 0 or len(visited) != n:
        return False, "tour failed to visit all unoccupied squares and return to start"
    return True, "OK"


def main() -> None:
    ap = argparse.ArgumentParser(description="Obstacle Knight's Tour Hamiltonian Cycle CNF generator")
    ap.add_argument("--rows", type=int, default=15)
    ap.add_argument("--cols", type=int, default=15)
    ap.add_argument("--density", type=float, default=0.22)
    ap.add_argument("--seed", type=int, default=95303742)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument(
        "--generate-suite",
        type=Path,
        help="Generate the full curated 10-instance suite (CNF + AIG + XCNF) into directory",
    )
    args = ap.parse_args()

    if args.generate_suite:
        from cnf2aig import cnf_to_aiger
        from cnf2xcnf import cnf_to_xcnf

        suite_dir = args.generate_suite
        for fname, rows, cols, dens, seed, status in CURATED_SUITE:
            cnf_path = suite_dir / fname
            nv, nc, nobs, nfree = write_cnf(cnf_path, rows, cols, dens, seed, status)
            stem = cnf_path.stem
            aig_path = suite_dir / "aig-version" / f"{stem}.aig"
            xcnf_path = suite_dir / "xcnf-version" / f"{stem}.xcnf"
            _, _, na = cnf_to_aiger(
                cnf_path,
                aig_path,
                comment=f"Obstacle Knight's Tour: {rows}x{cols}, d={dens:.2f}, obs={nobs}, free={nfree}, seed={seed} ({status})",
            )
            _, _, rem_c, nx = cnf_to_xcnf(cnf_path, xcnf_path)
            print(
                f"  {fname:<46} obs={nobs:2d} free={nfree:3d} vars={nv:5d} cls={nc:5d} aig_ands={na:6d} xors={nx} [{status}]"
            )
        return

    out = args.output or Path(f"knights_{args.rows}x{args.cols}_d{int(round(args.density*100))}_s{args.seed}.cnf")
    nv, nc, nobs, nfree = write_cnf(out, args.rows, args.cols, args.density, args.seed)
    print(f"Wrote {out}: obs={nobs}, free={nfree}, vars={nv}, clauses={nc}")


if __name__ == "__main__":
    main()
