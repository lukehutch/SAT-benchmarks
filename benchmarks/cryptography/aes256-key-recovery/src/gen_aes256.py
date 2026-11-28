#!/usr/bin/env python3
"""Clean-Room NIST FIPS 197 AES-256 Key-Recovery & Davies-Meyer Hash-Preimage
SAT/XCNF/AIGER/ANF Benchmark Generator (`aes256-key-recovery`).

Author: Luke Hutchison (`lukehutch`)
License: MIT License (see `../../LICENSE`)

Implements:
  1. Exact byte-level NIST FIPS 197 AES-256 reference encryption (parameterized
     by rounds R in 1..14, where final round R omits MixColumns per standard
     FIPS 197 convention so R=14 matches FIPS 197 byte-for-byte).
  2. Exact combinational gate-level Boolean circuit using the published
     Boyar-Peralta (SEA 2010, Table 1) 32-AND / 81-XOR-XNOR AES S-box
     (verified 256/256 against the FIPS 197 S-box) and factored MixColumns
     over GF(2^8) = F_2[x] / (x^8 + x^4 + x^3 + x + 1) so every XOR gate has
     arity 2 or 3 (maximum CNF clause width 4, zero auxiliary CNF vars needed).
  3. 100% transparent deterministic synthetic keys and plaintexts derived from
     `SHA-256("frobenius-aes256-benchmark-v1:<name>:<role>")`.
  4. Algebraic equivalence to Davies-Meyer AES-256 hash compression:
     `H = AES-256(K, P) XOR P` <=> `AES-256(K, P) = C` with `C = H XOR P`.
  5. Direct lossless export to all four uniform repository formats:
       - `xcnf-orig/*.xcnf.xz`     (native CryptoMiniSat XOR + Tseitin AND)
       - `cnf-converted/*.cnf.xz`  (exact Tseitin CNF expansion of XOR clauses)
       - `aig-converted/*.aig.xz`  (combinational Binary AIGER 1.9 miter, L=0, O=1)
       - `anf-converted/*.anf.xz`  (via `../../src/to_anf.py`, linear-size ANF)
  6. Complete programmatic verification:
       - FIPS 197 test vectors (`AES-256(0, 0)` and Appendix C.3) on both
         byte-level reference and gate-level Boolean circuit (128/128 bits).
       - Boyar-Peralta S-box 256/256 truth-table match.
       - Forward witness verification across all 4 exported formats for every
         SAT instance.
       - Exhaustive 2^k key-space verification in Python for every UNSAT
         instance (proving mathematical unsatisfiability).

Usage:
    python3 src/gen_aes256.py              # Generate & verify full benchmark suite
    python3 src/gen_aes256.py --self-test  # Run cryptographic & circuit self-tests only
"""
from __future__ import annotations

import argparse
import hashlib
import lzma
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SUITE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import to_anf  # noqa: E402


# ============================================================================
# 1. Exact Byte-Level NIST FIPS 197 AES-256 Reference Implementation
# ============================================================================

def _gf_mul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p


def _gf_inv(a: int) -> int:
    if a == 0:
        return 0
    r = 1
    base = a
    e = 254
    while e:
        if e & 1:
            r = _gf_mul(r, base)
        base = _gf_mul(base, base)
        e >>= 1
    return r


def _compute_fips_sbox() -> tuple[int, ...]:
    table = []
    for b in range(256):
        inv = _gf_inv(b)
        s = 0x63
        for i in range(8):
            bit = (
                ((inv >> i) & 1)
                ^ ((inv >> ((i + 4) % 8)) & 1)
                ^ ((inv >> ((i + 5) % 8)) & 1)
                ^ ((inv >> ((i + 6) % 8)) & 1)
                ^ ((inv >> ((i + 7) % 8)) & 1)
            )
            s ^= bit << i
        table.append(s)
    return tuple(table)


SBOX: tuple[int, ...] = _compute_fips_sbox()
RCON: tuple[int, ...] = (0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40)
XTIME: tuple[int, ...] = tuple(((b << 1) & 0xFF) ^ (0x1B if (b & 0x80) else 0) for b in range(256))


def aes256_key_expansion_bytes(key: bytes, rounds: int = 14) -> list[bytes]:
    """Expand 32-byte key into `rounds + 1` 16-byte round keys per FIPS 197."""
    if len(key) != 32:
        raise ValueError(f"AES-256 key must be 32 bytes, got {len(key)}")
    if not (1 <= rounds <= 14):
        raise ValueError(f"rounds must be in 1..14, got {rounds}")
    total_words = 4 * (rounds + 1)
    w: list[list[int]] = [[key[4 * i + j] for j in range(4)] for i in range(8)]
    sbox = SBOX
    rcon = RCON
    for i in range(8, total_words):
        t = w[i - 1]
        if i % 8 == 0:
            t = [sbox[t[1]] ^ rcon[i // 8], sbox[t[2]], sbox[t[3]], sbox[t[0]]]
        elif i % 8 == 4:
            t = [sbox[t[0]], sbox[t[1]], sbox[t[2]], sbox[t[3]]]
        prev = w[i - 8]
        w.append([prev[0] ^ t[0], prev[1] ^ t[1], prev[2] ^ t[2], prev[3] ^ t[3]])
    return [
        bytes(w[4 * r][0:4] + w[4 * r + 1][0:4] + w[4 * r + 2][0:4] + w[4 * r + 3][0:4])
        for r in range(rounds + 1)
    ]


def aes256_encrypt_bytes(key: bytes, plaintext: bytes, rounds: int = 14) -> bytes:
    """NIST FIPS 197 AES-256 encryption (final round `rounds` omits MixColumns)."""
    if len(plaintext) != 16:
        raise ValueError(f"Plaintext must be 16 bytes, got {len(plaintext)}")
    rks = aes256_key_expansion_bytes(key, rounds)
    sbox = SBOX
    xt = XTIME
    rk0 = rks[0]
    s = [plaintext[i] ^ rk0[i] for i in range(16)]

    for r in range(1, rounds + 1):
        # SubBytes + ShiftRows fused
        # Column-major index = 4*c + row; ShiftRows takes (row, (c + row) % 4)
        t0, t1, t2, t3 = sbox[s[0]], sbox[s[5]], sbox[s[10]], sbox[s[15]]
        t4, t5, t6, t7 = sbox[s[4]], sbox[s[9]], sbox[s[14]], sbox[s[3]]
        t8, t9, t10, t11 = sbox[s[8]], sbox[s[13]], sbox[s[2]], sbox[s[7]]
        t12, t13, t14, t15 = sbox[s[12]], sbox[s[1]], sbox[s[6]], sbox[s[11]]

        rk = rks[r]
        if r < rounds:
            # MixColumns + AddRoundKey
            s = [0] * 16
            cols = ((t0, t1, t2, t3), (t4, t5, t6, t7), (t8, t9, t10, t11), (t12, t13, t14, t15))
            for c, (a0, a1, a2, a3) in enumerate(cols):
                base = 4 * c
                d0 = a0 ^ a1
                d1 = a1 ^ a2
                d2 = a2 ^ a3
                d3 = a3 ^ a0
                s[base] = xt[d0] ^ a1 ^ d2 ^ rk[base]
                s[base + 1] = xt[d1] ^ a2 ^ d3 ^ rk[base + 1]
                s[base + 2] = xt[d2] ^ a3 ^ d0 ^ rk[base + 2]
                s[base + 3] = xt[d3] ^ a0 ^ d1 ^ rk[base + 3]
        else:
            s = [
                t0 ^ rk[0], t1 ^ rk[1], t2 ^ rk[2], t3 ^ rk[3],
                t4 ^ rk[4], t5 ^ rk[5], t6 ^ rk[6], t7 ^ rk[7],
                t8 ^ rk[8], t9 ^ rk[9], t10 ^ rk[10], t11 ^ rk[11],
                t12 ^ rk[12], t13 ^ rk[13], t14 ^ rk[14], t15 ^ rk[15],
            ]
    return bytes(s)


# ============================================================================
# 2. Gate-Level Boolean Circuit Builder (Boyar-Peralta SEA 2010 S-Box)
# ============================================================================

@dataclass
class Gate:
    """One combinational gate defining output variable `out` (1-based)."""
    kind: str  # "AND" or "XOR"
    out: int
    inputs: tuple[int, ...]  # positive 1-based variable IDs
    rhs: int = 0  # for XOR: out ^ XOR(inputs) == rhs  (i.e. out = XOR(inputs) ^ rhs)


class AesCircuitBuilder:
    """Clean-room gate-level Boolean circuit builder for FIPS 197 AES-256.

    Wire representation:
      - `0` denotes constant FALSE (0), `1` denotes constant TRUE (1) when
        folded via `(var_id, inv)` pairs, OR we track every wire as `(var, inv)`
        where `var == 0` means constant `inv` (`0` or `1`), and `var >= 1`
        means `x_var ^ inv`.
    Keeping `(var, inv)` lets plaintext bits, Rcon constants, and S-box `+0x63`
    affine flips fold cleanly into XOR parities with zero dummy variables!
    """

    def __init__(self) -> None:
        self.num_vars = 256  # vars 1..256 are always the 256-bit AES-256 key
        self.gates: list[Gate] = []
        self.n_and = 0
        self.n_xor = 0

    def new_var(self) -> int:
        self.num_vars += 1
        return self.num_vars

    def const_wire(self, bit: int) -> tuple[int, int]:
        return (0, bit & 1)

    def key_wires(self) -> list[list[tuple[int, int]]]:
        """Return 32 key bytes, each as 8 wires `[bit0(LSB) .. bit7(MSB)]`."""
        return [[(1 + 8 * byte_i + bit_i, 0) for bit_i in range(8)] for byte_i in range(32)]

    def xor_wires(self, wires: Iterable[tuple[int, int]], extra_inv: int = 0) -> tuple[int, int]:
        """Compute XOR of wires; cancel duplicates mod 2 and fold constants."""
        parity = extra_inv & 1
        counts: dict[int, int] = {}
        for v, inv in wires:
            parity ^= inv
            if v != 0:
                counts[v] = counts.get(v, 0) ^ 1
        vs = [v for v, c in counts.items() if c]
        if len(vs) == 0:
            return (0, parity)
        if len(vs) == 1:
            return (vs[0], parity)
        out = self.new_var()
        # out = XOR(vs) ^ parity  <=>  out ^ XOR(vs) == parity
        self.gates.append(Gate("XOR", out, tuple(vs), parity))
        self.n_xor += 1
        return (out, 0)

    def and2(self, w0: tuple[int, int], w1: tuple[int, int]) -> tuple[int, int]:
        """Compute AND of two wires `(v0, inv0) & (v1, inv1)` using signed literals."""
        v0, i0 = w0
        v1, i1 = w1
        if v0 == 0:
            return (0, 0) if i0 == 0 else w1
        if v1 == 0:
            return (0, 0) if i1 == 0 else w0
        if v0 == v1:
            return (0, 0) if i0 != i1 else w0
        l0 = -v0 if i0 else v0
        l1 = -v1 if i1 else v1
        out = self.new_var()
        self.gates.append(Gate("AND", out, (l0, l1), 0))
        self.n_and += 1
        return (out, 0)

    def sbox_byte(self, byte_wires: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Boyar-Peralta (SEA 2010, Table 1) 32-AND / 81-XOR-XNOR AES S-box.

        Input `byte_wires[0..7]` is LSB-first (`byte_wires[0]` = bit 0, `byte_wires[7]` = bit 7).
        Boyar-Peralta labels `x0 = MSB (bit 7) .. x7 = LSB (bit 0)` and outputs `s0 = MSB .. s7 = LSB`.
        Returns 8 wires in LSB-first order `[bit0 .. bit7]`.
        """
        x0, x1, x2, x3, x4, x5, x6, x7 = [byte_wires[7 - i] for i in range(8)]
        X = lambda a, b: self.xor_wires((a, b))
        XN = lambda a, b: self.xor_wires((a, b), 1)
        A = self.and2

        # Top linear transformation (23 XORs)
        y14 = X(x3, x5)
        y13 = X(x0, x6)
        y9  = X(x0, x3)
        y8  = X(x0, x5)
        t0  = X(x1, x2)
        y1  = X(t0, x7)
        y4  = X(y1, x3)
        y12 = X(y13, y14)
        y2  = X(y1, x0)
        y5  = X(y1, x6)
        y3  = X(y5, y8)
        t1  = X(x4, y12)
        y15 = X(t1, x5)
        y20 = X(t1, x1)
        y6  = X(y15, x7)
        y10 = X(y15, t0)
        y11 = X(y20, y9)
        y7  = X(x7, y11)
        y17 = X(y10, y11)
        y19 = X(y10, y8)
        y16 = X(t0, y11)
        y21 = X(y13, y16)
        y18 = X(x0, y16)

        # Middle nonlinear transformation (32 ANDs + 30 XORs)
        t2  = A(y12, y15)
        t3  = A(y3, y6)
        t4  = X(t3, t2)
        t5  = A(y4, x7)
        t6  = X(t5, t2)
        t7  = A(y13, y16)
        t8  = A(y5, y1)
        t9  = X(t8, t7)
        t10 = A(y2, y7)
        t11 = X(t10, t7)
        t12 = A(y9, y11)
        t13 = A(y14, y17)
        t14 = X(t13, t12)
        t15 = A(y8, y10)
        t16 = X(t15, t12)
        t17 = X(t4, t14)
        t18 = X(t6, t16)
        t19 = X(t9, t14)
        t20 = X(t11, t16)
        t21 = X(t17, y20)
        t22 = X(t18, y19)
        t23 = X(t19, y21)
        t24 = X(t20, y18)
        t25 = X(t21, t22)
        t26 = A(t21, t23)
        t27 = X(t24, t26)
        t28 = A(t25, t27)
        t29 = X(t28, t22)
        t30 = X(t23, t24)
        t31 = X(t22, t26)
        t32 = A(t31, t30)
        t33 = X(t32, t24)
        t34 = X(t23, t33)
        t35 = X(t27, t33)
        t36 = A(t24, t35)
        t37 = X(t36, t34)
        t38 = X(t27, t36)
        t39 = A(t29, t38)
        t40 = X(t25, t39)
        t41 = X(t40, t37)
        t42 = X(t29, t33)
        t43 = X(t29, t40)
        t44 = X(t33, t37)
        t45 = X(t42, t41)

        z0  = A(t44, y15)
        z1  = A(t37, y6)
        z2  = A(t33, x7)
        z3  = A(t43, y16)
        z4  = A(t40, y1)
        z5  = A(t29, y7)
        z6  = A(t42, y11)
        z7  = A(t45, y17)
        z8  = A(t41, y10)
        z9  = A(t44, y12)
        z10 = A(t37, y3)
        z11 = A(t33, y4)
        z12 = A(t43, y13)
        z13 = A(t40, y5)
        z14 = A(t29, y2)
        z15 = A(t42, y9)
        z16 = A(t45, y14)
        z17 = A(t41, y8)

        # Bottom linear transformation (24 XORs + 4 XNORs for +0x63)
        tc1  = X(z15, z16)
        tc2  = X(z10, tc1)
        tc3  = X(z9, tc2)
        tc4  = X(z0, z2)
        tc5  = X(z1, z0)
        tc6  = X(z3, z4)
        tc7  = X(z12, tc4)
        tc8  = X(z7, tc6)
        tc9  = X(z8, tc7)
        tc10 = X(tc8, tc9)
        tc11 = X(tc6, tc5)
        tc12 = X(z3, z5)
        tc13 = X(z13, tc1)
        tc14 = X(tc4, tc12)
        s3   = X(tc3, tc11)
        tc16 = X(z6, tc8)
        tc17 = X(z14, tc10)
        tc18 = X(tc13, tc14)
        s7   = XN(z12, tc18)
        tc20 = X(z15, tc16)
        tc21 = X(tc2, z11)
        s0   = X(tc3, tc16)
        s6   = XN(tc10, tc18)
        s4   = X(tc14, s3)
        s1   = XN(s3, tc16)
        tc26 = X(tc17, tc20)
        s2   = XN(tc26, z17)
        s5   = X(tc21, tc17)

        # Return LSB-first [bit0=s7 .. bit7=s0]
        return [s7, s6, s5, s4, s3, s2, s1, s0]

    def xtime_byte(self, byte_wires: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Multiply byte by x in GF(2^8) = F_2[x] / (x^8 + x^4 + x^3 + x + 1)."""
        b = byte_wires
        return [
            b[7],
            self.xor_wires((b[0], b[7])),
            b[1],
            self.xor_wires((b[2], b[7])),
            self.xor_wires((b[3], b[7])),
            b[4],
            b[5],
            b[6],
        ]

    def xor_bytes(self, a: list[tuple[int, int]], b: list[tuple[int, int]]) -> list[tuple[int, int]]:
        return [self.xor_wires((a[i], b[i])) for i in range(8)]

    def xor_byte_const(self, a: list[tuple[int, int]], c: int) -> list[tuple[int, int]]:
        return [(v, inv ^ ((c >> i) & 1)) for i, (v, inv) in enumerate(a)]

    def build_key_schedule(self, rounds: int) -> list[list[list[tuple[int, int]]]]:
        """Build gate-level FIPS 197 AES-256 key schedule returning `rounds + 1`
        round keys, each a list of 16 bytes (each byte = 8 wires LSB-first)."""
        kbytes = self.key_wires()
        words: list[list[list[tuple[int, int]]]] = [kbytes[4 * i : 4 * i + 4] for i in range(8)]
        total_words = 4 * (rounds + 1)
        for i in range(8, total_words):
            prev_w = words[i - 1]
            if i % 8 == 0:
                rot = [prev_w[1], prev_w[2], prev_w[3], prev_w[0]]
                t = [self.sbox_byte(b) for b in rot]
                t[0] = self.xor_byte_const(t[0], RCON[i // 8])
            elif i % 8 == 4:
                t = [self.sbox_byte(b) for b in prev_w]
            else:
                t = prev_w
            w_im8 = words[i - 8]
            words.append([self.xor_bytes(w_im8[j], t[j]) for j in range(4)])

        round_keys = []
        for r in range(rounds + 1):
            rk: list[list[tuple[int, int]]] = []
            for c in range(4):
                rk.extend(words[4 * r + c])
            round_keys.append(rk)
        return round_keys

    def build_encrypt_block(
        self,
        round_keys: list[list[list[tuple[int, int]]]],
        plaintext: bytes,
        rounds: int,
    ) -> list[list[tuple[int, int]]]:
        """Build gate-level `rounds`-round AES-256 encryption block for constant `plaintext`.
        Returns 16 output ciphertext bytes (each 8 wires LSB-first)."""
        # Initial AddRoundKey with constant plaintext
        state = [self.xor_byte_const(round_keys[0][i], plaintext[i]) for i in range(16)]

        for r in range(1, rounds + 1):
            # SubBytes
            sub = [self.sbox_byte(state[i]) for i in range(16)]
            # ShiftRows (pure wire permutation, 0 gates)
            sr = [
                sub[0],  sub[5],  sub[10], sub[15],
                sub[4],  sub[9],  sub[14], sub[3],
                sub[8],  sub[13], sub[2],  sub[7],
                sub[12], sub[1],  sub[6],  sub[11],
            ]
            rk = round_keys[r]
            if r < rounds:
                # Factored MixColumns: all XORs have arity <= 3!
                nxt: list[list[tuple[int, int]]] = []
                for c in range(4):
                    a0, a1, a2, a3 = sr[4 * c : 4 * c + 4]
                    d0 = self.xor_bytes(a0, a1)
                    d1 = self.xor_bytes(a1, a2)
                    d2 = self.xor_bytes(a2, a3)
                    d3 = self.xor_bytes(a3, a0)
                    xt0 = self.xtime_byte(d0)
                    xt1 = self.xtime_byte(d1)
                    xt2 = self.xtime_byte(d2)
                    xt3 = self.xtime_byte(d3)
                    b0 = [self.xor_wires((xt0[i], a1[i], d2[i])) for i in range(8)]
                    b1 = [self.xor_wires((xt1[i], a2[i], d3[i])) for i in range(8)]
                    b2 = [self.xor_wires((xt2[i], a3[i], d0[i])) for i in range(8)]
                    b3 = [self.xor_wires((xt3[i], a0[i], d1[i])) for i in range(8)]
                    nxt.append(self.xor_bytes(b0, rk[4 * c]))
                    nxt.append(self.xor_bytes(b1, rk[4 * c + 1]))
                    nxt.append(self.xor_bytes(b2, rk[4 * c + 2]))
                    nxt.append(self.xor_bytes(b3, rk[4 * c + 3]))
                state = nxt
            else:
                state = [self.xor_bytes(sr[i], rk[i]) for i in range(16)]
        return state

    def evaluate(self, key: bytes, out_blocks: list[list[list[tuple[int, int]]]]) -> tuple[list[int], list[bytes]]:
        """Evaluate every gate forward from 32-byte `key`; return `(vals_1based, output_bytes_list)`."""
        vals = [0] * (self.num_vars + 1)
        for byte_i in range(32):
            b = key[byte_i]
            for bit_i in range(8):
                vals[1 + 8 * byte_i + bit_i] = (b >> bit_i) & 1

        for g in self.gates:
            if g.kind == "AND":
                l0, l1 = g.inputs
                v0 = vals[abs(l0)] ^ (1 if l0 < 0 else 0)
                v1 = vals[abs(l1)] ^ (1 if l1 < 0 else 0)
                vals[g.out] = v0 & v1
            else:
                acc = g.rhs
                for u in g.inputs:
                    acc ^= vals[u]
                vals[g.out] = acc

        outs: list[bytes] = []
        for blk in out_blocks:
            bs = bytearray(16)
            for byte_i in range(16):
                val = 0
                for bit_i in range(8):
                    v, inv = blk[byte_i][bit_i]
                    bit = (vals[v] if v else 0) ^ inv
                    val |= bit << bit_i
                bs[byte_i] = val
            outs.append(bytes(bs))
        return vals, outs


# ============================================================================
# 3. Four-Format Lossless Exporters (XCNF, CNF, Binary AIGER 1.9, ANF)
# ============================================================================

def _collect_unit_constraints(
    key: bytes,
    free_k: int,
    out_blocks: list[list[list[tuple[int, int]]]],
    target_cts: list[bytes],
) -> tuple[list[int], list[tuple[int, int]]]:
    """Return `(key_units, ct_units_as_var_val)` where `key_units` are signed literals
    fixing key bits `free_k..255`, and `ct_units` are `(var, required_bit)` pairs."""
    key_units: list[int] = []
    for b in range(free_k, 256):
        bit = (key[b // 8] >> (b % 8)) & 1
        var = 1 + b
        key_units.append(var if bit else -var)

    ct_units: list[tuple[int, int]] = []
    for blk, ct in zip(out_blocks, target_cts):
        for byte_i in range(16):
            tb = ct[byte_i]
            for bit_i in range(8):
                req = (tb >> bit_i) & 1
                v, inv = blk[byte_i][bit_i]
                assert v > 0, "Output wire unexpectedly folded to constant"
                ct_units.append((v, req ^ inv))
    return key_units, ct_units


def export_xcnf_and_cnf(
    builder: AesCircuitBuilder,
    key_units: list[int],
    ct_units: list[tuple[int, int]],
    header_comments: list[str],
    xcnf_path: Path,
    cnf_path: Path,
) -> dict[str, int]:
    """Export native CryptoMiniSat `.xcnf.xz` and exact Tseitin `.cnf.xz`."""
    xcnf_reg: list[tuple[int, ...]] = []
    xcnf_xor: list[tuple[int, ...]] = []  # literal tuples where XOR(lits) == 1
    cnf_clauses: list[tuple[int, ...]] = []
    nvars_cnf = builder.num_vars

    # Fixed key unit clauses
    for u in key_units:
        xcnf_reg.append((u,))
        cnf_clauses.append((u,))

    # Gate definitions
    for g in builder.gates:
        if g.kind == "AND":
            z = g.out
            a, b = g.inputs
            # z <=> (a & b)
            c1 = (-z, a)
            c2 = (-z, b)
            c3 = (z, -a, -b)
            xcnf_reg.extend((c1, c2, c3))
            cnf_clauses.extend((c1, c2, c3))
        else:
            # g.out ^ XOR(g.inputs) == g.rhs
            # In XCNF (`x l1 ... lk 0` asserts XOR(l_i) == 1):
            # if rhs == 1: `x g.out u1 ... um 0`
            # if rhs == 0: `x -g.out u1 ... um 0`
            first = g.out if g.rhs == 1 else -g.out
            xcnf_xor.append((first,) + g.inputs)

            # Exact CNF expansion (width k = 1 + len(g.inputs) <= 4; split cleanly if ever > 4)
            vs = [g.out] + list(g.inputs)
            rhs = g.rhs
            while len(vs) > 4:
                nvars_cnf += 1
                t = nvars_cnf
                a, b, c = vs[0], vs[1], vs[2]
                for mask in range(16):
                    if (mask.bit_count() & 1) == 1:
                        cnf_clauses.append(tuple(-v if ((mask >> i) & 1) else v for i, v in enumerate((a, b, c, t))))
                vs = [t] + vs[3:]
            k = len(vs)
            for mask in range(1 << k):
                # Clause forbids assignment `x_i = (mask >> i) & 1`, which has parity mask.bit_count() & 1
                if (mask.bit_count() & 1) != rhs:
                    cnf_clauses.append(tuple(-v if ((mask >> i) & 1) else v for i, v in enumerate(vs)))

    # Ciphertext output unit clauses
    for v, req in ct_units:
        lit = v if req else -v
        xcnf_reg.append((lit,))
        cnf_clauses.append((lit,))

    nvars = builder.num_vars
    total_xcnf_lines = len(xcnf_reg) + len(xcnf_xor)

    # Write XCNF (.xcnf.xz)
    xcnf_path.parent.mkdir(parents=True, exist_ok=True)
    x_lines = [f"c {c}" for c in header_comments]
    x_lines.append(f"p cnf {nvars} {total_xcnf_lines}")
    for cl in xcnf_reg:
        x_lines.append(" ".join(map(str, cl)) + " 0")
    for xl in xcnf_xor:
        x_lines.append("x " + " ".join(map(str, xl)) + " 0")
    x_lines.append("")
    with lzma.open(xcnf_path, "wb", preset=6) as f:
        f.write("\n".join(x_lines).encode("ascii"))

    # Write CNF (.cnf.xz)
    cnf_path.parent.mkdir(parents=True, exist_ok=True)
    c_lines = [f"c {c}" for c in header_comments]
    c_lines.append(f"p cnf {nvars_cnf} {len(cnf_clauses)}")
    for cl in cnf_clauses:
        c_lines.append(" ".join(map(str, cl)) + " 0")
    c_lines.append("")
    with lzma.open(cnf_path, "wb", preset=6) as f:
        f.write("\n".join(c_lines).encode("ascii"))

    return {
        "vars": nvars,
        "cnf_vars": nvars_cnf,
        "xcnf_reg": len(xcnf_reg),
        "xcnf_xor": len(xcnf_xor),
        "cnf_clauses": len(cnf_clauses),
    }


def _encode_varint(buf: bytearray, x: int) -> None:
    while x >= 0x80:
        buf.append((x & 0x7F) | 0x80)
        x >>= 7
    buf.append(x)


def export_binary_aig(
    builder: AesCircuitBuilder,
    key: bytes,
    free_k: int,
    ct_units: list[tuple[int, int]],
    comment: str,
    aig_path: Path,
) -> dict[str, int]:
    """Export exact combinational Binary AIGER 1.9 miter (`L=0, O=1`, `PO_0=1` iff SAT).

    Primary inputs `1..free_k` correspond directly to free key bits `0..free_k-1`;
    fixed key bits `free_k..255` are constant-folded to `0`/`1`.
    Uses 3-AND XOR decomposition `!(a & b) & !(!a & !b) == a ^ b` with structural
    hashing (`strash`), matching `src/to_anf.py` and Frobenius native AIGER XOR extraction.
    """
    aig_lit: list[int] = [0] * (builder.num_vars + 1)
    for b in range(free_k):
        aig_lit[1 + b] = (1 + b) * 2
    for b in range(free_k, 256):
        bit = (key[b // 8] >> (b % 8)) & 1
        aig_lit[1 + b] = 1 if bit else 0

    next_var = free_k + 1
    ands: list[tuple[int, int, int]] = []
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
        hit = strash.get((a, b))
        if hit is not None:
            return hit
        lhs = next_var * 2
        next_var += 1
        ands.append((lhs, a, b))
        strash[(a, b)] = lhs
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
        # Exact 3-AND XOR: !(a & b) & !(!a & !b) == a ^ b
        t1 = mk_and(a, b)
        t2 = mk_and(a ^ 1, b ^ 1)
        return mk_and(t1 ^ 1, t2 ^ 1)

    for g in builder.gates:
        if g.kind == "AND":
            l0, l1 = g.inputs
            a0 = aig_lit[abs(l0)] ^ (1 if l0 < 0 else 0)
            a1 = aig_lit[abs(l1)] ^ (1 if l1 < 0 else 0)
            aig_lit[g.out] = mk_and(a0, a1)
        else:
            acc = 1 if g.rhs else 0
            for u in g.inputs:
                acc = mk_xor(acc, aig_lit[u])
            aig_lit[g.out] = acc

    # Balanced AND miter tree over all ciphertext bit assertions
    asserts = [aig_lit[v] if req else (aig_lit[v] ^ 1) for v, req in ct_units]
    while len(asserts) > 1:
        nxt: list[int] = []
        for i in range(0, len(asserts), 2):
            if i + 1 < len(asserts):
                nxt.append(mk_and(asserts[i], asserts[i + 1]))
            else:
                nxt.append(asserts[i])
        asserts = nxt
    po0 = asserts[0]
    assert po0 not in (0, 1), f"Miter PO_0 trivially collapsed to constant {po0}!"

    # Compact to active cone-of-influence so Binary AIGER has zero dead gates
    # (Optional? Keep only reachable gates for cleanest, smallest AIGER!)
    # Check dead gates count first; in AES, every gate flows into outputs unless fixed-key folded,
    # and fixed-key folding already returns constants 0/1 without allocating AND gates!
    # Wait: unused key-schedule or earlier constant-folded intermediates never allocate AND gates.
    I = free_k
    A = len(ands)
    M = I + A
    buf = bytearray()
    buf.extend(f"aig {M} {I} 0 1 {A}\n{po0}\n".encode("ascii"))
    for lhs, r0, r1 in ands:
        assert lhs > r0 >= r1 >= 0, f"Invalid AIGER gate ordering: {lhs}, {r0}, {r1}"
        _encode_varint(buf, lhs - r0)
        _encode_varint(buf, r0 - r1)
    if comment:
        buf.extend(b"c\n")
        buf.extend(comment.rstrip("\n").encode("ascii") + b"\n")

    aig_path.parent.mkdir(parents=True, exist_ok=True)
    aig_path.write_bytes(lzma.compress(bytes(buf), preset=6))
    return {"aig_pis": I, "aig_ands": A, "aig_po0": po0}


def export_anf_from_xcnf(xcnf_path: Path, anf_path: Path) -> dict[str, int]:
    """Convert native `.xcnf.xz` to `.anf.xz` via repository `src/to_anf.py`."""
    raw = to_anf.read_bytes_auto(str(xcnf_path))
    anf_text, meta = to_anf.convert_xcnf_to_anf(raw, source_name=xcnf_path.name)
    to_anf.write_text_auto(str(anf_path), anf_text, xz_preset=6)
    # Run to_anf's own independent parser + 64-random-vector equivalence verifier
    to_anf.verify_conversion(str(xcnf_path), str(anf_path), meta)
    return {"anf_vars": meta["nv"], "anf_eqs": meta["neq"], "anf_deg": meta["max_deg"]}


# ============================================================================
# 4. Deterministic Synthetic Provenance & Verification Routines
# ============================================================================

def derive_bytes(name: str, role: str, nbytes: int) -> bytes:
    seed = f"frobenius-aes256-benchmark-v1:{name}:{role}".encode("ascii")
    return hashlib.sha256(seed).digest()[:nbytes]


def verify_all_formats_on_witness(
    xcnf_path: Path,
    cnf_path: Path,
    aig_path: Path,
    anf_path: Path,
    vals_1based: list[int],
    key: bytes,
    free_k: int,
    expected_sat: bool,
) -> None:
    """Independently re-parse all 4 compressed files from disk and verify witness/format."""
    # 1. XCNF
    x_text = lzma.open(xcnf_path, "rt", encoding="ascii").read()
    x_nv, x_reg, x_xor = to_anf.parse_xcnf_text(x_text)
    assert x_nv == len(vals_1based) - 1
    x_ok = to_anf.eval_xcnf(x_reg, x_xor, vals_1based)
    assert x_ok == expected_sat, f"XCNF witness check failed on {xcnf_path.name}: got {x_ok}, expected {expected_sat}"

    # 2. CNF
    c_text = lzma.open(cnf_path, "rt", encoding="ascii").read()
    c_nv, c_reg, c_xor = to_anf.parse_xcnf_text(c_text)
    assert len(c_xor) == 0, f"CNF {cnf_path.name} unexpectedly contains XOR lines"
    assert c_nv == len(vals_1based) - 1
    c_ok = to_anf.eval_xcnf(c_reg, [], vals_1based)
    assert c_ok == expected_sat, f"CNF witness check failed on {cnf_path.name}: got {c_ok}, expected {expected_sat}"

    # 3. Binary AIGER 1.9
    a_raw = lzma.decompress(aig_path.read_bytes())
    a_I, a_outs, a_ands = to_anf.parse_aiger_bytes(a_raw)
    assert a_I == free_k and len(a_outs) == 1
    pis = [0] + [(key[b // 8] >> (b % 8)) & 1 for b in range(free_k)]
    a_ok, _ = to_anf.eval_aiger(a_I, a_outs, a_ands, pis)
    assert a_ok == expected_sat, f"AIG witness check failed on {aig_path.name}: got {a_ok}, expected {expected_sat}"
    # Also verify a random perturbed key fails the miter (sanity check against constant-1 miter)
    if expected_sat and free_k >= 1:
        pis_flip = list(pis)
        pis_flip[1] ^= 1
        a_flip_ok, _ = to_anf.eval_aiger(a_I, a_outs, a_ands, pis_flip)
        assert not a_flip_ok, f"Perturbed key unexpectedly satisfied {aig_path.name}!"

    # 4. DIMACS-ANF
    anf_text = lzma.open(anf_path, "rt", encoding="ascii").read()
    hdr_nv, hdr_neq, max_v, max_deg, eqs = to_anf.parse_dimacs_anf_text(anf_text)
    assert hdr_nv == len(vals_1based) - 1 and hdr_neq == len(eqs) and max_v <= hdr_nv and max_deg <= 3
    anf_ok = to_anf.eval_anf_eqs(eqs, vals_1based)
    assert anf_ok == expected_sat, f"ANF witness check failed on {anf_path.name}: got {anf_ok}, expected {expected_sat}"


def exhaustive_count_solutions(key_template: bytes, plaintext: bytes, target_ct: bytes, rounds: int, free_k: int) -> int:
    """Exhaustively enumerate all 2^free_k keys (for free_k <= 16) to prove exact solution count."""
    assert free_k <= 16, f"free_k={free_k} too large for exhaustive Python check"
    base_key = bytearray(key_template)
    # Clear bits 0..free_k-1
    for b in range(free_k):
        base_key[b // 8] &= ~(1 << (b % 8))
    hits = 0
    for mask in range(1 << free_k):
        k = bytearray(base_key)
        k[0] |= mask & 0xFF
        if free_k > 8:
            k[1] |= (mask >> 8) & 0xFF
        if aes256_encrypt_bytes(bytes(k), plaintext, rounds) == target_ct:
            hits += 1
    return hits


def run_self_tests() -> None:
    """Verify FIPS 197 test vectors, Boyar-Peralta 256/256 S-box, and circuit equivalence."""
    # 1. Boyar-Peralta S-box 256/256 check via gate-level builder
    b_sbox = AesCircuitBuilder()
    in_byte = [(1 + i, 0) for i in range(8)]
    out_byte = b_sbox.sbox_byte(in_byte)
    assert b_sbox.n_and == 32 and b_sbox.n_xor == 81, f"Unexpected BP S-box gate counts: {b_sbox.n_and} AND, {b_sbox.n_xor} XOR"
    for x in range(256):
        k32 = bytes([x]) + bytes(31)
        vals, _ = b_sbox.evaluate(k32, [])
        got = 0
        for bit_i in range(8):
            v, inv = out_byte[bit_i]
            got |= ((vals[v] if v else 0) ^ inv) << bit_i
        assert got == SBOX[x], f"BP S-box mismatch at 0x{x:02x}: got 0x{got:02x}, expected 0x{SBOX[x]:02x}"
    print("[PASS] Boyar-Peralta SEA 2010 S-box: 256/256 exact match (32 ANDs, 81 XOR/XNORs)")

    # 2. NIST FIPS 197 official test vectors (byte-level AND gate-level circuit)
    vectors = [
        (
            "AES-256(0, 0)",
            bytes(32),
            bytes(16),
            bytes.fromhex("dc95c078a2408989ad48a21492842087"),
        ),
        (
            "FIPS 197 Appendix C.3",
            bytes(range(32)),
            bytes(0x11 * i for i in range(16)),
            bytes.fromhex("8ea2b7ca516745bfeafc49904b496089"),
        ),
    ]
    for label, k, p, expected_c in vectors:
        ref_c = aes256_encrypt_bytes(k, p, 14)
        assert ref_c == expected_c, f"{label} ref mismatch: {ref_c.hex()} != {expected_c.hex()}"
        cb = AesCircuitBuilder()
        rks = cb.build_key_schedule(14)
        out_blk = cb.build_encrypt_block(rks, p, 14)
        _, [circ_c] = cb.evaluate(k, [out_blk])
        assert circ_c == expected_c, f"{label} circuit mismatch: {circ_c.hex()} != {expected_c.hex()}"
        print(f"[PASS] {label}: ref & gate-level circuit == {expected_c.hex()} (128/128 bits)")

    # 3. Cross-check gate-level vs byte-level for ALL R in 1..14
    rng = random.Random(20261126)
    for r in range(1, 15):
        k = rng.randbytes(32)
        p = rng.randbytes(16)
        ref_c = aes256_encrypt_bytes(k, p, r)
        cb = AesCircuitBuilder()
        rks = cb.build_key_schedule(r)
        out_blk = cb.build_encrypt_block(rks, p, r)
        _, [circ_c] = cb.evaluate(k, [out_blk])
        assert circ_c == ref_c, f"Round {r} circuit mismatch!"
    print("[PASS] Gate-level == byte-level FIPS 197 reference across all R = 1..14")


# ============================================================================
# 5. Benchmark Suite Specification & Generation Driver
# ============================================================================

@dataclass(frozen=True)
class InstanceSpec:
    name: str
    rounds: int
    free_k: int
    num_pairs: int  # 1 or 2 known plaintext/ciphertext pairs
    flip_ct_bit0: bool  # True for mathematically proven UNSAT
    expected: str  # "SAT" or "UNSAT"
    description: str


# Default 10-instance graduated ladder (8 SAT / 2 UNSAT)
SUITE_SPECS: list[InstanceSpec] = [
    InstanceSpec("aes256_r01_k128_sat",     1, 128, 1, False, "SAT",   "1-round AES-256, 128 free key bits (trivial propagation)"),
    InstanceSpec("aes256_r02_k16_sat",      2,  16, 1, False, "SAT",   "2-round AES-256, 16 free key bits (easy/medium)"),
    InstanceSpec("aes256_r02_k32_sat",      2,  32, 1, False, "SAT",   "2-round AES-256, 32 free key bits (medium)"),
    InstanceSpec("aes256_r03_k16_sat",      3,  16, 1, False, "SAT",   "3-round AES-256, 16 free key bits (medium-hard)"),
    InstanceSpec("aes256_r04_k12_sat",      4,  12, 1, False, "SAT",   "4-round AES-256, 12 free key bits (full diffusion, medium-hard)"),
    InstanceSpec("aes256_r04_k12_unsat",    4,  12, 1, True,  "UNSAT", "4-round AES-256, 12 free key bits, CT bit 0 flipped (exhaustive UNSAT)"),
    InstanceSpec("aes256_r14_k10_sat",     14,  10, 1, False, "SAT",   "Full 14-round AES-256, 10 free key bits (full-round easy-medium)"),
    InstanceSpec("aes256_r14_k12_sat",     14,  12, 1, False, "SAT",   "Full 14-round AES-256, 12 free key bits (full-round medium-hard)"),
    InstanceSpec("aes256_r14_k12_unsat",   14,  12, 1, True,  "UNSAT", "Full 14-round AES-256, 12 free key bits, CT bit 0 flipped (exhaustive UNSAT)"),
    InstanceSpec("aes256_r14_k256_dual_sat", 14, 256, 2, False, "SAT", "Full 14-round AES-256, all 256 key bits free, dual P/C miter (cryptographic challenge)"),
]


def generate_instance(spec: InstanceSpec, out_root: Path, verify_exhaustive: bool = True) -> dict:
    key = derive_bytes(spec.name, "key", 32)
    plaintexts = [derive_bytes(spec.name, f"plaintext{i + 1}", 16) for i in range(spec.num_pairs)]
    true_cts = [aes256_encrypt_bytes(key, p, spec.rounds) for p in plaintexts]

    target_cts = [bytearray(c) for c in true_cts]
    if spec.flip_ct_bit0:
        target_cts[0][0] ^= 0x01
    target_cts_bytes = [bytes(c) for c in target_cts]

    # Build gate-level Boolean circuit
    cb = AesCircuitBuilder()
    rks = cb.build_key_schedule(spec.rounds)
    out_blocks = [cb.build_encrypt_block(rks, p, spec.rounds) for p in plaintexts]

    # Verify gate-level forward evaluation matches byte-level FIPS-197 reference
    vals, circ_cts = cb.evaluate(key, out_blocks)
    assert circ_cts == true_cts, f"Gate-level evaluation mismatch on {spec.name}"

    # Exhaustive verification for UNSAT instances (and uniqueness check for small k <= 12)
    sol_count: int | None = None
    if verify_exhaustive and spec.free_k <= 12 and spec.num_pairs == 1:
        sol_count = exhaustive_count_solutions(key, plaintexts[0], target_cts_bytes[0], spec.rounds, spec.free_k)
        if spec.expected == "UNSAT":
            assert sol_count == 0, f"UNSAT instance {spec.name} unexpectedly has {sol_count} solution(s)!"
        else:
            assert sol_count >= 1, f"SAT instance {spec.name} has 0 solutions!"

    key_units, ct_units = _collect_unit_constraints(key, spec.free_k, out_blocks, target_cts_bytes)

    dm_hashes = [bytes(c ^ p for c, p in zip(ct, pt)) for ct, pt in zip(target_cts_bytes, plaintexts)]
    fixed_desc = "all 256/256 free" if spec.free_k == 256 else f"bits 0..{spec.free_k - 1} free, bits {spec.free_k}..255 fixed"
    comments = [
        f"Synthetic NIST FIPS 197 AES-256 Key-Recovery / Davies-Meyer Preimage Benchmark: {spec.name}",
        "Author: Luke Hutchison (lukehutch) | License: MIT",
        f"Parameters: rounds={spec.rounds} free_key_bits={spec.free_k}/256 ({fixed_desc}) pairs={spec.num_pairs} expected={spec.expected}",
        f"Seed: SHA-256('frobenius-aes256-benchmark-v1:{spec.name}:<role>')",
    ]
    for idx, (pt, ct, dm) in enumerate(zip(plaintexts, target_cts_bytes, dm_hashes), 1):
        comments.append(f"Plaintext P{idx}: {pt.hex()} | Target C{idx}: {ct.hex()} | Davies-Meyer H{idx}=C{idx}^P{idx}: {dm.hex()}")
    if spec.flip_ct_bit0:
        comments.append("UNSAT construction: bit 0 of C1 byte 0 flipped; exhaustively verified 0 solutions over 2^k keys.")

    xcnf_path = out_root / "xcnf-orig" / f"{spec.name}.xcnf.xz"
    cnf_path = out_root / "cnf-converted" / f"{spec.name}.cnf.xz"
    aig_path = out_root / "aig-converted" / f"{spec.name}.aig.xz"
    anf_path = out_root / "anf-converted" / f"{spec.name}.anf.xz"

    xc_stats = export_xcnf_and_cnf(cb, key_units, ct_units, comments, xcnf_path, cnf_path)
    aig_comment = (
        f"benchmark={spec.name}\nexpected={spec.expected}\norigin=XCNF\n"
        f"rounds={spec.rounds}\nfree_key_bits={spec.free_k}\nauthor=Luke Hutchison (MIT)\n"
    )
    aig_stats = export_binary_aig(cb, key, spec.free_k, ct_units, aig_comment, aig_path)
    anf_stats = export_anf_from_xcnf(xcnf_path, anf_path)

    # Verify all 4 files re-parsed from disk
    verify_all_formats_on_witness(
        xcnf_path, cnf_path, aig_path, anf_path,
        vals, key, spec.free_k, expected_sat=(spec.expected == "SAT"),
    )

    return {
        "name": spec.name,
        "rounds": spec.rounds,
        "free_k": spec.free_k,
        "pairs": spec.num_pairs,
        "expected": spec.expected,
        "sol_count": sol_count,
        "key_hex": key.hex(),
        "p_hex": [p.hex() for p in plaintexts],
        "c_hex": [c.hex() for c in target_cts_bytes],
        "vars": xc_stats["vars"],
        "xcnf_reg": xc_stats["xcnf_reg"],
        "xcnf_xor": xc_stats["xcnf_xor"],
        "cnf_clauses": xc_stats["cnf_clauses"],
        "aig_pis": aig_stats["aig_pis"],
        "aig_ands": aig_stats["aig_ands"],
        "anf_vars": anf_stats["anf_vars"],
        "anf_eqs": anf_stats["anf_eqs"],
        "xcnf_bytes": xcnf_path.stat().st_size,
        "cnf_bytes": cnf_path.stat().st_size,
        "aig_bytes": aig_path.stat().st_size,
        "anf_bytes": anf_path.stat().st_size,
    }


def write_expected_tsv(specs: list[InstanceSpec], out_root: Path) -> None:
    rows = sorted((f"{s.name}.xcnf", s.expected) for s in specs)
    tsv_path = out_root / "expected.tsv"
    tsv_path.write_text("".join(f"{k}\t{v}\n" for k, v in rows), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Clean-room NIST FIPS 197 AES-256 SAT/XCNF/AIG/ANF generator.")
    ap.add_argument("--self-test", action="store_true", help="Run FIPS 197 & Boyar-Peralta self-tests only")
    ap.add_argument("--out-dir", type=Path, default=SUITE_DIR, help="Output collection directory")
    ap.add_argument("--only", type=str, default="", help="Comma-separated subset of instance names to generate")
    args = ap.parse_args()

    run_self_tests()
    if args.self_test:
        return

    specs = SUITE_SPECS
    if args.only:
        wanted = set(args.only.split(","))
        specs = [s for s in specs if s.name in wanted]

    out_root = args.out_dir.resolve()
    results = []
    for spec in specs:
        res = generate_instance(spec, out_root)
        results.append(res)
        sol_str = f" [exhaustive sols={res['sol_count']}]" if res["sol_count"] is not None else ""
        print(
            f"[OK] {res['name']:24s} R={res['rounds']:2d} k={res['free_k']:3d} {res['expected']:5s}{sol_str} | "
            f"vars={res['vars']:6,d} cnf_cl={res['cnf_clauses']:7,d} xors={res['xcnf_xor']:6,d} aig_and={res['aig_ands']:7,d} | "
            f"xcnf={res['xcnf_bytes']/1024:6.1f}KB cnf={res['cnf_bytes']/1024:6.1f}KB "
            f"aig={res['aig_bytes']/1024:6.1f}KB anf={res['anf_bytes']/1024:6.1f}KB"
        )

    if not args.only:
        write_expected_tsv(specs, out_root)
        print(f"Wrote {out_root / 'expected.tsv'} ({len(specs)} rows)")
        print("\nDeterministic Synthetic Provenance (SHA-256('frobenius-aes256-benchmark-v1:<name>:<role>')):")
        for res in results:
            p_str = ", ".join(res["p_hex"])
            c_str = ", ".join(res["c_hex"])
            print(f"  {res['name']:24s} | K={res['key_hex']} | P={p_str} | C={c_str}")


if __name__ == "__main__":
    main()
