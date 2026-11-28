#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`vzhn-sat-inv-matrix-int` (Exact Integer Matrix Inversion over Z via SAT).

Zero external dependencies (Python 3 stdlib only). Parses the real upstream
4x4 unimodular matrix (`src/matrix/4x4.txt`), computes and verifies its exact
integer inverse A * B = I over Z, writes `../diagram.svg` deterministically,
and validates XML well-formedness via `xml.etree.ElementTree.parse`.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SUITE_DIR = SRC_DIR.parent
OUT_SVG = SUITE_DIR / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def parse_matrix(path: Path) -> list[list[int]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            rows.append([int(x) for x in s.split()])
    return rows


def exact_integer_inverse(a: list[list[int]]) -> list[list[int]]:
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
    # Verify A * inv == I_n over Z
    for i in range(n):
        for j in range(n):
            val = sum(a[i][k] * inv[k][j] for k in range(n))
            assert val == (1 if i == j else 0)
    return inv


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
    fill_bg: str = "#f8fafc",
    bracket_color: str = "#475569",
) -> tuple[float, float]:
    rows = len(mat)
    cols = len(mat[0])
    w = cols * cell_w + 16
    h = rows * cell_h + 12
    parts.append(
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="6" fill="{fill_bg}" stroke="#cbd5e1" stroke-width="1"/>'
    )
    bx0, bx1 = x + 4.5, x + w - 4.5
    by0, by1 = y + 4.5, y + h - 4.5
    tick = 5.5
    parts.append(
        f'  <path d="M {bx0 + tick:.1f} {by0:.1f} L {bx0:.1f} {by0:.1f} '
        f'L {bx0:.1f} {by1:.1f} L {bx0 + tick:.1f} {by1:.1f}" '
        f'fill="none" stroke="{bracket_color}" stroke-width="1.6" stroke-linecap="round"/>'
    )
    parts.append(
        f'  <path d="M {bx1 - tick:.1f} {by0:.1f} L {bx1:.1f} {by0:.1f} '
        f'L {bx1:.1f} {by1:.1f} L {bx1 - tick:.1f} {by1:.1f}" '
        f'fill="none" stroke="{bracket_color}" stroke-width="1.6" stroke-linecap="round"/>'
    )
    parts.append(
        f'  <text x="{x + w / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" '
        f'font-size="11.5" font-weight="700" fill="{label_color}">{esc(label)}</text>'
    )
    for r in range(rows):
        for c in range(cols):
            val = mat[r][c]
            cx = x + 8 + (c + 0.5) * cell_w
            cy = y + 6 + (r + 0.5) * cell_h + 4
            if highlight_diag and r == c:
                parts.append(
                    f'  <rect x="{x + 8 + c * cell_w + 2:.1f}" y="{y + 6 + r * cell_h + 2:.1f}" '
                    f'width="{cell_w - 4:.1f}" height="{cell_h - 4:.1f}" rx="3.5" '
                    f'fill="#dcfce7" stroke="#16a34a" stroke-width="1"/>'
                )
                color, weight = "#166534", "700"
            elif highlight_val is not None and val == highlight_val:
                parts.append(
                    f'  <rect x="{x + 8 + c * cell_w + 1.5:.1f}" y="{y + 6 + r * cell_h + 2:.1f}" '
                    f'width="{cell_w - 3:.1f}" height="{cell_h - 4:.1f}" rx="3.5" '
                    f'fill="#fef3c7" stroke="#d97706" stroke-width="1.1"/>'
                )
                color, weight = "#92400e", "700"
            else:
                color, weight = "#0f172a", "500"
            parts.append(
                f'  <text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="11.8" font-weight="{weight}" fill="{color}">{val}</text>'
            )
    return w, h


def build_svg() -> str:
    a4 = parse_matrix(SRC_DIR / "matrix" / "4x4.txt")
    b4 = exact_integer_inverse(a4)
    i4 = [[1 if r == c else 0 for c in range(4)] for r in range(4)]

    W, H = 940, 492
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Exact Integer Matrix Inversion over Z SAT Encoding (vzhn-sat-inv-matrix-int)">',
        "<defs>",
        '  <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "  </marker>",
        "</defs>",
        # Explicit light-card canvas
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        f'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Exact Integer Matrix Inversion over &#x2124; (vzhn-sat-inv-matrix-int)</text>',
        '  <text x="26" y="53" font-size="11.8" fill="#475569">'
        'Overflow-free signed two&#x2019;s-complement encoding of A &#x00B7; B = I&#x2099; via '
        'Dadda/Wallace bit-column adder trees (Vladimir Zhilin, invmatrix.py)</text>',
        '  <rect x="742" y="18" width="174" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '  <text x="829" y="34" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">'
        '11 Instances &#x00B7; 6 SAT / 5 UNSAT</text>',
        '  <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= SECTION 1: EXACT 4x4 MATRIX EQUATION + SIGNED RANGE =================
    y1 = 78
    p.append(
        f'  <rect x="24" y="{y1}" width="892" height="160" rx="10" '
        f'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'  <rect x="24" y="{y1}" width="892" height="28" rx="10" fill="#1d4ed8"/>'
    )
    p.append(
        f'  <rect x="24" y="{y1 + 16}" width="892" height="12" fill="#1d4ed8"/>'
    )
    p.append(
        f'  <text x="38" y="{y1 + 19}" font-size="12" font-weight="700" fill="#ffffff">'
        '1. Exact Unimodular Matrix Equation (Upstream src/matrix/4x4.txt &#x2014; det(A) = 1, No Modular Wrap-Around)</text>'
    )

    my = y1 + 52
    wA, hA = draw_matrix(p, 42, my, a4, 28, 22, "Constant A ∈ ℤ⁴×⁴", "#1d4ed8", fill_bg="#ffffff")
    x_mul = 42 + wA + 14
    p.append(
        f'  <text x="{x_mul:.1f}" y="{my + hA / 2 + 5:.1f}" text-anchor="middle" '
        f'font-size="18" font-weight="700" fill="#475569">&#x00D7;</text>'
    )
    xB = x_mul + 14
    wB, _ = draw_matrix(
        p, xB, my, b4, 34, 22, "Unknown B = A⁻¹ (w-bit signed)", "#15803d",
        highlight_val=22, fill_bg="#f0fdf4",
    )
    x_eq = xB + wB + 14
    p.append(
        f'  <text x="{x_eq:.1f}" y="{my + hA / 2 + 5:.1f}" text-anchor="middle" '
        f'font-size="18" font-weight="700" fill="#475569">=</text>'
    )
    xI = x_eq + 14
    wI, _ = draw_matrix(
        p, xI, my, i4, 24, 22, "Identity I₄", "#15803d", highlight_diag=True, fill_bg="#ffffff"
    )

    # Signed bit-width range callout box on right of Section 1
    rx = xI + wI + 22
    rw = 892 + 24 - rx - 14
    p.append(
        f'  <rect x="{rx:.1f}" y="{y1 + 38}" width="{rw:.1f}" height="112" rx="8" '
        f'fill="#ffffff" stroke="#bfdbfe" stroke-width="1.1"/>'
    )
    p.append(
        f'  <text x="{rx + 12:.1f}" y="{y1 + 56}" font-size="11" font-weight="700" fill="#1e3a8a">'
        'Signed Two&#x2019;s-Complement Domain</text>'
    )
    p.append(
        f'  <text x="{rx + 12:.1f}" y="{y1 + 74}" font-family="{MONO}" font-size="9.6" fill="#334155">'
        'B[k,j] = &#x2212;2^(w&#x2212;1)&#x00B7;b[w&#x2212;1] + &#x03A3; 2^t&#x00B7;b[t]</text>'
    )
    p.append(
        f'  <text x="{rx + 12:.1f}" y="{y1 + 91}" font-size="9.8" fill="#475569">'
        'Range: [&#x2212;2^(w&#x2212;1), 2^(w&#x2212;1) &#x2212; 1] per entry</text>'
    )
    # Mini threshold pills for entry 22
    p.append(
        f'  <rect x="{rx + 10:.1f}" y="{y1 + 100}" width="{rw - 20:.1f}" height="20" rx="4" '
        f'fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>'
    )
    p.append(
        f'  <text x="{rx + rw / 2:.1f}" y="{y1 + 113.5}" text-anchor="middle" font-size="9.3" font-weight="700" fill="#b91c1c">'
        'w = 5 &#x21D2; [&#x2212;16, 15]: entry 22 overflows (UNSAT)</text>'
    )
    p.append(
        f'  <rect x="{rx + 10:.1f}" y="{y1 + 124}" width="{rw - 20:.1f}" height="20" rx="4" '
        f'fill="#f0fdf4" stroke="#86efac" stroke-width="0.9"/>'
    )
    p.append(
        f'  <text x="{rx + rw / 2:.1f}" y="{y1 + 137.5}" text-anchor="middle" font-size="9.3" font-weight="700" fill="#15803d">'
        'w = 7 (Hadamard auto) &#x21D2; [&#x2212;64, 63]: SAT</text>'
    )

    # ================= SECTION 2: DADDA / WALLACE BIT-COLUMN COMPRESSION =================
    y2 = 250
    p.append(
        f'  <rect x="24" y="{y2}" width="892" height="148" rx="10" '
        f'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'  <text x="38" y="{y2 + 21}" font-size="12" font-weight="700" fill="#0f172a">'
        '2. Exact Dadda / Wallace Bit-Column Adder-Tree Compression (Per Matrix-Product Entry &#x03A3;&#x2096; A[i,k]&#x00B7;B[k,j] = &#x03B4;&#x1D62;&#x2C7C;)</text>'
    )

    # Stage 1 box: Weighted bit decomposition
    sy = y2 + 32
    sh = 104
    p.append(f'  <rect x="38" y="{sy}" width="246" height="{sh}" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.2"/>')
    p.append(f'  <text x="161" y="{sy + 18}" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">Stage A: Power-of-Two Buckets</text>')
    p.append(f'  <text x="50" y="{sy + 36}" font-size="9.6" fill="#1e293b">&#x2022; Expand each A[i,k]&#x00B7;(&#x00B1;2^t) into powers 2^p</text>')
    p.append(f'  <text x="50" y="{sy + 52}" font-size="9.6" fill="#1e293b">&#x2022; Flip negative weights via:</text>')
    p.append(f'  <text x="161" y="{sy + 68}" text-anchor="middle" font-family="{MONO}" font-size="9.6" font-weight="700" fill="#1d4ed8">c&#x00B7;x = |c|&#x00B7;(&#x00AC;x) &#x2212; |c|</text>')
    p.append(f'  <text x="50" y="{sy + 85}" font-size="9.4" fill="#475569">&#x2022; Shift all negative constants into target T</text>')
    p.append(f'  <text x="50" y="{sy + 98}" font-size="9.4" fill="#475569">&#x2022; Yields nonnegative bit columns col[0..P]</text>')

    p.append(f'  <line x1="285" y1="{sy + sh / 2:.1f}" x2="311" y2="{sy + sh / 2:.1f}" stroke="#475569" stroke-width="1.6" marker-end="url(#arr)"/>')

    # Stage 2 box: Bit-column reduction dot diagram + FA/HA gates
    p.append(f'  <rect x="314" y="{sy}" width="322" height="{sh}" rx="8" fill="#fffbeb" stroke="#d97706" stroke-width="1.2"/>')
    p.append(f'  <text x="475" y="{sy + 18}" text-anchor="middle" font-size="11" font-weight="700" fill="#b45309">Stage B: LSB-Upward FA / HA Compression</text>')

    # Mini dot-column visualization on left of Stage 2
    dx0, dy0 = 330, sy + 28
    p.append(f'  <rect x="{dx0}" y="{dy0}" width="136" height="66" rx="5" fill="#ffffff" stroke="#fde68a" stroke-width="1"/>')
    col_heights = [2, 4, 5, 4, 3, 2]
    for ci, ch_n in enumerate(col_heights):
        cx = dx0 + 18 + ci * 20
        p.append(f'  <text x="{cx}" y="{dy0 + 62}" text-anchor="middle" font-family="{MONO}" font-size="8" fill="#64748b">2^{5 - ci}</text>')
        for di in range(ch_n):
            cy = dy0 + 50 - di * 7.5
            is_fa = (ci == 2 and di < 3)
            fill_d = "#f59e0b" if is_fa else "#3b82f6"
            p.append(f'  <circle cx="{cx}" cy="{cy:.1f}" r="2.8" fill="{fill_d}"/>')
    # Highlight 3-dot FA group and carry arrow to next column left
    p.append(f'  <rect x="{dx0 + 52.5}" y="{dy0 + 30.5}" width="11" height="23.5" rx="3" fill="none" stroke="#dc2626" stroke-width="1.1"/>')
    p.append(f'  <path d="M {dx0 + 52.5} {dy0 + 38} Q {dx0 + 45} {dy0 + 17} {dx0 + 38} {dy0 + 21}" fill="none" stroke="#dc2626" stroke-width="1.1" marker-end="url(#arr)"/>')
    p.append(f'  <text x="{dx0 + 68}" y="{dy0 + 10.5}" text-anchor="middle" font-size="7.8" font-weight="700" fill="#b45309">carry 2^p &#x2192; 2^(p+1)</text>')

    # FA / HA gate clause accounting on right of Stage 2
    gx = 476
    p.append(f'  <text x="{gx}" y="{sy + 38}" font-size="9.6" font-weight="700" fill="#92400e">Full Adder (3 bits &#x2192; s, c):</text>')
    p.append(f'  <text x="{gx}" y="{sy + 51}" font-family="{MONO}" font-size="8.9" fill="#334155">s = a&#x2295;b&#x2295;c, c = Maj&#x2083; (14 cls)</text>')
    p.append(f'  <text x="{gx}" y="{sy + 68}" font-size="9.6" font-weight="700" fill="#92400e">Half Adder (2 bits &#x2192; s, c):</text>')
    p.append(f'  <text x="{gx}" y="{sy + 81}" font-family="{MONO}" font-size="8.9" fill="#334155">s = a&#x2295;b, c = a&#x2227;b (7 cls)</text>')
    p.append(f'  <text x="{gx}" y="{sy + 96}" font-size="8.9" font-weight="700" fill="#6d28d9">349,168 XORs collapsed in XCNF</text>')

    p.append(f'  <line x1="637" y1="{sy + sh / 2:.1f}" x2="663" y2="{sy + sh / 2:.1f}" stroke="#475569" stroke-width="1.6" marker-end="url(#arr)"/>')

    # Stage 3 box: Exact bit-for-bit clamping
    p.append(f'  <rect x="666" y="{sy}" width="236" height="{sh}" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.2"/>')
    p.append(f'  <text x="784" y="{sy + 18}" text-anchor="middle" font-size="11" font-weight="700" fill="#15803d">Stage C: Exact Target Clamp</text>')
    p.append(f'  <text x="678" y="{sy + 38}" font-size="9.6" fill="#1e293b">&#x2022; Every column reduces to &#x2264; 1 bit</text>')
    p.append(f'  <text x="678" y="{sy + 54}" font-size="9.6" fill="#1e293b">&#x2022; Clamp unit literal at every bit p:</text>')
    p.append(f'  <text x="784" y="{sy + 71}" text-anchor="middle" font-family="{MONO}" font-size="9.6" font-weight="700" fill="#15803d">col[p] = bit_p(&#x03B4;&#x1D62;&#x2C7C; &#x2212; const)</text>')
    p.append(f'  <text x="678" y="{sy + 88}" font-size="9.3" fill="#475569">&#x2022; Upper carry bits clamped strictly to 0</text>')
    p.append(f'  <text x="678" y="{sy + 100}" font-size="9.3" fill="#475569">&#x2022; Exact over &#x2124; (zero overflow aliasing)</text>')

    # ================= SECTION 3: FOUR VERDICT REGIMES ACROSS THE 11 INSTANCES =================
    y3 = 410
    p.append(f'  <rect x="24" y="{y3}" width="892" height="66" rx="9" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.1"/>')
    p.append(f'  <text x="38" y="{y3 + 18}" font-size="11.2" font-weight="700" fill="#0f172a">Exact Satisfiability Criterion &amp; Suite Coverage (3&#x00D7;3 to 16&#x00D7;16 &#x00B7; 64 to 187,060 Vars &#x00B7; up to 1.28M Clauses)</text>')

    pills = [
        (38, 224, "#dcfce7", "#16a34a", "#166534", "SAT (6 inst): det(A) = &#x00B1;1 &amp; fits w", "4&#x00D7;4 (w7) &#x00B7; 8&#x00D7;8 (w16,36) &#x00B7; 10&#x00D7;10 (w16,47) &#x00B7; 16&#x00D7;16"),
        (272, 200, "#fef2f2", "#dc2626", "#991b1b", "UNSAT #1: Non-Unimodular", "int_3x3_det2_w3 (det = 2 &#x2260; &#x00B1;1)"),
        (482, 214, "#fff7ed", "#ea580c", "#9a3412", "UNSAT #2: Width Overflow (3 inst)", "4&#x00D7;4 w5 &#x00B7; 10&#x00D7;10 w4 &#x00B7; 16&#x00D7;16 w5"),
        (706, 196, "#fdf2f8", "#be185d", "#9d174d", "UNSAT #3: Singular (det = 0)", "int_16x16_sing_w16 (row0=r1+r2)"),
    ]
    for px, pw, bg, bd, fg, t1, t2 in pills:
        p.append(f'  <rect x="{px}" y="{y3 + 25}" width="{pw}" height="34" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        p.append(f'  <text x="{px + pw / 2:.1f}" y="{y3 + 39}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{fg}">{t1}</text>')
        p.append(f'  <text x="{px + pw / 2:.1f}" y="{y3 + 52.5}" text-anchor="middle" font-size="8.6" fill="#334155">{t2}</text>')

    p.append("</g>")
    p.append("</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT_SVG.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
