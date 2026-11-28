#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-tensor-matmul.

Visualizes Strassen's verified 7-product bilinear decomposition of 2x2 matrix multiplication
(U, V, W factor matrices over Z -> Z/mZ), the Brent coefficient tensor equations, and the
10-instance UNSAT/SAT optimality-bracket scaling ladder. Zero external dependencies.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Strassen's exact 7 bilinear products for C = A * B (2x2, flattened row-major: 0=00, 1=01, 2=10, 3=11)
STRASSEN = [
    ("M1", "(a00 + a11)", "(b00 + b11)", [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], "+C00, +C11"),
    ("M2", "(a10 + a11)", "b00",         [0, 0, 1, 1], [1, 0, 0, 0], [0, 0, 1, -1], "+C10, -C11"),
    ("M3", "a00",         "(b01 - b11)", [1, 0, 0, 0], [0, 1, 0, -1], [0, 1, 0, 1], "+C01, +C11"),
    ("M4", "a11",         "(b10 - b00)", [0, 0, 0, 1], [-1, 0, 1, 0], [1, 0, 1, 0], "+C00, +C10"),
    ("M5", "(a00 + a01)", "b11",         [1, 1, 0, 0], [0, 0, 0, 1], [-1, 1, 0, 0], "-C00, +C01"),
    ("M6", "(a10 - a00)", "(b00 + b01)", [-1, 0, 1, 0], [1, 1, 0, 0], [0, 0, 0, 1], "+C11"),
    ("M7", "(a01 - a11)", "(b10 + b11)", [0, 1, 0, -1], [0, 0, 1, 1], [1, 0, 0, 0], "+C00"),
]


def verify_strassen() -> None:
    target = {(i * 2 + j, j * 2 + k, i * 2 + k): 1 for i in range(2) for j in range(2) for k in range(2)}
    for i in range(4):
        for j in range(4):
            for o in range(4):
                got = sum(row[3][i] * row[4][j] * row[5][o] for row in STRASSEN)
                exp = target.get((i, j, o), 0)
                assert got == exp, f"Brent equation failed at ({i},{j},{o}): {got} != {exp}"


def build_svg() -> str:
    verify_strassen()
    W, H = 960, 520
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Bilinear Rank-K Matrix Multiplication Tensor Synthesis (brewbaker-tensor-matmul)">',
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Bilinear Rank-K Matrix Multiplication Tensor Synthesis (brewbaker-tensor-matmul)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Brent coefficient tensor equations &#x03A3; U[t,i]&#x00B7;V[t,j]&#x00B7;W[t,o] &#x2261; T[i,j,o] (mod m) '
        '(Chad Brewbaker, sat_challenges.py matmul)</text>',
        '  <rect x="748" y="16" width="186" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '  <text x="841" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">'
        '10 Instances &#x00B7; 6 SAT / 4 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Section 1: Strassen 7-product verified table (left) + Tensor & Output reconstruction (right)
    y1 = 78
    p.append(f'  <rect x="24" y="{y1}" width="576" height="278" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="24" y="{y1}" width="576" height="28" rx="10" fill="#1d4ed8"/>')
    p.append(f'  <rect x="24" y="{y1+16}" width="576" height="12" fill="#1d4ed8"/>')
    p.append(f'  <text x="38" y="{y1+19}" font-size="11.8" font-weight="700" fill="#ffffff">'
             '1. Verified Strassen Rank-7 Decomposition of &lt;2, 2, 2&gt; (64/64 Brent Equations Exact)</text>')

    # Column headers
    hy = y1 + 48
    p.append(f'  <text x="42" y="{hy}" font-size="10.2" font-weight="700" fill="#334155">Term</text>')
    p.append(f'  <text x="90" y="{hy}" font-size="10.2" font-weight="700" fill="#1d4ed8">Left Form U[t]&#x00B7;A</text>')
    p.append(f'  <text x="216" y="{hy}" font-size="10.2" font-weight="700" fill="#0f766e">Right Form V[t]&#x00B7;B</text>')
    p.append(f'  <text x="342" y="{hy}" font-size="10.2" font-weight="700" fill="#6d28d9">U / V / W (&#x2208;&#x007B;&#x2212;1,0,1&#x007D;)</text>')
    p.append(f'  <text x="498" y="{hy}" font-size="10.2" font-weight="700" fill="#b45309">Output W[t]</text>')
    p.append(f'  <line x1="36" y1="{hy+7}" x2="588" y2="{hy+7}" stroke="#cbd5e1" stroke-width="1"/>')

    def fmt_vec(v: list[int]) -> str:
        return "".join("+" if x == 1 else ("-" if x == -1 else ".") for x in v)

    for idx, (mname, uexpr, vexpr, uvec, vvec, wvec, wtxt) in enumerate(STRASSEN):
        ry = y1 + 74 + idx * 28
        bg = "#ffffff" if idx % 2 == 0 else "#f1f5f9"
        p.append(f'  <rect x="36" y="{ry-14}" width="552" height="23" rx="4" fill="{bg}"/>')
        p.append(f'  <rect x="40" y="{ry-11}" width="32" height="17" rx="4" fill="#dbeafe" stroke="#93c5fd" stroke-width="0.9"/>')
        p.append(f'  <text x="56" y="{ry+1}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#1e40af">{mname}</text>')
        p.append(f'  <text x="90" y="{ry+1}" font-family="{MONO}" font-size="10" fill="#0f172a">{uexpr}</text>')
        p.append(f'  <text x="216" y="{ry+1}" font-family="{MONO}" font-size="10" fill="#0f172a">{vexpr}</text>')
        sig = f"{fmt_vec(uvec)} | {fmt_vec(vvec)} | {fmt_vec(wvec)}"
        p.append(f'  <text x="342" y="{ry+1}" font-family="{MONO}" font-size="9.6" fill="#5b21b6">{sig}</text>')
        p.append(f'  <text x="498" y="{ry+1}" font-family="{MONO}" font-size="9.6" font-weight="600" fill="#92400e">{wtxt}</text>')

    p.append(f'  <text x="38" y="{y1+269}" font-size="9.6" fill="#475569">'
             'Because all entries lie in &#x007B;&#x2212;1, 0, +1&#x007D;, this rank-7 witness reduces validly into EVERY ring &#x2124;/m&#x2124; (m &#x2265; 2).</text>')

    # Right Card: Output formulas + Dual Mod-2 vs Mod-m Encoding
    xr = 614
    wr = 322
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="134" rx="10" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2"/>')
    p.append(f'  <text x="{xr+14}" y="{y1+22}" font-size="11.8" font-weight="700" fill="#166534">'
             '2. Linear Output Reconstruction</text>')
    out_eqs = [
        "C00 = M1 + M4 - M5 + M7",
        "C01 = M3 + M5",
        "C10 = M2 + M4",
        "C11 = M1 - M2 + M3 + M6",
    ]
    for i, eq in enumerate(out_eqs):
        p.append(f'  <text x="{xr+18}" y="{y1+45+i*18}" font-family="{MONO}" font-size="10.4" font-weight="600" fill="#0f172a">{eq}</text>')
    p.append(f'  <text x="{xr+14}" y="{y1+123}" font-size="9.5" fill="#15803d">'
             'Winograd (1971) / Hopcroft-Kerr (1971): R(2,2,2) = 7.</text>')

    p.append(f'  <rect x="{xr}" y="{y1+144}" width="{wr}" height="134" rx="10" fill="#faf5ff" stroke="#c4b5fd" stroke-width="1.2"/>')
    p.append(f'  <text x="{xr+14}" y="{y1+166}" font-size="11.8" font-weight="700" fill="#6d28d9">'
             '3. Ring Encoding in sat_challenges.py</text>')
    enc_lines = [
        ("m = 2 (GF(2)):", "1 bit per coeff; mul = and2 (3 cls),"),
        ("", "add = xor2 (4 cls -> native XCNF XORs)."),
        ("m >= 3 (Z/mZ):", "m one-hot vars + EO(m) per coeff;"),
        ("", "mul/add = m^2 direct table implications."),
        ("Symmetry:", "K! term permutations x GL scaling."),
    ]
    for i, (k_lbl, desc) in enumerate(enc_lines):
        yy = y1 + 188 + i * 17.5
        if k_lbl:
            p.append(f'  <text x="{xr+14}" y="{yy:.1f}" font-size="9.6" font-weight="700" fill="#5b21b6">{k_lbl}</text>')
            p.append(f'  <text x="{xr+98}" y="{yy:.1f}" font-size="9.5" fill="#1e293b">{desc}</text>')
        else:
            p.append(f'  <text x="{xr+98}" y="{yy:.1f}" font-size="9.5" fill="#1e293b">{desc}</text>')

    # Bottom Card: Optimality-Bracket Scaling Ladder
    y2 = 370
    p.append(f'  <rect x="24" y="{y2}" width="912" height="132" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+21}" font-size="12" font-weight="700" fill="#0f172a">'
             '4. Exact Bilinear Rank Optimality Brackets (10 Instances across &lt;A, B, C&gt; and Moduli m &#x2208; &#x007B;2, 3, 4&#x007D;)</text>')

    cards = [
        ("<2, 2, 1> mod 2", "R* = 4", "k=3 UNSAT / k=4 SAT", "129-177 vars | 32-48 XORs", "#0f766e", "#f0fdfa"),
        ("<2, 2, 2> mod 2", "R* = 7 (Strassen)", "k=6 UNSAT / k=7 SAT", "873-1,029 vars | 320-384 XORs", "#1d4ed8", "#eff6ff"),
        ("<2, 2, 2> mod 3", "R* = 7 (Strassen)", "k=6 UNSAT / k=7 SAT", "2,617-3,085 vars | one-hot EO(3)", "#6d28d9", "#faf5ff"),
        ("<2, 2, 2> mod 4", "R* = 7 (Z/4Z)", "k=7 SAT", "4,113 vars | 22,365 clauses", "#b45309", "#fffbeb"),
        ("<2, 2, 3> & <2, 3, 2>", "R* = 11 (Hopcroft-Kerr)", "k=10 UNSAT / k=11 SAT", "3,137-3,597 vars | 1.3K-1.5K XORs", "#be123c", "#fff1f2"),
    ]
    cw = 169
    gap = 10
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for i, (t1, t2, t3, t4, sc, bg) in enumerate(cards):
        cx = 38 + i * (cw + gap)
        p.append(f'  <rect x="{cx}" y="{y2+34}" width="{cw}" height="82" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.2"/>')
        p.append(f'  <text x="{cx+cw/2:.1f}" y="{y2+52}" text-anchor="middle" font-family="{MONO}" font-size="9.8" font-weight="700" fill="{sc}">{esc(t1)}</text>')
        p.append(f'  <text x="{cx+cw/2:.1f}" y="{y2+69}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#0f172a">{esc(t2)}</text>')
        p.append(f'  <text x="{cx+cw/2:.1f}" y="{y2+86}" text-anchor="middle" font-family="{MONO}" font-size="9.0" fill="#334155">{esc(t3)}</text>')
        p.append(f'  <text x="{cx+cw/2:.1f}" y="{y2+103}" text-anchor="middle" font-size="8.4" fill="#475569">{esc(t4)}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
