#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-tensor-dot.

Visualizes the bilinear inner-product tensor I_N = sum_{t=0}^{K-1} u_t * v_t^T * w_t over Z/mZ,
illustrating why rank(I_N) = N forces K = N-1 UNSAT and K = N SAT across every modulus m >= 2.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def draw_small_mat(p: list[str], x: float, y: float, mat: list[list[int]], cell: float, title: str, accent: str) -> None:
    n = len(mat)
    w = n * cell + 12
    h = n * cell + 10
    p.append(f'  <text x="{x+w/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="10.2" font-weight="700" fill="{accent}">{title}</text>')
    p.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="#ffffff" stroke="{accent}" stroke-width="1.2"/>')
    for r in range(n):
        for c in range(n):
            v = mat[r][c]
            cx = x + 6 + c * cell
            cy = y + 5 + r * cell
            fill = "#dcfce7" if v == 1 else "#f8fafc"
            fg = "#166534" if v == 1 else "#94a3b8"
            p.append(f'  <rect x="{cx+1.5:.1f}" y="{cy+1.5:.1f}" width="{cell-3:.1f}" height="{cell-3:.1f}" rx="3" fill="{fill}"/>')
            p.append(f'  <text x="{cx+cell/2:.1f}" y="{cy+cell/2+3.8:.1f}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="{fg}">{v}</text>')


def build_svg() -> str:
    # Verify rank-3 exact decomposition of I_3
    e = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    i3 = [[1 if r == c else 0 for c in range(3)] for r in range(3)]
    for r in range(3):
        for c in range(3):
            assert sum(e[t][r] * e[t][c] for t in range(3)) == i3[r][c]

    W, H = 960, 486
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Bilinear Rank-K Inner-Product Tensor Synthesis (brewbaker-tensor-dot)">',
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Bilinear Rank-K Inner-Product Tensor Synthesis (brewbaker-tensor-dot)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Proving exact bilinear rank R(I&#x2099;) = N of &#x27E8;x, y&#x27E9; = &#x03A3; x&#x1D62;y&#x1D62; (mod m) via SAT '
        '(Chad Brewbaker, sat_challenges.py dot)</text>',
        '  <rect x="748" y="16" width="186" height="24" rx="12" fill="#f0fdfa" stroke="#0f766e" stroke-width="1.2"/>',
        '  <text x="841" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#0f766e">'
        '10 Instances &#x00B7; 5 SAT / 5 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Section 1: Exact Matrix Rank Identity (N = 3 visual)
    y1 = 78
    p.append(f'  <rect x="24" y="{y1}" width="912" height="162" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="24" y="{y1}" width="912" height="28" rx="10" fill="#0f766e"/>')
    p.append(f'  <rect x="24" y="{y1+16}" width="912" height="12" fill="#0f766e"/>')
    p.append(f'  <text x="38" y="{y1+19}" font-size="11.8" font-weight="700" fill="#ffffff">'
             '1. Bilinear Outer-Product Rank Bottleneck: I&#x2099; = &#x03A3;&#x209C;&#x208C;&#x2080;&#x1D37;&#x207B;&#x00B9; w&#x209C; (u&#x209C; &#x2297; v&#x209C;) over &#x2124;/m&#x2124; (Illustrated for N = 3)</text>')

    my = y1 + 58
    draw_small_mat(p, 44, my, i3, 25, "Target I3 (rank = 3)", "#0f766e")
    p.append(f'  <text x="148" y="{my+48}" text-anchor="middle" font-size="18" font-weight="700" fill="#475569">=</text>')
    r1 = [[1,0,0],[0,0,0],[0,0,0]]
    r2 = [[0,0,0],[0,1,0],[0,0,0]]
    r3 = [[0,0,0],[0,0,0],[0,0,1]]
    draw_small_mat(p, 166, my, r1, 25, "Term 0: e0 e0^T", "#2563eb")
    p.append(f'  <text x="270" y="{my+48}" text-anchor="middle" font-size="16" font-weight="700" fill="#475569">+</text>')
    draw_small_mat(p, 286, my, r2, 25, "Term 1: e1 e1^T", "#7c3aed")
    p.append(f'  <text x="390" y="{my+48}" text-anchor="middle" font-size="16" font-weight="700" fill="#475569">+</text>')
    draw_small_mat(p, 406, my, r3, 25, "Term 2: e2 e2^T", "#d97706")

    # Right callout box explaining K=N-1 UNSAT vs K=N SAT
    bx = 524
    p.append(f'  <rect x="{bx}" y="{y1+38}" width="396" height="112" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'  <text x="{bx+14}" y="{y1+57}" font-size="11.2" font-weight="700" fill="#0f172a">Universal Algebraic Lower Bound (Every m &#x2265; 2)</text>')
    p.append(f'  <text x="{bx+14}" y="{y1+75}" font-size="9.6" fill="#334155">'
             'For any prime p | m, projecting &#x2124;/m&#x2124; &#x2192; &#x1D53D;&#x209A; maps U&#x00B7;diag(W)&#x00B7;V&#x1D40; = I&#x2099; to an</text>')
    p.append(f'  <text x="{bx+14}" y="{y1+89}" font-size="9.6" fill="#334155">'
             'N&#x00D7;N matrix of rank at most K, which is impossible whenever K &lt; N.</text>')
    p.append(f'  <rect x="{bx+14}" y="{y1+100}" width="178" height="39" rx="6" fill="#fef2f2" stroke="#f87171" stroke-width="1"/>')
    p.append(f'  <text x="{bx+103}" y="{y1+116}" text-anchor="middle" font-size="10" font-weight="700" fill="#b91c1c">K = N - 1 : Always UNSAT</text>')
    p.append(f'  <text x="{bx+103}" y="{y1+131}" text-anchor="middle" font-size="8.6" fill="#7f1d1d">Hard resolution rank-lower-bound proof</text>')
    p.append(f'  <rect x="{bx+204}" y="{y1+100}" width="178" height="39" rx="6" fill="#f0fdf4" stroke="#4ade80" stroke-width="1"/>')
    p.append(f'  <text x="{bx+293}" y="{y1+116}" text-anchor="middle" font-size="10" font-weight="700" fill="#15803d">K = N : Always SAT</text>')
    p.append(f'  <text x="{bx+293}" y="{y1+131}" text-anchor="middle" font-size="8.6" fill="#166534">GL(N, Z/mZ) basis decompositions</text>')

    # Section 2: Encoding Contrast (Mod 2 vs Mod 3 vs Mod 4)
    y2 = 252
    p.append(f'  <rect x="24" y="{y2}" width="912" height="94" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+20}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '2. Algebraic Encoding Regimes Across Prime Fields (&#x1D53D;&#x2082;, &#x1D53D;&#x2083;) and Composite Ring &#x2124;/4&#x2124;</text>')
    regs = [
        (38, 286, "#eff6ff", "#2563eb", "#1d4ed8", "m = 2 (GF(2) Field)", "Bit-level and2 + xor2; exposes 75-180 native XORs in xcnf-converted/"),
        (337, 286, "#faf5ff", "#7c3aed", "#6d28d9", "m = 3 (GF(3) Odd Prime Field)", "One-hot EO(3) residues + 9-clause mult/add tables; 0 XORs, high density"),
        (636, 286, "#fffbeb", "#d97706", "#b45309", "m = 4 (Z/4Z with Zero Divisors)", "2*2 = 0 (mod 4) creates non-field nilpotent terms; 16-clause tables"),
    ]
    for rx, rw, bg, bd, fg, t1, t2 in regs:
        p.append(f'  <rect x="{rx}" y="{y2+31}" width="{rw}" height="51" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1.1"/>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+50}" text-anchor="middle" font-size="10.4" font-weight="700" fill="{fg}">{t1}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+69}" text-anchor="middle" font-size="8.6" fill="#334155">{t2}</text>')

    # Section 3: 5 Optimality Brackets (10 instances)
    y3 = 358
    p.append(f'  <rect x="24" y="{y3}" width="912" height="112" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y3+20}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '3. Five Tight UNSAT / SAT Optimality Brackets (10 Instances, N &#x2208; &#x007B;3, 5, 6&#x007D;, m &#x2208; &#x007B;2, 3, 4&#x007D;)</text>')
    brackets = [
        ("dot N=3, mod 4", "K = 2 / 3", "237-373 vars | 1.1K-1.8K cls", "Chad's headline example", "#d97706", "#fffbeb"),
        ("dot N=5, mod 2", "K = 4 / 5", "320-406 vars | 75-100 XORs", "GF(2) rank-5 proof", "#2563eb", "#eff6ff"),
        ("dot N=6, mod 2", "K = 5 / 6", "570-691 vars | 144-180 XORs", "GF(2) hard rank-6 proof", "#1d4ed8", "#eef2ff"),
        ("dot N=5, mod 3", "K = 4 / 5", "958-1,216 vars | 3.8K-4.8K cls", "GF(3) rank-5 frontier", "#7c3aed", "#faf5ff"),
        ("dot N=5, mod 4", "K = 4 / 5", "1,277-1,621 vars | 6.7K-8.5K cls", "Z/4Z composite ring", "#0f766e", "#f0fdfa"),
    ]
    bw = 169
    bgap = 10
    for i, (t1, t2, t3, t4, sc, bg) in enumerate(brackets):
        bx2 = 38 + i * (bw + bgap)
        p.append(f'  <rect x="{bx2}" y="{y3+31}" width="{bw}" height="68" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.1"/>')
        p.append(f'  <text x="{bx2+bw/2:.1f}" y="{y3+48}" text-anchor="middle" font-family="{MONO}" font-size="9.8" font-weight="700" fill="{sc}">{t1}</text>')
        p.append(f'  <text x="{bx2+bw/2:.1f}" y="{y3+64}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#0f172a">{t2} (UNSAT/SAT)</text>')
        p.append(f'  <text x="{bx2+bw/2:.1f}" y="{y3+78}" text-anchor="middle" font-size="8.4" fill="#334155">{t3}</text>')
        p.append(f'  <text x="{bx2+bw/2:.1f}" y="{y3+91}" text-anchor="middle" font-size="8.2" fill="#475569">{t4}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
