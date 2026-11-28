#!/usr/bin/env python3
"""Generate bespoke illustrative SVG (`diagram.svg`) for `picat-numberlink`
(Planar Numberlink Disjoint Paths via Picat-SAT `numberlink_b.pi`).

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
    # Verified exact solution of INo=2 (Afis / Janko Arukone 001, 5x5, 4 pairs):
    grid = [
        [3, 3, 3, 3, 2],
        [4, 1, 2, 3, 2],
        [4, 1, 2, 3, 2],
        [4, 1, 2, 2, 2],
        [4, 1, 1, 1, 1],
    ]
    paths = {
        1: [(1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)],
        2: [(0, 4), (1, 4), (2, 4), (3, 4), (3, 3), (3, 2), (2, 2), (1, 2)],
        3: [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3)],
        4: [(1, 0), (2, 0), (3, 0), (4, 0)],
    }
    colors = {
        1: ("#2563eb", "#dbeafe", "#1e3a8a"),
        2: ("#dc2626", "#fee2e2", "#991b1b"),
        3: ("#059669", "#d1fae5", "#065f46"),
        4: ("#d97706", "#fef3c7", "#92400e"),
    }

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-label="Picat-SAT Planar Numberlink Disjoint Paths and Espresso PB Degree Constraints">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Planar Numberlink Disjoint Paths (picat-numberlink)</text>',
        '    <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Picat 3.9#12 SAT compilation of Neng-Fa Zhou′s numberlink_b.pi (MPL-2.0) · '
        'Espresso-minimized Boolean degree PB constraints</text>',
        '    <rect x="780" y="18" width="136" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">6 SAT · 3 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: SOLVED 5x5 NUMBERLINK + TOPOLOGICAL SWAP INSET =================
    lx, ly, lw, lh = 24, 78, 444, 404
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 23}" font-size="13" font-weight="700" fill="#0f172a">1. Solved 5×5 Numberlink (numberlink_5x5_p4, INo=2)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 39}" font-size="10.2" fill="#475569">4 vertex-disjoint paths partition all 25 grid cells (deg=1 ends, deg=2 interior)</text>')

    gx0, gy0, cell = lx + 30, ly + 56, 46
    for r in range(5):
        for c in range(5):
            col_id = grid[r][c]
            _, bg, _ = colors[col_id]
            cx, cy = gx0 + c * cell, gy0 + r * cell
            p.append(f'    <rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" fill="{bg}" stroke="#cbd5e1" stroke-width="1.2"/>')

    # Draw thick rounded polylines for each colored path
    for pid, seq in paths.items():
        stroke, _, _ = colors[pid]
        pts_s = " ".join(f"{gx0 + c * cell + cell / 2:.1f},{gy0 + r * cell + cell / 2:.1f}" for r, c in seq)
        p.append(f'    <polyline points="{pts_s}" fill="none" stroke="{stroke}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity="0.88"/>')
        # Terminal circles at endpoints
        for r, c in (seq[0], seq[-1]):
            cx = gx0 + c * cell + cell / 2.0
            cy = gy0 + r * cell + cell / 2.0
            p.append(f'    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="{stroke}" stroke="#ffffff" stroke-width="2.2"/>')
            p.append(f'    <text x="{cx:.1f}" y="{cy + 4.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" font-weight="700" fill="#ffffff">{pid}</text>')

    # Side callout: Local Degree Rules + Jordan-Curve UNSAT Swap
    sx0 = gx0 + 5 * cell + 16
    sw = lx + lw - sx0 - 14
    p.append(f'    <rect x="{sx0}" y="{gy0}" width="{sw}" height="122" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{sx0 + 10}" y="{gy0 + 18}" font-size="9.8" font-weight="700" fill="#0f172a">Local Degree Rules</text>')
    rnotes = [
        ("Every cell (r,c):", "#475569", False),
        ("  Σₚ M[p,r,c] = 1", "#1e3a8a", True),
        ("Terminal cell p:", "#475569", False),
        ("  Σ_{nb} M[p,nb] = 1", "#047857", True),
        ("Interior cell p:", "#475569", False),
        ("  M[p] ⇒ Σ_{nb} = 2", "#7c3aed", True),
    ]
    for i, (txt, col, mono) in enumerate(rnotes):
        p.append(
            f'    <text x="{sx0 + 10}" y="{gy0 + 36 + i * 14}" '
            f'{"font-family=\"" + FONT_MONO + "\" " if mono else ""}'
            f'font-size="8.6" font-weight="{"700" if mono else "400"}" fill="{col}">{esc(txt)}</text>'
        )

    # Topological Crossing UNSAT inset below Local Degree Rules
    iy = gy0 + 132
    p.append(f'    <rect x="{sx0}" y="{iy}" width="{sw}" height="98" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>')
    p.append(f'    <text x="{sx0 + 10}" y="{iy + 17}" font-size="9.5" font-weight="700" fill="#991b1b">UNSAT Swap Obstruction</text>')
    p.append(f'    <line x1="{sx0 + 26}" y1="{iy + 32}" x2="{sx0 + sw - 26}" y2="{iy + 64}" stroke="#2563eb" stroke-width="2.5"/>')
    p.append(f'    <line x1="{sx0 + sw - 26}" y1="{iy + 32}" x2="{sx0 + 26}" y2="{iy + 64}" stroke="#dc2626" stroke-width="2.5"/>')
    p.append(f'    <circle cx="{sx0 + sw / 2:.1f}" cy="{iy + 48}" r="7" fill="#ffffff" stroke="#b91c1c" stroke-width="1.6"/>')
    p.append(f'    <text x="{sx0 + sw / 2:.1f}" y="{iy + 51.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b91c1c">×</text>')
    p.append(f'    <text x="{sx0 + sw / 2:.1f}" y="{iy + 80}" text-anchor="middle" font-size="8.3" fill="#7f1d1d">Swapping two terminals forces</text>')
    p.append(f'    <text x="{sx0 + sw / 2:.1f}" y="{iy + 91}" text-anchor="middle" font-size="8.3" fill="#7f1d1d">non-planar crossing ⇒ UNSAT</text>')

    # Bottom Espresso PB summary box
    by = ly + 304
    p.append(f'    <rect x="{lx + 14}" y="{by}" width="{lw - 28}" height="86" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 24}" y="{by + 18}" font-size="10.2" font-weight="700" fill="#0f172a">Berkeley Espresso PB Minimization in Picat-SAT:</text>')
    p.append(f'    <text x="{lx + 24}" y="{by + 36}" font-size="9.2" fill="#334155">• Each cell has ≤ 4 orthogonal neighbors, so Picat synthesizes minimal prime-implicant</text>')
    p.append(f'    <text x="{lx + 32}" y="{by + 51}" font-size="9.2" fill="#334155">CNF covers via embedded Berkeley Espresso for M[p,r,c] ⇒ Σ(Neibs) = 2 (0 aux vars).</text>')
    p.append(f'    <text x="{lx + 24}" y="{by + 68}" font-size="9.2" fill="#334155">• Scales from 60 vars (5×5, 4 pairs) up to 73,920 vars / 500k clauses (42×25, 62 pairs).</text>')

    # ================= RIGHT PANEL: 9-INSTANCE LADDER =================
    rx, ry, rw = 484, 78, 432
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="404" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 23}" font-size="12.5" font-weight="700" fill="#0f172a">2. Curated 9-Instance Numberlink Suite (5×5 .. 42×25)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 39}" font-size="9.8" fill="#475569">Authentic Janko/Afis/Wikipedia/Wired/Picat grids + 3 crossing UNSAT swaps</text>')

    hdrs = ["Instance", "Grid", "Pairs", "Verdict", "Vars / Cls"]
    xs = [rx + 14, rx + 196, rx + 250, rx + 306, rx + 418]
    p.append(f'    <rect x="{rx + 10}" y="{ry + 50}" width="{rw - 20}" height="22" rx="4" fill="#f1f5f9"/>')
    for idx, (h, x) in enumerate(zip(hdrs, xs)):
        anc = "end" if idx == 4 else ("middle" if idx in (1, 2, 3) else "start")
        p.append(f'    <text x="{x}" y="{ry + 65}" text-anchor="{anc}" font-size="8.9" font-weight="700" fill="#334155">{h}</text>')

    rows = [
        ("numberlink_5x5_p4", "5×5", "4", "SAT", "60 / 309"),
        ("numberlink_7x7_p5", "7×7", "5", "SAT", "195 / 1.2k"),
        ("numberlink_10x10_p8", "10×10", "8", "SAT", "672 / 5.3k"),
        ("numberlink_10x10_p8_swap", "10×10", "8", "UNSAT", "672 / 5.3k"),
        ("numberlink_12x12_p10", "12×12", "10", "SAT", "1.2k / 11.7k"),
        ("numberlink_12x12_p10_swap", "12×12", "10", "UNSAT", "1.2k / 11.7k"),
        ("numberlink_15x15_p12", "15×15", "12", "SAT", "2.6k / 22.2k"),
        ("numberlink_15x15_p12_swap", "15×15", "12", "UNSAT", "2.6k / 22.2k"),
        ("numberlink_42x25_p62", "42×25", "62", "SAT", "73.9k / 500k"),
    ]
    for r_i, (nm, gr, pr, verd, vc) in enumerate(rows):
        yy = ry + 92 + r_i * 26.5
        if r_i % 2 == 1:
            p.append(f'    <rect x="{rx + 10}" y="{yy - 16}" width="{rw - 20}" height="24" fill="#f8fafc"/>')
        vcol = "#047857" if verd == "SAT" else "#b91c1c"
        p.append(f'    <text x="{xs[0]}" y="{yy}" font-family="{FONT_MONO}" font-size="8.6" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{xs[1]}" y="{yy}" text-anchor="middle" font-size="8.8" fill="#334155">{gr}</text>')
        p.append(f'    <text x="{xs[2]}" y="{yy}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.8" fill="#0f172a">{pr}</text>')
        p.append(f'    <text x="{xs[3]}" y="{yy}" text-anchor="middle" font-size="8.8" font-weight="700" fill="{vcol}">{verd}</text>')
        p.append(f'    <text x="{xs[4]}" y="{yy}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.6" fill="#475569">{vc}</text>')

    # Note at bottom of right panel
    ny = ry + 340
    p.append(f'    <rect x="{rx + 14}" y="{ny}" width="{rw - 28}" height="50" rx="7" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
    p.append(f'    <text x="{rx + 24}" y="{ny + 19}" font-size="9.4" font-weight="700" fill="#1e3a8a">Challenge Frontier: numberlink_42x25_p62 (INo=4)</text>')
    p.append(f'    <text x="{rx + 24}" y="{ny + 35}" font-size="8.8" fill="#334155">1,050 cells × 62 colors (73,920 vars, 500,345 cls) — genuine 60 s stress test!</text>')

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
