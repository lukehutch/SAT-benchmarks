#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `vzhn-sat-inv-matrix` benchmark collection.

Parses the real upstream matrices (`src/matrix/4x4.txt` and
`src/samples/matrix3x3_mod_26.txt`), computes their exact mathematical inverses
(`A * B = I` over Z and `A * B = I (mod 26)`), verifies them, and renders a
clean light-card dual-panel schematic that reads crisply in both GitHub light
and dark modes.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SUITE_DIR = SRC_DIR.parent
OUT_SVG = SUITE_DIR / "diagram.svg"

sys.path.insert(0, str(SRC_DIR))
import generate_suite  # noqa: E402
import invmatrix  # noqa: E402
import modinv  # noqa: E402


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def draw_matrix(
    parts: list[str],
    x: float,
    y: float,
    mat: list[list[int]],
    cell_w: float,
    cell_h: float,
    label: str,
    label_color: str,
    highlight_diag: bool = False,
    highlight_val: int | None = None,
    fill_bg: str = "#f6f8fa",
    bracket_color: str = "#57606a",
) -> tuple[float, float]:
    rows = len(mat)
    cols = len(mat[0])
    w = cols * cell_w + 14
    h = rows * cell_h + 10
    # Subtle card behind matrix
    parts.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="5" fill="{fill_bg}" stroke="#d8dee4" stroke-width="1"/>'
    )
    # Left & right square brackets
    bx0 = x + 4
    bx1 = x + w - 4
    by0 = y + 4
    by1 = y + h - 4
    tick = 5
    parts.append(
        f'<path d="M {bx0+tick:.1f} {by0:.1f} L {bx0:.1f} {by0:.1f} '
        f'L {bx0:.1f} {by1:.1f} L {bx0+tick:.1f} {by1:.1f}" '
        f'fill="none" stroke="{bracket_color}" stroke-width="1.6" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="M {bx1-tick:.1f} {by0:.1f} L {bx1:.1f} {by0:.1f} '
        f'L {bx1:.1f} {by1:.1f} L {bx1-tick:.1f} {by1:.1f}" '
        f'fill="none" stroke="{bracket_color}" stroke-width="1.6" stroke-linecap="round"/>'
    )
    # Title above matrix
    parts.append(
        f'<text x="{x + w/2:.1f}" y="{y - 7:.1f}" text-anchor="middle" '
        f'font-size="11.5" font-weight="600" fill="{label_color}">{esc(label)}</text>'
    )
    # Entries
    for r in range(rows):
        for c in range(cols):
            val = mat[r][c]
            cx = x + 7 + (c + 0.5) * cell_w
            cy = y + 5 + (r + 0.5) * cell_h + 4
            if highlight_diag and r == c:
                parts.append(
                    f'<rect x="{x + 7 + c*cell_w + 2:.1f}" y="{y + 5 + r*cell_h + 2:.1f}" '
                    f'width="{cell_w - 4:.1f}" height="{cell_h - 4:.1f}" rx="3" '
                    f'fill="#dafbe1" stroke="#2da44e" stroke-width="0.9"/>'
                )
                color = "#116329"
                weight = "700"
            elif highlight_val is not None and val == highlight_val:
                parts.append(
                    f'<rect x="{x + 7 + c*cell_w + 1.5:.1f}" y="{y + 5 + r*cell_h + 2:.1f}" '
                    f'width="{cell_w - 3:.1f}" height="{cell_h - 4:.1f}" rx="3" '
                    f'fill="#fff8c5" stroke="#bf8700" stroke-width="1.0"/>'
                )
                color = "#7d4e00"
                weight = "700"
            else:
                color = "#24292f"
                weight = "500"
            parts.append(
                f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
                f'font-size="11.5" font-weight="{weight}" fill="{color}">{val}</text>'
            )
    return w, h


def build_svg() -> str:
    # Load real upstream matrices and compute exact inverses
    a4 = invmatrix.parse_matrix((SRC_DIR / "matrix" / "4x4.txt").read_text(encoding="utf-8"))
    b4 = generate_suite.exact_integer_inverse(a4)
    assert b4 is not None and invmatrix.is_identity(invmatrix.matmul(a4, b4))
    i4 = [[1 if r == c else 0 for c in range(4)] for r in range(4)]

    a3 = invmatrix.parse_matrix(
        (SRC_DIR / "samples" / "matrix3x3_mod_26.txt").read_text(encoding="utf-8")
    )
    b3 = modinv.inverse_mod_reference(a3, 26)
    assert b3 is not None and modinv.is_identity_mod(a3, b3, 26)
    i3 = [[1 if r == c else 0 for c in range(3)] for r in range(3)]

    W, H = 960, 440
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Exact integer and modular matrix inversion SAT encodings from vzhn/sat-inv-matrix-py">',
        "<defs>",
        '  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#57606a"/>',
        "  </marker>",
        "</defs>",
        # Explicit light card canvas for both GitHub light & dark modes
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" '
        f'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        # Global font group
        '<g font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif">',
        # Main Title
        f'<text x="{W/2:.1f}" y="30" text-anchor="middle" font-size="17" font-weight="700" fill="#1f2328">'
        "Matrix Inversion via SAT (vzhn/sat-inv-matrix-py)</text>",
        f'<text x="{W/2:.1f}" y="49" text-anchor="middle" font-size="12" fill="#57606a">'
        "Exact overflow-free integer inversion A &#x00B7; B = I over &#x2124; and modular ring inversion "
        "A &#x00B7; B &#x2261; I (mod m) over &#x2124;/m&#x2124;</text>",
    ]

    # ================= LEFT PANEL: EXACT INTEGER INVERSION =================
    px1, py1, pw1, ph1 = 20, 64, 456, 356
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="9" '
        f'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="30" rx="9" fill="#0969da"/>'
    )
    parts.append(
        f'<rect x="{px1}" y="{py1+18}" width="{pw1}" height="12" fill="#0969da"/>'
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 20}" text-anchor="middle" '
        f'font-size="12.5" font-weight="700" fill="#ffffff">'
        "1. Exact Integer Inversion over &#x2124; (invmatrix.py &#x2014; 4&#x00D7;4, det = 1)</text>"
    )

    # 4x4 matrices: A * B = I (centered inside left panel)
    my = py1 + 56
    wA, hA = draw_matrix(parts, px1 + 37, my, a4, 24, 22, "Constant A", "#0969da")
    x_mul = px1 + 37 + wA + 11
    parts.append(
        f'<text x="{x_mul:.1f}" y="{my + hA/2 + 5:.1f}" text-anchor="middle" '
        f'font-size="16" font-weight="700" fill="#57606a">&#x00D7;</text>'
    )
    xB = x_mul + 11
    wB, _ = draw_matrix(
        parts,
        xB,
        my,
        b4,
        29,
        22,
        "Unknown B (w=7 SAT)",
        "#116329",
        highlight_val=22,
        fill_bg="#f0fdf4",
    )
    x_eq = xB + wB + 11
    parts.append(
        f'<text x="{x_eq:.1f}" y="{my + hA/2 + 5:.1f}" text-anchor="middle" '
        f'font-size="16" font-weight="700" fill="#57606a">=</text>'
    )
    xI = x_eq + 11
    draw_matrix(
        parts, xI, my, i4, 21, 22, "Identity I&#x2084;", "#116329", highlight_diag=True
    )

    # Callout note for entry 22
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{my + hA + 18:.1f}" text-anchor="middle" '
        f'font-size="10.8" fill="#7d4e00">'
        "Highlighted entry 22 requires w &#x2265; 6 signed bits (w = 5 &#x21D2; UNSAT, w = 7 auto &#x21D2; SAT)</text>"
    )

    # Adder-tree pipeline box inside left panel
    ey = my + hA + 30
    parts.append(
        f'<rect x="{px1 + 14}" y="{ey:.1f}" width="{pw1 - 28}" height="110" rx="7" '
        f'fill="#ffffff" stroke="#d0d7de" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{px1 + 26}" y="{ey + 18:.1f}" font-size="11.2" font-weight="700" fill="#1f2328">'
        "Exact Dadda/Wallace Bit-Column Adder Compression (per entry i, j):</text>"
    )
    # 3 stage boxes connected by arrows
    s_y = ey + 28
    s_h = 48
    stages_l = [
        (px1 + 24, 126, "#ddf4ff", "#0969da", "Weighted Bits", "A[i,k]&#x00B7;(&#x00B1;2&#x1D57;)&#x00B7;b[k,j,t]", "bucket by 2&#x1D56;"),
        (px1 + 168, 134, "#fff8c5", "#9a6700", "Full / Half Adders", "XOR3+Maj3 / XOR2+AND2", "carry p &#x2192; p+1"),
        (px1 + 320, 112, "#dafbe1", "#1a7f37", "Exact Target", "col[p] = bit_p(T)", "T = &#x03B4;&#x1D62;&#x2C7C; &#x2212; const"),
    ]
    for sx, sw, bg, bd, t1, t2, t3 in stages_l:
        parts.append(
            f'<rect x="{sx}" y="{s_y:.1f}" width="{sw}" height="{s_h}" rx="5" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{sx + sw/2:.1f}" y="{s_y + 15:.1f}" text-anchor="middle" '
            f'font-size="10.5" font-weight="700" fill="#1f2328">{t1}</text>'
        )
        parts.append(
            f'<text x="{sx + sw/2:.1f}" y="{s_y + 29:.1f}" text-anchor="middle" '
            f'font-size="9.5" fill="#24292f">{t2}</text>'
        )
        parts.append(
            f'<text x="{sx + sw/2:.1f}" y="{s_y + 42:.1f}" text-anchor="middle" '
            f'font-size="9.2" fill="#57606a">{t3}</text>'
        )
    parts.append(
        f'<line x1="{px1+150}" y1="{s_y + s_h/2:.1f}" x2="{px1+166}" y2="{s_y + s_h/2:.1f}" '
        f'stroke="#57606a" stroke-width="1.5" marker-end="url(#arrow)"/>'
    )
    parts.append(
        f'<line x1="{px1+302}" y1="{s_y + s_h/2:.1f}" x2="{px1+318}" y2="{s_y + s_h/2:.1f}" '
        f'stroke="#57606a" stroke-width="1.5" marker-end="url(#arrow)"/>'
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{ey + 98:.1f}" text-anchor="middle" '
        f'font-size="10.2" fill="#57606a">'
        "All adder sum gates are Tseitin 2-/3-XOR blocks (collapsed natively in xcnf-converted/)</text>"
    )

    # Bottom status pills (Left)
    by = py1 + ph1 - 36
    parts.append(
        f'<rect x="{px1 + 14}" y="{by}" width="206" height="24" rx="5" fill="#dafbe1" stroke="#2da44e" stroke-width="0.9"/>'
    )
    parts.append(
        f'<text x="{px1 + 117}" y="{by + 15.5:.1f}" text-anchor="middle" font-size="10.2" font-weight="600" fill="#116329">'
        "SAT: det(A) = &#x00B1;1 &amp; B fits in w bits</text>"
    )
    parts.append(
        f'<rect x="{px1 + 228}" y="{by}" width="214" height="24" rx="5" fill="#ffebe9" stroke="#cf222e" stroke-width="0.9"/>'
    )
    parts.append(
        f'<text x="{px1 + 335}" y="{by + 15.5:.1f}" text-anchor="middle" font-size="10.2" font-weight="600" fill="#a40e26">'
        "UNSAT: det &#x2260; &#x00B1;1, det = 0, or w small</text>"
    )

    # ================= RIGHT PANEL: MODULAR RING INVERSION =================
    px2, py2, pw2, ph2 = 484, 64, 456, 356
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="{ph2}" rx="9" '
        f'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="30" rx="9" fill="#8250df"/>'
    )
    parts.append(
        f'<rect x="{px2}" y="{py2+18}" width="{pw2}" height="12" fill="#8250df"/>'
    )
    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{py2 + 20}" text-anchor="middle" '
        f'font-size="12.5" font-weight="700" fill="#ffffff">'
        "2. Modular Ring Inversion over &#x2124;/m&#x2124; (modinv.py &#x2014; 3&#x00D7;3 mod 26)</text>"
    )

    # 3x3 matrices: A * B == I (mod 26) (centered inside right panel)
    my2 = py2 + 66
    wA2, hA2 = draw_matrix(parts, px2 + 48, my2, a3, 30, 24, "A (det = 441)", "#8250df")
    x_mul2 = px2 + 48 + wA2 + 15
    parts.append(
        f'<text x="{x_mul2:.1f}" y="{my2 + hA2/2 + 5:.1f}" text-anchor="middle" '
        f'font-size="16" font-weight="700" fill="#57606a">&#x00D7;</text>'
    )
    xB2 = x_mul2 + 15
    wB2, _ = draw_matrix(
        parts, xB2, my2, b3, 30, 24, "Unique B mod 26", "#116329", fill_bg="#f0fdf4"
    )
    x_eq2 = xB2 + wB2 + 16
    parts.append(
        f'<text x="{x_eq2:.1f}" y="{my2 + hA2/2 + 5:.1f}" text-anchor="middle" '
        f'font-size="16" font-weight="700" fill="#57606a">&#x2261;</text>'
    )
    xI2 = x_eq2 + 16
    draw_matrix(
        parts, xI2, my2, i3, 25, 24, "I&#x2083; (mod 26)", "#116329", highlight_diag=True
    )

    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{my2 + hA2 + 24:.1f}" text-anchor="middle" '
        f'font-size="10.8" fill="#57606a">'
        "gcd(441, 26) = 1 &#x21D2; unique inverse; CRT splits mod 26 into independent mod 2 &#x00D7; mod 13</text>"
    )

    # Two encodings box inside right panel
    ey2 = ey
    parts.append(
        f'<rect x="{px2 + 14}" y="{ey2:.1f}" width="{pw2 - 28}" height="110" rx="7" '
        f'fill="#ffffff" stroke="#d0d7de" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{px2 + 26}" y="{ey2 + 18:.1f}" font-size="11.2" font-weight="700" fill="#1f2328">'
        "Two Exact Encodings &amp; Algebraic Scaling Regimes:</text>"
    )

    # Encoding 1: One-hot
    parts.append(
        f'<rect x="{px2 + 24}" y="{ey2 + 27:.1f}" width="200" height="72" rx="5" '
        f'fill="#fbefff" stroke="#8250df" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{px2 + 34}" y="{ey2 + 43:.1f}" font-size="10.5" font-weight="700" fill="#6639ba">'
        "One-Hot Running Sum (default)</text>"
    )
    parts.append(
        f'<text x="{px2 + 34}" y="{ey2 + 58:.1f}" font-size="9.6" fill="#24292f">'
        "s&#x2096; = (s&#x2096;&#x208B;&#x2081; + A[i,k]&#x00B7;B[k,j]) mod m</text>"
    )
    parts.append(
        f'<text x="{px2 + 34}" y="{ey2 + 72:.1f}" font-size="9.4" fill="#57606a">'
        "O(n&#x00B3;m&#x00B2;) direct clauses, EO(m) states</text>"
    )
    parts.append(
        f'<text x="{px2 + 34}" y="{ey2 + 86:.1f}" font-size="9.4" fill="#57606a">'
        "m=2 hides XORs behind EO(2) pairs</text>"
    )

    # Encoding 2: Binary
    parts.append(
        f'<rect x="{px2 + 234}" y="{ey2 + 27:.1f}" width="198" height="72" rx="5" '
        f'fill="#ddf4ff" stroke="#0969da" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{px2 + 244}" y="{ey2 + 43:.1f}" font-size="10.5" font-weight="700" fill="#0550ae">'
        "Binary + Quotient Adder Tree</text>"
    )
    parts.append(
        f'<text x="{px2 + 244}" y="{ey2 + 58:.1f}" font-size="9.6" fill="#24292f">'
        "&#x03A3; A[i,k]&#x00B7;B[k,j] &#x2212; m&#x00B7;Q[i,j] = &#x03B4;&#x1D62;&#x2C7C;</text>"
    )
    parts.append(
        f'<text x="{px2 + 244}" y="{ey2 + 72:.1f}" font-size="9.4" fill="#57606a">'
        "Compact &#x2308;log&#x2082; m&#x2309;-bit vectors &amp; adders</text>"
    )
    parts.append(
        f'<text x="{px2 + 244}" y="{ey2 + 86:.1f}" font-size="9.4" fill="#57606a">'
        "m=2 exposes native GF(2) XOR chains</text>"
    )

    # Bottom status pills (Right)
    parts.append(
        f'<rect x="{px2 + 14}" y="{by}" width="206" height="24" rx="5" fill="#dafbe1" stroke="#2da44e" stroke-width="0.9"/>'
    )
    parts.append(
        f'<text x="{px2 + 117}" y="{by + 15.5:.1f}" text-anchor="middle" font-size="10.2" font-weight="600" fill="#116329">'
        "SAT: gcd(det(A), m) = 1</text>"
    )
    parts.append(
        f'<rect x="{px2 + 228}" y="{by}" width="214" height="24" rx="5" fill="#ffebe9" stroke="#cf222e" stroke-width="0.9"/>'
    )
    parts.append(
        f'<text x="{px2 + 335}" y="{by + 15.5:.1f}" text-anchor="middle" font-size="10.2" font-weight="600" fill="#a40e26">'
        "UNSAT: gcd(det(A), m) &gt; 1 (singular)</text>"
    )

    parts.append("</g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    # Strictly validate well-formed XML
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
