#!/usr/bin/env python3
"""Lossless converter for Victor Sigal's AES-256 XCNF benchmarks (`w5.solved.xcnf`, `w126.unsolved.xcnf`).

Produces:
  - `cnf-version/<stem>.cnf.xz`: exact Tseitin-encoded DIMACS CNF (splitting XOR clauses of length > 4
    via fresh auxiliary variables and expanding each parity constraint of length <= 4 into 2^{k-1} clauses).
  - `aig-version/<stem>.aig`: exact Binary AIGER 1.9 combinational miter (`L = 0, O = 1`, 256 primary inputs
    corresponding to the 256-bit AES-256 key, `PO_0 = 1` iff all 256 ciphertext output bits match target).
"""
from __future__ import annotations

import lzma
import sys
from collections import defaultdict
from pathlib import Path


def parse_xcnf(path: Path):
    num_vars = 0
    units: list[int] = []
    bins: list[tuple[int, int]] = []
    other_clauses: list[list[int]] = []
    xors: list[tuple[list[int], int]] = []
    with path.open("r", encoding="latin-1") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] == "c":
                continue
            if s[0] == "p":
                parts = s.split()
                if len(parts) >= 3:
                    num_vars = max(num_vars, int(parts[2]))
                continue
            toks = s.split()
            if toks[0].lower() == "x":
                lits = [int(t) for t in toks[1:] if t != "0"]
                rhs = 1
                vs: list[int] = []
                for l in lits:
                    if l < 0:
                        rhs ^= 1
                    v = abs(l)
                    num_vars = max(num_vars, v)
                    vs.append(v)
                xors.append((vs, rhs))
            else:
                lits = [int(t) for t in toks if t != "0"]
                for l in lits:
                    num_vars = max(num_vars, abs(l))
                if len(lits) == 1:
                    units.append(lits[0])
                elif len(lits) == 2:
                    bins.append((lits[0], lits[1]))
                elif lits:
                    other_clauses.append(lits)
    return num_vars, units, bins, other_clauses, xors


def write_tseitin_cnf_xz(num_vars: int, units, bins, other_clauses, xors, out_path: Path) -> tuple[int, int]:
    nvars = num_vars
    clauses: list[list[int]] = []
    for a, b in bins:
        clauses.append([a, b])
    for cl in other_clauses:
        clauses.append(list(cl))
    for u in units:
        clauses.append([u])

    for orig_vs, rhs in xors:
        # Cancel duplicates mod 2
        cnt: dict[int, int] = {}
        for v in orig_vs:
            cnt[v] = cnt.get(v, 0) ^ 1
        vs = [v for v, c in cnt.items() if c]
        while len(vs) > 4:
            nvars += 1
            t = nvars
            a, b, c = vs[0], vs[1], vs[2]
            # a ^ b ^ c ^ t = 0 (even parity -> forbid odd-weight assignments)
            for mask in range(16):
                if (mask.bit_count() & 1) == 1:
                    clauses.append([(-v if (mask >> i) & 1 else v) for i, v in enumerate((a, b, c, t))])
            vs = [t] + vs[3:]
        k = len(vs)
        for mask in range(1 << k):
            if (mask.bit_count() & 1) != rhs:
                clauses.append([(-v if (mask >> i) & 1 else v) for i, v in enumerate(vs)])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with lzma.open(out_path, "wt", encoding="ascii", preset=6) as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    return nvars, len(clauses)


def encode_varint(buf: bytearray, x: int) -> None:
    while x >= 0x80:
        buf.append((x & 0x7F) | 0x80)
        x >>= 7
    buf.append(x)


def write_binary_aig(num_vars: int, units, bins, xors, out_path: Path) -> tuple[int, int]:
    # Recover exact (2-bin + 3-xor) AND gates and XOR definitions!
    xor_def: dict[int, tuple[list[int], int]] = {vs[0]: (vs[1:], rhs) for vs, rhs in xors}
    and_gates: dict[int, tuple[int, int]] = {}
    # Match sequential pairs (-z, b), (-b, -d) where d = a ^ z (rhs == 0)
    i = 0
    while i + 1 < len(bins):
        a1, b1 = bins[i]
        a2, b2 = bins[i + 1]
        if a1 < 0 and b1 > 0 and a2 == -b1 and b2 < 0:
            z, b, d = -a1, b1, -b2
            if d in xor_def and xor_def[d][1] == 0 and len(xor_def[d][0]) == 2 and z in xor_def[d][0]:
                a = [x for x in xor_def[d][0] if x != z][0]
                and_gates[z] = (a, b)
                i += 2
                continue
        break

    deps: dict[int, tuple[int, ...]] = {}
    for z, (a, b) in and_gates.items():
        deps[z] = (a, b)
    for v, (rhs_vs, _) in xor_def.items():
        deps[v] = tuple(rhs_vs)

    u_map = {abs(u): (u > 0) for u in units}
    rdeps: dict[int, list[int]] = defaultdict(list)
    indeg: dict[int, int] = {}
    free: list[int] = []
    for v in range(1, num_vars + 1):
        if v in deps:
            indeg[v] = len(deps[v])
            for u in deps[v]:
                rdeps[u].append(v)
        else:
            free.append(v)

    unknown_pis = sorted(v for v in free if v not in u_map)
    known_outs = sorted(v for v in u_map if v in xor_def)

    # Topological sort
    q = list(free)
    order: list[int] = []
    for v in q:
        for nxt in rdeps[v]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                order.append(nxt)
                q.append(nxt)
    assert len(free) + len(order) == num_vars, f"Incomplete DAG: {len(free)+len(order)}/{num_vars}"

    # Build Binary AIGER 1.9 DAG (0 = FALSE, 1 = TRUE, inputs = 2, 4, ..., 2*I)
    aig_lit: dict[int, int] = {}
    next_var = 1
    for v in unknown_pis:
        aig_lit[v] = next_var * 2
        next_var += 1
    for v in free:
        if v in u_map:
            aig_lit[v] = 1 if u_map[v] else 0

    ands: list[tuple[int, int, int]] = []  # (lhs_even, rhs0, rhs1) with rhs0 >= rhs1
    strash: dict[tuple[int, int], int] = {}

    def mk_and(a: int, b: int) -> int:
        nonlocal next_var
        if a == 0 or b == 0 or a == (b ^ 1):
            return 0
        if a == 1:
            return b
        if b == 1 or a == b:
            return a
        if a < b:
            a, b = b, a
        key = (a, b)
        hit = strash.get(key)
        if hit is not None:
            return hit
        lhs = next_var * 2
        next_var += 1
        ands.append((lhs, a, b))
        strash[key] = lhs
        return lhs

    def mk_xor(a: int, b: int) -> int:
        if a == 0:
            return b
        if b == 0:
            return a
        if a == 1:
            return b ^ 1
        if b == 1:
            return a ^ 1
        if a == b:
            return 0
        if a == (b ^ 1):
            return 1
        # a ^ b = !( !(a & !b) & !(!a & b) )
        t1 = mk_and(a, b ^ 1)
        t2 = mk_and(a ^ 1, b)
        return mk_and(t1 ^ 1, t2 ^ 1) ^ 1

    for v in order:
        if v in and_gates:
            a, b = and_gates[v]
            aig_lit[v] = mk_and(aig_lit[a], aig_lit[b])
        else:
            rhs_vs, r = xor_def[v]
            acc = 1 if r else 0
            for u in rhs_vs:
                acc = mk_xor(acc, aig_lit[u])
            aig_lit[v] = acc

    # Miter PO_0: balanced AND tree of (aig_lit[out] == target_bit)
    assert_lits = [aig_lit[v] if u_map[v] else (aig_lit[v] ^ 1) for v in known_outs]
    while len(assert_lits) > 1:
        nxt_lits: list[int] = []
        for k in range(0, len(assert_lits), 2):
            if k + 1 < len(assert_lits):
                nxt_lits.append(mk_and(assert_lits[k], assert_lits[k + 1]))
            else:
                nxt_lits.append(assert_lits[k])
        assert_lits = nxt_lits
    po0 = assert_lits[0]

    I = len(unknown_pis)
    A = len(ands)
    M = I + A
    buf = bytearray()
    buf.extend(f"aig {M} {I} 0 1 {A}\n{po0}\n".encode("ascii"))
    for lhs, r0, r1 in ands:
        assert lhs > r0 >= r1
        encode_varint(buf, lhs - r0)
        encode_varint(buf, r0 - r1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(buf)
    return I, A


def main() -> None:
    suite_dir = Path(__file__).resolve().parent.parent
    for xcnf_path in sorted(suite_dir.glob("*.xcnf")):
        stem = xcnf_path.stem
        nvars, units, bins, other, xors = parse_xcnf(xcnf_path)
        cnf_out = suite_dir / "cnf-version" / f"{stem}.cnf.xz"
        aig_out = suite_dir / "aig-version" / f"{stem}.aig"
        cn, cm = write_tseitin_cnf_xz(nvars, units, bins, other, xors, cnf_out)
        ai, aa = write_binary_aig(nvars, units, bins, xors, aig_out)
        print(
            f"{xcnf_path.name}: XCNF({nvars}v, {len(units)+len(bins)+len(other)}cl, {len(xors)}xors) "
            f"-> CNF({cn}v, {cm}cl, {cnf_out.stat().st_size/1024:.1f}KB xz) "
            f"| AIG({ai}pi, {aa}ands, {aig_out.stat().st_size/1024:.1f}KB)"
        )


if __name__ == "__main__":
    main()
