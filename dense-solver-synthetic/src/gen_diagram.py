#!/usr/bin/env python3
"""Generate illustrative SVG diagram for dense-solver-synthetic.

Illustrates the two core synthetic cardinality & tiling families in the suite:
  1. Mutilated Chessboard domino-tiling UNSAT (opposite corners removed -> 32 black vs 30 white)
  2. Pigeonhole Principle (PHP^n_{n-1}) across 8 cardinality encodings (pairwise -> totalizer)

Writes ../diagram.svg deterministically using stdlib only.
"""
from __future__ import annotations

from pathlib import Path


def build_svg() -> str:
    W, H = 940, 490
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.8px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .badge-u { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #b91c1c; }
      .lbl { font: 700 10.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #ffffff; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Synthetic Cardinality &amp; Tiling Benchmarks (dense-solver-synthetic)</text>')
    out.append('  <text x="26" y="54" class="sub">20 structured cardinality UNSAT/SAT CNFs: Mutilated Chessboard domino tiling (N = 12, 16, 32) &amp; 8-encoding PHP suite</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # LEFT PANEL: 8x8 Mutilated Chessboard with partial domino tiling & parity obstruction
    lx, ly, lw, lh = 24, 80, 412, 388
    out.append(f'  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{lx+16}" y="{ly+24}" class="h3">1. Mutilated Chessboard Domino Tiling</text>')
    out.append(f'  <rect x="{lx+lw-96}" y="{ly+10}" width="82" height="21" rx="10.5" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>')
    out.append(f'  <text x="{lx+lw-55}" y="{ly+24}" text-anchor="middle" class="badge-u">UNSAT</text>')
    out.append(f'  <text x="{lx+16}" y="{ly+42}" class="body">Opposite light corners (0,0) &amp; (N−1,N−1) removed</text>')

    N = 8
    cell = 32
    bx, by = lx + 78, ly + 56
    out.append(f'  <rect x="{bx-2}" y="{by-2}" width="{N*cell+4}" height="{N*cell+4}" rx="4" fill="#334155"/>')

    for r in range(N):
        for c in range(N):
            x, y = bx + c * cell, by + r * cell
            if (r, c) in ((0, 0), (N - 1, N - 1)):
                # Removed corner
                out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>')
                out.append(f'  <line x1="{x+7}" y1="{y+7}" x2="{x+cell-7}" y2="{y+cell-7}" stroke="#dc2626" stroke-width="2.2"/>')
                out.append(f'  <line x1="{x+cell-7}" y1="{y+7}" x2="{x+7}" y2="{y+cell-7}" stroke="#dc2626" stroke-width="2.2"/>')
            else:
                fill = "#cbd5e1" if (r + c) % 2 == 1 else "#ffffff"
                out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#94a3b8" stroke-width="0.6"/>')

    # Draw illustrative 1x2 dominoes covering pairs of (Light, Dark) cells
    dominoes = [
        ((0, 1), (0, 2), "#2563eb"),
        ((0, 3), (0, 4), "#2563eb"),
        ((0, 5), (0, 6), "#2563eb"),
        ((0, 7), (1, 7), "#059669"),
        ((1, 0), (2, 0), "#059669"),
        ((1, 1), (1, 2), "#2563eb"),
        ((2, 1), (2, 2), "#2563eb"),
        ((3, 0), (4, 0), "#059669"),
    ]
    for (r1, c1), (r2, c2), col in dominoes:
        x1 = bx + min(c1, c2) * cell + 3
        y1 = by + min(r1, r2) * cell + 3
        w = (abs(c2 - c1) + 1) * cell - 6
        h = (abs(r2 - r1) + 1) * cell - 6
        out.append(f'  <rect x="{x1}" y="{y1}" width="{w}" height="{h}" rx="5" fill="{col}" fill-opacity="0.24" stroke="{col}" stroke-width="2"/>')

    # Highlight two leftover unmatched dark squares
    for rr, cc in ((7, 0), (6, 7)):
        x, y = bx + cc * cell, by + rr * cell
        out.append(f'  <rect x="{x+3}" y="{y+3}" width="{cell-6}" height="{cell-6}" rx="4" fill="#dc2626" fill-opacity="0.22" stroke="#dc2626" stroke-width="2" stroke-dasharray="3,2"/>')

    out.append(f'  <text x="{lx+16}" y="{ly+334}" class="mono">Every 1×2 domino covers 1 Light + 1 Dark square</text>')
    out.append(f'  <text x="{lx+16}" y="{ly+353}" class="body">Remaining squares: 32 Dark ≠ 30 Light → 2 Dark unmatched!</text>')
    out.append(f'  <text x="{lx+16}" y="{ly+372}" class="body">Suite scales to chessboard12, 16, 32 (hard for CDCL; 2 ms for card/GA).</text>')

    # RIGHT PANEL: Multi-Encoding PHP Cardinality Family
    rx, ry, rw, rh = 452, 80, 464, 388
    out.append(f'  <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="{ry+24}" class="h3">2. Multi-Encoding Pigeonhole (PHPⁿₙ₋₁)</text>')
    out.append(f'  <text x="{rx+16}" y="{ry+42}" class="body">Same global counting contradiction across 8 At-Most-One CNF encodings</text>')

    # Compact visual PHP^5_4 bipartite diagram at top of right card
    p_x, h_x = rx + 62, rx + 216
    for i in range(5):
        py = ry + 68 + i * 24
        for j in range(4):
            hy = ry + 80 + j * 24
            col = "#cbd5e1"
            sw = "1.0"
            if i < 4 and i == j:
                col, sw = "#2563eb", "2.0"
            elif i == 4 and j == 3:
                col, sw = "#dc2626", "2.2"
            out.append(f'  <line x1="{p_x+12}" y1="{py}" x2="{h_x-12}" y2="{hy}" stroke="{col}" stroke-width="{sw}"/>')
    for i in range(5):
        py = ry + 68 + i * 24
        col = "#dc2626" if i == 4 else "#2563eb"
        out.append(f'  <circle cx="{p_x}" cy="{py}" r="9.5" fill="{col}" stroke="#ffffff" stroke-width="1.5"/>')
        out.append(f'  <text x="{p_x}" y="{py+3.5}" text-anchor="middle" class="lbl">p{i+1}</text>')
    for j in range(4):
        hy = ry + 80 + j * 24
        col = "#dc2626" if j == 3 else "#059669"
        out.append(f'  <rect x="{h_x-10}" y="{hy-9.5}" width="20" height="19" rx="4" fill="{col}" stroke="#ffffff" stroke-width="1.5"/>')
        out.append(f'  <text x="{h_x}" y="{hy+3.5}" text-anchor="middle" class="lbl">h{j+1}</text>')

    # Callout beside bipartite graph
    out.append(f'  <rect x="{rx+246}" y="{ry+62}" width="202" height="114" rx="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>')
    out.append(f'  <text x="{rx+258}" y="{ry+82}" class="mono">∀i: ∨ⱼ xᵢ,ⱼ  (ALO)</text>')
    out.append(f'  <text x="{rx+258}" y="{ry+101}" class="mono">∀j: ∑ᵢ xᵢ,ⱼ ≤ 1 (AMO)</text>')
    out.append(f'  <text x="{rx+258}" y="{ry+124}" class="body">n+1 pigeons, n holes</text>')
    out.append(f'  <text x="{rx+258}" y="{ry+142}" class="body">• SAT: PHP⁸₈ (2 files)</text>')
    out.append(f'  <text x="{rx+258}" y="{ry+160}" class="body">• UNSAT: up to PHP⁶⁵₆₄</text>')

    # 8 AMO encoding comparison grid
    out.append(f'  <text x="{rx+16}" y="{ry+204}" class="h3">8 Cardinality Encodings Benchmarked (php9x8..php65x64)</text>')
    encs = [
        ("Pairwise / Func", "O(n²) binary clauses · 0 aux", "#2563eb"),
        ("Sinz Sequential", "O(n) ladder counter · linear", "#059669"),
        ("Bitwise", "O(n log n) binary ID bits", "#7c3aed"),
        ("Ladder", "O(n) valid-state chain", "#0284c7"),
        ("Totalizer / Mod", "Binary adder merge tree", "#d97706"),
        ("Sort / Card Net", "Odd-even merge network", "#dc2626"),
    ]
    for idx, (ename, edesc, ecol) in enumerate(encs):
        col_i = idx % 2
        row_i = idx // 2
        ex = rx + 16 + col_i * 220
        ey = ry + 216 + row_i * 52
        out.append(f'  <rect x="{ex}" y="{ey}" width="210" height="44" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
        out.append(f'  <rect x="{ex}" y="{ey}" width="5" height="44" rx="2.5" fill="{ecol}"/>')
        out.append(f'  <text x="{ex+13}" y="{ey+18}" class="mono">{ename}</text>')
        out.append(f'  <text x="{ex+13}" y="{ey+34}" class="body">{edesc}</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
