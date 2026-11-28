#!/usr/bin/env python3
"""Generate bespoke illustrative SVG (`diagram.svg`) for `picat-golomb-rulers`
(Optimal Golomb Rulers via Picat-SAT `golomb_ruler.pi`).

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
    marks = [0, 1, 4, 10, 12, 17]
    diffs = sorted(marks[j] - marks[i] for i in range(len(marks)) for j in range(i + 1, len(marks)))
    assert len(diffs) == 15 and len(set(diffs)) == 15

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-label="Picat-SAT Optimal Golomb Rulers Difference Comb and Optimality Frontier">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Optimal Golomb Rulers — Optimality Frontier (picat-golomb-rulers)</text>',
        '    <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Picat 3.9#12 SAT compilation of golomb_ruler.pi (MIT, H. Kjellerstrand &amp; N.-F. Zhou) · '
        'Log-encoded differences + Chen-AMO all_different</text>',
        '    <rect x="780" y="18" width="136" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">5 SAT · 5 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: G_6 RULER + DIFFERENCE COMB =================
    lx, ly, lw, lh = 24, 78, 488, 404
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 23}" font-size="13" font-weight="700" fill="#0f172a">1. Optimal 6-Mark Golomb Ruler G₆ (L* = 17, 15 Distinct Spans)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 39}" font-size="10.2" fill="#475569">Marks a = [0, 1, 4, 10, 12, 17] · Reflection breaking: a₂−a₁ = 1 &lt; 5 = a₆−a₅</text>')

    # Ruler body
    rx0, rx1, ry_bar = lx + 34, lx + lw - 34, ly + 178
    unit = (rx1 - rx0) / 17.0
    p.append(f'    <rect x="{rx0 - 8:.1f}" y="{ry_bar}" width="{rx1 - rx0 + 16:.1f}" height="34" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.6"/>')
    for u in range(18):
        ux = rx0 + u * unit
        is_m = u in marks
        th = 16 if is_m else 8
        col = "#1d4ed8" if is_m else "#b45309"
        sw = "2.6" if is_m else "1"
        p.append(f'    <line x1="{ux:.1f}" y1="{ry_bar}" x2="{ux:.1f}" y2="{ry_bar + th}" stroke="{col}" stroke-width="{sw}"/>')
        if is_m:
            p.append(f'    <circle cx="{ux:.1f}" cy="{ry_bar}" r="5.5" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"/>')
            p.append(f'    <text x="{ux:.1f}" y="{ry_bar + 28}" text-anchor="middle" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" fill="#1e3a8a">{u}</text>')
        elif u in (2, 6, 8, 14, 15):
            p.append(f'    <text x="{ux:.1f}" y="{ry_bar + 27}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8" fill="#92400e">{u}</text>')

    # Upper difference arcs (adjacent & medium spans) + lower arcs (long spans)
    palette = ["#2563eb", "#059669", "#7c3aed", "#d97706", "#dc2626"]
    # Draw clean tiered horizontal span brackets above the ruler for adjacent + 2-hop pairs, and below for 3..5-hop pairs
    pairs_by_hop = {h: [] for h in range(1, 6)}
    for i in range(len(marks)):
        for j in range(i + 1, len(marks)):
            pairs_by_hop[j - i].append((marks[i], marks[j], marks[j] - marks[i]))

    # Above ruler: hops 1, 2, 3 (3 clean tiers)
    tier_y_above = {1: ry_bar - 22, 2: ry_bar - 54, 3: ry_bar - 88}
    for hop in (1, 2, 3):
        ty = tier_y_above[hop]
        col = palette[hop - 1]
        for idx_p, (a, b, d) in enumerate(pairs_by_hop[hop]):
            x1 = rx0 + a * unit
            x2 = rx0 + b * unit
            yy = ty - (idx_p % 2) * 14 if hop > 1 else ty
            p.append(f'    <path d="M {x1:.1f} {ry_bar - 6} L {x1:.1f} {yy:.1f} L {x2:.1f} {yy:.1f} L {x2:.1f} {ry_bar - 6}" '
                     f'fill="none" stroke="{col}" stroke-width="1.35" opacity="0.88"/>')
            mx = (x1 + x2) / 2.0
            p.append(f'    <rect x="{mx - 9:.1f}" y="{yy - 8:.1f}" width="18" height="14" rx="4" fill="#ffffff" stroke="{col}" stroke-width="1"/>')
            p.append(f'    <text x="{mx:.1f}" y="{yy + 2.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" font-weight="700" fill="{col}">{d}</text>')

    # Below ruler: hops 4, 5
    for hop, base_y, col in ((4, ry_bar + 54, palette[3]), (5, ry_bar + 84, palette[4])):
        for idx_p, (a, b, d) in enumerate(pairs_by_hop[hop]):
            x1 = rx0 + a * unit
            x2 = rx0 + b * unit
            yy = base_y + idx_p * 14
            p.append(f'    <path d="M {x1:.1f} {ry_bar + 35} L {x1:.1f} {yy:.1f} L {x2:.1f} {yy:.1f} L {x2:.1f} {ry_bar + 35}" '
                     f'fill="none" stroke="{col}" stroke-width="1.35" opacity="0.9"/>')
            mx = (x1 + x2) / 2.0
            p.append(f'    <rect x="{mx - 10:.1f}" y="{yy - 7:.1f}" width="20" height="14" rx="4" fill="#ffffff" stroke="{col}" stroke-width="1"/>')
            p.append(f'    <text x="{mx:.1f}" y="{yy + 3:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" font-weight="700" fill="{col}">{d}</text>')

    # Difference spectrum bar (1..17) at bottom of left panel
    sy = ly + 318
    p.append(f'    <rect x="{lx + 14}" y="{sy}" width="{lw - 28}" height="72" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 24}" y="{sy + 18}" font-size="10" font-weight="700" fill="#0f172a">Pairwise Difference Coverage in {{1 .. 17}} (15 Measured, 2 Gaps: 14, 15):</text>')
    bw = (lw - 56) / 17.0
    for d in range(1, 18):
        bx = lx + 28 + (d - 1) * bw
        present = d in diffs
        fill = "#dcfce7" if present else "#f1f5f9"
        st = "#16a34a" if present else "#cbd5e1"
        tc = "#166534" if present else "#94a3b8"
        p.append(f'    <rect x="{bx + 1:.1f}" y="{sy + 28}" width="{bw - 2:.1f}" height="24" rx="4" fill="{fill}" stroke="{st}" stroke-width="1"/>')
        p.append(f'    <text x="{bx + bw / 2:.1f}" y="{sy + 44}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" font-weight="700" fill="{tc}">{d}</text>')
    p.append(f'    <text x="{lx + 24}" y="{sy + 65}" font-size="9" fill="#475569">At L = 16 (L*−1), no 6 marks fit 15 distinct spans into {{1..16}} ⇒ UNSAT</text>')

    # ================= RIGHT PANEL: ENCODING + FRONTIER TABLE =================
    rx, ry, rw = 528, 78, 388

    # Card 2: Picat-SAT Encoding Architecture
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="142" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#0f172a">2. Picat-SAT Compilation Pipeline</text>')
    steps = [
        ("Log-encoded marks Xᵢ ∈ [0..L]", "⌈log₂(L+1)⌉ bits/mark, X₁=0, X_M=L, Xᵢ₋₁ < Xᵢ", "#eff6ff", "#93c5fd", "#1e3a8a"),
        ("M(M−1)/2 pairwise subtractors", "Dᵢⱼ = Xⱼ − Xᵢ ∈ [1..L] via Espresso adders", "#f5f3ff", "#c4b5fd", "#5b21b6"),
        ("Global all_different(Diffs)", "Domain channeling + Chen 2-product AMO", "#ecfdf5", "#6ee7b7", "#065f46"),
    ]
    for idx, (t1, t2, bg, bd, fg) in enumerate(steps):
        yy = ry + 32 + idx * 35
        p.append(f'    <rect x="{rx + 14}" y="{yy}" width="{rw - 28}" height="29" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 12.5}" font-size="9.3" font-weight="700" fill="{fg}">{esc(t1)}</text>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 24}" font-size="8.5" fill="#475569">{esc(t2)}</text>')

    # Card 3: 10-Instance Optimality Frontier M=6..10
    ty = ry + 154
    th = 250
    p.append(f'    <rect x="{rx}" y="{ty}" width="{rw}" height="{th}" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ty + 21}" font-size="12.2" font-weight="700" fill="#0f172a">3. Exact L*−1 / L* Frontier (OEIS A003022)</text>')

    hdrs = ["Instance", "M", "L", "Diffs", "Verdict", "Vars / Cls"]
    xs = [rx + 14, rx + 126, rx + 154, rx + 190, rx + 248, rx + 374]
    p.append(f'    <rect x="{rx + 10}" y="{ty + 30}" width="{rw - 20}" height="20" rx="4" fill="#f1f5f9"/>')
    for idx, (h, x) in enumerate(zip(hdrs, xs)):
        anc = "end" if idx == 5 else ("middle" if idx in (1, 2, 3, 4) else "start")
        p.append(f'    <text x="{x}" y="{ty + 43.5}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{h}</text>')

    rows = [
        ("golomb_m6_l16", "6", "16", "15", "UNSAT", "260 / 2.2k"),
        ("golomb_m6_l17", "6", "17", "15", "SAT", "276 / 2.4k"),
        ("golomb_m7_l24", "7", "24", "21", "UNSAT", "604 / 5.9k"),
        ("golomb_m7_l25", "7", "25", "21", "SAT", "622 / 6.3k"),
        ("golomb_m8_l33", "8", "33", "28", "UNSAT", "1.4k / 9.9k"),
        ("golomb_m8_l34", "8", "34", "28", "SAT", "1.5k / 10.3k"),
        ("golomb_m9_l43", "9", "43", "36", "UNSAT", "2.4k / 17.9k"),
        ("golomb_m9_l44", "9", "44", "36", "SAT", "2.5k / 18.3k"),
        ("golomb_m10_l54", "10", "54", "45", "UNSAT", "3.8k / 27.8k"),
        ("golomb_m10_l55", "10", "55", "45", "SAT", "3.8k / 28.2k"),
    ]
    for r_i, (nm, mv, lv, dv, verd, vc) in enumerate(rows):
        yy = ty + 64 + r_i * 18.2
        if r_i % 2 == 1:
            p.append(f'    <rect x="{rx + 10}" y="{yy - 12}" width="{rw - 20}" height="17.5" fill="#f8fafc"/>')
        vcol = "#047857" if verd == "SAT" else "#b91c1c"
        p.append(f'    <text x="{xs[0]}" y="{yy}" font-family="{FONT_MONO}" font-size="8.6" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{xs[1]}" y="{yy}" text-anchor="middle" font-size="8.6" fill="#334155">{mv}</text>')
        p.append(f'    <text x="{xs[2]}" y="{yy}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" fill="#0f172a">{lv}</text>')
        p.append(f'    <text x="{xs[3]}" y="{yy}" text-anchor="middle" font-size="8.5" fill="#475569">{dv}</text>')
        p.append(f'    <text x="{xs[4]}" y="{yy}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{vcol}">{verd}</text>')
        p.append(f'    <text x="{xs[5]}" y="{yy}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.4" fill="#475569">{vc}</text>')

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
