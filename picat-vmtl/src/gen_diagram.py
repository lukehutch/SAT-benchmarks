#!/usr/bin/env python3
"""Generate bespoke illustrative SVG (`diagram.svg`) for `picat-vmtl`
(Vertex Magic Total Labeling on K_n via Picat-SAT `vmtl.pi`).

Standalone Python 3 stdlib only. Writes `../diagram.svg` and validates XML.
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"
FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_svg() -> str:
    W, H = 940, 504
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-label="Picat-SAT Vertex Magic Total Labeling on Complete Graphs K_n">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        # Title bar
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Vertex Magic Total Labeling on Complete Graphs (picat-vmtl)</text>',
        '    <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Picat 3.9#12 SAT compilation of Neng-Fa Zhou′s vmtl.pi (MPL-2.0) · '
        'all_different over n + n(n−1)/2 labels + n simultaneous log-encoded vertex sums</text>',
        '    <rect x="780" y="18" width="136" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">6 SAT · 4 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: VERIFIED K_4 VMTL (K=20) =================
    lx, ly, lw, lh = 24, 78, 434, 404
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 23}" font-size="13" font-weight="700" fill="#0f172a">1. Verified VMTL Witness on K₄ (Magic Constant K = 20)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 39}" font-size="10.2" fill="#475569">Bijection V ∪ E → {{1, …, 10}}; every vertex + incident edges sums to 20</text>')

    # K4 node coordinates (clean square with well-separated diagonals)
    nodes = [
        ("v₁", 9, lx + 110, ly + 104, "#dbeafe", "#2563eb", "#1e3a8a"),
        ("v₂", 8, lx + 324, ly + 104, "#dbeafe", "#2563eb", "#1e3a8a"),
        ("v₃", 10, lx + 324, ly + 266, "#dbeafe", "#2563eb", "#1e3a8a"),
        ("v₄", 3, lx + 110, ly + 266, "#dbeafe", "#2563eb", "#1e3a8a"),
    ]
    # Edges: (i, j, label, frac_along_segment_for_badge, offset_x, offset_y)
    edges = [
        (0, 1, 5, 0.50, 0, -14),   # e12 = 5
        (1, 2, 1, 0.50, 18, 0),    # e23 = 1
        (2, 3, 7, 0.50, 0, 15),    # e34 = 7
        (3, 0, 4, 0.50, -18, 0),   # e14 = 4
        (0, 2, 2, 0.30, 8, -14),   # e13 = 2 (diagonal, offset away from center)
        (1, 3, 6, 0.30, -8, -14),  # e24 = 6 (diagonal, offset away from center)
    ]
    for i, j, lbl, t, ox, oy in edges:
        x1, y1 = nodes[i][2], nodes[i][3]
        x2, y2 = nodes[j][2], nodes[j][3]
        is_diag = (i == 0 and j == 2) or (i == 1 and j == 3)
        stroke = "#64748b" if not is_diag else "#94a3b8"
        sw = "2.2" if not is_diag else "1.8"
        dash = ' stroke-dasharray="5,3"' if is_diag else ""
        p.append(f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        mx = x1 + t * (x2 - x1) + ox
        my = y1 + t * (y2 - y1) + oy
        p.append(f'    <rect x="{mx - 13:.1f}" y="{my - 11:.1f}" width="26" height="22" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>')
        p.append(f'    <text x="{mx:.1f}" y="{my + 4:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="11" font-weight="700" fill="#b45309">{lbl}</text>')

    for nm, val, nx, ny, fill, st, tc in nodes:
        p.append(f'    <circle cx="{nx}" cy="{ny}" r="24" fill="{fill}" stroke="{st}" stroke-width="2"/>')
        p.append(f'    <text x="{nx}" y="{ny - 3}" text-anchor="middle" font-size="9.5" font-weight="600" fill="#475569">{nm}</text>')
        p.append(f'    <text x="{nx}" y="{ny + 12}" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" font-weight="700" fill="{tc}">{val}</text>')

    # Legend + Exact Vertex Sum Verification Box
    by = ly + 306
    p.append(f'    <rect x="{lx + 14}" y="{by}" width="{lw - 28}" height="84" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 26}" y="{by + 18}" font-size="10.2" font-weight="700" fill="#0f172a">Exact Vertex-Sum Equations (All 4 Vertices = K = 20):</text>')
    eqs = [
        ("v₁:  9 + (5 + 2 + 4) = 20", lx + 26, by + 38),
        ("v₂:  8 + (5 + 1 + 6) = 20", lx + 224, by + 38),
        ("v₃: 10 + (2 + 1 + 7) = 20", lx + 26, by + 56),
        ("v₄:  3 + (4 + 6 + 7) = 20", lx + 224, by + 56),
    ]
    for txt, ex, ey in eqs:
        p.append(f'    <text x="{ex}" y="{ey}" font-family="{FONT_MONO}" font-size="9.6" font-weight="600" fill="#047857">{esc(txt)}</text>')
    p.append(f'    <text x="{lx + 26}" y="{by + 74}" font-size="9.2" fill="#475569">'
             'Labels used: V = {3, 8, 9, 10}, E = {1, 2, 4, 5, 6, 7}  ⇒  exact bijection onto {1..10}</text>')

    # ================= RIGHT PANEL: DOUBLE-COUNTING BOUND & LADDER =================
    rx, ry, rw = 474, 78, 442

    # Card 2: Global Double-Counting Identity & CDCL Blind Spot
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="154" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 22}" font-size="12.4" font-weight="700" fill="#0f172a">2. Arithmetic Feasibility Bound &amp; CDCL Hardness</text>')
    p.append(f'    <rect x="{rx + 14}" y="{ry + 32}" width="{rw - 28}" height="46" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>')
    p.append(f'    <text x="{rx + rw / 2:.1f}" y="{ry + 50}" text-anchor="middle" font-family="{FONT_MONO}" font-size="10.2" font-weight="700" fill="#991b1b">n·K + Σᵢ Vᵢ = M(M+1),   M = n(n+1)/2</text>')
    p.append(f'    <text x="{rx + rw / 2:.1f}" y="{ry + 68}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.6" font-weight="600" fill="#7f1d1d">K_min(n) = ⌈n(n²+3)/4⌉  ≤  K  ≤  ⌊n(n+1)²/4⌋ = K_max(n)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 96}" font-size="9.8" fill="#334155">• Any K &lt; K_min(n) (e.g., K₅ at K=34, K₆ at K=58, K₁₀ at K=257) is</text>')
    p.append(f'    <text x="{rx + 22}" y="{ry + 111}" font-size="9.8" fill="#334155">mathematically UNSAT by global double-counting of edge labels.</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 128}" font-size="9.8" fill="#334155">• Picat-SAT compiles all_different + n log-bit adder trees separately,</text>')
    p.append(f'    <text x="{rx + 22}" y="{ry + 143}" font-size="9.8" fill="#334155">hiding the global sum identity and creating 490-var CDCL killers.</text>')

    # Card 3: 10-Instance Scaling Ladder Table
    ty = ry + 166
    th = 238
    p.append(f'    <rect x="{rx}" y="{ty}" width="{rw}" height="{th}" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ty + 21}" font-size="12.2" font-weight="700" fill="#0f172a">3. Curated 10-Instance Ladder (K₄ .. K₁₀)</text>')

    hdrs = ["Instance", "K_n", "K", "Bound", "Verdict", "Vars / Cls"]
    xs = [rx + 14, rx + 128, rx + 162, rx + 212, rx + 292, rx + 428]
    p.append(f'    <rect x="{rx + 10}" y="{ty + 30}" width="{rw - 20}" height="20" rx="4" fill="#f1f5f9"/>')
    for idx, (h, x) in enumerate(zip(hdrs, xs)):
        anc = "end" if idx == 5 else ("middle" if idx in (1, 2, 4) else "start")
        p.append(f'    <text x="{x}" y="{ty + 43.5}" text-anchor="{anc}" font-size="8.8" font-weight="700" fill="#334155">{h}</text>')

    rows = [
        ("vmtl_n4_k19", "K₄", "19", "[20,23]*", "UNSAT", "204 / 1.6k"),
        ("vmtl_n5_k34", "K₅", "34", "K_min−1", "UNSAT", "490 / 3.5k"),
        ("vmtl_n5_k35", "K₅", "35", "K_min", "SAT", "475 / 3.5k"),
        ("vmtl_n6_k58", "K₆", "58", "K_min−1", "UNSAT", "870 / 7.9k"),
        ("vmtl_n6_k59", "K₆", "59", "K_min", "SAT", "852 / 7.9k"),
        ("vmtl_n7_k111", "K₇", "111", "near K_max", "SAT", "1.8k / 11.6k"),
        ("vmtl_n8_k148", "K₈", "148", "mid [134,162]", "SAT", "2.9k / 20.6k"),
        ("vmtl_n9_k207", "K₉", "207", "mid [189,225]", "SAT", "4.4k / 30.3k"),
        ("vmtl_n10_k257", "K₁₀", "257", "K_min−1", "UNSAT", "6.1k / 43.7k"),
        ("vmtl_n10_k280", "K₁₀", "280", "mid [258,302]", "SAT", "6.1k / 43.9k"),
    ]
    for r_i, (nm, kn, kv, bnd, verd, vc) in enumerate(rows):
        yy = ty + 64 + r_i * 17.5
        if r_i % 2 == 1:
            p.append(f'    <rect x="{rx + 10}" y="{yy - 12}" width="{rw - 20}" height="17" fill="#f8fafc"/>')
        vcol = "#047857" if verd == "SAT" else "#b91c1c"
        p.append(f'    <text x="{xs[0]}" y="{yy}" font-family="{FONT_MONO}" font-size="8.6" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{xs[1]}" y="{yy}" text-anchor="middle" font-size="8.7" fill="#334155">{kn}</text>')
        p.append(f'    <text x="{xs[2]}" y="{yy}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" fill="#0f172a">{kv}</text>')
        p.append(f'    <text x="{xs[3]}" y="{yy}" font-size="8.4" fill="#475569">{esc(bnd)}</text>')
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
