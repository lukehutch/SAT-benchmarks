#!/usr/bin/env python3
"""
Exact Binary AIGER 1.9 converter for DIMACS CNF files (.cnf or .cnf.xz).

Constructs a logically equivalent combinational AIG miter (L=0, O=1) over the
exact N DIMACS variables as primary inputs:
  - Clause C = (l_1 | ... | l_k)  =>  !(!l_1 & ... & !l_k)  (balanced AND tree)
  - Formula F = C_1 & ... & C_m   =>  PO_0                  (balanced AND tree)
PO_0 evaluates to 1 iff the assignment satisfies every clause in the CNF.
"""
from __future__ import annotations

import lzma
import sys
from pathlib import Path


def _encode_varint(x: int, out: bytearray) -> None:
    while x >= 0x80:
        out.append((x & 0x7F) | 0x80)
        x >>= 7
    out.append(x)


def cnf_to_aiger(cnf_path: Path, aig_path: Path, comment: str = "") -> tuple[int, int, int]:
    """Convert DIMACS CNF (`.cnf` or `.cnf.xz`) to Binary AIGER 1.9 (`.aig` or `.aig.xz`)."""
    opener = lzma.open if str(cnf_path).endswith(".xz") else open
    num_vars = 0
    clauses: list[list[int]] = []
    cur: list[int] = []
    with opener(cnf_path, "rt", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] == "c":
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

    ands: list[tuple[int, int]] = []
    table: dict[tuple[int, int], int] = {}

    def mk_and(a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        if a == 1:
            return b
        if b == 1:
            return a
        if a == b:
            return a
        if (a ^ b) == 1:
            return 0
        if a < b:
            a, b = b, a
        hit = table.get((a, b))
        if hit is not None:
            return hit
        lhs = (num_vars + 1 + len(ands)) << 1
        ands.append((a, b))
        table[(a, b)] = lhs
        return lhs

    def balanced_and(lits: list[int]) -> int:
        if not lits:
            return 1
        while len(lits) > 1:
            nxt: list[int] = []
            i = 0
            n = len(lits)
            while i + 1 < n:
                g = mk_and(lits[i], lits[i + 1])
                if g == 0:
                    return 0
                nxt.append(g)
                i += 2
            if i < n:
                nxt.append(lits[i])
            lits = nxt
        return lits[0]

    cl_lits: list[int] = []
    unsat = False
    for cl in clauses:
        if not cl:
            unsat = True
            break
        a_lits = sorted({(abs(l) << 1) | (1 if l < 0 else 0) for l in cl})
        if any((a_lits[i] ^ a_lits[i + 1]) == 1 for i in range(len(a_lits) - 1)):
            continue  # tautology
        neg_conj = balanced_and([l ^ 1 for l in a_lits])
        cl_lits.append(neg_conj ^ 1)

    out_lit = 0 if unsat else balanced_and(cl_lits)
    m = num_vars + len(ands)
    buf = bytearray(f"aig {m} {num_vars} 0 1 {len(ands)}\n{out_lit}\n".encode("ascii"))
    for k, (rhs0, rhs1) in enumerate(ands):
        lhs = (num_vars + 1 + k) << 1
        _encode_varint(lhs - rhs0, buf)
        _encode_varint(rhs0 - rhs1, buf)
    if comment:
        buf.extend(b"c\n")
        for line in comment.splitlines():
            buf.extend(line.encode("utf-8") + b"\n")
    aig_path.parent.mkdir(parents=True, exist_ok=True)
    if str(aig_path).endswith(".xz"):
        aig_path.write_bytes(lzma.compress(bytes(buf), preset=6))
    else:
        aig_path.write_bytes(buf)
    return num_vars, len(clauses), len(ands)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: cnf2aig.py <input.cnf[.xz]> <output.aig[.xz]>", file=sys.stderr)
        sys.exit(2)
    nv, nc, na = cnf_to_aiger(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Wrote {sys.argv[2]}: inputs={nv}, clauses={nc}, and_gates={na}")


if __name__ == "__main__":
    main()
