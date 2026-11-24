#!/usr/bin/env python3
"""Reproducible benchmark generator for vzhn-sat-inv-matrix-mod
(Modular Ring Matrix Inversion over Z/mZ from vzhn/sat-inv-matrix-py).

Upstream source & credit:
  - Author: Vladimir Zhilin (@vzhilin_me, https://twitter.com/vzhilin_me)
  - Repository: https://github.com/vzhn/sat-inv-matrix-py
    (commit 6bfcdafea648913655d4d838d8a9adc847925c11)
  - Original Kotlin / Z3 predecessors:
    https://github.com/vzhn/sat-inv-matrix
    https://github.com/vzhn/z3-inv-matrix

Generates the 15 modular ring matrix inversion DIMACS CNF instances
(10 SAT / 5 UNSAT) for A * B = I (mod m) over Z/mZ (modinv.py), converts every
instance losslessly into all 4 repository formats (.cnf.xz, .aig.xz, .xcnf.xz,
.anf.xz), and emits exact ground-truth expected.tsv verified by exact Bareiss
determinant gcd(det(A), m) = 1 and modular Gauss-Jordan inversion.

Usage:
  python3 src/generate_suite.py
"""
from __future__ import annotations

import lzma
import math
import subprocess
import sys
import tempfile
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


def load_mat(rel: str) -> list[list[int]]:
    return invmatrix.parse_matrix((SRC_DIR / rel).read_text(encoding="utf-8"))


def build_specs() -> list[dict]:
    """Return the exact deterministic 15-instance modular inversion specification."""
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
        {
            "name": "mod_3x3_m26_bin_sat",
            "matrix": s3_m26,
            "mod": 26,
            "encoding": "binary",
            "columns": None,
            "expected": "SAT",
            "desc": "Upstream samples/matrix3x3_mod_26.txt (det=441, mod 26), binary encoding",
        },
        {
            "name": "mod_3x3_m26_oh_sat",
            "matrix": s3_m26,
            "mod": 26,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Upstream samples/matrix3x3_mod_26.txt (det=441, mod 26), one-hot encoding",
        },
        {
            "name": "mod_5x5_m27_oh_sat",
            "matrix": s5_m27,
            "mod": 27,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Upstream samples/matrix5x5_mod_27.txt (det=34772, mod 27), one-hot encoding",
        },
        {
            "name": "mod_5x5_m27_sing_oh_unsat",
            "matrix": s5_m27_sing,
            "mod": 27,
            "encoding": "onehot",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular mod 27 perturbation of matrix5x5_mod_27.txt (row0*=3 mod 27), one-hot",
        },
        {
            "name": "mod_10x10_m13_c0_oh_sat",
            "matrix": s10_m26,
            "mod": 13,
            "encoding": "onehot",
            "columns": [0],
            "expected": "SAT",
            "desc": "Upstream samples/matrix10x10_mod_26.txt CRT mod-13 factor, column 0, one-hot",
        },
        {
            "name": "mod_12x12_m3_oh_sat",
            "matrix": r12_m3,
            "mod": 3,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 12x12 matrix mod 3 (seed=22), one-hot encoding",
        },
        {
            "name": "mod_12x12_m3_sing_oh_unsat",
            "matrix": r12_m3_sing,
            "mod": 3,
            "encoding": "onehot",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 12x12 matrix mod 3 (seed=22, row0=row1+row2 mod 3), one-hot encoding",
        },
        {
            "name": "mod_24x24_m2_bin_sat",
            "matrix": r24_m2,
            "mod": 2,
            "encoding": "binary",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 24x24 matrix over GF(2) (seed=124), binary encoding",
        },
        {
            "name": "mod_24x24_m2_bin_unsat",
            "matrix": r24_m2_sing,
            "mod": 2,
            "encoding": "binary",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 24x24 matrix over GF(2) (seed=124, row0=r1^r2^r3), binary encoding",
        },
        {
            "name": "mod_24x24_m2_oh_sat",
            "matrix": r24_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 24x24 matrix over GF(2) (seed=124), one-hot encoding",
        },
        {
            "name": "mod_24x24_m2_oh_unsat",
            "matrix": r24_m2_sing,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 24x24 matrix over GF(2) (seed=124, row0=r1^r2^r3), one-hot encoding",
        },
        {
            "name": "mod_32x32_m2_oh_sat",
            "matrix": r32_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 32x32 matrix over GF(2) (seed=132), one-hot encoding",
        },
        {
            "name": "mod_40x40_m2_oh_sat",
            "matrix": r40_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 40x40 matrix over GF(2) (seed=140), one-hot encoding",
        },
        {
            "name": "mod_40x40_m2_bin_unsat",
            "matrix": r40_m2_sing,
            "mod": 2,
            "encoding": "binary",
            "columns": None,
            "expected": "UNSAT",
            "desc": "Singular 40x40 matrix over GF(2) (seed=140, row0=r1^r2^r3), binary encoding",
        },
        {
            "name": "mod_48x48_m2_oh_sat",
            "matrix": r48_m2,
            "mod": 2,
            "encoding": "onehot",
            "columns": None,
            "expected": "SAT",
            "desc": "Random invertible 48x48 matrix over GF(2) (seed=148), one-hot encoding",
        },
    ]


def verify_ground_truth(spec: dict) -> None:
    a = spec["matrix"]
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

    with tempfile.TemporaryDirectory(prefix="vzhn_mod_gen_") as td:
        tdir = Path(td)
        for spec in specs:
            name = spec["name"]
            verify_ground_truth(spec)
            a = spec["matrix"]
            n = len(a)
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
