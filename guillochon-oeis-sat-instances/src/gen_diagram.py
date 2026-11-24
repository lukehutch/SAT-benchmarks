#!/usr/bin/env python3
"""
Generate an illustrative multi-panel SVG diagram (`diagram.svg`) for the
James Guillochon OEIS SAT Instances collection (`guillochon-oeis-sat-instances`).

Renders all 5 problem families using verified combinatorial objects from the repository:
  1. A067782: Optimal-depth sorting network (verified 8-input depth-6 comparator network; open: n=18, d=10)
  2. A171081: Van der Waerden w(2;3,10) > 96 (verified Frobenius 2-coloring of {1..96})
  3. A250000: Peaceable Queens on 15x15 (verified Frobenius 32+32 queen placement)
  4. A350304: Zarankiewicz z(17;3) >= 135 (verified 17x17 0/1 matrix with no K_{3,3})
  5. point-patterns: tri-axis side 16 (verified Frobenius 54-point triangle-free configuration)
"""
from __future__ import annotations

import json
import lzma
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_true_vars(path: Path) -> set[int]:
    opener = lzma.open if path.suffix == ".xz" else open
    true_vars: set[int] = set()
    with opener(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ("c", "s"):
                continue
            toks = s.split()
            if toks[0] == "v":
                toks = toks[1:]
            for tok in toks:
                lit = int(tok)
                if lit > 0:
                    true_vars.add(lit)
    return true_vars


def verify_sortnet_8(layers: list[list[tuple[int, int]]]) -> bool:
    for mask in range(1 << 8):
        bits = [(mask >> (7 - i)) & 1 for i in range(8)]
        for layer in layers:
            for i, j in layer:
                if bits[i] > bits[j]:
                    bits[i], bits[j] = bits[j], bits[i]
        if bits != sorted(bits):
            return False
    return True


def build_svg() -> str:
    W, H = 1120, 690
    els: list[str] = []
    add = els.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    add("""  <defs>
    <style>
      .title { font: 700 18px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .subtitle { font: 400 12px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .ptitle { font: 700 13.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .psub { font: 400 11px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .mono { font: 600 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #334155; }
      .badge { font: 700 10px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .cap { font: 400 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #334155; }
    </style>
  </defs>""")

    # Explicit light card background for crisp readability in both GitHub light & dark modes
    add(f'  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>')
    add('  <text x="24" y="34" class="title">James Guillochon OEIS SAT Instances — Five Combinatorial Frontier Families</text>')
    add('  <text x="24" y="53" class="subtitle">Each SAT model decodes directly to an independently checkable combinatorial object; each UNSAT proof (DRAT/LRAT) certifies an exact OEIS optimality bound.</text>')

    def card(x: int, y: int, w: int, h: int, title: str, sub: str, badge_txt: str, badge_col: str) -> None:
        add(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
        add(f'  <text x="{x+14}" y="{y+23}" class="ptitle">{title}</text>')
        add(f'  <text x="{x+14}" y="{y+39}" class="psub">{sub}</text>')
        bw = max(72, len(badge_txt) * 6 + 16)
        add(f'  <rect x="{x+w-bw-12}" y="{y+10}" width="{bw}" height="19" rx="9.5" fill="{badge_col}"/>')
        add(f'  <text x="{x+w-bw/2-12:.1f}" y="{y+23}" text-anchor="middle" class="badge">{badge_txt}</text>')

    # =========================================================================
    # PANEL 1 (Top Left): A067782 Optimal-Depth Sorting Network (8-input, d=6)
    # =========================================================================
    p1x, p1y, p1w, p1h = 20, 68, 530, 278
    card(p1x, p1y, p1w, p1h,
         "1. OEIS A067782 — Optimal-Depth Sorting Networks",
         "Verified optimal 8-input depth-6 network (19 comparators); open target: a(18) in {10, 11}",
         "OPEN: n=18, d=10", "#dc2626")

    # Classic optimal 8-input depth-6 sorting network (Batcher / Knuth)
    layers8 = [
        [(0, 1), (2, 3), (4, 5), (6, 7)],
        [(0, 2), (1, 3), (4, 6), (5, 7)],
        [(1, 2), (5, 6), (0, 4), (3, 7)],
        [(1, 5), (2, 6)],
        [(1, 4), (3, 6)],
        [(2, 4), (3, 5), (0, 1), (6, 7)],  # adjusted below if needed
    ]
    # Exact optimal 19-comparator depth-6 8-input sorting network (Knuth TAOCP Vol. 3, Fig. 49)
    layers8 = [
        [(0, 1), (2, 3), (4, 5), (6, 7)],
        [(0, 2), (1, 3), (4, 6), (5, 7)],
        [(0, 4), (1, 5), (2, 6), (3, 7)],
        [(1, 2), (5, 6)],
        [(2, 4), (3, 5)],
        [(1, 2), (3, 4), (5, 6)],
    ]
    assert verify_sortnet_8(layers8), "8-input sorting network failed 0/1 check!"

    wx0, wx1 = p1x + 42, p1x + p1w - 28
    wy0, wdy = p1y + 68, 22
    layer_colors = ["#2563eb", "#0d9488", "#7c3aed", "#d97706", "#db2777", "#059669"]

    for ch in range(8):
        cy = wy0 + ch * wdy
        add(f'  <line x1="{wx0}" y1="{cy}" x2="{wx1}" y2="{cy}" stroke="#94a3b8" stroke-width="1.5"/>')
        add(f'  <text x="{wx0-10}" y="{cy+4}" text-anchor="end" class="mono">x{ch}</text>')
        add(f'  <text x="{wx1+6}" y="{cy+4}" class="mono">y{ch}</text>')

    lx_positions = [p1x + 74, p1x + 144, p1x + 226, p1x + 318, p1x + 382, p1x + 448]
    for li, layer in enumerate(layers8):
        col = layer_colors[li]
        bx = lx_positions[li]
        # subtle layer band
        add(f'  <rect x="{bx-14}" y="{wy0-11}" width="54" height="{7*wdy+22}" rx="5" fill="{col}" fill-opacity="0.06"/>')
        add(f'  <text x="{bx+13}" y="{wy0+7*wdy+26}" text-anchor="middle" class="mono">L{li+1}</text>')
        for ci, (a, b) in enumerate(layer):
            # slight horizontal stagger for overlapping vertical spans
            dx = (ci % 4) * 10 if len(layer) >= 3 else ci * 14
            cx = bx + dx - 4
            ya, yb = wy0 + a * wdy, wy0 + b * wdy
            add(f'  <line x1="{cx}" y1="{ya}" x2="{cx}" y2="{yb}" stroke="{col}" stroke-width="2.2"/>')
            add(f'  <circle cx="{cx}" cy="{ya}" r="3.6" fill="{col}"/>')
            add(f'  <circle cx="{cx}" cy="{yb}" r="3.6" fill="{col}"/>')

    add(f'  <text x="{p1x+14}" y="{p1y+p1h-12}" class="cap">L1 fixed (Parberry 1991); L6 adjacent-only (Codish et al. 2015). Open n=18, d=10: 2.60M vars, 63.3M cls.</text>')

    # =========================================================================
    # PANEL 2 (Top Right): A171081 Van der Waerden w(2;3,10) > 96
    # =========================================================================
    p2x, p2y, p2w, p2h = 568, 68, 532, 278
    card(p2x, p2y, p2w, p2h,
         "2. OEIS A171081 — Van der Waerden w(2; 3, t)",
         "Verified Frobenius model for w(2;3,10) &gt; 96: no red 3-AP, no blue 10-AP (0.31 s)",
         "OPEN: w(2;3,20)?", "#2563eb")

    vdw_true = read_true_vars(ROOT / "solutions/A171081/vdw_3_10_N96.model.xz")
    # 6 rows of 16 cells = 96 integers
    gx0, gy0 = p2x + 22, p2y + 62
    cw, ch_cell, gap = 28, 24, 3
    n_red = 0
    for idx in range(1, 97):
        r = (idx - 1) // 16
        c = (idx - 1) % 16
        cx = gx0 + c * (cw + gap)
        cy = gy0 + r * (ch_cell + gap)
        is_red = idx in vdw_true
        if is_red:
            n_red += 1
        fill = "#ef4444" if is_red else "#3b82f6"
        add(f'  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch_cell}" rx="4" fill="{fill}" fill-opacity="0.90"/>')
        add(f'  <text x="{cx+cw/2:.1f}" y="{cy+15.5:.1f}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="9.5" font-weight="700" fill="#ffffff">{idx}</text>')

    # Legend
    ly = p2y + 236
    add(f'  <rect x="{gx0}" y="{ly-10}" width="12" height="12" rx="3" fill="#ef4444"/>')
    add(f'  <text x="{gx0+17}" y="{ly}" class="cap">Red ({n_red} ints, max AP = 2 &lt; 3)</text>')
    add(f'  <rect x="{gx0+190}" y="{ly-10}" width="12" height="12" rx="3" fill="#3b82f6"/>')
    add(f'  <text x="{gx0+207}" y="{ly}" class="cap">Blue ({96-n_red} ints, max AP = 9 &lt; 10)</text>')
    add(f'  <text x="{p2x+14}" y="{p2y+p2h-12}" class="cap">Open instance vdw_3_20_N389: 389 vars, 41,426 clauses (UNSAT proves w(2;3,20) = 389).</text>')

    # =========================================================================
    # PANEL 3 (Bottom Left): A250000 Peaceable Queens 15x15 (32 + 32)
    # =========================================================================
    p3x, p3y, p3w, p3h = 20, 362, 348, 308
    card(p3x, p3y, p3w, p3h,
         "3. A250000 — Peaceable Queens",
         "Verified Frobenius 15x15 model: 32 W + 32 B (3.84 s)",
         "OPEN: n=21", "#7c3aed")

    q_true = read_true_vars(ROOT / "solutions/A250000/queens_n15_m32.model.xz")
    qn = 15
    qcell = 14.5
    qbx = p3x + (p3w - qn * qcell) / 2
    qby = p3y + 54
    add(f'  <rect x="{qbx-1.5:.1f}" y="{qby-1.5:.1f}" width="{qn*qcell+3:.1f}" height="{qn*qcell+3:.1f}" fill="none" stroke="#64748b" stroke-width="1.2"/>')
    for r in range(qn):
        for c in range(qn):
            cx = qbx + c * qcell
            cy = qby + r * qcell
            sq_col = "#f1f5f9" if (r + c) % 2 == 0 else "#cbd5e1"
            add(f'  <rect x="{cx:.1f}" y="{cy:.1f}" width="{qcell:.1f}" height="{qcell:.1f}" fill="{sq_col}"/>')
            w_var = r * qn + c + 1
            b_var = qn * qn + r * qn + c + 1
            if w_var in q_true:
                add(f'  <circle cx="{cx+qcell/2:.1f}" cy="{cy+qcell/2:.1f}" r="5.0" fill="#ffffff" stroke="#0f172a" stroke-width="1.4"/>')
            elif b_var in q_true:
                add(f'  <circle cx="{cx+qcell/2:.1f}" cy="{cy+qcell/2:.1f}" r="5.0" fill="#0f172a" stroke="#0f172a" stroke-width="1.0"/>')
    add(f'  <text x="{p3x+14}" y="{p3y+p3h-12}" class="cap">Zero white-black attacks along any row, col, or diagonal.</text>')

    # =========================================================================
    # PANEL 4 (Bottom Middle): A350304 Zarankiewicz z(17;3) >= 135
    # =========================================================================
    p4x, p4y, p4w, p4h = 386, 362, 348, 308
    card(p4x, p4y, p4w, p4h,
         "4. A350304 — Zarankiewicz z(n; 3)",
         "Verified 17x17 matrix: 135 ones, no 3x3 all-1s block",
         "OPEN: n=17", "#0d9488")

    z_true = read_true_vars(ROOT / "src/upstream/sequences/A350304/certificates/zaran3_n17_135.model")
    zn = 17
    zcell = 12.8
    zbx = p4x + (p4w - zn * zcell) / 2
    zby = p4y + 54
    add(f'  <rect x="{zbx-1.5:.1f}" y="{zby-1.5:.1f}" width="{zn*zcell+3:.1f}" height="{zn*zcell+3:.1f}" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>')
    for r in range(zn):
        for c in range(zn):
            cx = zbx + c * zcell
            cy = zby + r * zcell
            is_one = (r * zn + c + 1) in z_true
            fill = "#0f766e" if is_one else "#f1f5f9"
            add(f'  <rect x="{cx+0.8:.1f}" y="{cy+0.8:.1f}" width="{zcell-1.6:.1f}" height="{zcell-1.6:.1f}" rx="1.5" fill="{fill}"/>')
    add(f'  <text x="{p4x+14}" y="{p4y+p4h-12}" class="cap">Open bracket n=17: m in {{136,140,144,148}} (462k clauses).</text>')

    # =========================================================================
    # PANEL 5 (Bottom Right): point-patterns tri-axis side 16 (54 points)
    # =========================================================================
    p5x, p5y, p5w, p5h = 752, 362, 348, 308
    card(p5x, p5y, p5w, p5h,
         "5. Grid Point Patterns",
         "Verified Frobenius tri-axis n=16: 54 pts (2.78 s)",
         "5 OPEN FRONTIERS", "#d97706")

    pp_map = json.loads((ROOT / "src/upstream/sequences/point-patterns/cnf/tri-axis_n16_m54.cnf.map.json").read_text())
    pp_true = read_true_vars(ROOT / "solutions/point-patterns/tri-axis_n16_m54.model.xz")
    pts = [tuple(p) for p in pp_map["points"]]
    painted = {p for i, p in enumerate(pts) if (i + 1) in pp_true}
    tn = 16
    step_x = 15.2
    step_y = step_x * math.sqrt(3) / 2.0
    base_w = (tn - 1) * step_x
    ox = p5x + (p5w - base_w) / 2.0
    oy = p5y + 266.0

    # Faint triangular grid outline
    top_x = ox + (tn - 1) * step_x * 0.5
    top_y = oy - (tn - 1) * step_y
    add(f'  <polygon points="{ox:.1f},{oy:.1f} {ox+base_w:.1f},{oy:.1f} {top_x:.1f},{top_y:.1f}" fill="#fffbeb" stroke="#fcd34d" stroke-width="1.0"/>')
    for (x, y) in pts:
        px = ox + (x + 0.5 * y) * step_x
        py = oy - y * step_y
        if (x, y) in painted:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.3" fill="#d97706" stroke="#78350f" stroke-width="0.9"/>')
        else:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#cbd5e1"/>')
    add(f'  <text x="{p5x+14}" y="{p5y+p5h-12}" class="cap">No grid-aligned equilateral triangle; open: m=55 (+4 more).</text>')

    add("</svg>")
    return "\n".join(els) + "\n"


def main() -> None:
    svg = build_svg()
    out = ROOT / "diagram.svg"
    out.write_text(svg, encoding="utf-8")
    # Strict XML validation
    ET.parse(out)
    print(f"Wrote and XML-validated {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
