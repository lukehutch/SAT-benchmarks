#!/usr/bin/env python3
"""Generate illustrative SVG diagram for knights-tour-obstacles.

Directly parses the real 12x12 obstacle layout from:
  cnf-orig/knights_12x12_d15_obs16_s12150144_sat.cnf.xz
verifies the 128-square closed knight's tour (every move is a valid L-jump,
visits all 128 unoccupied squares exactly once, avoids all 16 obstacles, and
closes back to the start square), and writes ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path
from xml.sax.saxutils import escape

# Verified closed Hamiltonian knight's tour for knights_12x12_d15_obs16_s12150144_sat
# (solved from cnf-orig/knights_12x12_d15_obs16_s12150144_sat.cnf.xz via Frobenius)
VERIFIED_TOUR_12X12: list[tuple[int, int]] = [
    (0, 0), (1, 2), (0, 4), (2, 5), (4, 6), (5, 8), (7, 9), (8, 11),
    (10, 10), (11, 8), (10, 6), (11, 4), (9, 3), (8, 1), (10, 0), (11, 2),
    (10, 4), (11, 6), (9, 7), (10, 5), (11, 3), (10, 1), (8, 0), (6, 1),
    (7, 3), (6, 5), (4, 4), (3, 6), (2, 4), (0, 3), (1, 1), (2, 3),
    (3, 5), (4, 7), (5, 5), (6, 7), (7, 5), (8, 7), (6, 8), (7, 6),
    (8, 4), (9, 6), (11, 7), (10, 9), (11, 11), (9, 10), (11, 9), (10, 7),
    (11, 5), (9, 4), (10, 2), (11, 0), (9, 1), (10, 3), (11, 1), (9, 0),
    (7, 1), (5, 0), (3, 1), (4, 3), (6, 2), (7, 0), (5, 1), (7, 2),
    (6, 4), (8, 5), (7, 7), (5, 6), (4, 8), (6, 9), (7, 11), (5, 10),
    (3, 11), (2, 9), (4, 10), (6, 11), (5, 9), (3, 8), (1, 7), (0, 5),
    (2, 6), (1, 8), (0, 10), (2, 11), (1, 9), (0, 11), (2, 10), (0, 9),
    (1, 11), (3, 10), (2, 8), (0, 7), (1, 5), (3, 4), (2, 2), (4, 1),
    (2, 0), (3, 2), (4, 0), (5, 2), (3, 3), (4, 5), (5, 3), (7, 4),
    (8, 6), (9, 8), (8, 10), (10, 11), (9, 9), (11, 10), (10, 8), (8, 9),
    (9, 11), (7, 10), (5, 11), (4, 9), (5, 7), (7, 8), (6, 10), (4, 11),
    (3, 9), (1, 10), (0, 8), (2, 7), (0, 6), (1, 4), (0, 2), (2, 1),
]


def parse_board_from_cnf(cnf_xz: Path) -> tuple[int, int, set[tuple[int, int]], int, int]:
    """Read board ASCII comments and DIMACS p-line from the real .cnf.xz instance."""
    rows: list[str] = []
    n_vars, n_clauses = 0, 0
    with lzma.open(cnf_xz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("c board "):
                rows.append(line.split(":", 1)[1].strip())
            elif line.startswith("p cnf"):
                parts = line.split()
                n_vars, n_clauses = int(parts[2]), int(parts[3])
                break
    r_cnt = len(rows)
    c_cnt = len(rows[0])
    obstacles = {(r, c) for r, row in enumerate(rows) for c, ch in enumerate(row) if ch == "#"}
    return r_cnt, c_cnt, obstacles, n_vars, n_clauses


def verify_tour(rows: int, cols: int, obstacles: set[tuple[int, int]], tour: list[tuple[int, int]]) -> None:
    expected_free = {(r, c) for r in range(rows) for c in range(cols) if (r, c) not in obstacles}
    assert len(tour) == len(expected_free), f"tour len {len(tour)} != free {len(expected_free)}"
    assert set(tour) == expected_free, "tour does not visit exact set of unoccupied squares"
    for i in range(len(tour)):
        r1, c1 = tour[i]
        r2, c2 = tour[(i + 1) % len(tour)]
        assert sorted((abs(r1 - r2), abs(c1 - c2))) == [1, 2], f"invalid knight move {tour[i]} -> {tour[(i+1)%len(tour)]}"


def lerp_color(t: float) -> str:
    """Smooth 4-stop perceptual palette along the closed cycle t in [0, 1]."""
    stops = [
        (0.00, (37, 99, 235)),   # royal blue
        (0.33, (13, 148, 136)),  # teal
        (0.66, (217, 119, 6)),   # amber
        (1.00, (124, 58, 237)),  # violet
    ]
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            r = int(round(c0[0] + u * (c1[0] - c0[0])))
            g = int(round(c0[1] + u * (c1[1] - c0[1])))
            b = int(round(c0[2] + u * (c1[2] - c0[2])))
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#7c3aed"


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    cnf_xz = col_dir / "cnf-orig" / "knights_12x12_d15_obs16_s12150144_sat.cnf.xz"
    rows, cols, obstacles, n_vars, n_clauses = parse_board_from_cnf(cnf_xz)
    verify_tour(rows, cols, obstacles, VERIFIED_TOUR_12X12)

    free_white = sum(1 for r in range(rows) for c in range(cols) if (r, c) not in obstacles and (r + c) % 2 == 0)
    free_black = sum(1 for r in range(rows) for c in range(cols) if (r, c) not in obstacles and (r + c) % 2 == 1)

    W, H = 940, 540
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <linearGradient id="tourGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="33%" stop-color="#0d9488"/>
      <stop offset="66%" stop-color="#d97706"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.8px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .coord { font: 600 10.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #64748b; }
      .badge { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
      .tiny { font: 600 10px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
    </style>
  </defs>""")

    # Explicit light canvas card (crisp on GitHub Light & Dark mode)
    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')

    # Header
    out.append('  <text x="26" y="34" class="title">Obstacle Knight\'s Tour — Solved Real Instance (12×12 Board)</text>')
    out.append(f'  <text x="26" y="54" class="sub">Parsed directly from cnf-orig/knights_12x12_d15_obs16_s12150144_sat.cnf.xz · 16 obstacles, 128-square verified closed tour</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Board geometry on left
    cell = 34
    bx, by = 50, 86
    bw, bh = cols * cell, rows * cell

    # Outer board frame
    out.append(f'  <rect x="{bx-3}" y="{by-3}" width="{bw+6}" height="{bh+6}" rx="6" fill="#334155"/>')

    # Squares + obstacle blocks
    for r in range(rows):
        for c in range(cols):
            x = bx + c * cell
            y = by + r * cell
            is_dark = (r + c) % 2 == 1
            if (r, c) in obstacles:
                # Blocked obstacle square
                out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="#fecaca" stroke="#ef4444" stroke-width="0.9"/>')
                # Clean solid obstacle block icon inside square
                pad = 6
                out.append(f'  <rect x="{x+pad}" y="{y+pad}" width="{cell-2*pad}" height="{cell-2*pad}" rx="4" fill="#dc2626"/>')
                out.append(f'  <line x1="{x+pad+5}" y1="{y+pad+5}" x2="{x+cell-pad-5}" y2="{y+cell-pad-5}" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
                out.append(f'  <line x1="{x+cell-pad-5}" y1="{y+pad+5}" x2="{x+pad+5}" y2="{y+cell-pad-5}" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>')
            else:
                sq_fill = "#e2e8f0" if is_dark else "#f8fafc"
                out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{sq_fill}" stroke="#cbd5e1" stroke-width="0.5"/>')

    # Coordinate labels around board
    for c in range(cols):
        cx = bx + c * cell + cell / 2
        out.append(f'  <text x="{cx:.1f}" y="{by + bh + 18}" text-anchor="middle" class="coord">{chr(97 + c)}</text>')
    for r in range(rows):
        cy = by + r * cell + cell / 2 + 3.5
        out.append(f'  <text x="{bx - 12}" y="{cy:.1f}" text-anchor="end" class="coord">{rows - r}</text>')

    # Draw verified closed knight's tour with gradient progression
    n_steps = len(VERIFIED_TOUR_12X12)
    def center(sq: tuple[int, int]) -> tuple[float, float]:
        return (bx + sq[1] * cell + cell / 2.0, by + sq[0] * cell + cell / 2.0)

    # Subtle halo under tour for clean readability over dark/light squares
    pts_str = " ".join(f"{center(sq)[0]:.1f},{center(sq)[1]:.1f}" for sq in VERIFIED_TOUR_12X12)
    out.append(f'  <polygon points="{pts_str}" fill="none" stroke="#ffffff" stroke-width="4.2" stroke-linejoin="round" opacity="0.72"/>')

    for i in range(n_steps):
        x1, y1 = center(VERIFIED_TOUR_12X12[i])
        x2, y2 = center(VERIFIED_TOUR_12X12[(i + 1) % n_steps])
        col = lerp_color(i / n_steps)
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.35" stroke-linecap="round"/>')

    # Visited vertices dots + Start square (0,0) beacon
    for i, sq in enumerate(VERIFIED_TOUR_12X12):
        x, y = center(sq)
        if i == 0:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="9.5" fill="#1d4ed8" stroke="#ffffff" stroke-width="2.2"/>')
            out.append(f'  <text x="{x:.1f}" y="{y+3.5:.1f}" text-anchor="middle" style="font:700 10px sans-serif;fill:#ffffff;">0</text>')
        else:
            col = lerp_color(i / n_steps)
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="2.7" fill="{col}" stroke="#ffffff" stroke-width="0.9"/>')

    # Legend strip under board
    out.append(f'  <rect x="{bx}" y="{by+bh+25}" width="126" height="9" rx="4.5" fill="url(#tourGrad)"/>')
    out.append(f'  <text x="{bx+134}" y="{by+bh+33}" class="tiny">Closed 128-jump cycle (step 0 → 127 → 0)</text>')

    # Right explanatory column
    rx, rw = 486, 430

    # Card 1: Real Instance Summary
    out.append(f'  <rect x="{rx}" y="82" width="{rw}" height="122" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="105" class="h3">Instance Anatomy</text>')
    out.append(f'  <rect x="{rx+rw-106}" y="90" width="90" height="21" rx="10.5" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append(f'  <text x="{rx+rw-61}" y="104" text-anchor="middle" class="badge">SAT · Verified</text>')
    out.append(f'  <text x="{rx+16}" y="128" class="mono">knights_12x12_d15_obs16_s12150144_sat</text>')
    out.append(f'  <text x="{rx+16}" y="148" class="body">• Grid: 12×12 (144 squares) − {len(obstacles)} obstacles = {n_steps} free vertices</text>')
    out.append(f'  <text x="{rx+16}" y="167" class="body">• Bipartite balance: {free_white} Light = {free_black} Dark squares (necessary)</text>')
    out.append(f'  <text x="{rx+16}" y="186" class="body">• DIMACS CNF: {n_vars:,} vars · {n_clauses:,} clauses (directed MTZ)</text>')

    # Card 2: Mini 5x5 Knight Bipartite Jump Widget
    out.append(f'  <rect x="{rx}" y="216" width="{rw}" height="132" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="239" class="h3">Bipartite Knight Graph &amp; Global Obstruction</text>')
    mx, my, mc = rx + 18, 250, 17
    moves_5 = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    for rr in range(5):
        for cc in range(5):
            sx, sy = mx + cc * mc, my + rr * mc
            fill = "#cbd5e1" if (rr + cc) % 2 == 1 else "#ffffff"
            if (rr, cc) == (2, 2):
                fill = "#2563eb"
            elif (rr - 2, cc - 2) in moves_5:
                fill = "#d1fae5"
            out.append(f'  <rect x="{sx}" y="{sy}" width="{mc}" height="{mc}" fill="{fill}" stroke="#94a3b8" stroke-width="0.6"/>')
    # Draw jump rays from center
    c5x, c5y = mx + 2.5 * mc, my + 2.5 * mc
    for dr, dc in moves_5:
        tx, ty = mx + (2.5 + dc) * mc, my + (2.5 + dr) * mc
        out.append(f'  <line x1="{c5x:.1f}" y1="{c5y:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#059669" stroke-width="1.2" opacity="0.8"/>')
        out.append(f'  <circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.3" fill="#059669"/>')
    out.append(f'  <text x="{c5x:.1f}" y="{c5y+3.5:.1f}" text-anchor="middle" style="font:700 10px sans-serif;fill:#ffffff;">K</text>')

    tx0 = rx + 118
    out.append(f'  <text x="{tx0}" y="266" class="body">Every L-jump flips square color:</text>')
    out.append(f'  <text x="{tx0}" y="284" class="mono">Light ↔ Dark  (bipartite graph)</text>')
    out.append(f'  <text x="{tx0}" y="305" class="body">Every UNSAT board in this suite is</text>')
    out.append(f'  <text x="{tx0}" y="322" class="body">color-balanced, 2-connected, AND has a</text>')
    out.append(f'  <text x="{tx0}" y="339" class="body">2-factor — failing only by subtour clash.</text>')

    # Card 3: CNF Encoding Stack
    out.append(f'  <rect x="{rx}" y="360" width="{rw}" height="154" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="384" class="h3">Hamiltonian Cycle CNF Encoding (MTZ)</text>')
    out.append(f'  <text x="{rx+16}" y="406" class="mono">1. Exact-1 Out/In:  ∑ aᵤ→ᵥ = 1,  ∑ aᵥ→ᵤ = 1</text>')
    out.append(f'  <text x="{rx+16}" y="426" class="mono">2. No 2-Cycles:     (¬aᵤ→ᵥ ∨ ¬aᵥ→ᵤ)</text>')
    out.append(f'  <text x="{rx+16}" y="446" class="mono">3. Root Symmetry:   succ(0) &lt; pred(0)</text>')
    out.append(f'  <text x="{rx+16}" y="466" class="mono">4. Binary MTZ Rank: aᵤ→ᵥ ⇒ rank(u) &lt; rank(v)</text>')
    out.append(f'  <text x="{rx+16}" y="487" class="body">Strict ⌈log₂ |V|⌉-bit rank ordering forbids disconnected</text>')
    out.append(f'  <text x="{rx+16}" y="503" class="body">subtours in O(|E| log |V|) clauses (suite: 12×12–16×16).</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
