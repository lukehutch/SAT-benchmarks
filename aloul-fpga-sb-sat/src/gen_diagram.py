#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`aloul-fpga-sb-sat` (Aloul FPGA Switch-Box SAT Benchmarks — "Bart").

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sub(text: str) -> str:
    return f'<tspan baseline-shift="sub" font-size="72%">{esc(text)}</tspan>'


def build_svg() -> str:
    W, H = 920, 470
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Aloul FPGA Switch-Box SAT Routing Benchmark Architecture">',
        "  <defs>",
        '    <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        "  </defs>",
        # Explicit white card canvas for GitHub light & dark mode compatibility
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Aloul FPGA Switch-Box SAT Routing — "Bart" (aloul-fpga-sb-sat)</text>',
        f'    <text x="28" y="53" font-size="11.8" fill="#475569">'
        f'4-sided programmable switch-box channels with N ≤ W tracks per side · '
        f'11 satisfiable instances (fpga10_8 .. fpga13_12) with S{sub("N")} × S{sub("W")} symmetry</text>',
        '    <rect x="786" y="18" width="108" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="840" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">11 SAT · Routable</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: 4-SIDED FPGA SWITCH BOX =================
    lx, ly, lw, lh = 24, 78, 514, 370
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Programmable 4-Sided Switch Box (Illustrative W = 5 Tracks, N = 4 Nets)</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.5" fill="#475569">'
        'Each connection selects a collision-free track via pass-transistor switches; spare track t₅ remains free</text>'
    )

    # Geometry of the switch box centered at (cx, cy) — balanced vertical margin above legend!
    cx, cy = lx + 257, ly + 194
    sb = 118  # switch box square size
    sb_x0, sb_y0 = cx - sb / 2, cy - sb / 2
    sb_x1, sb_y1 = cx + sb / 2, cy + sb / 2
    ch_h = 94   # horizontal arm length (West / East)
    ch_v = 60   # vertical arm length (North / South)
    step = 20
    offs = [-2 * step, -step, 0, step, 2 * step]  # t1..t5

    # Channel arm background rectangles (West, East, North, South)
    p.append(f'    <rect x="{sb_x0 - ch_h:.1f}" y="{sb_y0 + 5:.1f}" width="{ch_h:.1f}" height="{sb - 10:.1f}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <rect x="{sb_x1:.1f}" y="{sb_y0 + 5:.1f}" width="{ch_h:.1f}" height="{sb - 10:.1f}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <rect x="{sb_x0 + 5:.1f}" y="{sb_y0 - ch_v:.1f}" width="{sb - 10:.1f}" height="{ch_v:.1f}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <rect x="{sb_x0 + 5:.1f}" y="{sb_y1:.1f}" width="{sb - 10:.1f}" height="{ch_v:.1f}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')

    # Subtle CLB blocks in the 4 corners around the switch box (generous gap above WEST/EAST)
    clb_w, clb_h = 84, 42
    clb_coords = [
        (sb_x0 - ch_h + 2, sb_y0 - ch_v + 1, "CLB (0,0)"),
        (sb_x1 + 8, sb_y0 - ch_v + 1, "CLB (1,0)"),
        (sb_x0 - ch_h + 2, sb_y1 + 12, "CLB (0,1)"),
        (sb_x1 + 8, sb_y1 + 12, "CLB (1,1)"),
    ]
    for bx, by, blbl in clb_coords:
        p.append(f'    <rect x="{bx:.1f}" y="{by:.1f}" width="{clb_w}" height="{clb_h}" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1" stroke-dasharray="4,2"/>')
        p.append(f'    <text x="{bx + clb_w/2:.1f}" y="{by + clb_h/2 + 4:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="#1d4ed8">{blbl}</text>')

    # Central switch-box matrix
    p.append(
        f'    <rect x="{sb_x0:.1f}" y="{sb_y0:.1f}" width="{sb}" height="{sb}" rx="7" '
        'fill="#ffffff" stroke="#334155" stroke-width="1.8"/>'
    )
    for d in offs:
        p.append(f'    <line x1="{sb_x0:.1f}" y1="{cy + d:.1f}" x2="{sb_x1:.1f}" y2="{cy + d:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        p.append(f'    <line x1="{cx + d:.1f}" y1="{sb_y0:.1f}" x2="{cx + d:.1f}" y2="{sb_y1:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
    # Draw unused/open tracks first in light dashed slate
    for d in offs:
        p.append(f'    <line x1="{sb_x0 - ch_h + 4:.1f}" y1="{cy + d:.1f}" x2="{sb_x0:.1f}" y2="{cy + d:.1f}" stroke="#cbd5e1" stroke-width="1.3" stroke-dasharray="3,2"/>')
        p.append(f'    <line x1="{sb_x1:.1f}" y1="{cy + d:.1f}" x2="{sb_x1 + ch_h - 4:.1f}" y2="{cy + d:.1f}" stroke="#cbd5e1" stroke-width="1.3" stroke-dasharray="3,2"/>')
        p.append(f'    <line x1="{cx + d:.1f}" y1="{sb_y0 - ch_v + 4:.1f}" x2="{cx + d:.1f}" y2="{sb_y0:.1f}" stroke="#cbd5e1" stroke-width="1.3" stroke-dasharray="3,2"/>')
        p.append(f'    <line x1="{cx + d:.1f}" y1="{sb_y1:.1f}" x2="{cx + d:.1f}" y2="{sb_y1 + ch_v - 4:.1f}" stroke="#cbd5e1" stroke-width="1.3" stroke-dasharray="3,2"/>')

    # Unprogrammed pass-transistor dots on diagonal inside SB
    for i in range(5):
        px_d = cx + offs[i]
        py_d = cy + offs[i]
        p.append(f'    <circle cx="{px_d:.1f}" cy="{py_d:.1f}" r="3" fill="#e2e8f0" stroke="#94a3b8" stroke-width="0.9"/>')

    # Active routed nets (4 collision-free paths across tracks t1..t4; t5 left spare!)
    y_t1 = cy + offs[0]
    p.append(f'    <path d="M {sb_x0 - ch_h + 4:.1f} {y_t1:.1f} L {sb_x1 + ch_h - 4:.1f} {y_t1:.1f}" fill="none" stroke="#2563eb" stroke-width="2.8" stroke-linecap="round"/>')
    y_t2 = cy + offs[1]
    x_t2 = cx + offs[1]
    p.append(f'    <path d="M {sb_x0 - ch_h + 4:.1f} {y_t2:.1f} L {x_t2:.1f} {y_t2:.1f} L {x_t2:.1f} {sb_y0 - ch_v + 4:.1f}" fill="none" stroke="#059669" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    x_t4 = cx + offs[3]
    y_t3 = cy + offs[2]
    p.append(f'    <path d="M {x_t4:.1f} {sb_y0 - ch_v + 4:.1f} L {x_t4:.1f} {y_t3:.1f} L {sb_x1 + ch_h - 4:.1f} {y_t3:.1f}" fill="none" stroke="#7c3aed" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    x_t3 = cx + offs[2]
    y_t4 = cy + offs[3]
    p.append(f'    <path d="M {x_t3:.1f} {sb_y1 + ch_v - 4:.1f} L {x_t3:.1f} {y_t4:.1f} L {sb_x0 - ch_h + 4:.1f} {y_t4:.1f}" fill="none" stroke="#d97706" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')

    # Programmed pass-transistor switch nodes
    for sx, sy, scol in [
        (cx + offs[0], y_t1, "#2563eb"),
        (x_t2, y_t2, "#059669"),
        (x_t4, y_t3, "#7c3aed"),
        (x_t3, y_t4, "#d97706"),
    ]:
        p.append(f'    <circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{scol}" stroke="#ffffff" stroke-width="1.6"/>')

    # Track labels on West & East edges
    t_labels = ["t₁ (n₁)", "t₂ (n₂)", "t₃ (free)", "t₄ (n₄)", "t₅ (spare)"]
    t_cols = ["#1d4ed8", "#047857", "#64748b", "#b45309", "#64748b"]
    for idx, d in enumerate(offs):
        p.append(
            f'    <text x="{sb_x0 - ch_h - 5:.1f}" y="{cy + d + 3.5:.1f}" text-anchor="end" '
            f'font-size="9.5" font-weight="600" fill="{t_cols[idx]}">{t_labels[idx]}</text>'
        )
    e_labels = ["n₁", "free", "n₃", "free", "spare"]
    e_cols = ["#1d4ed8", "#64748b", "#6d28d9", "#64748b", "#64748b"]
    for idx, d in enumerate(offs):
        p.append(
            f'    <text x="{sb_x1 + ch_h + 5:.1f}" y="{cy + d + 3.5:.1f}" text-anchor="start" '
            f'font-size="9.5" font-weight="600" fill="{e_cols[idx]}">{e_labels[idx]}</text>'
        )

    # Channel direction badges (plenty of clearance above North & below South!)
    p.append(f'    <text x="{cx:.1f}" y="{sb_y0 - ch_v - 8:.1f}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#334155">NORTH CHANNEL (W tracks)</text>')
    p.append(f'    <text x="{cx:.1f}" y="{sb_y1 + ch_v + 15:.1f}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#334155">SOUTH CHANNEL (W tracks)</text>')
    p.append(f'    <text x="{sb_x0 - ch_h/2:.1f}" y="{sb_y0 - 4:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#475569">WEST</text>')
    p.append(f'    <text x="{sb_x1 + ch_h/2:.1f}" y="{sb_y0 - 4:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#475569">EAST</text>')

    # Legend strip at bottom of left panel
    leg_y = ly + lh - 20
    p.append(f'    <rect x="{lx + 14}" y="{leg_y - 13}" width="{lw - 28}" height="24" rx="5" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    legend_items = [
        (lx + 26, "#2563eb", "Net n₁ (W→E)"),
        (lx + 124, "#059669", "Net n₂ (W→N)"),
        (lx + 222, "#7c3aed", "Net n₃ (N→E)"),
        (lx + 320, "#d97706", "Net n₄ (S→W)"),
        (lx + 416, "#94a3b8", "t₅ Spare"),
    ]
    for ix, icol, ilbl in legend_items:
        p.append(f'    <circle cx="{ix}" cy="{leg_y - 1}" r="4" fill="{icol}"/>')
        p.append(f'    <text x="{ix + 9}" y="{leg_y + 2.5}" font-size="9.8" font-weight="600" fill="#334155">{ilbl}</text>')

    # ================= RIGHT PANEL: ENCODING, SYMMETRY & CORPUS =================
    rx, ry, rw = 554, 78, 342

    # Card 1: CNF Encoding
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="122" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#0f172a">CNF Encoding (fpga10_8_sat_rcr Example)</text>')
    enc_lines = [
        ("Variables:", f'x{sub("i,t")} = 1 iff net i assigned to track t (120 vars)'),
        ("ALO (8 cls):", f'⋁{sub("t=1..W")} x{sub("i,t")}  (each net gets ≥ 1 track, len W)'),
        ("SB Coupling:", '80 mixed 5-clauses (pass-transistor fan-out rules)'),
        ("Track AMO:", f'360 binary clauses ¬x{sub("i,t")} ∨ ¬x{sub("j,t")} (disjoint)'),
        ("Randomize:", 'Variables &amp; clauses randomly reordered (_rcr)'),
    ]
    for i, (k, v) in enumerate(enc_lines):
        yy = ry + 41 + i * 16.5
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="10" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 84}" y="{yy:.1f}" font-size="9.8" fill="#334155">{v}</text>')

    # Card 2: Symmetry Orbit Structure
    sy = ry + 134
    p.append(f'    <rect x="{rx}" y="{sy}" width="{rw}" height="96" rx="9" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{sy + 20}" font-size="12" font-weight="700" fill="#6d28d9">Permutation Symmetry Group (S{sub("N")} × S{sub("W")})</text>')
    p.append(f'    <text x="{rx + 14}" y="{sy + 38}" font-size="10" fill="#334155">• Track indices t₁..t{sub("W")} are fully interchangeable (S{sub("W")})</text>')
    p.append(f'    <text x="{rx + 14}" y="{sy + 54}" font-size="10" fill="#334155">• Identical net demands permute freely in channels (S{sub("N")})</text>')
    p.append(f'    <text x="{rx + 14}" y="{sy + 70}" font-size="10" fill="#334155">• Unlike Homer UNSAT, N ≤ W guarantees many valid</text>')
    p.append(f'    <text x="{rx + 22}" y="{sy + 85}" font-size="10" fill="#334155">track assignments (solved in ~1.6–2.4 ms on 1 core)</text>')

    # Card 3: Corpus Profile Table
    cy3 = sy + 108
    p.append(f'    <rect x="{rx}" y="{cy3}" width="{rw}" height="128" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy3 + 20}" font-size="12" font-weight="700" fill="#0f172a">Corpus Profile (11 Instances · 0 XORs)</text>')

    rows = [
        ("fpga10 (N=8–9)", "2 files", "448–549 c", 0.44, "#2563eb"),
        ("fpga12 (N=8–12)", "5 files", "560–1,128 c", 0.91, "#059669"),
        ("fpga13 (N=9–12)", "4 files", "759–1,242 c", 1.00, "#7c3aed"),
    ]
    for i, (fam, cnt, cs, frac, col) in enumerate(rows):
        yy = cy3 + 42 + i * 24
        p.append(f'    <text x="{rx + 14}" y="{yy}" font-family="{mono}" font-size="9.4" font-weight="700" fill="#0f172a">{fam}</text>')
        p.append(f'    <text x="{rx + 122}" y="{yy}" font-size="9.4" fill="#475569">{cnt}</text>')
        bar_x, bar_w = rx + 162, 92
        p.append(f'    <rect x="{bar_x}" y="{yy - 9}" width="{bar_w}" height="11" rx="3" fill="#f1f5f9"/>')
        p.append(f'    <rect x="{bar_x}" y="{yy - 9}" width="{bar_w * frac:.1f}" height="11" rx="3" fill="{col}" fill-opacity="0.85"/>')
        p.append(f'    <text x="{rx + rw - 12}" y="{yy}" text-anchor="end" font-size="9.2" fill="#334155">{cs}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy3 + 116}" font-size="9.8" fill="#475569">'
        f'Regime: Over (ρ{sub("crit")} = 3.03×–4.60×) · 80–86% Binary Horn · κ = 1.61</text>'
    )

    p.append("  </g>")
    p.append("</svg>\n")
    return "\n".join(p)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "diagram.svg"
    out.write_text(build_svg(), encoding="utf-8")
    ET.parse(out)
    print(f"Wrote and validated {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
