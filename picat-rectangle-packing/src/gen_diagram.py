#!/usr/bin/env python3
"""Generate bespoke illustrative SVG (`diagram.svg`) for `picat-rectangle-packing`
(2D Consecutive-Square / Rectangle Packing via Picat-SAT `diffn` + `cumulative`).

Standalone Python 3 stdlib only. Writes `../diagram.svg` and validates XML.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"
FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_svg() -> str:
    W, H = 940, 504
    # Exact verified Picat-SAT optimal solution for rpack_n8_14x15 (W=15, H=14, sum=204, waste=6):
    # Squares s = 1..8 at (x, y)
    xs_sol = [8, 10, 12, 11, 6, 0, 8, 0]
    ys_sol = [7, 7, 7, 10, 9, 8, 0, 0]
    box_w, box_h = 15, 14
    # Sanity-check exact non-overlap and bounds
    occ = [[0] * box_w for _ in range(box_h)]
    for idx in range(8):
        s = idx + 1
        x0, y0 = xs_sol[idx], ys_sol[idx]
        assert 0 <= x0 and x0 + s <= box_w and 0 <= y0 and y0 + s <= box_h
        for dy in range(s):
            for dx in range(s):
                assert occ[y0 + dy][x0 + dx] == 0
                occ[y0 + dy][x0 + dx] = s
    empty_cells = sum(1 for r in occ for v in r if v == 0)
    assert empty_cells == 6

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-label="Picat-SAT 2D Rectangle Packing diffn and cumulative Tile Layout">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        '2D Square &amp; Rectangle Packing — diffn + cumulative (picat-rectangle-packing)</text>',
        '    <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Picat 3.9#12 SAT compilation (MIT, H. Kjellerstrand / MiniZinc rect_packing.mzn) · '
        'Pack squares 1×1..n×n into tight H×W boxes</text>',
        '    <rect x="780" y="18" width="136" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">5 SAT · 5 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: EXACT OPTIMAL 14x15 PACKING FOR N=8 =================
    lx, ly, lw, lh = 24, 78, 452, 404
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 23}" font-size="13" font-weight="700" fill="#0f172a">1. Verified Optimal Packing: n = 8 in 14 × 15 (Area = 210)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 39}" font-size="10.2" fill="#475569">Σᵢ₌₁⁸ i² = 204 occupied + 6 empty unit cells (2.86% slack) · 13×16 (208) is UNSAT</text>')

    gx0, gy0, cell = lx + 42, ly + 60, 21
    # Background bounding box (shows 6 empty cells in light hatched gray)
    p.append(f'    <rect x="{gx0}" y="{gy0}" width="{box_w * cell}" height="{box_h * cell}" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>')
    for r in range(box_h):
        for c in range(box_w):
            if occ[r][c] == 0:
                ex, ey = gx0 + c * cell, gy0 + r * cell
                p.append(f'    <rect x="{ex}" y="{ey}" width="{cell}" height="{cell}" fill="#e2e8f0" stroke="#94a3b8" stroke-width="0.8"/>')
                p.append(f'    <line x1="{ex + 4}" y1="{ey + 4}" x2="{ex + cell - 4}" y2="{ey + cell - 4}" stroke="#94a3b8" stroke-width="1"/>')

    # Distinct clean pastel/bold tile palette for squares 1..8
    tile_style = {
        8: ("#dbeafe", "#2563eb", "#1e3a8a"),
        7: ("#d1fae5", "#059669", "#065f46"),
        6: ("#ede9fe", "#7c3aed", "#4c1d95"),
        5: ("#fef3c7", "#d97706", "#92400e"),
        4: ("#ffe4e6", "#e11d48", "#9f1239"),
        3: ("#cffafe", "#0891b2", "#155e75"),
        2: ("#fce7f3", "#db2777", "#831843"),
        1: ("#ecfccb", "#65a30d", "#365314"),
    }
    for s in range(8, 0, -1):
        x0, y0 = xs_sol[s - 1], ys_sol[s - 1]
        bg, bd, fg = tile_style[s]
        rx_t = gx0 + x0 * cell
        ry_t = gy0 + y0 * cell
        rw_t = s * cell
        p.append(f'    <rect x="{rx_t}" y="{ry_t}" width="{rw_t}" height="{rw_t}" fill="{bg}" stroke="{bd}" stroke-width="1.8"/>')
        fsize = 13.5 if s >= 6 else (11 if s >= 4 else (9.5 if s >= 2 else 8.5))
        lbl = f"{s}×{s}" if s >= 3 else str(s)
        p.append(f'    <text x="{rx_t + rw_t / 2:.1f}" y="{ry_t + rw_t / 2 + fsize * 0.35:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="{fsize}" font-weight="700" fill="{fg}">{lbl}</text>')

    # Outer bounding box dimension ticks (W=15 top/bottom, H=14 left)
    p.append(f'    <text x="{gx0 + box_w * cell / 2:.1f}" y="{gy0 + box_h * cell + 20}" text-anchor="middle" font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="#334155">Width W = 15  (Xᵢ ∈ [0 .. W−i])</text>')
    p.append(f'    <text x="{gx0 - 18}" y="{gy0 + box_h * cell / 2:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="#334155" transform="rotate(-90 {gx0 - 18} {gy0 + box_h * cell / 2:.1f})">Height H = 14</text>')

    # Symmetry callout at right edge of box (ample padding)
    scx = gx0 + box_w * cell + 12
    scw = lx + lw - scx - 12
    p.append(f'    <rect x="{scx}" y="{gy0}" width="{scw}" height="126" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 18}" font-size="9.0" font-weight="700" fill="#0f172a">Symmetry</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 35}" font-family="{FONT_MONO}" font-size="7.8" fill="#1e3a8a">2·X₈ ≤ W−8</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 49}" font-family="{FONT_MONO}" font-size="7.8" fill="#1e3a8a">2·Y₈ ≤ H−8</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 69}" font-size="8.4" fill="#475569">Pins 8×8</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 83}" font-size="8.4" fill="#475569">into top-</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 97}" font-size="8.4" fill="#475569">left quad</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 113}" font-size="8.4" font-weight="700" fill="#047857">(4× cut)</text>')

    # Legend for empty slack
    p.append(f'    <rect x="{scx}" y="{gy0 + 136}" width="{scw}" height="78" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <rect x="{scx + 8}" y="{gy0 + 147}" width="12" height="12" fill="#e2e8f0" stroke="#94a3b8" stroke-width="0.9"/>')
    p.append(f'    <text x="{scx + 25}" y="{gy0 + 156.5}" font-size="8.4" font-weight="700" fill="#475569">Empty</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 175}" font-size="8.4" fill="#475569">6 cells</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 189}" font-size="8.4" fill="#475569">2.86% slack</text>')
    p.append(f'    <text x="{scx + 8}" y="{gy0 + 204}" font-size="8.2" font-weight="700" fill="#0f172a">Min area!</text>')

    # ================= RIGHT PANEL: GLOBAL CONSTRAINTS & 10-INSTANCE LADDER =================
    rx, ry, rw = 492, 78, 424

    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="142" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#0f172a">2. Picat-SAT Global Packing Constraints</text>')
    cboxes = [
        ("2D non-overlap: diffn([[Xᵢ, Yᵢ, i, i] : i ∈ 1..n])", "Disjunctive separation Xᵢ+i≤Xⱼ ∨ Xⱼ+j≤Xᵢ ∨ Yᵢ+i≤Yⱼ ∨ Yⱼ+j≤Yᵢ", "#eff6ff", "#93c5fd", "#1e3a8a"),
        ("Redundant 1D projections: cumulative(X, S, S, H) &amp; (Y, S, S, W)", "Time-indexed resource-capacity PB bounds at every strip x, y", "#f5f3ff", "#c4b5fd", "#5b21b6"),
        ("Area-sufficient infeasible traps (W·H ≥ Σ i² yet UNSAT)", "e.g., n=12 in 25×26 (exact area 650) & n=17 in 40×45 (area 1,800)", "#fef2f2", "#fca5a5", "#991b1b"),
    ]
    for idx, (t1, t2, bg, bd, fg) in enumerate(cboxes):
        yy = ry + 31 + idx * 35
        p.append(f'    <rect x="{rx + 14}" y="{yy}" width="{rw - 28}" height="29" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 12.5}" font-size="9.0" font-weight="700" fill="{fg}">{t1}</text>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 24}" font-size="8.2" fill="#475569">{esc(t2)}</text>')

    ty = ry + 154
    th = 250
    p.append(f'    <rect x="{rx}" y="{ty}" width="{rw}" height="{th}" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ty + 21}" font-size="12.2" font-weight="700" fill="#0f172a">3. Tight Bounding-Box Ladder (n = 8 .. 17)</text>')

    hdrs = ["Instance", "Box", "Area (Slack)", "Verdict", "Vars / Cls"]
    xs = [rx + 14, rx + 146, rx + 226, rx + 302, rx + 410]
    p.append(f'    <rect x="{rx + 10}" y="{ty + 30}" width="{rw - 20}" height="20" rx="4" fill="#f1f5f9"/>')
    for idx, (h, x) in enumerate(zip(hdrs, xs)):
        anc = "end" if idx == 4 else ("middle" if idx in (1, 2, 3) else "start")
        p.append(f'    <text x="{x}" y="{ty + 43.5}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{h}</text>')

    rows = [
        ("rpack_n8_13x16", "13×16", "208 (+4)", "UNSAT", "1.2k / 6.9k"),
        ("rpack_n8_14x15", "14×15", "210 (+6)", "SAT", "1.2k / 6.8k"),
        ("rpack_n10_20x20", "20×20", "400 (+15)", "UNSAT", "2.3k / 13.8k"),
        ("rpack_n10_15x27", "15×27", "405 (+20)", "SAT", "2.1k / 12.9k"),
        ("rpack_n12_25x26", "25×26", "650 (+0)", "UNSAT", "3.6k / 22.9k"),
        ("rpack_n12_23x29", "23×29", "667 (+17)", "SAT", "3.5k / 22.9k"),
        ("rpack_n14_31x33", "31×33", "1023 (+8)", "UNSAT", "6.1k / 34.6k"),
        ("rpack_n14_23x45", "23×45", "1035 (+20)", "SAT", "6.2k / 34.9k"),
        ("rpack_n17_40x45", "40×45", "1800 (+15)", "UNSAT", "11.3k / 60.5k"),
        ("rpack_n17_41x44", "41×44", "1804 (+19)", "SAT", "11.3k / 60.6k"),
    ]
    for r_i, (nm, bx, ar, verd, vc) in enumerate(rows):
        yy = ty + 64 + r_i * 18.2
        if r_i % 2 == 1:
            p.append(f'    <rect x="{rx + 10}" y="{yy - 12}" width="{rw - 20}" height="17.5" fill="#f8fafc"/>')
        vcol = "#047857" if verd == "SAT" else "#b91c1c"
        p.append(f'    <text x="{xs[0]}" y="{yy}" font-family="{FONT_MONO}" font-size="8.6" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{xs[1]}" y="{yy}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.5" fill="#334155">{bx}</text>')
        p.append(f'    <text x="{xs[2]}" y="{yy}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.4" fill="#475569">{ar}</text>')
        p.append(f'    <text x="{xs[3]}" y="{yy}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{vcol}">{verd}</text>')
        p.append(f'    <text x="{xs[4]}" y="{yy}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.4" fill="#475569">{vc}</text>')

    p.append("  </g>")
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
