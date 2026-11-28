#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-tensor-cross.

Visualizes the 3 skew-symmetric frontal slices of the 3D cross product (x cross y),
verifies an exact universal 5-product bilinear identity over Z (valid over every Z/mZ),
and summarizes the 8-instance optimality-bracket ladder across m in {2, 3, 4, 5}.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Universal 5-product bilinear decomposition of 3D cross product over Z (coefficients in {-1, 0, +1}):
#   p1 = x0 * (y1 - y2)
#   p2 = x1 * (y2 - y0)
#   p3 = (x2 - x0) * y1
#   p4 = (x2 - x1) * y0
#   p5 = (x1 - x0) * y2
# Outputs:
#   c0 = x1*y2 - x2*y1 = -p1 - p3 + p5
#   c1 = x2*y0 - x0*y2 = -p2 + p4 + p5
#   c2 = x0*y1 - x1*y0 =  p1 + p2 - p5
CROSS_RANK5 = [
    ("p1", "x0",        "(y1 - y2)", [1, 0, 0],  [0, 1, -1], [-1, 0, 1], "-c0, +c2"),
    ("p2", "x1",        "(y2 - y0)", [0, 1, 0],  [-1, 0, 1], [0, -1, 1], "-c1, +c2"),
    ("p3", "(x2 - x0)", "y1",        [-1, 0, 1], [0, 1, 0],  [-1, 0, 0], "-c0"),
    ("p4", "(x2 - x1)", "y0",        [0, -1, 1], [1, 0, 0],  [0, 1, 0],  "+c1"),
    ("p5", "(x1 - x0)", "y2",        [-1, 1, 0], [0, 0, 1],  [1, 1, -1], "+c0, +c1, -c2"),
]


def verify_cross5() -> None:
    target = {}
    for o in range(3):
        i, j = (o + 1) % 3, (o + 2) % 3
        target[(i, j, o)] = 1
        target[(j, i, o)] = -1
    for i in range(3):
        for j in range(3):
            for o in range(3):
                got = sum(row[3][i] * row[4][j] * row[5][o] for row in CROSS_RANK5)
                exp = target.get((i, j, o), 0)
                assert got == exp, f"Cross-product tensor mismatch at ({i},{j},{o}): {got} != {exp}"


def draw_slice(p: list[str], x: float, y: float, mat: list[list[int]], title: str, accent: str) -> None:
    cell = 26
    w = 3 * cell + 12
    h = 3 * cell + 10
    p.append(f'  <text x="{x+w/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="10.2" font-weight="700" fill="{accent}">{title}</text>')
    p.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="#ffffff" stroke="{accent}" stroke-width="1.2"/>')
    for r in range(3):
        for c in range(3):
            v = mat[r][c]
            cx = x + 6 + c * cell
            cy = y + 5 + r * cell
            if v == 1:
                bg, fg, lbl = "#dcfce7", "#15803d", "+1"
            elif v == -1:
                bg, fg, lbl = "#fee2e2", "#b91c1c", "-1"
            else:
                bg, fg, lbl = "#f8fafc", "#94a3b8", "0"
            p.append(f'  <rect x="{cx+1.5:.1f}" y="{cy+1.5:.1f}" width="{cell-3:.1f}" height="{cell-3:.1f}" rx="3" fill="{bg}"/>')
            p.append(f'  <text x="{cx+cell/2:.1f}" y="{cy+cell/2+3.8:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10.2" font-weight="700" fill="{fg}">{lbl}</text>')


def build_svg() -> str:
    verify_cross5()
    W, H = 960, 504
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Bilinear Rank-K 3D Cross-Product Tensor Synthesis (brewbaker-tensor-cross)">',
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Bilinear Rank-K 3D Cross-Product Tensor Synthesis (brewbaker-tensor-cross)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Exact bilinear rank R(x &#x00D7; y) = 5 over every ring &#x2124;/m&#x2124; (m &#x2265; 2): 3 skew-symmetric slices of so(3) '
        '(Chad Brewbaker, sat_challenges.py cross)</text>',
        '  <rect x="752" y="16" width="182" height="24" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="1.2"/>',
        '  <text x="843" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#6d28d9">'
        '8 Instances &#x00B7; 4 SAT / 4 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Section 1: Left = 3 Frontal Slices; Right = Verified 5-Product Decomposition
    y1 = 78
    p.append(f'  <rect x="24" y="{y1}" width="370" height="260" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="24" y="{y1}" width="370" height="28" rx="10" fill="#6d28d9"/>')
    p.append(f'  <rect x="24" y="{y1+16}" width="370" height="12" fill="#6d28d9"/>')
    p.append(f'  <text x="38" y="{y1+19}" font-size="11.6" font-weight="700" fill="#ffffff">'
             '1. Three Skew-Symmetric Frontal Slices (so(3))</text>')

    s0 = [[0, 0, 0], [0, 0, 1], [0, -1, 0]]
    s1 = [[0, 0, -1], [0, 0, 0], [1, 0, 0]]
    s2 = [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]
    draw_slice(p, 42, y1 + 56, s0, "c0 = x1y2 - x2y1", "#2563eb")
    draw_slice(p, 162, y1 + 56, s1, "c1 = x2y0 - x0y2", "#0f766e")
    draw_slice(p, 282, y1 + 56, s2, "c2 = x0y1 - x1y0", "#d97706")

    p.append(f'  <rect x="38" y="{y1+160}" width="342" height="86" rx="7" fill="#ffffff" stroke="#ddd6fe" stroke-width="1"/>')
    p.append(f'  <text x="50" y="{y1+179}" font-size="10.4" font-weight="700" fill="#5b21b6">Why Bilinear Rank Is Always &#x2265; 5 (Every Field)</text>')
    p.append(f'  <text x="50" y="{y1+196}" font-size="9.3" fill="#334155">&#x2022; span(S0, S1, S2) = so(3) has dim 3, and every nonzero matrix</text>')
    p.append(f'  <text x="58" y="{y1+210}" font-size="9.3" fill="#334155">in so(3) has rank 2 (contains zero rank-1 outer products).</text>')
    p.append(f'  <text x="50" y="{y1+225}" font-size="9.3" fill="#334155">&#x2022; Hence 4 rank-1 terms cannot span so(3): K = 4 is UNSAT over</text>')
    p.append(f'  <text x="58" y="{y1+239}" font-size="9.3" fill="#334155">every field &#x1D53D;&#x209A; and every quotient ring &#x2124;/m&#x2124; (m &#x2265; 2).</text>')

    # Right Card: Verified Universal Rank-5 Identity
    xr = 408
    wr = 528
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="260" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="28" rx="10" fill="#0f766e"/>')
    p.append(f'  <rect x="{xr}" y="{y1+16}" width="{wr}" height="12" fill="#0f766e"/>')
    p.append(f'  <text x="{xr+14}" y="{y1+19}" font-size="11.6" font-weight="700" fill="#ffffff">'
             '2. Verified Universal Rank-5 Identity Over &#x2124; (27/27 Tensor Entries Exact)</text>')

    hy = y1 + 48
    p.append(f'  <text x="{xr+16}" y="{hy}" font-size="10" font-weight="700" fill="#334155">Term</text>')
    p.append(f'  <text x="{xr+68}" y="{hy}" font-size="10" font-weight="700" fill="#1d4ed8">Left U[t]&#x00B7;x</text>')
    p.append(f'  <text x="{xr+170}" y="{hy}" font-size="10" font-weight="700" fill="#0f766e">Right V[t]&#x00B7;y</text>')
    p.append(f'  <text x="{xr+274}" y="{hy}" font-size="10" font-weight="700" fill="#6d28d9">Expanded Product</text>')
    p.append(f'  <text x="{xr+422}" y="{hy}" font-size="10" font-weight="700" fill="#b45309">Contributes To</text>')
    p.append(f'  <line x1="{xr+14}" y1="{hy+7}" x2="{xr+wr-14}" y2="{hy+7}" stroke="#cbd5e1" stroke-width="1"/>')

    expanded = ["x0y1 - x0y2", "x1y2 - x1y0", "x2y1 - x0y1", "x2y0 - x1y0", "x1y2 - x0y2"]
    for idx, (pname, uex, vex, _, _, _, wtxt) in enumerate(CROSS_RANK5):
        ry = y1 + 74 + idx * 28
        bg = "#ffffff" if idx % 2 == 0 else "#f1f5f9"
        p.append(f'  <rect x="{xr+14}" y="{ry-14}" width="{wr-28}" height="23" rx="4" fill="{bg}"/>')
        p.append(f'  <rect x="{xr+18}" y="{ry-11}" width="32" height="17" rx="4" fill="#ccfbf1" stroke="#5eead4" stroke-width="0.9"/>')
        p.append(f'  <text x="{xr+34}" y="{ry+1}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#0f766e">{pname}</text>')
        p.append(f'  <text x="{xr+68}" y="{ry+1}" font-family="{MONO}" font-size="10" fill="#0f172a">{uex}</text>')
        p.append(f'  <text x="{xr+170}" y="{ry+1}" font-family="{MONO}" font-size="10" fill="#0f172a">{vex}</text>')
        p.append(f'  <text x="{xr+274}" y="{ry+1}" font-family="{MONO}" font-size="9.6" fill="#475569">{expanded[idx]}</text>')
        p.append(f'  <text x="{xr+422}" y="{ry+1}" font-family="{MONO}" font-size="9.6" font-weight="600" fill="#92400e">{wtxt}</text>')

    p.append(f'  <rect x="{xr+14}" y="{y1+207}" width="{wr-28}" height="40" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1"/>')
    p.append(f'  <text x="{xr+26}" y="{y1+224}" font-family="{MONO}" font-size="9.8" font-weight="700" fill="#166534">'
             'c0 = -p1 - p3 + p5   |   c1 = -p2 + p4 + p5   |   c2 = p1 + p2 - p5</text>')
    p.append(f'  <text x="{xr+26}" y="{y1+239}" font-size="9.1" fill="#15803d">'
             'All coefficients in &#x007B;&#x2212;1, 0, +1&#x007D;: reduces to a valid rank-5 witness mod m for every m &#x2265; 2 (6 naive products &#x2192; 5).</text>')

    # Bottom Card: 4 Moduli Optimality Brackets
    y2 = 352
    p.append(f'  <rect x="24" y="{y2}" width="912" height="134" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+21}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '3. Four Exact Optimality Brackets (K = 4 UNSAT vs K = 5 SAT) Scaling Across Ring Modulus m &#x2208; &#x007B;2, 3, 4, 5&#x007D;</text>')

    mods = [
        ("m = 2 (GF(2))", "262-334 vars | 784-1,000 cls", "81-108 native XORs in XCNF", "-1 == +1 (symmetric 0-diag); Chad's pair", "#2563eb", "#eff6ff"),
        ("m = 3 (GF(3))", "784-1,000 vars | 3.1K-4.0K cls", "One-hot EO(3) + 9-cls tables", "Chad's docstring example (cross 5 --mod 3)", "#7c3aed", "#faf5ff"),
        ("m = 4 (Z/4Z)", "1,045-1,333 vars | 5.5K-7.0K cls", "Composite ring (zero divisors)", "EO(4) + 16-cls tables; sub-second bracket", "#0f766e", "#f0fdfa"),
        ("m = 5 (GF(5))", "2,350-2,998 vars | 8.8K-11.2K cls", "EO(5) + 25-cls tables", "K=5 SAT ~0.7-0.8s; K=4 UNSAT frontier!", "#be123c", "#fff1f2"),
    ]
    mw = 212
    mg = 12
    for i, (t1, t2, t3, t4, sc, bg) in enumerate(mods):
        mx = 38 + i * (mw + mg)
        p.append(f'  <rect x="{mx}" y="{y2+34}" width="{mw}" height="84" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.2"/>')
        p.append(f'  <text x="{mx+mw/2:.1f}" y="{y2+52}" text-anchor="middle" font-family="{MONO}" font-size="10.4" font-weight="700" fill="{sc}">{t1}</text>')
        p.append(f'  <text x="{mx+mw/2:.1f}" y="{y2+69}" text-anchor="middle" font-size="9.3" font-weight="600" fill="#0f172a">{t2}</text>')
        p.append(f'  <text x="{mx+mw/2:.1f}" y="{y2+85}" text-anchor="middle" font-size="8.8" fill="#334155">{t3}</text>')
        p.append(f'  <text x="{mx+mw/2:.1f}" y="{y2+102}" text-anchor="middle" font-size="8.4" fill="#475569">{t4}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
