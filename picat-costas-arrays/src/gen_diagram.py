#!/usr/bin/env python3
"""Generate bespoke illustrative SVG (`diagram.svg`) for `picat-costas-arrays`
(Costas Arrays via Picat-SAT `costas_array.pi`).

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
    # Verified Welch order-6 Costas array: 3^k mod 7 for k = 0..5 -> [1, 3, 2, 6, 4, 5]
    perm = [1, 3, 2, 6, 4, 5]
    n = len(perm)
    tri = [[perm[j] - perm[j - d] for j in range(d, n)] for d in range(1, n)]
    for row in tri:
        assert len(row) == len(set(row)) and 0 not in row

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-label="Picat-SAT Costas Array Permutation Matrix and Signed Difference Triangle">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Costas Arrays — Permutation &amp; Signed Difference Triangle (picat-costas-arrays)</text>',
        '    <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Picat 3.9#12 SAT compilation of costas_array.pi (MIT, H. Kjellerstrand / B. O′Sullivan) · '
        'Sign-magnitude signed diffs + row all_different</text>',
        '    <rect x="780" y="18" width="136" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">9 SAT · N = 8..16</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: 6x6 PERMUTATION MATRIX + DIFFERENCE TRIANGLE =================
    lx, ly, lw, lh = 24, 78, 466, 404
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 23}" font-size="13" font-weight="700" fill="#0f172a">1. Verified Order-6 Costas Array π = [1, 3, 2, 6, 4, 5]</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 39}" font-size="10.2" fill="#475569">All 15 displacement vectors (Δcol, Δrow) between dots are pairwise distinct</text>')

    # 6x6 Grid on left sub-area
    gx0, gy0, cell = lx + 42, ly + 56, 30
    for r in range(n):
        for c in range(n):
            cx = gx0 + c * cell
            cy = gy0 + r * cell
            fill = "#eff6ff" if (r + c) % 2 == 0 else "#ffffff"
            p.append(f'    <rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" fill="{fill}" stroke="#cbd5e1" stroke-width="1"/>')
        # Row label (value 6 down to 1 so y increases upward)
        val_lbl = n - r
        p.append(f'    <text x="{gx0 - 10}" y="{gy0 + r * cell + 19}" text-anchor="end" font-family="{FONT_MONO}" font-size="9.5" fill="#475569">{val_lbl}</text>')
    for c in range(n):
        p.append(f'    <text x="{gx0 + c * cell + cell / 2:.1f}" y="{gy0 + n * cell + 16}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.5" fill="#475569">{c + 1}</text>')

    # Plot dots and highlight 2 distinct displacement vectors (d=1)
    pts = [(gx0 + c * cell + cell / 2.0, gy0 + (n - perm[c]) * cell + cell / 2.0) for c in range(n)]
    # Highlight d=1 vectors (col1->col2: +2, col2->col3: -1, col3->col4: +4)
    vec_cols = ["#2563eb", "#dc2626", "#059669", "#dc2626", "#2563eb"]
    for i in range(n - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        p.append(f'    <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{vec_cols[i]}" stroke-width="1.8" stroke-dasharray="3,2"/>')
    for c, (px, py) in enumerate(pts):
        p.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="8.5" fill="#1d4ed8" stroke="#ffffff" stroke-width="1.8"/>')
        p.append(f'    <text x="{px:.1f}" y="{py + 3.2:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" font-weight="700" fill="#ffffff">{perm[c]}</text>')

    # Side note next to matrix
    nx0 = gx0 + n * cell + 16
    p.append(f'    <rect x="{nx0}" y="{gy0}" width="{lx + lw - nx0 - 14}" height="{n * cell}" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{nx0 + 10}" y="{gy0 + 18}" font-size="10" font-weight="700" fill="#0f172a">Radar / Sonar Property</text>')
    notes = [
        "Every shift (Δx, Δy) ≠ (0,0)",
        "causes at most 1 coincidence",
        "between π and its shifted copy.",
        "",
        "Symmetry breaking:",
        "  π[1] < π[n]  (1 < 5)",
        "",
        "Diamond redundancy:",
        "  D[k−2,l−1] + D[k,l]",
        "  = D[k−1,l−1] + D[k−1,l]",
    ]
    for idx, line in enumerate(notes):
        is_code = line.startswith("  ")
        p.append(
            f'    <text x="{nx0 + 10}" y="{gy0 + 36 + idx * 14}" '
            f'{"font-family=\"" + FONT_MONO + "\" " if is_code else ""}'
            f'font-size="8.8" fill="{"#1e3a8a" if is_code else "#475569"}">{esc(line)}</text>'
        )

    # Signed Difference Triangle below the matrix
    ty0 = ly + 260
    p.append(f'    <rect x="{lx + 14}" y="{ty0}" width="{lw - 28}" height="130" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 24}" y="{ty0 + 17}" font-size="10.2" font-weight="700" fill="#0f172a">Signed Difference Triangle (Each Row Strictly Distinct via all_different):</text>')

    cx_mid = lx + lw / 2.0 + 18
    for r_i, row in enumerate(tri):
        d = r_i + 1
        ry_row = ty0 + 34 + r_i * 20
        p.append(f'    <text x="{lx + 24}" y="{ry_row + 4}" font-family="{FONT_MONO}" font-size="8.6" font-weight="700" fill="#475569">d={d}:</text>')
        start_x = cx_mid - (len(row) * 44) / 2.0
        for c_i, val in enumerate(row):
            bx = start_x + c_i * 44
            bg = "#dbeafe" if val > 0 else "#ffe4e6"
            bd = "#2563eb" if val > 0 else "#e11d48"
            fg = "#1e3a8a" if val > 0 else "#9f1239"
            sval = f"+{val}" if val > 0 else f"−{abs(val)}"
            p.append(f'    <rect x="{bx:.1f}" y="{ry_row - 9:.1f}" width="36" height="16" rx="4" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
            p.append(f'    <text x="{bx + 18:.1f}" y="{ry_row + 2.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.8" font-weight="700" fill="{fg}">{sval}</text>')

    # ================= RIGHT PANEL: SIGN-MAGNITUDE ENCODING & N=8..16 LADDER =================
    rx, ry, rw = 506, 78, 410

    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="138" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#0f172a">2. Picat-SAT Sign-Magnitude Compilation</text>')
    items = [
        ("Signed differences D[i,j] ∈ [−(n−1) .. +(n−1)] \\ {0}", "Compiled as (sign bit s, log magnitude |D|) with guarded adders", "#eff6ff", "#93c5fd", "#1e3a8a"),
        ("n−1 triangular all_different rows + diamond sums", "Couples Espresso prime-implicant clauses with Chen-AMO", "#fef2f2", "#fda4af", "#9f1239"),
        ("Power-of-2 bit-width step at N=8 vs N=9", "N=8 spans [−7..7] (3-bit mag) vs N=9 [−8..8] (4-bit mag)", "#fffbeb", "#fcd34d", "#92400e"),
    ]
    for idx, (t1, t2, bg, bd, fg) in enumerate(items):
        yy = ry + 31 + idx * 34
        p.append(f'    <rect x="{rx + 14}" y="{yy}" width="{rw - 28}" height="28" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 12}" font-size="9.1" font-weight="700" fill="{fg}">{esc(t1)}</text>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 23.5}" font-size="8.3" fill="#475569">{esc(t2)}</text>')

    # Scaling table N=8..16
    ty = ry + 150
    th = 254
    p.append(f'    <rect x="{rx}" y="{ty}" width="{rw}" height="{th}" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ty + 21}" font-size="12.2" font-weight="700" fill="#0f172a">3. Scaling Ladder costas_n8 .. costas_n16 (OEIS A008404)</text>')

    hdrs = ["Instance", "N", "Diffs", "OEIS A008404", "Verdict", "Vars / Cls"]
    xs = [rx + 14, rx + 106, rx + 144, rx + 218, rx + 292, rx + 396]
    p.append(f'    <rect x="{rx + 10}" y="{ty + 30}" width="{rw - 20}" height="20" rx="4" fill="#f1f5f9"/>')
    for idx, (h, x) in enumerate(zip(hdrs, xs)):
        anc = "end" if idx in (3, 5) else ("middle" if idx in (1, 2, 4) else "start")
        p.append(f'    <text x="{x}" y="{ty + 43.5}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{h}</text>')

    rows = [
        ("costas_n8", "8", "28", "444", "SAT", "808 / 35.6k"),
        ("costas_n9", "9", "36", "760", "SAT", "1.5k / 21.3k"),
        ("costas_n10", "10", "45", "2,160", "SAT", "2.0k / 28.9k"),
        ("costas_n11", "11", "55", "4,368", "SAT", "2.6k / 38.0k"),
        ("costas_n12", "12", "66", "7,852", "SAT", "3.3k / 48.8k"),
        ("costas_n13", "13", "78", "12,828", "SAT", "4.5k / 59.4k"),
        ("costas_n14", "14", "91", "17,252", "SAT", "5.7k / 71.6k"),
        ("costas_n15", "15", "105", "19,612", "SAT", "7.0k / 86.2k"),
        ("costas_n16", "16", "120", "21,104", "SAT", "8.7k / 104.7k"),
    ]
    for r_i, (nm, nv, dv, oeis, verd, vc) in enumerate(rows):
        yy = ty + 66 + r_i * 20
        if r_i % 2 == 1:
            p.append(f'    <rect x="{rx + 10}" y="{yy - 13}" width="{rw - 20}" height="19" fill="#f8fafc"/>')
        p.append(f'    <text x="{xs[0]}" y="{yy}" font-family="{FONT_MONO}" font-size="8.8" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{xs[1]}" y="{yy}" text-anchor="middle" font-size="8.8" fill="#334155">{nv}</text>')
        p.append(f'    <text x="{xs[2]}" y="{yy}" text-anchor="middle" font-size="8.6" fill="#475569">{dv}</text>')
        p.append(f'    <text x="{xs[3]}" y="{yy}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.6" fill="#1d4ed8">{oeis}</text>')
        p.append(f'    <text x="{xs[4]}" y="{yy}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#047857">{verd}</text>')
        p.append(f'    <text x="{xs[5]}" y="{yy}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.5" fill="#475569">{vc}</text>')

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
