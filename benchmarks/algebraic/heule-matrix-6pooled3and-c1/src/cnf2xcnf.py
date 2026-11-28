#!/usr/bin/env python3
"""
Exact, lossless DIMACS CNF (.cnf / .cnf.xz) -> CryptoMiniSat XCNF (.xcnf / .xcnf.xz) converter.

Detects exact 2^{k-1}-clause XOR parity blocks over identical sorted variable tuples
(arity k in {3, 4, 5, 6}, i.e., 4, 8, 16, or 32 clauses whose negated-literal counts
all share even or odd parity) and collapses each complete XOR block into a single
native CryptoMiniSat parity clause:

    x l1 l2 ... lk 0

following the CryptoMiniSat XCNF convention:
  - odd parity  (v1 ^ v2 ^ ... ^ vk = 1): all positive literals  `x v1 v2 ... vk 0`
  - even parity (v1 ^ v2 ^ ... ^ vk = 0): first literal negated  `x -v1 v2 ... vk 0`

Every clause not belonging to a complete 2^{k-1}-clause XOR block is preserved verbatim.
"""
from __future__ import annotations

import lzma
import sys
from collections import defaultdict
from pathlib import Path

MIN_XOR_K = 3
MAX_XOR_K = 6


def cnf_to_xcnf(cnf_path: Path, xcnf_path: Path) -> tuple[int, int, int, int]:
    """Convert DIMACS CNF to XCNF. Returns (num_vars, orig_clauses, out_clauses, out_xors)."""
    opener = lzma.open if str(cnf_path).endswith(".xz") else open
    num_vars = 0
    comments: list[str] = []
    clauses: list[list[int]] = []
    cur: list[int] = []

    with opener(cnf_path, "rt", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s[0] == "c":
                if len(comments) < 32:
                    comments.append(s)
                continue
            if s[0] == "%":
                break
            if s[0] == "p":
                parts = s.split()
                if len(parts) >= 3:
                    num_vars = max(num_vars, int(parts[2]))
                continue
            for tok in s.split():
                lit = int(tok)
                if lit == 0:
                    clauses.append(cur)
                    cur = []
                else:
                    num_vars = max(num_vars, abs(lit))
                    cur.append(lit)
    if cur:
        clauses.append(cur)

    # Group non-tautological, duplicate-free clauses of length k in [3, 6] by sorted var tuple.
    groups: dict[tuple[int, ...], dict[int, list[int]]] = defaultdict(dict)
    for idx, cl in enumerate(clauses):
        k = len(cl)
        if not (MIN_XOR_K <= k <= MAX_XOR_K):
            continue
        # Deduplicate literals and skip tautologies or duplicate vars.
        seen: dict[int, int] = {}
        ok = True
        for l in cl:
            v = abs(l)
            if v in seen:
                ok = False
                break
            seen[v] = l
        if not ok:
            continue
        vtuple = tuple(sorted(seen.keys()))
        neg_mask = 0
        for bit_i, v in enumerate(vtuple):
            if seen[v] < 0:
                neg_mask |= 1 << bit_i
        groups[vtuple].setdefault(neg_mask, []).append(idx)

    consumed: set[int] = set()
    xors: list[tuple[tuple[int, ...], int]] = []  # (vtuple, rhs in {0, 1})

    for vtuple, mask_map in groups.items():
        k = len(vtuple)
        need = 1 << (k - 1)
        if len(mask_map) < need:
            continue
        # In a clause (l_1 | ... | l_k), the single falsified assignment sets x_i = (l_i < 0).
        # Thus a clause with `popcount(neg_mask)` negated literals forbids an assignment of
        # Hamming weight `popcount(neg_mask)`.
        # - Forbidding ALL odd-weight assignments  => XOR(vtuple) = 0 (even parity, rhs = 0)
        # - Forbidding ALL even-weight assignments => XOR(vtuple) = 1 (odd parity,  rhs = 1)
        even_masks = [m for m in mask_map if (m.bit_count() & 1) == 0]
        odd_masks = [m for m in mask_map if (m.bit_count() & 1) == 1]

        # If BOTH halves are present (UNSAT contradiction), keep as raw clauses or emit both;
        # emit each complete half cleanly so exact semantics are always preserved.
        if len(odd_masks) == need:
            idxs = [mask_map[m][0] for m in odd_masks]
            if not any(i in consumed for i in idxs):
                consumed.update(idxs)
                xors.append((vtuple, 0))
        if len(even_masks) == need:
            idxs = [mask_map[m][0] for m in even_masks]
            if not any(i in consumed for i in idxs):
                consumed.update(idxs)
                xors.append((vtuple, 1))

    rem_clauses = [cl for i, cl in enumerate(clauses) if i not in consumed]
    total_lines = len(rem_clauses) + len(xors)

    xcnf_path.parent.mkdir(parents=True, exist_ok=True)
    out_opener = (lambda p: lzma.open(p, "wt", preset=6)) if str(xcnf_path).endswith(".xz") else (lambda p: open(p, "w"))
    with out_opener(xcnf_path) as out:
        for c in comments:
            out.write(c + "\n")
        out.write(f"c XCNF conversion: extracted {len(xors)} native XOR clauses ({len(consumed)} CNF clauses collapsed)\n")
        out.write(f"p cnf {num_vars} {total_lines}\n")
        for cl in rem_clauses:
            out.write(" ".join(str(x) for x in cl) + " 0\n")
        for vtuple, rhs in xors:
            lits = list(vtuple)
            if rhs == 0:
                lits[0] = -lits[0]
            out.write("x " + " ".join(str(x) for x in lits) + " 0\n")

    return num_vars, len(clauses), len(rem_clauses), len(xors)


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.cnf[.xz]> <output.xcnf[.xz]>", file=sys.stderr)
        sys.exit(2)
    nv, orig_c, rem_c, nx = cnf_to_xcnf(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Wrote {sys.argv[2]}: vars={nv}, orig_clauses={orig_c}, rem_clauses={rem_c}, xors={nx}")


if __name__ == "__main__":
    main()
