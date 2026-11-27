#!/usr/bin/env python3
"""Lossless Linear-Size Converter to Standard DIMACS-ANF (.anf / .anf.xz).

Converts combinational AIGER (.aig / .aag, optional .xz/.gz/.bz2) and
DIMACS CNF / CryptoMiniSat XCNF (.cnf / .xcnf, optional .xz/.gz/.bz2)
into standard Bosphorus/PolyBoRi DIMACS-ANF:

    p anf <nv> <neq>
    x <mon1> <mon2> ... 0

Convention (matching Frobenius `solver/src/formats.rs` and CryptoMiniSat XCNF):
  - `x t1 t2 ... tk 0` asserts `t1 XOR t2 XOR ... XOR tk == 1` over GF(2).
  - `T` denotes the constant `1`, so `x T t1 t2 ... tk 0` asserts `t1 XOR ... XOR tk == 0`.
  - Monomial products use `.` (e.g. `1.2` = x1 * x2, `1.2.3` = x1 * x2 * x3).
  - Empty equation `x 0` asserts `0 == 1` (UNSAT); `x T 0` asserts `0 == 0` (tautology).

Guarantees:
  - From AIGER: recovers 3-AND `Xor(a, b)` patterns as degree-1 linear equations,
    inlines single-fanout XOR intermediates feeding only XORs/assertions,
    unpacks top-level positive AND assertion trees, and encodes each remaining
    AND gate `z = l0 & l1` as a single degree-2 quadratic polynomial (<= 4 monomials).
    Strictly O(|V|) linear size, degree <= 2. Original PIs retain IDs 1..=I.
  - From CNF/XCNF: preserves every `x l1 ... lk 0` XOR clause verbatim as a single
    degree-1 linear ANF equation; encodes every regular clause of length k <= 3
    directly into a single degree-<=3 ANF polynomial with 0 auxiliary variables;
    splits any clause of length k >= 4 via balanced linear-size Tseitin (`t = l1 | l2`,
    1 quadratic eq per split, exactly k-3 aux vars) so degree <= 3 and size is
    strictly O(sum |C|) with zero 2^k blowup. Original vars retain IDs 1..=orig_nv.
"""

import argparse
import bz2
from collections import Counter
import gzip
import lzma
import os
import random
import subprocess
import sys
import time


# ============================================================================
# Transparent Compressed I/O
# ============================================================================

def read_bytes_auto(path: str) -> bytes:
    with open(path, "rb") as f:
        data = f.read()
    if data[:6] == b"\xfd7zXZ\x00":
        return lzma.decompress(data)
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    if data[:3] == b"BZh":
        return bz2.decompress(data)
    return data


def write_text_auto(path: str, text: str, xz_preset: int = 3) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    raw = text.encode("ascii")
    low = path.lower()
    if low.endswith(".xz"):
        with lzma.open(path, "wb", preset=xz_preset) as f:
            f.write(raw)
    elif low.endswith(".gz"):
        with gzip.open(path, "wb", compresslevel=6) as f:
            f.write(raw)
    elif low.endswith(".bz2"):
        with bz2.open(path, "wb", compresslevel=6) as f:
            f.write(raw)
    else:
        with open(path, "wb") as f:
            f.write(raw)


def strip_comp_ext(path: str) -> str:
    low = path.lower()
    for ext in (".xz", ".gz", ".bz2", ".zst"):
        if low.endswith(ext):
            return path[:-len(ext)]
    return path


def detect_input_kind(path: str, raw: bytes) -> str:
    inner = strip_comp_ext(path).lower()
    if inner.endswith(".aig") or inner.endswith(".aag"):
        return "aiger"
    if inner.endswith(".cnf") or inner.endswith(".xcnf") or inner.endswith(".dimacs"):
        return "xcnf"
    if raw.startswith(b"aig ") or raw.startswith(b"aag "):
        return "aiger"
    return "xcnf"


# ============================================================================
# DIMACS-ANF Formatter & Independent Verifier
# ============================================================================

def format_anf_line(mons, rhs: int) -> str:
    """Format `(mons, rhs)` where `XOR_{m in mons} prod(m) == rhs` (1-based vars)."""
    parts = ["x"]
    if rhs == 0:
        parts.append("T")
    for m in mons:
        if len(m) == 1:
            parts.append(str(m[0]))
        else:
            parts.append(".".join(str(v) for v in m))
    parts.append("0")
    return " ".join(parts)


def parse_dimacs_anf_text(text: str):
    """Independent reference DIMACS-ANF parser for --verify."""
    hdr_nv = 0
    hdr_neq = 0
    max_v = 0
    max_deg = 0
    eqs = []
    for raw_line in text.splitlines():
        s = raw_line.strip()
        if not s or s.startswith("c") or s.startswith("#"):
            continue
        if s.startswith("p "):
            parts = s.split()
            if len(parts) < 4 or parts[1] != "anf":
                raise ValueError(f"Bad p anf header: {s}")
            hdr_nv = int(parts[2])
            hdr_neq = int(parts[3])
            continue
        if s.startswith("x") or s.startswith("X"):
            s = s[1:].strip()
        rhs = 1
        mons = []
        for tok in s.split():
            if tok == "0":
                break
            if tok == "T" or tok.lower() == "true":
                rhs ^= 1
                continue
            if tok.startswith("-"):
                rhs ^= 1
                tok = tok[1:]
            facs = tuple(sorted(set(int(x) for x in tok.split(".") if x)))
            if facs:
                if facs[-1] > max_v:
                    max_v = facs[-1]
                if len(facs) > max_deg:
                    max_deg = len(facs)
                mons.append(facs)
        eqs.append((mons, rhs))
    return hdr_nv, hdr_neq, max_v, max_deg, eqs


def eval_anf_eqs(eqs, vals_1based) -> bool:
    for mons, rhs in eqs:
        acc = 0
        for m in mons:
            p = 1
            for v in m:
                if not vals_1based[v]:
                    p = 0
                    break
            acc ^= p
        if acc != rhs:
            return False
    return True


# ============================================================================
# AIGER (Binary 1.9 + ASCII) Parser & Linear-Size Degree-<=2 ANF Converter
# ============================================================================

def parse_aiger_bytes(data: bytes):
    nl = data.index(b"\n")
    hdr = data[:nl].decode("ascii").strip().split()
    if len(hdr) < 6 or hdr[0] not in ("aig", "aag"):
        raise ValueError(f"Unsupported AIGER header: {hdr}")
    is_bin = hdr[0] == "aig"
    M, I, L, O, A = map(int, hdr[1:6])
    if L != 0:
        raise ValueError(f"Sequential AIGER (L={L}) not supported")
    if O == 0:
        raise ValueError("AIGER file has O=0 outputs")

    pos = nl + 1
    n = len(data)

    def next_line() -> str:
        nonlocal pos
        end = data.find(b"\n", pos)
        if end == -1:
            end = n
        s = data[pos:end].decode("ascii").strip()
        pos = min(end + 1, n)
        return s

    outputs = []
    ands = []
    if is_bin:
        if I + A != M:
            raise ValueError(f"Binary AIGER requires I+A==M (got I={I}, A={A}, M={M})")
        for _ in range(O):
            outputs.append(int(next_line().split()[0]))
        for i in range(A):
            lhs = (I + 1 + i) << 1
            d0 = 0
            sh = 0
            while True:
                b = data[pos]
                pos += 1
                d0 |= (b & 0x7F) << sh
                if (b & 0x80) == 0:
                    break
                sh += 7
            d1 = 0
            sh = 0
            while True:
                b = data[pos]
                pos += 1
                d1 |= (b & 0x7F) << sh
                if (b & 0x80) == 0:
                    break
                sh += 7
            r0 = lhs - d0
            r1 = r0 - d1
            ands.append((r0, r1))
    else:
        in_map = {}
        for idx in range(I):
            lit = int(next_line().split()[0])
            in_map[lit >> 1] = idx + 1
        raw_outs = [int(next_line().split()[0]) for _ in range(O)]
        raw_defs = {}
        order = []
        for _ in range(A):
            lhs, r0, r1 = map(int, next_line().split()[:3])
            v = lhs >> 1
            raw_defs[v] = (r0, r1)
            order.append(v)
        remap = {0: 0}
        remap.update(in_map)
        nxt = I + 1
        for v in order:
            remap[v] = nxt
            nxt += 1

        def ml(l: int) -> int:
            v = l >> 1
            return (remap[v] << 1) | (l & 1) if v > 0 else (l & 1)

        for v in order:
            r0, r1 = raw_defs[v]
            ands.append((ml(r0), ml(r1)))
        outputs = [ml(po) for po in raw_outs]

    return I, outputs, ands


def eval_aiger(num_inputs: int, outputs, ands, pi_vals_1based):
    """Evaluate raw AIGER forward; return `(all_pos_true, vals_1based)`."""
    vals = [0] * (num_inputs + len(ands) + 1)
    for i in range(1, num_inputs + 1):
        vals[i] = 1 if pi_vals_1based[i] else 0
    for idx, (r0, r1) in enumerate(ands):
        v0, n0 = r0 >> 1, r0 & 1
        v1, n1 = r1 >> 1, r1 & 1
        b0 = (vals[v0] if v0 else 0) ^ n0
        b1 = (vals[v1] if v1 else 0) ^ n1
        vals[num_inputs + 1 + idx] = b0 & b1
    ok = True
    for po in outputs:
        pv, pn = po >> 1, po & 1
        if ((vals[pv] if pv else 0) ^ pn) == 0:
            ok = False
            break
    return ok, vals


def _toggle_mon(mons: set, m: tuple) -> None:
    if m in mons:
        mons.remove(m)
    else:
        mons.add(m)


def _expand_and_lits(v0: int, n0: int, v1: int, n1: int):
    """Return `(mons_set, const_parity)` for `(x_{v0} ^ n0) * (x_{v1} ^ n1)` with 1-based vars (0 = const 0)."""
    if v0 == 0:
        if n0 == 0:
            return set(), 0
        # 1 * (v1 ^ n1)
        if v1 == 0:
            return set(), n1
        return {(v1,)}, n1
    if v1 == 0:
        if n1 == 0:
            return set(), 0
        return {(v0,)}, n0
    if v0 == v1:
        if n0 != n1:
            return set(), 0  # x & !x == 0
        return {(v0,)}, n0  # (x ^ n0)^2 == x ^ n0
    a, na, b, nb = (v0, n0, v1, n1) if v0 < v1 else (v1, n1, v0, n0)
    mons = {(a, b)}
    if na:
        _toggle_mon(mons, (b,))
    if nb:
        _toggle_mon(mons, (a,))
    const = na & nb
    return mons, const


def convert_aiger_to_anf(data: bytes, source_name: str = ""):
    num_inputs, outputs, ands = parse_aiger_bytes(data)
    num_ands = len(ands)
    max_var = num_inputs + num_ands

    # Step 1: Detect 3-AND XOR patterns: `!(x1 & y1) & !(!x1 & !y1) == x1 ^ y1`.
    xors = {}
    for i, (r0, r1) in enumerate(ands):
        if (r0 & 1) == 1 and (r1 & 1) == 1:
            v0, v1 = r0 >> 1, r1 >> 1
            if num_inputs < v0 <= max_var and num_inputs < v1 <= max_var:
                x1, y1 = ands[v0 - num_inputs - 1]
                x2, y2 = ands[v1 - num_inputs - 1]
                if (x1 == (x2 ^ 1) and y1 == (y2 ^ 1)) or (x1 == (y2 ^ 1) and y1 == (x2 ^ 1)):
                    xors[num_inputs + 1 + i] = (x1, y1)

    # Step 2: Unpack top-level positive AND conjunction trees on POs (stopping at 3-AND XORs).
    raw_asserts = []
    stack = list(reversed(outputs))
    while stack:
        lit = stack.pop()
        v = lit >> 1
        if (lit & 1) == 0 and num_inputs < v <= max_var and v not in xors:
            r0, r1 = ands[v - num_inputs - 1]
            stack.append(r1)
            stack.append(r0)
        else:
            raw_asserts.append(lit)
    # Deduplicate preserving order
    seen_a = set()
    asserts = []
    for l in raw_asserts:
        if l not in seen_a:
            seen_a.add(l)
            asserts.append(l)

    # Step 3: Active COI over XOR + AND gates.
    needed = set()
    work = []
    for lit in asserts:
        v = lit >> 1
        if v > num_inputs and v not in needed:
            needed.add(v)
            work.append(v)
    while work:
        v = work.pop()
        c0, c1 = xors[v] if v in xors else ands[v - num_inputs - 1]
        for c in (c0 >> 1, c1 >> 1):
            if c > num_inputs and c not in needed:
                needed.add(c)
                work.append(c)

    # Step 4: Count active fanout to inline single-fanout XOR intermediates (feeding only XORs/asserts)
    # and single-fanout negated-AND top-level assertions (`!And(l0, l1) == 1` => `l0 * l1 == 0`).
    fo = Counter()
    fo_and = Counter()
    fo_assert_neg = Counter()
    for lit in asserts:
        v = lit >> 1
        fo[v] += 1
        if (lit & 1) == 1:
            fo_assert_neg[v] += 1
    for v in needed:
        c0, c1 = xors[v] if v in xors else ands[v - num_inputs - 1]
        is_x = v in xors
        for c in (c0 >> 1, c1 >> 1):
            fo[c] += 1
            if not is_x:
                fo_and[c] += 1

    # Inline single-fanout XOR gates whose sole consumer is an XOR or assertion (bounded width <= 256).
    inlined_xor = set()
    xor_expanded = {}  # v -> (frozenset_of_orig_vars, parity_bit)
    for v in sorted(needed):
        if v not in xors:
            continue
        if fo[v] == 1 and fo_and[v] == 0:
            c0, c1 = xors[v]
            v0, n0 = c0 >> 1, c0 & 1
            v1, n1 = c1 >> 1, c1 & 1
            if v0 in xor_expanded:
                s0, p0 = xor_expanded[v0]
                p0 ^= n0
            else:
                s0, p0 = ({v0} if v0 > 0 else set()), n0
            if v1 in xor_expanded:
                s1, p1 = xor_expanded[v1]
                p1 ^= n1
            else:
                s1, p1 = ({v1} if v1 > 0 else set()), n1
            sym = s0 ^ s1
            if len(sym) <= 256:
                inlined_xor.add(v)
                xor_expanded[v] = (sym, p0 ^ p1)

    # Inline single-fanout AND gates used ONLY as a single negated assertion (`!g == 1` <=> `l0 * l1 == 0`).
    inlined_neg_and = {
        v for v in needed
        if v not in xors and fo[v] == 1 and fo_assert_neg[v] == 1
    }

    # Step 5: Compactly assign 1-based ANF variable IDs:
    # PIs stay 1..=num_inputs; remaining kept active gates get num_inputs+1..=nv.
    kept_gates = [v for v in sorted(needed) if v not in inlined_xor and v not in inlined_neg_and]
    vmap = {i: i for i in range(1, num_inputs + 1)}
    next_id = num_inputs + 1
    for v in kept_gates:
        vmap[v] = next_id
        next_id += 1
    nv = next_id - 1

    def expand_lit_linear(lit: int):
        v = lit >> 1
        neg = lit & 1
        if v in xor_expanded:
            s, p = xor_expanded[v]
            return {vmap[u] for u in s if u > 0}, p ^ neg
        if v == 0:
            return set(), neg
        return {vmap[v]}, neg

    eqs = []
    n_xor_eqs = 0
    n_and_eqs = 0

    for v in kept_gates:
        zv = vmap[v]
        if v in xors:
            c0, c1 = xors[v]
            s0, p0 = expand_lit_linear(c0)
            s1, p1 = expand_lit_linear(c1)
            vs = s0 ^ s1
            if zv in vs:
                vs.remove(zv)
            else:
                vs.add(zv)
            rhs = p0 ^ p1
            mons = [(u,) for u in sorted(vs)]
            eqs.append((mons, rhs))
            n_xor_eqs += 1
        else:
            r0, r1 = ands[v - num_inputs - 1]
            v0 = vmap[r0 >> 1] if (r0 >> 1) > 0 else 0
            v1 = vmap[r1 >> 1] if (r1 >> 1) > 0 else 0
            mons, const = _expand_and_lits(v0, r0 & 1, v1, r1 & 1)
            _toggle_mon(mons, (zv,))
            # `zv ^ poly == const`
            eqs.append((sorted(mons), const))
            n_and_eqs += 1

    # Emit top-level assertions (`lit == 1`)
    for lit in asserts:
        v = lit >> 1
        neg = lit & 1
        if neg == 1 and v in inlined_neg_and:
            # `!And(r0, r1) == 1` <=> `(r0 & r1) == 0`
            r0, r1 = ands[v - num_inputs - 1]
            v0 = vmap[r0 >> 1] if (r0 >> 1) > 0 else 0
            v1 = vmap[r1 >> 1] if (r1 >> 1) > 0 else 0
            mons, const = _expand_and_lits(v0, r0 & 1, v1, r1 & 1)
            if not mons and const == 0:
                continue  # tautology 0 == 0
            eqs.append((sorted(mons), const))
            n_and_eqs += 1
        else:
            vs, p = expand_lit_linear(lit)
            # `(XOR vs) ^ p == 1` <=> `XOR vs == 1 ^ p`
            rhs = 1 ^ p
            if not vs and rhs == 0:
                continue  # tautology
            mons = [(u,) for u in sorted(vs)]
            eqs.append((mons, rhs))
            n_xor_eqs += 1

    if not eqs:
        eqs.append(([], 0))  # tautology `x T 0`

    # Build DIMACS-ANF output text
    lines = [
        f"c Converted from AIGER ({source_name}) by to_anf.py",
        f"c orig_inputs={num_inputs} orig_ands={num_ands} anf_vars={nv} linear_eqs={n_xor_eqs} quad_eqs={n_and_eqs}",
        f"p anf {nv} {len(eqs)}",
    ]
    for mons, rhs in eqs:
        lines.append(format_anf_line(mons, rhs))
    lines.append("")
    meta = {
        "kind": "aiger",
        "orig_inputs": num_inputs,
        "outputs": outputs,
        "ands": ands,
        "vmap": vmap,
        "kept_gates": kept_gates,
        "nv": nv,
        "neq": len(eqs),
        "max_deg": max((max((len(m) for m in ms), default=0) for ms, _ in eqs), default=0),
    }
    return "\n".join(lines), meta


# ============================================================================
# DIMACS CNF / XCNF Parser & Linear-Size Degree-<=3 ANF Converter
# ============================================================================

def parse_xcnf_text(text: str):
    nv = 0
    reg_clauses = []
    xor_clauses = []
    cur = []
    in_xor = False

    for raw_line in text.splitlines():
        s = raw_line.strip()
        if not s or s.startswith("c") or s.startswith("%"):
            continue
        if s.startswith("p "):
            parts = s.split()
            if len(parts) >= 3:
                nv = max(nv, int(parts[2]))
            continue
        if s.startswith("x") and (len(s) == 1 or s[1].isspace()):
            in_xor = True
            s = s[1:].strip()
        elif not cur:
            in_xor = False
        for tok in s.split():
            lit = int(tok)
            if lit == 0:
                if in_xor:
                    xor_clauses.append(cur)
                else:
                    reg_clauses.append(cur)
                cur = []
                in_xor = False
            else:
                v = abs(lit)
                if v > nv:
                    nv = v
                cur.append(lit)
    if cur:
        if in_xor:
            xor_clauses.append(cur)
        else:
            reg_clauses.append(cur)
    return nv, reg_clauses, xor_clauses


def eval_xcnf(reg_clauses, xor_clauses, vals_1based) -> bool:
    for cl in reg_clauses:
        sat = False
        for lit in cl:
            v = vals_1based[abs(lit)]
            if (lit > 0 and v) or (lit < 0 and not v):
                sat = True
                break
        if not sat:
            return False
    for xl in xor_clauses:
        acc = 0
        for lit in xl:
            v = 1 if vals_1based[abs(lit)] else 0
            acc ^= (v if lit > 0 else (1 ^ v))
        if acc != 1:
            return False
    return True


def _clause_le3_to_anf(lits):
    """Convert deduplicated non-tautological clause of length <= 3 into `(mons, rhs)`."""
    # Clause `l1 | ... | lk` <=> `prod_i (!l_i) == 0`, where `!l_i = x_v ^ (1 if l_i > 0 else 0)`.
    if not lits:
        return [], 1  # empty clause -> 0 == 1 (UNSAT)
    mons = {()}
    for lit in lits:
        v = abs(lit)
        pos = 1 if lit > 0 else 0
        nxt = set()
        for m in mons:
            m2 = tuple(sorted(m + (v,)))
            _toggle_mon(nxt, m2)
            if pos:
                _toggle_mon(nxt, m)
        mons = nxt
    rhs = 0
    if () in mons:
        mons.remove(())
        rhs ^= 1
    return sorted(mons), rhs


def _tseitin_or_to_anf(t: int, l1: int, l2: int):
    """Encode `t = l1 | l2` <=> `t ^ (!l1 & !l2) == 1` as a single degree-2 ANF equation."""
    v1, p1 = abs(l1), (1 if l1 > 0 else 0)
    v2, p2 = abs(l2), (1 if l2 > 0 else 0)
    # `!l1 & !l2 = (x_{v1} ^ p1) * (x_{v2} ^ p2)`
    mons, const = _expand_and_lits(v1, p1, v2, p2)
    _toggle_mon(mons, (t,))
    # `t ^ (!l1 & !l2) == 1` <=> `t ^ (mons ^ const) == 1` <=> `(t ^ mons) == 1 ^ const`
    return sorted(mons), 1 ^ const


def convert_xcnf_to_anf(data: bytes, source_name: str = ""):
    text = data.decode("utf-8", errors="replace")
    orig_nv, reg_clauses, xor_clauses = parse_xcnf_text(text)

    nv = orig_nv
    eqs = []
    tseitin_defs = []  # (t_var, l1, l2) for --verify forward evaluation
    n_xor_eqs = 0
    n_tseitin_eqs = 0
    n_clause_eqs = 0

    # 1. Preserve every XOR clause verbatim as a single degree-1 linear ANF equation.
    for xl in xor_clauses:
        rhs = 1
        vs = set()
        for lit in xl:
            if lit < 0:
                rhs ^= 1
            v = abs(lit)
            if v in vs:
                vs.remove(v)
            else:
                vs.add(v)
        if not vs and rhs == 0:
            continue  # tautology
        eqs.append(([(v,) for v in sorted(vs)], rhs))
        n_xor_eqs += 1

    # 2. Regular clauses: k <= 3 direct (0 aux vars); k >= 4 balanced Tseitin split (`t = l1 | l2`).
    for cl in reg_clauses:
        # Deduplicate literals and check tautology
        seen = {}
        taut = False
        clean = []
        for lit in cl:
            v = abs(lit)
            pos = lit > 0
            prev = seen.get(v)
            if prev is not None:
                if prev != pos:
                    taut = True
                    break
            else:
                seen[v] = pos
                clean.append(lit)
        if taut:
            continue

        cur = clean
        while len(cur) >= 4:
            nxt = []
            i = 0
            k = len(cur)
            # Pairwise balanced Tseitin split while remaining length > 3
            rem = k
            while i + 1 < k and rem >= 4:
                nv += 1
                t = nv
                l1, l2 = cur[i], cur[i + 1]
                eqs.append(_tseitin_or_to_anf(t, l1, l2))
                tseitin_defs.append((t, l1, l2))
                n_tseitin_eqs += 1
                nxt.append(t)
                i += 2
                rem -= 1
            while i < k:
                nxt.append(cur[i])
                i += 1
            cur = nxt

        eqs.append(_clause_le3_to_anf(cur))
        n_clause_eqs += 1

    if not eqs:
        eqs.append(([], 0))  # tautology `x T 0`

    lines = [
        f"c Converted from CNF/XCNF ({source_name}) by to_anf.py",
        f"c orig_vars={orig_nv} orig_reg={len(reg_clauses)} orig_xor={len(xor_clauses)} anf_vars={nv} tseitin_aux={n_tseitin_eqs}",
        f"p anf {nv} {len(eqs)}",
    ]
    for mons, rhs in eqs:
        lines.append(format_anf_line(mons, rhs))
    lines.append("")
    meta = {
        "kind": "xcnf",
        "orig_nv": orig_nv,
        "reg_clauses": reg_clauses,
        "xor_clauses": xor_clauses,
        "tseitin_defs": tseitin_defs,
        "nv": nv,
        "neq": len(eqs),
        "max_deg": max((max((len(m) for m in ms), default=0) for ms, _ in eqs), default=0),
    }
    return "\n".join(lines), meta


# ============================================================================
# Independent Verification Suite (--verify)
# ============================================================================

def run_solver(solver_bin: str, path: str, timeout_s: float, pin_cores: str = ""):
    cmd = []
    if pin_cores:
        cmd.extend(["taskset", "-c", pin_cores])
    cmd.extend([solver_bin, path, "--timeout", str(timeout_s)])
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    wall_ms = (time.perf_counter() - t0) * 1000.0
    status = "UNKNOWN"
    parse_ms = None
    solve_ms = None
    model = {}
    for line in proc.stdout.splitlines():
        if line.startswith("s SATISFIABLE"):
            status = "SAT"
        elif line.startswith("s UNSATISFIABLE"):
            status = "UNSAT"
        elif line.startswith("c Frobenius ") and "parse=" in line:
            try:
                seg = line.split("parse=")[1].split("ms")[0]
                parse_ms = float(seg)
            except Exception:
                pass
        elif line.startswith("c time=") and "solve=" in line:
            try:
                seg = line.split("solve=")[1].split("ms")[0]
                solve_ms = float(seg)
            except Exception:
                pass
        elif line.startswith("v "):
            for tok in line[2:].split():
                lit = int(tok)
                if lit == 0:
                    break
                model[abs(lit)] = 1 if lit > 0 else 0
    return {
        "rc": proc.returncode,
        "status": status,
        "wall_ms": wall_ms,
        "parse_ms": parse_ms,
        "solve_ms": solve_ms,
        "model": model,
        "stderr": proc.stderr.strip(),
    }


def verify_conversion(in_path: str, out_path: str, meta: dict, solver_bin: str = "", timeout_s: float = 30.0, pin_cores: str = ""):
    # 1. Re-read & parse written output from disk
    anf_text = read_bytes_auto(out_path).decode("ascii")
    hdr_nv, hdr_neq, max_v, max_deg, eqs = parse_dimacs_anf_text(anf_text)
    assert hdr_nv == meta["nv"], f"header nv {hdr_nv} != {meta['nv']}"
    assert hdr_neq == len(eqs), f"header neq {hdr_neq} != {len(eqs)}"
    assert max_v <= hdr_nv, f"var {max_v} exceeds header nv {hdr_nv}"
    deg_bound = 2 if meta["kind"] == "aiger" else 3
    assert max_deg <= deg_bound, f"max degree {max_deg} exceeds bound {deg_bound}"

    # 2. Random assignment forward equivalence check (64 vectors)
    rng = random.Random(20261123)
    if meta["kind"] == "aiger":
        I = meta["orig_inputs"]
        for _ in range(64):
            pis = [0] + [rng.randint(0, 1) for _ in range(I)]
            aig_ok, aig_vals = eval_aiger(I, meta["outputs"], meta["ands"], pis)
            anf_vals = [0] * (hdr_nv + 1)
            for orig_v, anf_v in meta["vmap"].items():
                anf_vals[anf_v] = aig_vals[orig_v]
            anf_ok = eval_anf_eqs(eqs, anf_vals)
            assert anf_ok == aig_ok, f"Random vector mismatch on AIGER->ANF (aig={aig_ok}, anf={anf_ok})"
    else:
        orig_nv = meta["orig_nv"]
        for _ in range(64):
            vals = [0] + [rng.randint(0, 1) for _ in range(orig_nv)] + [0] * (hdr_nv - orig_nv)
            orig_ok = eval_xcnf(meta["reg_clauses"], meta["xor_clauses"], vals)
            for t, l1, l2 in meta["tseitin_defs"]:
                b1 = vals[abs(l1)] if l1 > 0 else (1 ^ vals[abs(l1)])
                b2 = vals[abs(l2)] if l2 > 0 else (1 ^ vals[abs(l2)])
                vals[t] = b1 | b2
            anf_ok = eval_anf_eqs(eqs, vals)
            assert anf_ok == orig_ok, f"Random vector mismatch on XCNF->ANF (orig={orig_ok}, anf={anf_ok})"

    # 3. Optional end-to-end solver verification
    res_info = {"hdr_nv": hdr_nv, "hdr_neq": hdr_neq, "max_deg": max_deg}
    if solver_bin:
        r_orig = run_solver(solver_bin, in_path, timeout_s, pin_cores)
        r_anf = run_solver(solver_bin, out_path, timeout_s, pin_cores)
        res_info["orig"] = r_orig
        res_info["anf"] = r_anf
        if r_orig["status"] != "UNKNOWN" and r_anf["status"] != "UNKNOWN":
            assert r_orig["status"] == r_anf["status"], (
                f"SAT/UNSAT MISMATCH on {in_path}: orig={r_orig['status']} vs anf={r_anf['status']}"
            )
        if r_anf["status"] == "SAT":
            m = r_anf["model"]
            full = [0] + [m.get(v, 0) for v in range(1, hdr_nv + 1)]
            assert eval_anf_eqs(eqs, full), f"ANF model failed independent ANF verification on {out_path}!"
            if meta["kind"] == "aiger":
                ok, _ = eval_aiger(meta["orig_inputs"], meta["outputs"], meta["ands"], full)
                assert ok, f"Projected ANF model failed raw AIGER verification on {in_path}!"
            else:
                ok = eval_xcnf(meta["reg_clauses"], meta["xor_clauses"], full)
                assert ok, f"Projected ANF model failed raw CNF/XCNF verification on {in_path}!"
    return res_info


# ============================================================================
# Optional compiled accelerator (src/bench_tools -> `sat-bench-tools aig-to-anf`)
# ============================================================================

BENCH_TOOLS_BIN = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "bench_tools", "target", "release", "sat-bench-tools"
)


def try_rust_aig_to_anf(args) -> bool:
    """Dispatch binary AIGER -> ANF to the compiled `sat-bench-tools` when available.

    Produces byte-identical DIMACS-ANF text. Returns False (caller falls back to the
    pure-Python path) when disabled, unsupported for these arguments, absent, or failing.
    """
    if args.pure_python or args.solver or os.environ.get("SAT_BENCH_PURE_PYTHON", "") == "1":
        return False
    if not (os.path.isfile(BENCH_TOOLS_BIN) and os.access(BENCH_TOOLS_BIN, os.X_OK)):
        return False
    in_low = args.input.lower()
    out_low = args.output.lower()
    if not (in_low.endswith(".aig") or in_low.endswith(".aig.xz")):
        return False
    if not (out_low.endswith(".anf") or out_low.endswith(".anf.xz")):
        return False
    cmd = [BENCH_TOOLS_BIN, "aig-to-anf", args.input, args.output, "--preset", str(args.preset)]
    if args.verify:
        cmd.append("--verify")
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError as e:
        print(f"[warn] sat-bench-tools unavailable ({e}); falling back to pure Python", file=sys.stderr)
        return False
    if proc.returncode != 0:
        print(
            f"[warn] sat-bench-tools failed (rc={proc.returncode}): {proc.stderr.strip()}; "
            f"falling back to pure Python",
            file=sys.stderr,
        )
        return False
    sys.stdout.write(proc.stdout)
    return True


def main():
    ap = argparse.ArgumentParser(description="Convert .aig/.aag/.cnf/.xcnf (optionally compressed) to DIMACS-ANF (.anf/.anf.xz).")
    ap.add_argument("input", help="Input .aig/.aag/.cnf/.xcnf (or .xz/.gz/.bz2)")
    ap.add_argument("output", help="Output .anf or .anf.xz/.anf.gz/.anf.bz2")
    ap.add_argument("--preset", type=int, default=3, help="XZ compression preset (0-9, default 3)")
    ap.add_argument("--verify", action="store_true", help="Verify converted ANF equivalence (and solver agreement if --solver set)")
    ap.add_argument("--solver", default="", help="Path to frobenius binary for end-to-end --verify")
    ap.add_argument("--timeout", type=float, default=30.0, help="Per-instance solver timeout in seconds")
    ap.add_argument("--pin", default="", help="Optional taskset CPU list for --solver runs (e.g. 8-11)")
    ap.add_argument("--pure-python", action="store_true",
                    help="Never dispatch binary AIGER conversion to the compiled src/bench_tools accelerator")
    args = ap.parse_args()

    if try_rust_aig_to_anf(args):
        return

    t0 = time.perf_counter()
    raw = read_bytes_auto(args.input)
    kind = detect_input_kind(args.input, raw)
    src_name = os.path.basename(args.input)
    if kind == "aiger":
        anf_text, meta = convert_aiger_to_anf(raw, src_name)
    else:
        anf_text, meta = convert_xcnf_to_anf(raw, src_name)
    write_text_auto(args.output, anf_text, xz_preset=args.preset)
    conv_ms = (time.perf_counter() - t0) * 1000.0

    print(
        f"[ok] {src_name} ({kind}) -> {os.path.basename(args.output)}: "
        f"nv={meta['nv']} neq={meta['neq']} max_deg={meta['max_deg']} ({conv_ms:.1f}ms)"
    )

    if args.verify:
        vinfo = verify_conversion(args.input, args.output, meta, args.solver, args.timeout, args.pin)
        if args.solver:
            ro, ra = vinfo["orig"], vinfo["anf"]
            ap_s = f"{ra['parse_ms']:.2f}ms" if ra["parse_ms"] is not None else "n/a"
            as_s = f"{ra['solve_ms']:.2f}ms" if ra["solve_ms"] is not None else f"{ra['wall_ms']:.2f}ms"
            print(
                f"  [verified] status={ra['status']} (orig={ro['status']}) | "
                f"orig_wall={ro['wall_ms']:.2f}ms | anf_parse={ap_s} anf_solve={as_s} anf_wall={ra['wall_ms']:.2f}ms"
            )
        else:
            print(f"  [verified] structural + 64-vector forward equivalence passed (max_deg={vinfo['max_deg']})")


if __name__ == "__main__":
    main()
