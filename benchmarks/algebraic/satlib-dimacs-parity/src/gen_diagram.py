#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `satlib-dimacs-parity` benchmark collection.

Illustrates the Crawford-Kearns-Schapire (1994) parity-learning SAT benchmark
suite (`par8`, `par16`, `par32`, original & `-c` simplified):
  - Left: Binary sample matrix A · s = b (mod 2) over k in {8, 16, 32}
    unknown parity bits s = (s_1, ..., s_k), highlighting one inner-product
    row a^(i) · s = b_i
  - Right Top: Binary Tseitin XOR reduction tree decomposing the inner-product
    parity into 3-XOR auxiliary variables (4 CNF clauses per gate -> 1 native
    XCNF XOR clause)
  - Right Bottom: Original vs `-c` simplified scaling & the sharp par32 cliff
    where pure CDCL times out (>5 s) while XOR-aware Gauss solves all 10/10.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"

FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg() -> str:
    W, H = 920, 480
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="SATLIB parity-learning A*s = b (mod 2) inner-product system compiled via binary Tseitin XOR trees">',
        "<defs>",
        '  <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '  <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>',
        '  <marker id="arr-amber" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/></marker>',
        "</defs>",
        # Explicit white card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "SATLIB Parity-Learning Benchmarks: par8 / par16 / par32 (satlib-dimacs-parity)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Crawford–Kearns–Schapire (1994) learning parity over k ∈ {8, 16, 32} bits: "
        "A · s = b (mod 2) compiled via binary Tseitin XOR trees</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: INNER-PRODUCT MATRIX A * s = b (MOD 2) =====================
    px1, py1, pw1, ph1 = 24, 76, 434, 334
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "1. Parity-Learning Linear System:  A · s = b (mod 2)</text>"
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 35}" font-size="9.4" fill="#475569">'
        "Recover unknown secret parity mask s ∈ 𝔽₂ᵏ from labeled sample vectors a⁽ⁱ⁾</text>"
    )

    # Illustrative 8x8 binary sample matrix A (k = 8 bits)
    A_rows = [
        [1, 0, 1, 1, 0, 0, 1, 0],
        [0, 1, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0],  # Highlighted row i = 2: s1 ^ s3 ^ s5 ^ s7 = b3
        [0, 1, 0, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [0, 0, 1, 1, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 1, 0],
    ]
    secret_s = [1, 0, 1, 1, 0, 1, 1, 0]
    b_vec = [sum(a * s for a, s in zip(row, secret_s)) % 2 for row in A_rows]

    mx, my = px1 + 22, py1 + 64
    cw, ch = 26, 22
    mat_w = 8 * cw
    mat_h = 8 * ch

    # Matrix A header
    parts.append(
        f'<text x="{mx + mat_w/2:.1f}" y="{my - 10}" text-anchor="middle" '
        'font-size="10.2" font-weight="700" fill="#1d4ed8">Sample Matrix A (m × k)</text>'
    )
    parts.append(
        f'<rect x="{mx - 3}" y="{my - 3}" width="{mat_w + 6}" height="{mat_h + 6}" '
        'rx="5" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>'
    )
    # Highlight row 2 (a^(3))
    hl_row = 2
    parts.append(
        f'<rect x="{mx - 1}" y="{my + hl_row * ch - 1}" width="{mat_w + 2}" height="{ch + 2}" '
        'rx="3" fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>'
    )
    for r_i, row in enumerate(A_rows):
        for c_i, val in enumerate(row):
            cx = mx + c_i * cw
            cy = my + r_i * ch
            if r_i == hl_row and val == 1:
                fill, fg = "#d97706", "#ffffff"
            elif val == 1:
                fill, fg = "#dbeafe", "#1d4ed8"
            else:
                fill, fg = "#f8fafc", "#94a3b8"
            parts.append(f'<rect x="{cx + 2}" y="{cy + 2}" width="{cw - 4}" height="{ch - 4}" rx="3" fill="{fill}"/>')
            parts.append(
                f'<text x="{cx + cw/2:.1f}" y="{cy + ch/2 + 3.8:.1f}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="{fg}">{val}</text>'
            )

    # Dot operator
    x_dot = mx + mat_w + 15
    parts.append(f'<text x="{x_dot}" y="{my + mat_h/2 + 5:.1f}" text-anchor="middle" font-size="16" font-weight="700" fill="#475569">·</text>')

    # Unknown Secret Vector s (Green)
    sx = x_dot + 14
    sw = 34
    parts.append(f'<text x="{sx + sw/2:.1f}" y="{my - 10}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#047857">Secret s</text>')
    parts.append(f'<rect x="{sx - 2}" y="{my - 3}" width="{sw + 4}" height="{mat_h + 6}" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
    for i in range(8):
        cy = my + i * ch
        hl_s = A_rows[hl_row][i] == 1
        parts.append(
            f'<rect x="{sx + 2}" y="{cy + 2}" width="{sw - 4}" height="{ch - 4}" rx="3" '
            f'fill="{"#059669" if hl_s else "#ffffff"}" stroke="#6ee7b7" stroke-width="0.8"/>'
        )
        parts.append(
            f'<text x="{sx + sw/2:.1f}" y="{cy + ch/2 + 3.8:.1f}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="9.5" font-weight="700" '
            f'fill="{"#ffffff" if hl_s else "#047857"}">s{chr(0x2081 + i)}</text>'
        )

    # Equals operator
    x_eq = sx + sw + 16
    parts.append(f'<text x="{x_eq}" y="{my + mat_h/2 + 5:.1f}" text-anchor="middle" font-size="15" font-weight="700" fill="#475569">=</text>')

    # Observed Parity Vector b (Amber)
    bx_v = x_eq + 14
    bw_v = 34
    parts.append(f'<text x="{bx_v + bw_v/2:.1f}" y="{my - 10}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#b45309">Labels b</text>')
    parts.append(f'<rect x="{bx_v - 2}" y="{my - 3}" width="{bw_v + 4}" height="{mat_h + 6}" rx="5" fill="#fffbeb" stroke="#d97706" stroke-width="1.2"/>')
    for i, bv in enumerate(b_vec):
        cy = my + i * ch
        is_hl = i == hl_row
        parts.append(
            f'<rect x="{bx_v + 2}" y="{cy + 2}" width="{bw_v - 4}" height="{ch - 4}" rx="3" '
            f'fill="{"#d97706" if is_hl else "#ffffff"}" stroke="#fcd34d" stroke-width="0.8"/>'
        )
        parts.append(
            f'<text x="{bx_v + bw_v/2:.1f}" y="{cy + ch/2 + 3.8:.1f}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="10" font-weight="700" '
            f'fill="{"#ffffff" if is_hl else "#b45309"}">{bv}</text>'
        )

    # Selected row equation box under matrix
    parts.append(
        f'<rect x="{px1 + 16}" y="{py1 + 256}" width="{pw1 - 32}" height="62" rx="7" '
        'fill="#ffffff" stroke="#d97706" stroke-width="1.15"/>'
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 275}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="10.1" font-weight="700" fill="#b45309">'
        "Row 3:  a⁽³⁾ · s  =  s₁ ⊕ s₃ ⊕ s₅ ⊕ s₇  =  b₃ (mod 2)</text>"
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 293}" text-anchor="middle" font-size="9.2" fill="#334155">'
        "Each active parity row is compiled into a binary Tseitin XOR tree;</text>"
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 308}" text-anchor="middle" font-size="9.2" fill="#475569">'
        "all 30 instances are planted SAT (5 random seeds × k ∈ {8, 16, 32} × {orig, -c}).</text>"
    )

    # Connector arrow from Matrix row to Right Panel XOR Tree
    parts.append(
        f'<line x1="{px1 + pw1 - 4}" y1="{my + hl_row * ch + ch/2:.1f}" x2="{474 - 2}" y2="{my + hl_row * ch + ch/2:.1f}" '
        'stroke="#d97706" stroke-width="2.0" marker-end="url(#arr-amber)"/>'
    )

    # ===================== RIGHT PANEL: BINARY TSEITIN XOR TREE + PAR32 CLIFF =====================
    px2, py2, pw2, ph2 = 474, 76, 422, 334
    # Top Card: Binary Tseitin XOR Tree
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="184" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{py2 + 20}" font-size="11.8" font-weight="700" fill="#0f172a">'
        "2. Binary Tseitin XOR Tree Decomposition (CNF ↔ XCNF)</text>"
    )

    # Tree layout inside Top Card (y = py2 + 32 .. py2 + 168)
    # Leaves at bottom of tree: s1, s3, s5, s7
    leaf_xs = [px2 + 54, px2 + 130, px2 + 236, px2 + 312]
    leaf_y = py2 + 146
    mid_xs = [px2 + 92, px2 + 274]
    mid_y = py2 + 96
    root_x, root_y = px2 + 183, py2 + 52

    # Tree edges
    for lx_i, mx_i in [(leaf_xs[0], mid_xs[0]), (leaf_xs[1], mid_xs[0]), (leaf_xs[2], mid_xs[1]), (leaf_xs[3], mid_xs[1])]:
        parts.append(f'<line x1="{lx_i}" y1="{leaf_y - 13}" x2="{mx_i}" y2="{mid_y + 15}" stroke="#7c3aed" stroke-width="1.6"/>')
    for mx_i in mid_xs:
        parts.append(f'<line x1="{mx_i}" y1="{mid_y - 15}" x2="{root_x}" y2="{root_y + 15}" stroke="#2563eb" stroke-width="1.7"/>')

    # Leaf nodes (secret bits)
    for lx_i, lbl in zip(leaf_xs, ["s₁", "s₃", "s₅", "s₇"]):
        parts.append(f'<rect x="{lx_i - 18}" y="{leaf_y - 13}" width="36" height="24" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
        parts.append(f'<text x="{lx_i}" y="{leaf_y + 3}" text-anchor="middle" font-family="{FONT_MONO}" font-size="10.2" font-weight="700" fill="#047857">{lbl}</text>')

    # Intermediate Tseitin 3-XOR nodes t1, t2
    for mx_i, tlbl in zip(mid_xs, ["t₁ = s₁⊕s₃", "t₂ = s₅⊕s₇"]):
        parts.append(f'<rect x="{mx_i - 46}" y="{mid_y - 14}" width="92" height="26" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.25"/>')
        parts.append(f'<text x="{mx_i}" y="{mid_y + 3}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.4" font-weight="700" fill="#6d28d9">{tlbl}</text>')

    # Root XOR assertion node t1 ^ t2 = b3
    parts.append(f'<rect x="{root_x - 62}" y="{root_y - 14}" width="124" height="28" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
    parts.append(f'<text x="{root_x}" y="{root_y + 4}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.8" font-weight="700" fill="#1d4ed8">t₁ ⊕ t₂ = b₃</text>')

    # Side callout box explaining CNF vs XCNF collapse
    cx_n = px2 + 324
    parts.append(f'<rect x="{cx_n}" y="{py2 + 36}" width="86" height="90" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{cx_n + 43}" y="{py2 + 52}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#0f172a">Per ⊕ Gate:</text>')
    parts.append(f'<text x="{cx_n + 43}" y="{py2 + 67}" text-anchor="middle" font-size="8.4" fill="#475569">4 CNF 3-cls</text>')
    parts.append(f'<text x="{cx_n + 43}" y="{py2 + 81}" text-anchor="middle" font-size="9" font-weight="700" fill="#2563eb">↓ XCNF</text>')
    parts.append(f'<text x="{cx_n + 43}" y="{py2 + 95}" text-anchor="middle" font-size="8.4" font-weight="700" fill="#1d4ed8">1 native XOR</text>')
    parts.append(f'<text x="{cx_n + 43}" y="{py2 + 114}" text-anchor="middle" font-size="8.1" fill="#475569">-c simplifies</text>')
    parts.append(f'<text x="{cx_n + 43}" y="{py2 + 123}" text-anchor="middle" font-size="8.1" fill="#475569">trivial gates</text>')

    # Bottom Card: Scaling & par32 CDCL vs Gauss Cliff
    cy_b = py2 + 194
    parts.append(
        f'<rect x="{px2}" y="{cy_b}" width="{pw2}" height="140" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{cy_b + 19}" font-size="11.6" font-weight="700" fill="#0f172a">'
        "3. Scaling Across par8 / par16 / par32 (orig vs. -c)</text>"
    )
    th_y = cy_b + 36
    parts.append(f'<rect x="{px2 + 10}" y="{th_y - 10}" width="{pw2 - 20}" height="16" rx="4" fill="#e2e8f0"/>')
    for cx_h, lbl_h, anc in [
        (px2 + 16, "Family (10)", "start"),
        (px2 + 124, "Vars Range", "middle"),
        (px2 + 190, "XORs", "middle"),
        (px2 + 266, "Pure CDCL", "middle"),
        (px2 + 358, "CMS (Gauss)", "middle"),
    ]:
        parts.append(f'<text x="{cx_h}" y="{th_y + 1}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{lbl_h}</text>')

    par_rows = [
        ("par8  / -c", "64–350", "1,103", "1.6–3.6 ms", "20–29 ms", "#334155", "#047857"),
        ("par16 / -c", "317–1,015", "3,835", "9–79 ms", "48–62 ms", "#334155", "#047857"),
        ("par32 / -c", "1,315–3,176", "13,610", ">5 s (0/10 T/O)", "0.40–1.98 s (10/10)", "#b91c1c", "#047857"),
    ]
    for i, (fam, vs, xr, cdcl, cms, cc, gc) in enumerate(par_rows):
        ry_r = th_y + 19 + i * 24
        if i == 2:
            parts.append(f'<rect x="{px2 + 10}" y="{ry_r - 12}" width="{pw2 - 20}" height="21" rx="4" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
        elif i % 2 == 1:
            parts.append(f'<rect x="{px2 + 10}" y="{ry_r - 12}" width="{pw2 - 20}" height="20" rx="3" fill="#ffffff"/>')
        parts.append(f'<text x="{px2 + 16}" y="{ry_r + 2}" font-family="{FONT_MONO}" font-size="8.8" font-weight="700" fill="#0f172a">{fam}</text>')
        parts.append(f'<text x="{px2 + 124}" y="{ry_r + 2}" text-anchor="middle" font-size="8.8" fill="#334155">{vs}</text>')
        parts.append(f'<text x="{px2 + 190}" y="{ry_r + 2}" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1d4ed8">{xr}</text>')
        parts.append(f'<text x="{px2 + 266}" y="{ry_r + 2}" text-anchor="middle" font-size="8.6" font-weight="700" fill="{cc}">{cdcl}</text>')
        parts.append(f'<text x="{px2 + 358}" y="{ry_r + 2}" text-anchor="middle" font-size="8.6" font-weight="700" fill="{gc}">{cms}</text>')

    parts.append(
        f'<text x="{px2 + 14}" y="{cy_b + 129}" font-size="8.7" fill="#475569">'
        "Only CryptoMiniSat (30/30, 11.2 s) solves all par32 via native XOR Gaussian elimination.</text>"
    )

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 424
    pills = [
        (24, 210, "#ecfdf5", "#059669", "#047857", "30 / 30 SAT (par8, par16, par32)"),
        (244, 212, "#eff6ff", "#2563eb", "#1d4ed8", "18,548 Extracted Native XORs"),
        (466, 206, "#fffbeb", "#d97706", "#b45309", "ρ_c = 1.15×–1.59× (Over)"),
        (682, 214, "#f5f3ff", "#7c3aed", "#6d28d9", "4 Formats: CNF · AIG · XCNF · ANF"),
    ]
    for px_p, pw_p, bg, bd, fg, lbl in pills:
        parts.append(f'<rect x="{px_p}" y="{by_s}" width="{pw_p}" height="34" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        parts.append(f'<text x="{px_p + pw_p/2:.1f}" y="{by_s + 21}" text-anchor="middle" font-size="10.1" font-weight="700" fill="{fg}">{esc(lbl)}</text>')

    parts.append("</g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
