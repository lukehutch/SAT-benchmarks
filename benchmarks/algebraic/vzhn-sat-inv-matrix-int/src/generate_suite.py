#!/usr/bin/env python3
"""Reproducible benchmark generator for vzhn-sat-inv-matrix-int
(Exact Integer Matrix Inversion over Z from vzhn/sat-inv-matrix-py).

Upstream source & credit:
  - Author: Vladimir Zhilin (@vzhilin_me, https://twitter.com/vzhilin_me)
  - Repository: https://github.com/vzhn/sat-inv-matrix-py
    (commit 6bfcdafea648913655d4d838d8a9adc847925c11)
  - Original Kotlin / Z3 predecessors:
    https://github.com/vzhn/sat-inv-matrix
    https://github.com/vzhn/z3-inv-matrix

Generates the 11 exact integer matrix inversion DIMACS CNF instances
(6 SAT / 5 UNSAT) for A * B = I over Z (invmatrix.py), converts every instance
losslessly into all 4 repository formats (.cnf.xz, .aig.xz, .xcnf.xz, .anf.xz),
and emits exact ground-truth expected.tsv verified by Bareiss determinant and
exact rational Gauss-Jordan inversion.

Usage:
  python3 src/generate_suite.py
"""
from __future__ import annotations

import lzma
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


def bareiss_det(a: list[list[int]]) -> int:
    """Exact integer determinant via fraction-free Bareiss elimination."""
    n = len(a)
    m = [row[:] for row in a]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if m[k][k] == 0:
            piv = next((r for r in range(k + 1, n) if m[r][k] != 0), None)
            if piv is None:
                return 0
            m[k], m[piv] = m[piv], m[k]
            sign = -sign
        pk = m[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * pk - m[i][k] * m[k][j]) // prev
        prev = pk
    return sign * m[n - 1][n - 1]


def exact_integer_inverse(a: list[list[int]]) -> list[list[int]] | None:
    """Return exact integer inverse A^-1 iff det(A) in {+1, -1}, else None."""
    d = bareiss_det(a)
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
    """Return the exact deterministic 11-instance integer inversion specification."""
    m4 = load_mat("matrix/4x4.txt")
    m8 = load_mat("matrix/8x8.txt")
    m10 = load_mat("matrix/10x10.txt")
    m16 = load_mat("matrix/16x16.txt")
    m16_sing = [[x + y for x, y in zip(m16[1], m16[2])]] + m16[1:]
    m3_det2 = [[2, 0, 0], [0, 1, 1], [1, 0, 1]]

    return [
        {
            "name": "int_3x3_det2_w3_unsat",
            "matrix": m3_det2,
            "width": invmatrix.auto_width(m3_det2),
            "expected": "UNSAT",
            "desc": "Upstream README 3x3 matrix with det=2 (non-unimodular), auto width w=3",
        },
        {
            "name": "int_4x4_w5_unsat",
            "matrix": m4,
            "width": 5,
            "expected": "UNSAT",
            "desc": "Upstream matrix/4x4.txt (det=1, max entry 22), width-tight w=5 (<6)",
        },
        {
            "name": "int_4x4_w7_sat",
            "matrix": m4,
            "width": invmatrix.auto_width(m4),
            "expected": "SAT",
            "desc": "Upstream matrix/4x4.txt (det=1), Hadamard auto width w=7",
        },
        {
            "name": "int_8x8_w16_sat",
            "matrix": m8,
            "width": 16,
            "expected": "SAT",
            "desc": "Upstream matrix/8x8.txt (det=1), fixed width w=16",
        },
        {
            "name": "int_8x8_w36_sat",
            "matrix": m8,
            "width": invmatrix.auto_width(m8),
            "expected": "SAT",
            "desc": "Upstream matrix/8x8.txt (det=1), Hadamard auto width w=36",
        },
        {
            "name": "int_10x10_w4_unsat",
            "matrix": m10,
            "width": 4,
            "expected": "UNSAT",
            "desc": "Upstream matrix/10x10.txt (det=1, entry 11), width-tight w=4 (<5)",
        },
        {
            "name": "int_10x10_w16_sat",
            "matrix": m10,
            "width": 16,
            "expected": "SAT",
            "desc": "Upstream matrix/10x10.txt (det=1), fixed width w=16",
        },
        {
            "name": "int_10x10_w47_sat",
            "matrix": m10,
            "width": invmatrix.auto_width(m10),
            "expected": "SAT",
            "desc": "Upstream matrix/10x10.txt (det=1), Hadamard auto width w=47",
        },
        {
            "name": "int_16x16_w5_unsat",
            "matrix": m16,
            "width": 5,
            "expected": "UNSAT",
            "desc": "Upstream matrix/16x16.txt (det=1, entry 29), width-tight w=5 (<6)",
        },
        {
            "name": "int_16x16_sing_w16_unsat",
            "matrix": m16_sing,
            "width": 16,
            "expected": "UNSAT",
            "desc": "Singular perturbation of matrix/16x16.txt (row0=row1+row2, det=0), w=16",
        },
        {
            "name": "int_16x16_w16_sat",
            "matrix": m16,
            "width": 16,
            "expected": "SAT",
            "desc": "Upstream matrix/16x16.txt (det=1), fixed width w=16",
        },
    ]


def verify_ground_truth(spec: dict) -> None:
    a = spec["matrix"]
    w = spec["width"]
    inv = exact_integer_inverse(a)
    is_sat = inv is not None and integer_fits_width(inv, w)
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

    with tempfile.TemporaryDirectory(prefix="vzhn_int_gen_") as td:
        tdir = Path(td)
        for spec in specs:
            name = spec["name"]
            verify_ground_truth(spec)
            a = spec["matrix"]
            n = len(a)
            w = spec["width"]
            cnf, _vmap = invmatrix.encode(a, w)
            comments = [
                f"vzhn/sat-inv-matrix-py: {spec['desc']}",
                f"integer matrix inversion A*B = I, n={n}, width={w} (exact, no overflow)",
                f"expected={spec['expected']}",
            ]
            dimacs_text = cnf.dimacs(comments)
            cnf_raw = tdir / f"{name}.cnf"
            cnf_raw.write_text(dimacs_text, encoding="ascii")

            cnf_xz = cnf_dir / f"{name}.cnf.xz"
            with lzma.open(cnf_xz, "wb", preset=6) as f:
                f.write(dimacs_text.encode("ascii"))

            aig_raw = tdir / f"{name}.aig"
            _, _, n_ands = cnf2aig.cnf_to_aiger(
                cnf_raw, aig_raw, comment=f"Converted from cnf-orig/{name}.cnf.xz"
            )
            aig_xz = aig_dir / f"{name}.aig.xz"
            with lzma.open(aig_xz, "wb", preset=6) as f:
                f.write(aig_raw.read_bytes())

            xcnf_xz = xcnf_dir / f"{name}.xcnf.xz"
            _, _, rem_cls, n_xors = cnf2xcnf.cnf_to_xcnf(cnf_raw, xcnf_xz)

            anf_xz = anf_dir / f"{name}.anf.xz"
            subprocess.run(
                [sys.executable, str(TO_ANF), str(xcnf_xz), str(anf_xz), "--verify"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            meta_rows.append({"name": name, "expected": spec["expected"]})
            print(f"[OK] {name:<28} {spec['expected']:<5} v={cnf.nvars:>6} c={len(cnf.clauses):>7} xors={n_xors:>5}")

    tsv_lines = sorted(f"{r['name']}.cnf\t{r['expected']}" for r in meta_rows)
    (SUITE_DIR / "expected.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")
    return meta_rows


if __name__ == "__main__":
    generate_all()
