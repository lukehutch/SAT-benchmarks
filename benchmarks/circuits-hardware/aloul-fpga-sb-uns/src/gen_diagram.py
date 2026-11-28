#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`aloul-fpga-sb-uns` (Aloul FPGA Switch-Box UNSAT Benchmarks — "Homer").

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


def sup(text: str) -> str:
    return f'<tspan baseline-shift="super" font-size="72%">{esc(text)}</tspan>'


def build_svg() -> str:
    W, H = 920, 470
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Aloul FPGA Switch-Box UNSAT Congestion Bottleneck Architecture">',
        "  <defs>",
        '    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Aloul FPGA Switch-Box UNSAT Bottlenecks — "Homer" (aloul-fpga-sb-uns)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Over-subscribed switch-box channels (N &gt; W tracks per side) · '
        '10 UNSAT instances (fpga10_11 .. fpga11_20) · Double Pigeonhole Core</text>',
        '    <rect x="774" y="18" width="120" height="24" rx="12" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>',
        '    <text x="834" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#b91c1c">10 UNSAT · Congested</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: CONGESTED SWITCH-BOX BOTTLENECK =================
    lx, ly, lw, lh = 24, 78, 514, 370
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Congested Switch-Box Channel (Illustrative N = 5 Nets &gt; W = 4 Tracks)</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.5" fill="#475569">'
        f'All W tracks saturate; the (W+1)-th net collides — creating 2 × PHP{sub("W")}{sup("N")}</text>'
    )

    # Top diagram: Congested switch-box cross-section
    by0 = ly + 56
    # Left incoming nets bank
    p.append(f'    <rect x="{lx + 18}" y="{by0}" width="106" height="148" rx="7" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 71}" y="{by0 + 16}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#334155">N = 5 Nets</text>')

    # Central congested switch box (narrower height representing W=4 tracks)
    sb_x, sb_y, sb_w, sb_h = lx + 196, by0 + 12, 134, 114
    p.append(f'    <rect x="{sb_x}" y="{sb_y}" width="{sb_w}" height="{sb_h}" rx="8" fill="#fff5f5" stroke="#dc2626" stroke-width="2"/>')
    p.append(f'    <text x="{sb_x + sb_w/2:.1f}" y="{sb_y - 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#b91c1c">Switch Box (W = 4)</text>')

    # Right channel bank
    rx_box = lx + 394
    p.append(f'    <rect x="{rx_box}" y="{by0}" width="102" height="148" rx="7" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx_box + 51}" y="{by0 + 16}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#334155">Side B (W = 4)</text>')

    net_cols = ["#2563eb", "#059669", "#7c3aed", "#d97706", "#dc2626"]
    # Draw 4 saturated tracks inside SB
    for i in range(4):
        ty = sb_y + 20 + i * 24
        ny = by0 + 34 + i * 24
        col = net_cols[i]
        # Net pill on left
        p.append(f'    <rect x="{lx + 30}" y="{ny - 9}" width="82" height="18" rx="4" fill="#f8fafc" stroke="{col}" stroke-width="1.2"/>')
        p.append(f'    <text x="{lx + 71}" y="{ny + 3.5}" text-anchor="middle" font-size="9.8" font-weight="700" fill="{col}">Net n{chr(0x2081 + i)}</text>')
        # Wire from left bank into switch box track t_i and out to right bank
        p.append(f'    <path d="M {lx + 112} {ny} C {lx + 152} {ny}, {sb_x - 36} {ty}, {sb_x} {ty} L {sb_x + sb_w} {ty} C {sb_x + sb_w + 30} {ty}, {rx_box - 28} {ny}, {rx_box + 12} {ny}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        # Track slot inside switch box
        p.append(f'    <rect x="{sb_x + 28}" y="{ty - 8}" width="78" height="16" rx="3" fill="#ffffff" stroke="{col}" stroke-width="1"/>')
        p.append(f'    <text x="{sb_x + 67}" y="{ty + 3.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#0f172a">Track t{chr(0x2081 + i)} FULL</text>')
        # Destination port on right
        p.append(f'    <circle cx="{rx_box + 16}" cy="{ny}" r="4.5" fill="{col}"/>')
        p.append(f'    <text x="{rx_box + 27}" y="{ny + 3.5}" font-size="9.5" font-weight="600" fill="#334155">Port t{chr(0x2081 + i)}</text>')

    # 5th overflow net — BLOCKED!
    ny5 = by0 + 34 + 4 * 24
    p.append(f'    <rect x="{lx + 30}" y="{ny5 - 9}" width="82" height="18" rx="4" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>')
    p.append(f'    <text x="{lx + 71}" y="{ny5 + 3.5}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#b91c1c">Net n₅ (!)</text>')
    # Blocked dashed red arrow hitting SB wall
    p.append(
        f'    <path d="M {lx + 112} {ny5} L {sb_x - 18} {ny5} L {sb_x - 8} {sb_y + sb_h - 6}" '
        'fill="none" stroke="#dc2626" stroke-width="2.4" stroke-dasharray="5,3" marker-end="url(#arr-red)"/>'
    )
    # Red collision badge
    cx_b, cy_b = sb_x + sb_w / 2, sb_y + sb_h + 18
    p.append(f'    <rect x="{sb_x - 8}" y="{sb_y + sb_h + 7}" width="{sb_w + 16}" height="22" rx="5" fill="#dc2626"/>')
    p.append(f'    <text x="{cx_b:.1f}" y="{cy_b + 3.5:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">× COLLISION: 0 Free Tracks</text>')
    p.append(f'    <text x="{rx_box + 51}" y="{ny5 + 3}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b91c1c">No slot left!</text>')

    # Bottom sub-panel inside left card: Bipartite Double-PHP structure
    sub_y = ly + 220
    p.append(f'    <rect x="{lx + 18}" y="{sub_y}" width="{lw - 36}" height="134" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 32}" y="{sub_y + 19}" font-size="11.5" font-weight="700" fill="#0f172a">Exact Combinatorial Core: Symmetric 2-Side Channel PHP (K{sub("N,W")})</text>')

    # Draw Left-side bipartite graph (5 nets -> 4 tracks)
    gx_l = lx + 54
    gx_r = lx + 174
    net_ys = [sub_y + 38 + i * 21 for i in range(5)]
    trk_ys = [sub_y + 48 + j * 22 for j in range(4)]
    for i, y1 in enumerate(net_ys):
        for j, y2 in enumerate(trk_ys):
            if i == j and i < 4:
                p.append(f'    <line x1="{gx_l + 9}" y1="{y1}" x2="{gx_r - 9}" y2="{y2}" stroke="{net_cols[i]}" stroke-width="2"/>')
            elif i == 4:
                p.append(f'    <line x1="{gx_l + 9}" y1="{y1}" x2="{gx_r - 9}" y2="{y2}" stroke="#fca5a5" stroke-width="1" stroke-dasharray="3,2"/>')
            else:
                p.append(f'    <line x1="{gx_l + 9}" y1="{y1}" x2="{gx_r - 9}" y2="{y2}" stroke="#e2e8f0" stroke-width="0.9"/>')
    for i, y1 in enumerate(net_ys):
        fill_n = "#fef2f2" if i == 4 else "#eff6ff"
        strk_n = "#dc2626" if i == 4 else net_cols[i]
        p.append(f'    <circle cx="{gx_l}" cy="{y1}" r="8" fill="{fill_n}" stroke="{strk_n}" stroke-width="1.4"/>')
        p.append(f'    <text x="{gx_l}" y="{y1 + 3.2}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{strk_n}">n{i+1}</text>')
    for j, y2 in enumerate(trk_ys):
        p.append(f'    <rect x="{gx_r - 9}" y="{y2 - 8}" width="18" height="16" rx="3" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>')
        p.append(f'    <text x="{gx_r}" y="{y2 + 3.2}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#0f172a">t{j+1}</text>')

    # Mathematical explanation to the right of the bipartite graph
    mx = lx + 206
    math_lines = [
        ("ALO (2N clauses):", f'⋁{sub("t=1..W")} x{sub("s,i,t")}  (s ∈ {{L, R}}, len W)'),
        ("AMO (2W·C(N,2)):", f'¬x{sub("s,i,t")} ∨ ¬x{sub("s,j,t")}  (100% binary)'),
        ("Degree Profile:", 'Every variable has exact identical degree'),
        ("", 'd = 1 + (N − 1) = N  ⇒  Deg CV = 0.00!'),
        ("Proof Complexity:", f'Haken (1985): Resolution needs 2{sup("Ω(W)")}'),
    ]
    for i, (k, v) in enumerate(math_lines):
        yy = sub_y + 42 + i * 18.5
        if k:
            p.append(f'    <text x="{mx}" y="{yy:.1f}" font-size="9.6" font-weight="700" fill="#b91c1c">{esc(k)}</text>')
            p.append(f'    <text x="{mx + 96}" y="{yy:.1f}" font-size="9.4" fill="#334155">{v}</text>')
        else:
            p.append(f'    <text x="{mx + 96}" y="{yy:.1f}" font-size="9.4" font-weight="600" fill="#0f172a">{v}</text>')

    # ================= RIGHT PANEL: STATS, CDCL WALL & SCALING =================
    rx, ry, rw = 554, 78, 342

    # Card 1: Why CDCL Fails vs Cardinality/Symmetry Solvers
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="120" rx="9" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#b91c1c">Resolution Wall &amp; Symmetry Explosion</text>')
    wall_lines = [
        "• Pure CDCL (CaDiCaL 3.1 / CMS 5.18): 0/10 solved (&lt; 5 s)",
        "• Kissat 4.0.4: 1/10 solved (3.07 s on fpga10_20)",
        "• Cardinality / Symmetry-aware solvers: 10/10 in 16–23 ms",
        f'• Symmetry group Aut(F) contains S{sub("N")} × S{sub("W")} × Z₂',
        "• Random variable/clause shuffling (_rcr) hides block order",
    ]
    for i, ln in enumerate(wall_lines):
        p.append(f'    <text x="{rx + 14}" y="{ry + 41 + i * 16.5:.1f}" font-size="9.8" fill="#334155">{ln}</text>')

    # Card 2: Exact Scaling Chart across all 10 instances
    cy2 = ry + 132
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="238" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 21}" font-size="12" font-weight="700" fill="#0f172a">All 10 Instances: Clauses &amp; Constrainedness</text>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 36}" font-size="9.6" fill="#64748b">fpgaW_N_uns_rcr · Vars = 2·W·N · 98–99% Binary Horn · 0 XORs</text>')

    insts = [
        ("fpga10_11", 220, 1122, "5.0×"),
        ("fpga10_12", 240, 1344, "5.5×"),
        ("fpga10_13", 260, 1586, "6.0×"),
        ("fpga10_15", 300, 2130, "7.0×"),
        ("fpga10_20", 400, 3840, "9.5×"),
        ("fpga11_12", 264, 1476, "5.5×"),
        ("fpga11_13", 286, 1742, "6.0×"),
        ("fpga11_14", 308, 2030, "6.5×"),
        ("fpga11_15", 330, 2340, "7.0×"),
        ("fpga11_20", 440, 4220, "9.5×"),
    ]
    max_cls = 4220
    for i, (name, nv, nc, rho) in enumerate(insts):
        yy = cy2 + 54 + i * 17.5
        col = "#dc2626" if name.startswith("fpga11") else "#d97706"
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-family="{mono}" font-size="9.2" font-weight="600" fill="#0f172a">{name}</text>')
        bx, bw = rx + 84, 152
        p.append(f'    <rect x="{bx}" y="{yy - 8.5:.1f}" width="{bw}" height="10" rx="2.5" fill="#f1f5f9"/>')
        p.append(f'    <rect x="{bx}" y="{yy - 8.5:.1f}" width="{bw * nc / max_cls:.1f}" height="10" rx="2.5" fill="{col}" fill-opacity="0.85"/>')
        p.append(f'    <text x="{rx + rw - 50}" y="{yy:.1f}" text-anchor="end" font-size="9" fill="#334155">{nc:,} c</text>')
        p.append(f'    <text x="{rx + rw - 12}" y="{yy:.1f}" text-anchor="end" font-size="9" font-weight="700" fill="{col}">{rho}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy2 + 230}" font-size="9.5" fill="#475569">'
        f'Median ρ{sub("crit")} = 6.25× (range 5.00×–9.50×) · Median κ = 2.59</text>'
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
