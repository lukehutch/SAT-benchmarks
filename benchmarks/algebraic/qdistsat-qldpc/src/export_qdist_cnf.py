#!/usr/bin/env python3
"""
Standalone zero-dependency DIMACS CNF / XCNF / Binary AIGER 1.9 exporter for
CSS Quantum LDPC minimum-distance SAT decision instances.

Given CSS X-stabilizer matrix H_x (m x n over F_2), Z-stabilizer orthogonal logical basis
G_z (k x n over F_2, satisfying H_z * G_z^T = 0, i.e. G_z spans ker(H_z) / row(H_x)),
and weight bound w:
  - Variables 1..n represent the Z-operator support vector z in F_2^n.
  - Commutation with X stabilizers: H_x * z = 0 (mod 2).
  - Non-triviality (z not in rowspace(H_z)): since ker(H_z) = row(H_x) + row(G_z) and
    H_x * z = 0, z in row(H_z) iff G_z * z = 0 (mod 2). Hence z is a non-trivial Z-logical
    iff exists i in 1..k with G_z[i] * z = 1 (mod 2).
  - Hamming weight bound: sum_{j=1}^n z_j <= w (Sinz 2005 sequential counter).

Resulting formula is SAT iff the Z-distance satisfies d_Z <= w, and UNSAT iff d_Z > w.
"""
from __future__ import annotations

import lzma
import pathlib
import sys


def load_binary_matrix(path: pathlib.Path) -> list[list[int]]:
    rows: list[list[int]] = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        rows.append([int(x) & 1 for x in s.split()])
    return rows


def add_xor_cnf(clauses: list[list[int]], lits: list[int], rhs: int, next_var: list[int]) -> None:
    """Encode XOR(lits) = rhs (0 or 1) using Tseitin 3-XOR splitting."""
    if not lits:
        if rhs:
            clauses.append([])
        return
    if len(lits) == 1:
        clauses.append([lits[0] if rhs else -lits[0]])
        return
    if len(lits) == 2:
        a, b = lits
        if rhs:
            clauses.append([a, b])
            clauses.append([-a, -b])
        else:
            clauses.append([a, -b])
            clauses.append([-a, b])
        return
    cur = list(lits)
    while len(cur) > 3:
        a, b = cur[0], cur[1]
        t = next_var[0]
        next_var[0] += 1
        # t <-> (a ^ b)
        clauses.append([-a, -b, -t])
        clauses.append([a, b, -t])
        clauses.append([a, -b, t])
        clauses.append([-a, b, t])
        cur = [t] + cur[2:]
    a, b, c = cur
    if rhs:
        # odd parity: forbid 000, 011, 101, 110
        clauses.append([a, b, c])
        clauses.append([a, -b, -c])
        clauses.append([-a, b, -c])
        clauses.append([-a, -b, c])
    else:
        # even parity: forbid 100, 010, 001, 111
        clauses.append([-a, b, c])
        clauses.append([a, -b, c])
        clauses.append([a, b, -c])
        clauses.append([-a, -b, -c])


def add_sinz_atmost_k(clauses: list[list[int]], vars_list: list[int], k: int, next_var: list[int]) -> None:
    """Sinz (2005) sequential counter encoding of sum(vars_list) <= k."""
    n = len(vars_list)
    if k >= n:
        return
    if k == 0:
        for v in vars_list:
            clauses.append([-v])
        return
    # s[i][j] for i in 0..n-1, j in 0..k-1
    s = [[0] * k for _ in range(n - 1)]
    for i in range(n - 1):
        for j in range(k):
            s[i][j] = next_var[0]
            next_var[0] += 1
    clauses.append([-vars_list[0], s[0][0]])
    for j in range(1, k):
        clauses.append([-s[0][j]])
    for i in range(1, n - 1):
        clauses.append([-vars_list[i], s[i][0]])
        clauses.append([-s[i - 1][0], s[i][0]])
        for j in range(1, k):
            clauses.append([-vars_list[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-vars_list[i], -s[i - 1][k - 1]])
    clauses.append([-vars_list[n - 1], -s[n - 2][k - 1]])


def encode_css_z_distance(
    hx_path: pathlib.Path,
    gz_path: pathlib.Path,
    w: int,
    out_cnf: pathlib.Path,
    out_xcnf: pathlib.Path | None = None,
) -> tuple[int, int]:
    hx = load_binary_matrix(hx_path)
    gz = load_binary_matrix(gz_path)
    # Sanity-check against Hz if present alongside Hx: every row of Gz must commute with Hz
    hz_path = hx_path.with_name(hx_path.name.replace("_Hx.txt", "_Hz.txt"))
    if hz_path.exists():
        hz = load_binary_matrix(hz_path)
        for r1 in hz:
            for r2 in gz:
                assert sum(a & b for a, b in zip(r1, r2)) % 2 == 0, "Hz * Gz^T != 0!"
    n = len(hx[0])
    next_var = [n + 1]
    cnf_clauses: list[list[int]] = []
    xcnf_xors: list[tuple[list[int], int]] = []
    xcnf_clauses: list[list[int]] = []

    # 1. H_x * z = 0 (mod 2)
    for row in hx:
        supp = [j + 1 for j, bit in enumerate(row) if bit]
        if supp:
            add_xor_cnf(cnf_clauses, supp, 0, next_var)
            xcnf_xors.append((supp, 0))

    # 2. Non-triviality: g_i <-> XOR(G_z[i] * z), and OR_i g_i
    g_vars: list[int] = []
    for row in gz:
        supp = [j + 1 for j, bit in enumerate(row) if bit]
        if not supp:
            continue
        gv = next_var[0]
        next_var[0] += 1
        g_vars.append(gv)
        # gv ^ XOR(supp) = 0  <=>  gv = XOR(supp)
        add_xor_cnf(cnf_clauses, [gv] + supp, 0, next_var)
        xcnf_xors.append(([gv] + supp, 0))
    cnf_clauses.append(g_vars)
    xcnf_clauses.append(g_vars)

    # 3. Sinz sequential counter sum_{j=1}^n z_j <= w
    sinz_clauses: list[list[int]] = []
    add_sinz_atmost_k(sinz_clauses, list(range(1, n + 1)), w, next_var)
    cnf_clauses.extend(sinz_clauses)
    xcnf_clauses.extend(sinz_clauses)

    num_vars = next_var[0] - 1
    out_cnf.parent.mkdir(parents=True, exist_ok=True)
    cnf_opener = (lambda path: lzma.open(path, "wt", preset=6)) if out_cnf.suffix == ".xz" else (lambda path: open(path, "w"))
    with cnf_opener(out_cnf) as f:
        f.write(f"c CSS Quantum LDPC Z-distance decision problem (n={n}, w<={w})\n")
        f.write(f"p cnf {num_vars} {len(cnf_clauses)}\n")
        for cl in cnf_clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")

    if out_xcnf is not None:
        out_xcnf.parent.mkdir(parents=True, exist_ok=True)
        xcnf_opener = (lambda path: lzma.open(path, "wt", preset=6)) if out_xcnf.suffix == ".xz" else (lambda path: open(path, "w"))
        with xcnf_opener(out_xcnf) as f:
            f.write(f"c CSS Quantum LDPC Z-distance XCNF (n={n}, w<={w})\n")
            f.write(f"p cnf {num_vars} {len(xcnf_clauses) + len(xcnf_xors)}\n")
            for cl in xcnf_clauses:
                f.write(" ".join(str(x) for x in cl) + " 0\n")
            for supp, rhs in xcnf_xors:
                # CryptoMiniSat x-clause: odd parity (rhs=1) directly; even parity negates first lit
                xl = list(supp)
                if rhs == 0:
                    xl[0] = -xl[0]
                f.write("x " + " ".join(str(x) for x in xl) + " 0\n")

    return num_vars, len(cnf_clauses)


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: export_qdist_cnf.py <Hx.txt> <Gz.txt> <w> <out.cnf[.xz]> [out.xcnf[.xz]]", file=sys.stderr)
        sys.exit(2)
    out_x = pathlib.Path(sys.argv[5]) if len(sys.argv) > 5 else None
    nv, nc = encode_css_z_distance(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3]), pathlib.Path(sys.argv[4]), out_x)
    print(f"Wrote {sys.argv[4]}: vars={nv}, clauses={nc}")


if __name__ == "__main__":
    main()
