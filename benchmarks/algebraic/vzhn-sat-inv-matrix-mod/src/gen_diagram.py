#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`vzhn-sat-inv-matrix-mod` (Modular Ring Matrix Inversion over Z/mZ via SAT).

Zero external dependencies (Python 3 stdlib only). Parses the real upstream
3x3 matrix (`src/samples/matrix3x3_mod_26.txt`), computes and verifies its exact
modular inverse A * B = I (mod 26), writes `../diagram.svg` deterministically,
and validates XML well-formedness via `xml.etree.ElementTree.parse`.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
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


def bareiss_det(a: list[list[int]]) -> int:
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


def inverse_mod(a: list[list[int]], mod: int) -> list[list[int]]:
    """Exact modular matrix inverse via adjugate / det (works for composite mod)."""
    n = len(a)
    d = bareiss_det(a)
    assert math.gcd(d, mod) == 1
    d_inv = pow(d % mod, -1, mod)
    inv = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [
                [a[r][c] for c in range(n) if c != j]
                for r in range(n) if r != i
            ]
            cof = ((-1) ** (i + j)) * bareiss_det(minor)
            inv[j][i] = (cof * d_inv) % mod
    # Verify A * inv == I (mod mod)
    for i in range(n):
        for j in range(n):
            val = sum(a[i][k] * inv[k][j] for k in range(n)) % mod
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
            else:
                color, weight = "#0f172a", "600" if fill_bg != "#ffffff" else "500"
            parts.append(
                f'  <text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="12" font-weight="{weight}" fill="{color}">{val}</text>'
            )
    return w, h


def build_svg() -> str:
    a3 = parse_matrix(SRC_DIR / "samples" / "matrix3x3_mod_26.txt")
    d3 = bareiss_det(a3)
    b3 = inverse_mod(a3, 26)
    i3 = [[1 if r == c else 0 for c in range(3)] for r in range(3)]

    W, H = 940, 496
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Modular Ring Matrix Inversion over Z/mZ SAT Encodings (vzhn-sat-inv-matrix-mod)">',
        "<defs>",
        '  <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#6d28d9"/>',
        "  </marker>",
        '  <marker id="arr-b" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#1d4ed8"/>',
        "  </marker>",
        "</defs>",
        # Explicit light-card canvas
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        f'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Modular Ring Matrix Inversion over &#x2124;/m&#x2124; (vzhn-sat-inv-matrix-mod)</text>',
        '  <text x="26" y="53" font-size="11.8" fill="#475569">'
        'One-hot running-sum &amp; binary quotient adder-tree SAT encodings of A &#x00B7; B &#x2261; I&#x2099; (mod m) '
        '(Vladimir Zhilin, modinv.py)</text>',
        '  <rect x="738" y="18" width="178" height="24" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>',
        '  <text x="827" y="34" text-anchor="middle" font-size="10.8" font-weight="700" fill="#6d28d9">'
        '15 Instances &#x00B7; 10 SAT / 5 UNSAT</text>',
        '  <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= SECTION 1: REAL 3x3 MOD-26 EQUATION + CRT SPLITTING =================
    y1 = 78
    p.append(
        f'  <rect x="24" y="{y1}" width="892" height="148" rx="10" '
        f'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(f'  <rect x="24" y="{y1}" width="892" height="28" rx="10" fill="#7c3aed"/>')
    p.append(f'  <rect x="24" y="{y1 + 16}" width="892" height="12" fill="#7c3aed"/>')
    p.append(
        f'  <text x="38" y="{y1 + 19}" font-size="12" font-weight="700" fill="#ffffff">'
        f'1. Modular Ring Equation (Upstream src/samples/matrix3x3_mod_26.txt &#x2014; det(A) = {d3}, gcd({d3}, 26) = 1)</text>'
    )

    my = y1 + 52
    wA, hA = draw_matrix(p, 46, my, a3, 34, 24, f"Constant A (det = {d3})", "#6d28d9", fill_bg="#ffffff")
    x_mul = 46 + wA + 16
    p.append(
        f'  <text x="{x_mul:.1f}" y="{my + hA / 2 + 5:.1f}" text-anchor="middle" '
        f'font-size="18" font-weight="700" fill="#475569">&#x00D7;</text>'
    )
    xB = x_mul + 16
    wB, _ = draw_matrix(p, xB, my, b3, 34, 24, "Unique B ∈ (ℤ/26ℤ)³×³", "#15803d", fill_bg="#f0fdf4")
    x_eq = xB + wB + 18
    p.append(
        f'  <text x="{x_eq:.1f}" y="{my + hA / 2 + 5:.1f}" text-anchor="middle" '
        f'font-size="18" font-weight="700" fill="#475569">&#x2261;</text>'
    )
    xI = x_eq + 18
    wI, _ = draw_matrix(p, xI, my, i3, 28, 24, "I₃ (mod 26)", "#15803d", highlight_diag=True, fill_bg="#ffffff")

    # Right callout: CRT & Invertibility Criterion
    rx = xI + wI + 28
    rw = 916 - rx - 14
    p.append(
        f'  <rect x="{rx:.1f}" y="{y1 + 37}" width="{rw:.1f}" height="101" rx="8" '
        f'fill="#ffffff" stroke="#ddd6fe" stroke-width="1.1"/>'
    )
    p.append(
        f'  <text x="{rx + 14:.1f}" y="{y1 + 55}" font-size="11" font-weight="700" fill="#5b21b6">'
        'CRT Factorization &amp; Column Independence</text>'
    )
    p.append(
        f'  <text x="{rx + 14:.1f}" y="{y1 + 73}" font-family="{MONO}" font-size="9.8" fill="#1e293b">'
        '&#x2124;/26&#x2124; &#x2245; &#x2124;/2&#x2124; &#x00D7; &#x2124;/13&#x2124;</text>'
    )
    p.append(
        f'  <text x="{rx + 14:.1f}" y="{y1 + 90}" font-size="9.6" fill="#475569">'
        'Each column solves A&#x00B7;b&#x2C7C; &#x2261; e&#x2C7C; (mod p^e) independently</text>'
    )
    p.append(
        f'  <rect x="{rx + 12:.1f}" y="{y1 + 100}" width="{(rw - 30) / 2:.1f}" height="28" rx="5" '
        f'fill="#f0fdf4" stroke="#86efac" stroke-width="0.9"/>'
    )
    p.append(
        f'  <text x="{rx + 12 + (rw - 30) / 4:.1f}" y="{y1 + 112.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#15803d">'
        'SAT &#x21D4; gcd(det A, m) = 1</text>'
    )
    p.append(
        f'  <text x="{rx + 12 + (rw - 30) / 4:.1f}" y="{y1 + 124}" text-anchor="middle" font-size="8.4" fill="#334155">'
        'Unique unit in GL&#x2099;(&#x2124;/m&#x2124;)</text>'
    )
    x_u = rx + 18 + (rw - 30) / 2
    p.append(
        f'  <rect x="{x_u:.1f}" y="{y1 + 100}" width="{(rw - 30) / 2:.1f}" height="28" rx="5" '
        f'fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>'
    )
    p.append(
        f'  <text x="{x_u + (rw - 30) / 4:.1f}" y="{y1 + 112.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#b91c1c">'
        'UNSAT &#x21D4; gcd(det A, m) &gt; 1</text>'
    )
    p.append(
        f'  <text x="{x_u + (rw - 30) / 4:.1f}" y="{y1 + 124}" text-anchor="middle" font-size="8.4" fill="#334155">'
        'Singular / zero-divisor det</text>'
    )

    # ================= SECTION 2: DUAL ENCODINGS (ONE-HOT VS BINARY QUOTIENT) =================
    y2 = 238
    h2 = 166
    w2 = 438
    # --- Left Card: One-Hot Running Sum ---
    xl = 24
    p.append(f'  <rect x="{xl}" y="{y2}" width="{w2}" height="{h2}" rx="10" fill="#faf5ff" stroke="#c4b5fd" stroke-width="1.3"/>')
    p.append(f'  <text x="{xl + 14}" y="{y2 + 22}" font-size="12" font-weight="700" fill="#6d28d9">2A. One-Hot Running-Sum Encoding (onehot)</text>')
    p.append(f'  <text x="{xl + 14}" y="{y2 + 38}" font-size="9.6" fill="#475569">Domain: m Boolean vars per entry with EO(m) exactly-one constraints</text>')

    # Running-sum state chain visual
    cy = y2 + 50
    p.append(f'  <rect x="{xl + 14}" y="{cy}" width="410" height="58" rx="7" fill="#ffffff" stroke="#e9d5ff" stroke-width="1"/>')
    nodes = [
        (xl + 26, 62, "s&#x2080; = 0", "init"),
        (xl + 116, 86, "s&#x2081; (mod m)", "+A[i,0]&#x00B7;B[0,j]"),
        (xl + 230, 86, "s&#x2096; (mod m)", "+A[i,k]&#x00B7;B[k,j]"),
        (xl + 344, 68, "s&#x2099; = &#x03B4;&#x1D62;&#x2C7C;", "clamped"),
    ]
    for nx, nw, t1, t2 in nodes:
        bg_n = "#dcfce7" if "&#x03B4;" in t1 else "#f5f3ff"
        bd_n = "#16a34a" if "&#x03B4;" in t1 else "#7c3aed"
        fg_n = "#15803d" if "&#x03B4;" in t1 else "#5b21b6"
        p.append(f'  <rect x="{nx}" y="{cy + 10}" width="{nw}" height="38" rx="6" fill="{bg_n}" stroke="{bd_n}" stroke-width="1.1"/>')
        p.append(f'  <text x="{nx + nw / 2:.1f}" y="{cy + 26}" text-anchor="middle" font-size="9.6" font-weight="700" fill="{fg_n}">{t1}</text>')
        p.append(f'  <text x="{nx + nw / 2:.1f}" y="{cy + 40}" text-anchor="middle" font-size="8.4" fill="#475569">{t2}</text>')
    for x1, x2 in [(xl + 89, xl + 113), (xl + 203, xl + 227), (xl + 317, xl + 341)]:
        p.append(f'  <line x1="{x1}" y1="{cy + 29}" x2="{x2}" y2="{cy + 29}" stroke="#6d28d9" stroke-width="1.4" marker-end="url(#arr)"/>')

    p.append(f'  <text x="{xl + 16}" y="{y2 + 126}" font-size="9.5" fill="#1e293b">&#x2022; Transition implications: &#x00AC;s[k&#x2212;1,u] &#x2228; &#x00AC;B[k,j,v] &#x2228; s[k, (u+A&#x00B7;v) mod m]</text>')
    p.append(f'  <text x="{xl + 16}" y="{y2 + 141}" font-size="9.5" fill="#1e293b">&#x2022; Clause size O(n&#x00B3;m&#x00B2;): direct table transitions for m &#x2208; &#x007B;2, 3, 13, 26, 27&#x007D;</text>')
    p.append(f'  <text x="{xl + 16}" y="{y2 + 156}" font-size="9.4" font-weight="700" fill="#6d28d9">&#x2022; Over &#x1D53D;&#x2082; (m = 2): EO(2) bit pairs (b&#x2080;, b&#x2081;) disguise parity from syntactic XOR scanners</text>')

    # --- Right Card: Binary Quotient Adder Tree ---
    xr = 478
    p.append(f'  <rect x="{xr}" y="{y2}" width="{w2}" height="{h2}" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.3"/>')
    p.append(f'  <text x="{xr + 14}" y="{y2 + 22}" font-size="12" font-weight="700" fill="#1d4ed8">2B. Binary + Explicit Quotient Encoding (binary)</text>')
    p.append(f'  <text x="{xr + 14}" y="{y2 + 38}" font-size="9.6" fill="#475569">Domain: unsigned &#x2308;log&#x2082; m&#x2309;-bit B[k,j] &#x2264; m&#x2212;1 + unsigned quotient Q[i,j]</text>')

    p.append(f'  <rect x="{xr + 14}" y="{cy}" width="410" height="58" rx="7" fill="#ffffff" stroke="#bfdbfe" stroke-width="1"/>')
    bnodes = [
        (xr + 24, 110, "&#x03A3; A[i,k]&#x00B7;B[k,j]", "unsigned bits"),
        (xr + 162, 110, "&#x2212; m &#x00B7; Q[i,j]", "exact quotient"),
        (xr + 300, 112, "Adder Tree = &#x03B4;&#x1D62;&#x2C7C;", "FA/HA XOR sum"),
    ]
    for nx, nw, t1, t2 in bnodes:
        bg_n = "#dcfce7" if "&#x03B4;" in t1 else "#eff6ff"
        bd_n = "#16a34a" if "&#x03B4;" in t1 else "#2563eb"
        fg_n = "#15803d" if "&#x03B4;" in t1 else "#1e40af"
        p.append(f'  <rect x="{nx}" y="{cy + 10}" width="{nw}" height="38" rx="6" fill="{bg_n}" stroke="{bd_n}" stroke-width="1.1"/>')
        p.append(f'  <text x="{nx + nw / 2:.1f}" y="{cy + 26}" text-anchor="middle" font-size="9.6" font-weight="700" fill="{fg_n}">{t1}</text>')
        p.append(f'  <text x="{nx + nw / 2:.1f}" y="{cy + 40}" text-anchor="middle" font-size="8.4" fill="#475569">{t2}</text>')
    p.append(f'  <text x="{xr + 148}" y="{cy + 33}" text-anchor="middle" font-size="14" font-weight="700" fill="#1d4ed8">+</text>')
    p.append(f'  <line x1="{xr + 273}" y1="{cy + 29}" x2="{xr + 297}" y2="{cy + 29}" stroke="#1d4ed8" stroke-width="1.4" marker-end="url(#arr-b)"/>')

    p.append(f'  <text x="{xr + 16}" y="{y2 + 126}" font-size="9.5" fill="#1e293b">&#x2022; Exact integer identity: &#x03A3;&#x2096; A[i,k]&#x00B7;B[k,j] &#x2212; m&#x00B7;Q[i,j] = &#x03B4;&#x1D62;&#x2C7C; (0 &#x2264; B &lt; m)</text>')
    p.append(f'  <text x="{xr + 16}" y="{y2 + 141}" font-size="9.5" fill="#1e293b">&#x2022; Compact for large m (e.g. mod 26: 5,079 binary vs 20,970 one-hot clauses)</text>')
    p.append(f'  <text x="{xr + 16}" y="{y2 + 156}" font-size="9.4" font-weight="700" fill="#1d4ed8">&#x2022; Over &#x1D53D;&#x2082; (m = 2): exposes 43,911 explicit Tseitin XORs in xcnf-converted/</text>')

    # ================= SECTION 3: ALGEBRAIC REGIMES ACROSS THE 15 INSTANCES =================
    y3 = 416
    p.append(f'  <rect x="24" y="{y3}" width="892" height="64" rx="9" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.1"/>')
    p.append(f'  <text x="38" y="{y3 + 17}" font-size="11.2" font-weight="700" fill="#0f172a">Three Algebraic Scaling Regimes (15 Instances &#x00B7; 702 to 113,664 Vars &#x00B7; 43,911 Native XORs)</text>')

    regimes = [
        (38, 282, "#eff6ff", "#2563eb", "#1d4ed8", "GF(2) Parity Wall (8 inst: 24&#x00D7;24&#x2013;48&#x00D7;48)", "m = 2 (binary &amp; one-hot) &#x00B7; 2^&#x03A9;(n) CDCL barrier"),
        (332, 282, "#faf5ff", "#7c3aed", "#6d28d9", "Odd Prime / Prime-Power (5 inst)", "m &#x2208; &#x007B;3, 27&#x007D;: 12&#x00D7;12 mod 3 &amp; 5&#x00D7;5 mod 27 (SAT/UNSAT)"),
        (626, 276, "#fffbeb", "#d97706", "#b45309", "Composite &amp; CRT Frontier (2 + 1 inst)", "3&#x00D7;3 mod 26 (bin/oh) &#x00B7; 10&#x00D7;10 mod 13 col 0 (hard!)"),
    ]
    for px, pw, bg, bd, fg, t1, t2 in regimes:
        p.append(f'  <rect x="{px}" y="{y3 + 24}" width="{pw}" height="33" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        p.append(f'  <text x="{px + pw / 2:.1f}" y="{y3 + 37.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{fg}">{t1}</text>')
        p.append(f'  <text x="{px + pw / 2:.1f}" y="{y3 + 50.5}" text-anchor="middle" font-size="8.6" fill="#334155">{t2}</text>')

    p.append("</g>")
    p.append("</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT_SVG.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
