#!/usr/bin/env python3
"""Reproducible benchmark generator for vzhn/sat-inv-matrix-py.

Upstream source & credit:
  - Author: Vladimir Zhilin (@vzhilin_me, https://twitter.com/vzhilin_me)
  - Repository: https://github.com/vzhn/sat-inv-matrix-py
    (commit 6bfcdafea648913655d4d838d8a9adc847925c11)
  - Original Kotlin / Z3 predecessors:
    https://github.com/vzhn/sat-inv-matrix
    https://github.com/vzhn/z3-inv-matrix

Generates 26 exact DIMACS CNF instances (16 SAT / 10 UNSAT) spanning both:
  1. Exact integer matrix inversion A * B = I over Z (invmatrix.py), and
  2. Modular matrix inversion A * B = I (mod m) over Z/mZ (modinv.py),
then converts every instance losslessly into all 4 repository formats:
  - cnf-orig/*.cnf.xz
  - aig-converted/*.aig.xz   (Binary AIGER 1.9 combinational miter)
  - xcnf-converted/*.xcnf.xz (CryptoMiniSat XCNF with extracted native XORs)
  - anf-converted/*.anf.xz   (DIMACS-ANF, degree <= 3)
and emits exact ground-truth expected.tsv (verified mathematically by exact
Bareiss determinant and rational/modular Gauss-Jordan inversion).

Usage:
  python3 src/generate_suite.py
"""
from __future__ import annotations

import json
import lzma
import math
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SUITE_DIR = SRC_DIR.parent
REPO_ROOT = SUITE_DIR.parent
TO_ANF = REPO_ROOT / "src" / "to_anf.py"

sys.path.insert(0, str(SRC_DIR))
import cnf2aig  # noqa: E402
import cnf2xcnf  # noqa: E402
import invmatrix  # noqa: E402
import modinv  # noqa: E402


def exact_integer_inverse(a: list[list[int]]) -> list[list[int]] | None:
    """Return exact integer inverse A^-1 iff det(A) in {+1, -1}, else None."""
    d = modinv.det(a)
    if abs(d) != 1:
        return None
    n = len(a)
    aug = [
        [Fraction(x) for x in row] + [Fraction(1 if i == j else 0) for j in range(n)]
        for i, row in enumerate(a)
    ]
    for c in range(n):
        p = next(r for r in range(c, n) if aug[r][c] != 0)
        aug[c], aug[p] = aug[p], aug[c]
        pv = aug[c][c]
        aug[c] = [x / pv for x in aug[c]]
        for r in range(n):
            if r != c and aug[r][c] != 0:
                f = aug[r][c]
                aug[r] = [x - f * y for x, y in zip(aug[r], aug[c])]
    inv = [[int(aug[i][n + j]) for j in range(n)] for i in range(n)]
    assert invmatrix.is_identity(invmatrix.matmul(a, inv))
    return inv


def integer_fits_width(inv: list[list[int]], w: int) -> bool:
    lo = -(1 << (w - 1))
    hi = (1 << (w - 1)) - 1
    return all(lo <= x <= hi for row in inv for x in row)


def load_mat(rel: str) -> list[list[int]]:
    return invmatrix.parse_matrix((SRC_DIR / rel).read_text(encoding="utf-8"))


def build_specs() -> list[dict]:
    """Return the exact deterministic 26-instance suite specification."""
    m4 = load_mat("matrix/4x4.txt")
    m8 = load_mat("matrix/8x8.txt")
    m10 = load_mat("matrix/10x10.txt")
    m16 = load_mat("matrix/16x16.txt")
    m16_sing = [[x + y for x, y in zip(m16[1], m16[2])]] + m16[1:]
    m3_det2 = [[2, 0, 0], [0, 1, 1], [1, 0, 1]]

    s3_m26 = load_mat("samples/matrix3x3_mod_26.txt")
    s5_m27 = load_mat("samples/matrix5x5_mod_27.txt")
    s5_m27_sing = [[(3 * x) % 27 for x in s5_m27[0]]] + s5_m27[1:]
    s10_m26 = load_mat("samples/matrix10x10_mod_26.txt")

    r12_m3 = modinv.random_invertible(12, 3, 22)
    r12_m3_sing = [[(x + y) % 3 for x, y in zip(r12_m3[1], r12_m3[2])]] + r12_m3[1:]

    r24_m2 = modinv.random_invertible(24, 2, 124)
    r24_m2_sing = [[(r24_m2[1][j] ^ r24_m2[2][j] ^ r24_m2[3][j]) for j in range(24)]] + r24_m2[1:]

    r32_m2 = modinv.random_invertible(32, 2, 132)

    r40_m2 = modinv.random_invertible(40, 2, 140)
    r40_m2_sing = [[(r40_m2[1][j] ^ r40_m2[2][j] ^ r40_m2[3][j]) for j in range(40)]] + r40_m2[1:]

    r48_m2 = modinv.random_invertible(48, 2, 148)

    return [
        # --- Exact integer matrix inversion over Z (invmatrix.py): 11 instances (6 SAT / 5 UNSAT) ---
        {
            "name": "int_3x3_det2_w3_unsat",
            "family": "int",
            "matrix": m3_det2,
            "width": invmatrix.auto_width(m3_det2),
            "expected": "UNSAT",
            "desc": "Upstream README 3x3 matrix with det=2 (non-unimodular), auto width w=3",
        },
        {
            "name": "int_4x4_w5_unsat",
            "family": "int",
            "matrix": m4,
            "width": 5,
            "expected": "UNSAT",
            "desc": "Upstream matrix/4x4.txt (det=1, max entry 22), width-tight w=5 (<6)",
        },
        {
            "name": "int_4x4_w7_sat",
            "family": "int",
            "matrix": m4,
            "width": invmatrix.auto_width(m4),
            "expected": "SAT",
            "desc": "Upstream matrix/4x4.txt (det=1), Hadamard auto width w=7",
        },
        {
            "name": "int_8x8_w16_sat",
            "family": "int",
            "matrix": m8,
            "width": 16,
            "expected": "SAT",
            "desc": "Upstream matrix/8x8.txt (det=1), fixed width w=16",
        },
        {
            "name": "int_8x8_w36_sat",
            "family": "int",
            "matrix": m8,
            "width": invmatrix.auto_width(m8),
            "expected": "SAT",
            "desc": "Upstream matrix/8x8.txt (det=1), Hadamard auto width w=36",
        },
        {
            "name": "int_10x10_w4_unsat",
            "family": "int",
            "matrix": m10,
            "width": 4,
            "expected": "UNSAT",
            "desc": "Upstream matrix/10x10.txt (det=1, entry 11), width-tight w=4 (<5)",
        },
        {
            "name": "int_10x10_w16_sat",
            "family": "int",
            "matrix": m10,
            "width": 16,
            "expected": "SAT",
            "desc": "Upstream matrix/10x10.txt (det=1), fixed width w=16",
        },
        {
            "name": "int_10x10_w47_sat",
            "family": "int",
            "matrix": m10,
            "width": invmatrix.auto_width(m10),
            "expected": "SAT",
            "desc": "Upstream matrix/10x10.txt (det=1), Hadamard auto width w=47",
        },
        {
            "name": "int_16x16_w5_unsat",
            "family": "int",
            "matrix": m16,
            "width": 5,
            "expected": "UNSAT",
            "desc": "Upstream matrix/16x16.txt (det=1, entry 29), width-tight w=5 (<6)",
        },
        {
            "name": "int_16x16_sing_w16_unsat",
            "family": "int",
            "matrix": m16_sing,
            "width": 16,
            "expected": "UNSAT",
            "desc": "Singular perturbation of matrix/16x16.txt (row0=row1+row2, det=0), w=16",
        },
        {
            "name": "int_16x16_w16_sat",
            "family": "int",
            "matrix": m16,
            "width": 16,
            "expected": "SAT",
            "desc": "Upstream matrix/16x16.txt (det=1), fixed width w=16",
        },
        # --- Modular matrix inversion over Z/mZ (modinv.py): 15 instances (10 SAT / 5 UNSAT) ---
        {
            "name": "mod_3x3_m26_bin_sat",
            "family": "mod",
            "matrix": s3_m26,
            "mod": 26,
            "encoding": "binary",
            "columns": None,
            "expected": "SAT",
            "desc": "Upstream samples/matrix3x3_mod_26.txt (det=441, mod 26), binary encoding",
        },
        {
            "name": "mod_3x3_m26_oh_sat",
            "family": "mod",
            "matrix": s3_m26,
            "mod": 26,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Upstream samples/matrix3x3_mod_26.txt (det=441, mod 26), one-hot encoding",
        },
        {
            "name": "mod_5x5_m27_oh_sat",
            "family": "mod",
            "matrix": s5_m27,
            "mod": 27,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Upstream samples/matrix5x5_mod_27.txt (det=34772, mod 27), one-hot encoding",
        },
        {
            "name": "mod_5x5_m27_sing_oh_unsat",
            "family": "mod",
            "matrix": s5_m27_sing,
            "mod": 27,
            "encoding": "onehot",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular mod 27 perturbation of matrix5x5_mod_27.txt (row0*=3 mod 27), one-hot",
        },
        {
            "name": "mod_10x10_m13_c0_oh_sat",
            "family": "mod",
            "matrix": s10_m26,
            "mod": 13,
            "encoding": "onehot",
            "columns": [0],
            "expected": "SAT",
            "desc": "Upstream samples/matrix10x10_mod_26.txt CRT mod-13 factor, column 0, one-hot",
        },
        {
            "name": "mod_12x12_m3_oh_sat",
            "family": "mod",
            "matrix": r12_m3,
            "mod": 3,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 12x12 matrix mod 3 (seed=22), one-hot encoding",
        },
        {
            "name": "mod_12x12_m3_sing_oh_unsat",
            "family": "mod",
            "matrix": r12_m3_sing,
            "mod": 3,
            "encoding": "onehot",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 12x12 matrix mod 3 (seed=22, row0=row1+row2 mod 3), one-hot encoding",
        },
        {
            "name": "mod_24x24_m2_bin_sat",
            "family": "mod",
            "matrix": r24_m2,
            "mod": 2,
            "encoding": "binary",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 24x24 matrix over GF(2) (seed=124), binary encoding",
        },
        {
            "name": "mod_24x24_m2_bin_unsat",
            "family": "mod",
            "matrix": r24_m2_sing,
            "mod": 2,
            "encoding": "binary",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 24x24 matrix over GF(2) (seed=124, row0=r1^r2^r3), binary encoding",
        },
        {
            "name": "mod_24x24_m2_oh_sat",
            "family": "mod",
            "matrix": r24_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 24x24 matrix over GF(2) (seed=124), one-hot encoding",
        },
        {
            "name": "mod_24x24_m2_oh_unsat",
            "family": "mod",
            "matrix": r24_m2_sing,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 24x24 matrix over GF(2) (seed=124, row0=r1^r2^r3), one-hot encoding",
        },
        {
            "name": "mod_32x32_m2_oh_sat",
            "family": "mod",
            "matrix": r32_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 32x32 matrix over GF(2) (seed=132), one-hot encoding",
        },
        {
            "name": "mod_40x40_m2_oh_sat",
            "family": "mod",
            "matrix": r40_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 40x40 matrix over GF(2) (seed=140), one-hot encoding",
        },
        {
            "name": "mod_40x40_m2_bin_unsat",
            "family": "mod",
            "matrix": r40_m2_sing,
            "mod": 2,
            "encoding": "binary",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 40x40 matrix over GF(2) (seed=140, row0=r1^r2^r3), binary encoding",
        },
        {
            "name": "mod_48x48_m2_oh_sat",
            "family": "mod",
            "matrix": r48_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 48x48 matrix over GF(2) (seed=148), one-hot encoding",
        },
    ]


def verify_ground_truth(spec: dict) -> None:
    """Independently verify mathematical satisfiability via exact linear algebra."""
    a = spec["matrix"]
    if spec["family"] == "int":
        w = spec["width"]
        inv = exact_integer_inverse(a)
        is_sat = inv is not None and integer_fits_width(inv, w)
    else:
        m = spec["mod"]
        d = modinv.det(a)
        is_sat = math.gcd(d, m) == 1
        if is_sat:
            ref = modinv.inverse_mod_reference(a, m)
            assert ref is not None and modinv.is_identity_mod(a, ref, m)
    actual = "SAT" if is_sat else "UNSAT"
    assert actual == spec["expected"], (
        f"Ground-truth mismatch on {spec['name']}: computed {actual} != expected {spec['expected']}"
    )


def generate_all() -> list[dict]:
    cnf_dir = SUITE_DIR / "cnf-orig"
    aig_dir = SUITE_DIR / "aig-converted"
    xcnf_dir = SUITE_DIR / "xcnf-converted"
    anf_dir = SUITE_DIR / "anf-converted"
    for d in (cnf_dir, aig_dir, xcnf_dir, anf_dir):
        d.mkdir(parents=True, exist_ok=True)

    specs = build_specs()
    meta_rows: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="vzhn_gen_") as td:
        tdir = Path(td)
        for spec in specs:
            name = spec["name"]
            verify_ground_truth(spec)
            a = spec["matrix"]
            n = len(a)

            if spec["family"] == "int":
                w = spec["width"]
                cnf, _vmap = invmatrix.encode(a, w)
                comments = [
                    f"vzhn/sat-inv-matrix-py: {spec['desc']}",
                    f"integer matrix inversion A*B = I, n={n}, width={w} (exact, no overflow)",
                    f"expected={spec['expected']}",
                ]
            else:
                m = spec["mod"]
                enc = spec["encoding"]
                cols = spec["columns"]
                if enc == "onehot":
                    cnf, _vmap = modinv.encode_onehot(a, m, cols)
                else:
                    cnf, _vmap = modinv.encode(a, m)
                col_str = f", columns={cols}" if cols is not None else ""
                comments = [
                    f"vzhn/sat-inv-matrix-py: {spec['desc']}",
                    f"modular matrix inversion A*B = I mod {m}, n={n}, encoding={enc}{col_str}",
                    f"expected={spec['expected']}",
                ]

            dimacs_text = cnf.dimacs(comments)
            cnf_raw = tdir / f"{name}.cnf"
            cnf_raw.write_text(dimacs_text, encoding="ascii")

            # 1. cnf-orig/*.cnf.xz
            cnf_xz = cnf_dir / f"{name}.cnf.xz"
            with lzma.open(cnf_xz, "wb", preset=6) as f:
                f.write(dimacs_text.encode("ascii"))

            # 2. aig-converted/*.aig.xz
            aig_raw = tdir / f"{name}.aig"
            _, _, n_ands = cnf2aig.cnf_to_aiger(
                cnf_raw, aig_raw, comment=f"Converted from cnf-orig/{name}.cnf.xz"
            )
            aig_xz = aig_dir / f"{name}.aig.xz"
            with lzma.open(aig_xz, "wb", preset=6) as f:
                f.write(aig_raw.read_bytes())

            # 3. xcnf-converted/*.xcnf.xz
            xcnf_xz = xcnf_dir / f"{name}.xcnf.xz"
            _, _, rem_cls, n_xors = cnf2xcnf.cnf_to_xcnf(cnf_raw, xcnf_xz)

            # 4. anf-converted/*.anf.xz (convert from xcnf to preserve native XORs as degree-1 linear eqs)
            anf_xz = anf_dir / f"{name}.anf.xz"
            subprocess.run(
                [sys.executable, str(TO_ANF), str(xcnf_xz), str(anf_xz), "--verify"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Verify size cap (< 95 MB)
            for p in (cnf_xz, aig_xz, xcnf_xz, anf_xz):
                sz = p.stat().st_size
                assert sz < 95 * 1024 * 1024, f"{p} exceeds 95 MB ({sz} bytes)"

            row = {
                "name": name,
                "family": spec["family"],
                "n": n,
                "expected": spec["expected"],
                "desc": spec["desc"],
                "vars": cnf.nvars,
                "clauses": len(cnf.clauses),
                "aig_ands": n_ands,
                "xcnf_rem_clauses": rem_cls,
                "xcnf_xors": n_xors,
                "cnf_xz_bytes": cnf_xz.stat().st_size,
                "aig_xz_bytes": aig_xz.stat().st_size,
                "xcnf_xz_bytes": xcnf_xz.stat().st_size,
                "anf_xz_bytes": anf_xz.stat().st_size,
            }
            if spec["family"] == "int":
                row["width"] = spec["width"]
            else:
                row["mod"] = spec["mod"]
                row["encoding"] = spec["encoding"]
                row["columns"] = spec["columns"]
            meta_rows.append(row)
            print(
                f"[OK] {name:<28} {spec['expected']:<5} v={cnf.nvars:>6} c={len(cnf.clauses):>7} "
                f"xors={n_xors:>5} | cnf={row['cnf_xz_bytes']/1024:6.1f}KB "
                f"aig={row['aig_xz_bytes']/1024:6.1f}KB xcnf={row['xcnf_xz_bytes']/1024:6.1f}KB "
                f"anf={row['anf_xz_bytes']/1024:6.1f}KB",
                flush=True,
            )

    # Write strict 2-col expected.tsv (no header, ASCII-sorted by <instance_without_.xz>)
    tsv_lines = sorted(f"{r['name']}.cnf\t{r['expected']}" for r in meta_rows)
    (SUITE_DIR / "expected.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")
    print(f"\nGenerated {len(meta_rows)} instances across 4 formats + expected.tsv.")
    return meta_rows


if __name__ == "__main__":
    generate_all()
