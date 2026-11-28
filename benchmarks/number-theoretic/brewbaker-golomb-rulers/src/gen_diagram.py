#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-golomb-rulers.

Visualizes exact optimal Golomb rulers G(5) = 11 ({0, 1, 4, 9, 11}) with all 10 distinct
pairwise distance arcs, G(8) = 34 ({0, 1, 4, 9, 15, 22, 32, 34}) with its complete 28/34
difference comb, the sequential prefix-counter + pairwise-AMO encoding, and OEIS A003022 ladder.
"""
from __future__ import annotations

from itertools import combinations
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

OGR5 = [0, 1, 4, 9, 11]
OGR8 = [0, 1, 4, 9, 15, 22, 32, 34]


def verify_ogr(marks: list[int], expected_len: int) -> list[int]:
    assert marks[0] == 0 and marks[-1] == expected_len
    diffs = [b - a for a, b in combinations(marks, 2)]
    assert len(diffs) == len(set(diffs)), f"Duplicate difference in {marks}!"
    return sorted(diffs)


def build_svg() -> str:
    d5 = verify_ogr(OGR5, 11)
    d8 = verify_ogr(OGR8, 34)

    W, H = 960, 520
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Optimal Golomb Ruler Synthesis (brewbaker-golomb-rulers)">',
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Optimal Golomb Ruler Synthesis (brewbaker-golomb-rulers)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'OEIS A003022: M integer marks on 0..L with all C(M,2) pairwise distances distinct '
        '(Chad Brewbaker, sat_challenges.py golomb)</text>',
        '  <rect x="748" y="16" width="186" height="24" rx="12" fill="#fffbeb" stroke="#d97706" stroke-width="1.2"/>',
        '  <text x="841" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#b45309">'
        '12 Instances &#x00B7; 6 SAT / 6 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Section 1A: OGR-5 {0, 1, 4, 9, 11} with pairwise distance arcs
    y1 = 78
    p.append(f'  <rect x="24" y="{y1}" width="446" height="190" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="24" y="{y1}" width="446" height="28" rx="10" fill="#d97706"/>')
    p.append(f'  <rect x="24" y="{y1+16}" width="446" height="12" fill="#d97706"/>')
    p.append(f'  <text x="38" y="{y1+19}" font-size="11.5" font-weight="700" fill="#ffffff">'
             '1A. Optimal 5-Mark Ruler: G(5) = 11 (Chad\'s Pair: L=10 UNSAT / L=11 SAT)</text>')

    rx0, rx1, ry = 54, 440, y1 + 126
    scale5 = (rx1 - rx0) / 11.0
    # Pairwise arcs above ruler
    arc_colors = ["#2563eb", "#0d9488", "#7c3aed", "#dc2626", "#d97706", "#0284c7", "#4f46e5", "#059669", "#db2777", "#334155"]
    pairs5 = sorted(combinations(OGR5, 2), key=lambda pr: pr[1] - pr[0])
    for idx, (a, b) in enumerate(pairs5):
        xa, xb = rx0 + a * scale5, rx0 + b * scale5
        dist = b - a
        h_arc = 14 + dist * 6.8
        xm = (xa + xb) / 2.0
        col = arc_colors[idx % len(arc_colors)]
        p.append(f'  <path d="M {xa:.1f} {ry-4:.1f} Q {xm:.1f} {ry-4-h_arc:.1f} {xb:.1f} {ry-4:.1f}" '
                 f'fill="none" stroke="{col}" stroke-width="1.5" stroke-opacity="0.82"/>')

    # Wooden/amber ruler bar
    p.append(f'  <rect x="{rx0-8}" y="{ry-2}" width="{rx1-rx0+16}" height="22" rx="4" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>')
    mark_set5 = set(OGR5)
    for t in range(12):
        tx = rx0 + t * scale5
        if t in mark_set5:
            p.append(f'  <line x1="{tx:.1f}" y1="{ry-4}" x2="{tx:.1f}" y2="{ry+20}" stroke="#b45309" stroke-width="2.6"/>')
            p.append(f'  <circle cx="{tx:.1f}" cy="{ry-4}" r="3.6" fill="#b45309"/>')
            p.append(f'  <text x="{tx:.1f}" y="{ry+33}" text-anchor="middle" font-family="{MONO}" font-size="10.2" font-weight="700" fill="#92400e">{t}</text>')
        else:
            p.append(f'  <line x1="{tx:.1f}" y1="{ry+10}" x2="{tx:.1f}" y2="{ry+20}" stroke="#d97706" stroke-width="1" stroke-opacity="0.5"/>')
            p.append(f'  <text x="{tx:.1f}" y="{ry+32}" text-anchor="middle" font-family="{MONO}" font-size="8.4" fill="#94a3b8">{t}</text>')

    p.append(f'  <text x="38" y="{y1+178}" font-family="{MONO}" font-size="9.0" fill="#334155">'
             f'10 unique distances: {d5} (only d=6 absent)</text>')

    # Section 1B: OGR-8 {0, 1, 4, 9, 15, 22, 32, 34} + Difference Comb
    xr = 484
    wr = 452
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="190" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="28" rx="10" fill="#0f766e"/>')
    p.append(f'  <rect x="{xr}" y="{y1+16}" width="{wr}" height="12" fill="#0f766e"/>')
    p.append(f'  <text x="{xr+14}" y="{y1+19}" font-size="11.5" font-weight="700" fill="#ffffff">'
             '1B. Optimal 8-Mark Ruler: G(8) = 34 (28 / 34 Differences Realized)</text>')

    gx0, gx1, gy = xr + 20, xr + wr - 20, y1 + 64
    scale8 = (gx1 - gx0) / 34.0
    p.append(f'  <rect x="{gx0-6}" y="{gy}" width="{gx1-gx0+12}" height="20" rx="4" fill="#ccfbf1" stroke="#0f766e" stroke-width="1.2"/>')
    mset8 = set(OGR8)
    for t in range(35):
        tx = gx0 + t * scale8
        if t in mset8:
            p.append(f'  <line x1="{tx:.1f}" y1="{gy-3}" x2="{tx:.1f}" y2="{gy+20}" stroke="#0f766e" stroke-width="2.4"/>')
            p.append(f'  <circle cx="{tx:.1f}" cy="{gy-3}" r="3.2" fill="#0f766e"/>')
            lbl_y = gy - 10 if t not in (1, 32) else gy + 32
            p.append(f'  <text x="{tx:.1f}" y="{lbl_y}" text-anchor="middle" font-family="{MONO}" font-size="9.0" font-weight="700" fill="#0f766e">{t}</text>')
        else:
            p.append(f'  <line x1="{tx:.1f}" y1="{gy+12}" x2="{tx:.1f}" y2="{gy+20}" stroke="#0f766e" stroke-width="0.8" stroke-opacity="0.4"/>')

    # Difference occupancy strip (d = 1..34)
    p.append(f'  <text x="{xr+16}" y="{y1+120}" font-size="9.8" font-weight="700" fill="#334155">'
             'Pairwise Distance Comb d &#x2208; &#x007B;1..34&#x007D; (green = realized once, gray = unused):</text>')
    d8_set = set(d8)
    cw = (wr - 32) / 34.0
    for d in range(1, 35):
        cx = xr + 16 + (d - 1) * cw
        hit = d in d8_set
        bg = "#16a34a" if hit else "#e2e8f0"
        fg = "#ffffff" if hit else "#64748b"
        p.append(f'  <rect x="{cx+0.6:.1f}" y="{y1+129}" width="{cw-1.2:.1f}" height="24" rx="2.5" fill="{bg}"/>')
        if cw >= 11:
            p.append(f'  <text x="{cx+cw/2:.1f}" y="{y1+144}" text-anchor="middle" font-family="{MONO}" font-size="7.4" font-weight="700" fill="{fg}">{d}</text>')
    missing8 = [d for d in range(1, 35) if d not in d8_set]
    m_str = ",".join(str(x) for x in OGR8)
    abs_str = ",".join(str(x) for x in missing8)
    p.append(f'  <text x="{xr+16}" y="{y1+174}" font-family="{MONO}" font-size="8.5" fill="#475569">'
             f'Marks: {{{m_str}}} | Absent (6): {{{abs_str}}}</text>')

    # Section 2: SAT Encoding Architecture
    y2 = 282
    p.append(f'  <rect x="24" y="{y2}" width="912" height="90" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+21}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '2. SAT Encoding Structure (sat_challenges.py golomb M L)</text>')
    enc_cards = [
        (38, 286, "#eff6ff", "#2563eb", "#1d4ed8", "Tick Variables + Translation Break", "mark[0..L] boolean ticks; unit clause mark[0]=1 pins origin"),
        (337, 286, "#faf5ff", "#7c3aed", "#6d28d9", "Exact-M Sequential Prefix Counter", "ge[j] = at least j marks in prefix; asserts ge[M] &amp; !ge[M+1]"),
        (636, 286, "#fffbeb", "#d97706", "#b45309", "Distinct Pairwise Distances (AMO)", "For each d=1..L: at_most_one({mark[i] &amp; mark[i+d]})"),
    ]
    for ex, ew, bg, bd, fg, t1, t2 in enc_cards:
        p.append(f'  <rect x="{ex}" y="{y2+31}" width="{ew}" height="48" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1.1"/>')
        p.append(f'  <text x="{ex+ew/2:.1f}" y="{y2+49}" text-anchor="middle" font-size="10" font-weight="700" fill="{fg}">{t1}</text>')
        p.append(f'  <text x="{ex+ew/2:.1f}" y="{y2+67}" text-anchor="middle" font-size="8.6" fill="#334155">{t2}</text>')

    # Section 3: 12-Instance OEIS A003022 Optimality Ladder (M = 5..10)
    y3 = 384
    p.append(f'  <rect x="24" y="{y3}" width="912" height="120" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y3+20}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '3. Six Exact OEIS A003022 Optimality Brackets: L = G(M)&#x2212;1 UNSAT vs L = G(M) SAT (12 Instances)</text>')

    ladder = [
        ("M = 5", "G(5) = 11", "L=10 / 11", "191-224 vars", "545-640 cls", "#0f766e", "#f0fdfa"),
        ("M = 6", "G(6) = 17", "L=16 / 17", "440-487 vars", "1.3K-1.4K cls", "#0284c7", "#f0f9ff"),
        ("M = 7", "G(7) = 25", "L=24 / 25", "907-972 vars", "2.6K-2.8K cls", "#2563eb", "#eff6ff"),
        ("M = 8", "G(8) = 34", "L=33 / 34", "1.6K-1.7K vars", "4.7K-5.0K cls", "#7c3aed", "#faf5ff"),
        ("M = 9", "G(9) = 44", "L=43 / 44", "2.6K-2.7K vars", "7.7K-8.0K cls", "#d97706", "#fffbeb"),
        ("M = 10", "G(10) = 55", "L=54 / 55", "4.0K-4.1K vars", "11.8K-12.2K cls", "#be123c", "#fff1f2"),
    ]
    lw = 140
    lgap = 8.8
    for i, (t1, t2, t3, t4, t5, sc, bg) in enumerate(ladder):
        lx = 38 + i * (lw + lgap)
        p.append(f'  <rect x="{lx:.1f}" y="{y3+32}" width="{lw}" height="74" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.2"/>')
        p.append(f'  <text x="{lx+lw/2:.1f}" y="{y3+48}" text-anchor="middle" font-family="{MONO}" font-size="9.8" font-weight="700" fill="{sc}">{t1}</text>')
        p.append(f'  <text x="{lx+lw/2:.1f}" y="{y3+64}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#0f172a">{t2}</text>')
        p.append(f'  <text x="{lx+lw/2:.1f}" y="{y3+79}" text-anchor="middle" font-family="{MONO}" font-size="8.6" fill="#334155">{t3}</text>')
        p.append(f'  <text x="{lx+lw/2:.1f}" y="{y3+95}" text-anchor="middle" font-size="7.8" fill="#475569">{t4} | {t5}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
