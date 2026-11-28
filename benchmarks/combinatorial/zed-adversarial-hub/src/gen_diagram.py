#!/usr/bin/env python3
"""Generate a bespoke illustrative SVG diagram (`diagram.svg`) for
`zed-adversarial-hub` (Adversarial High-Fanout Bit-Vector Hub Circuits).

Illustrates the single problem family constructed in `src/main.rs`:
  1. Left: Star-topology bit-level AIGER 1.9 circuit where one shared 10-bit
     two's-complement hub register h in [low, 63] fans out to n in {20..80}
     satellite arithmetic disjunction gadgets enforcing:
       (-x_i - 2h + 40 + (i mod 7) >= 0) OR (y_i - h - 10 + (i mod 5) >= 0)
  2. Right: Exact feasibility interval proof on h in [0, 63] pinpointing the
     razor-sharp SAT/UNSAT boundary at h = 30 (low=25 SAT vs low=31 UNSAT),
     paired with exact 6-instance AIG/CNF/XCNF scaling & Deg CV skew.

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"
FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sub(s: str) -> str:
    return f'<tspan baseline-shift="sub" font-size="72%">{esc(s)}</tspan>'


def build_svg() -> str:
    W, H = 940, 496
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Adversarial High-Fanout 10-Bit Shared-Hub Arithmetic Disjunction Circuits">',
        "  <defs>",
        '    <marker id="arr-amber" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/></marker>',
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        # Header
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Adversarial Bit-Vector Hub Disjunction Circuits (zed-adversarial-hub)</text>',
        '    <text x="26" y="53" font-size="11.8" fill="#475569">'
        '6 native AIGER 1.9 high-fanout soundness-audit circuits (hub_20..80) · '
        '10-bit shared hub h coupled to n two′s-complement adder gadgets</text>',
        '    <rect x="782" y="18" width="134" height="24" rx="12" fill="#fffbeb" stroke="#d97706" stroke-width="1.2"/>',
        '    <text x="849" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#b45309">1 SAT · 5 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: STAR-TOPOLOGY HUB & SATELLITE AIG CIRCUIT =================
    lx, ly, lw, lh = 24, 78, 456, 396
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">1. Star-Topology Bit-Blasted Hub AIG (src/main.rs)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">Single 10-bit hub h fans out across n ∈ {{20, 24, 30, 60, 80}} satellite adders</text>')

    # Central Shared Hub Register h
    hx, hy, hw, hh = lx + 14, ly + 114, 138, 126
    p.append(f'    <rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="9" fill="#fffbeb" stroke="#d97706" stroke-width="1.8"/>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + 21}" text-anchor="middle" font-size="11.2" font-weight="700" fill="#b45309">Shared Hub h</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + 38}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.5" font-weight="700" fill="#0f172a">h[0..9] (10-bit)</text>')
    p.append(f'    <rect x="{hx + 12}" y="{hy + 48}" width="{hw - 24}" height="24" rx="5" fill="#ffffff" stroke="#fbbf24" stroke-width="1"/>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + 64}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.2" font-weight="700" fill="#92400e">low ≤ h ≤ 63</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + 89}" text-anchor="middle" font-size="8.6" fill="#475569">2′s-comp bounds:</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + 103}" text-anchor="middle" font-family="{FONT_MONO}" font-size="7.7" fill="#475569">¬msb(h−low) ∧ ¬msb(63−h)</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + 119}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#d97706">Deg CV: 1.16 → 2.31</text>')

    # Expanded Satellite Gadget i = 0
    sx, sw = lx + 190, 250
    g0y, g0h = ly + 52, 168
    p.append(f'    <rect x="{sx}" y="{g0y}" width="{sw}" height="{g0h}" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="1.4"/>')
    p.append(f'    <text x="{sx + 10}" y="{g0y + 18}" font-size="10.4" font-weight="700" fill="#1d4ed8">Satellite Gadget i = 0 (Critical Witness)</text>')
    p.append(f'    <text x="{sx + 10}" y="{g0y + 33}" font-size="9" fill="#475569">Private 10-bit inputs: x₀ ∈ [20, 63],  y₀ ∈ [0, 40]</text>')

    # Two arithmetic branch boxes
    p.append(f'    <rect x="{sx + 10}" y="{g0y + 42}" width="{sw - 20}" height="36" rx="5" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
    p.append(f'    <text x="{sx + 18}" y="{g0y + 57}" font-family="{FONT_MONO}" font-size="9.1" font-weight="700" fill="#1e3a8a">pᵢ = −xᵢ − 2h + 40 + (i mod 7)</text>')
    p.append(f'    <text x="{sx + 18}" y="{g0y + 71}" font-size="8.6" fill="#475569">10-bit shift + ripple full-adders → sign ¬pᵢ[9]</text>')

    p.append(f'    <rect x="{sx + 10}" y="{g0y + 84}" width="{sw - 20}" height="36" rx="5" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1"/>')
    p.append(f'    <text x="{sx + 18}" y="{g0y + 99}" font-family="{FONT_MONO}" font-size="9.1" font-weight="700" fill="#5b21b6">rᵢ = yᵢ − h − 10 + (i mod 5)</text>')
    p.append(f'    <text x="{sx + 18}" y="{g0y + 113}" font-size="8.6" fill="#475569">10-bit 2′s-comp subtractor → sign ¬rᵢ[9]</text>')

    # Disjunction assert gate
    p.append(f'    <rect x="{sx + 26}" y="{g0y + 128}" width="{sw - 52}" height="28" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.1"/>')
    p.append(f'    <text x="{sx + sw / 2:.1f}" y="{g0y + 146}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.2" font-weight="700" fill="#047857">Assert (pᵢ ≥ 0) ∨ (rᵢ ≥ 0)</text>')

    # Stacked satellite copies i = 1..n-1
    mini = [
        (ly + 232, "Satellite Gadget i = 1  (+1 mod 7, +1 mod 5)"),
        (ly + 268, "Satellite Gadget i = 2  (+2 mod 7, +2 mod 5)"),
        (ly + 304, "⋯  n ∈ {20, 24, 30, 60, 80} parallel gadgets  ⋯"),
        (ly + 340, "Satellite Gadget i = n−1  (AND miter root)"),
    ]
    for my_s, mlbl in mini:
        is_d = "⋯" in mlbl
        p.append(
            f'    <rect x="{sx}" y="{my_s}" width="{sw}" height="28" rx="6" '
            f'fill="{"#f1f5f9" if is_d else "#ffffff"}" stroke="#cbd5e1" stroke-width="1"/>'
        )
        p.append(
            f'    <text x="{sx + sw / 2:.1f}" y="{my_s + 17.5}" text-anchor="middle" '
            f'font-size="9.2" font-weight="{"700" if is_d else "600"}" fill="#334155">{esc(mlbl)}</text>'
        )

    # High-fanout bus curves from Hub -> all satellites
    for ty_a in (g0y + 62, g0y + 104, ly + 246, ly + 282, ly + 318, ly + 354):
        p.append(
            f'    <path d="M {hx + hw} {hy + hh / 2:.1f} C {hx + hw + 24} {hy + hh / 2:.1f}, {sx - 24} {ty_a:.1f}, {sx - 2} {ty_a:.1f}" '
            'fill="none" stroke="#d97706" stroke-width="1.5" marker-end="url(#arr-amber)"/>'
        )

    # Full-adder XOR callout below hub
    p.append(f'    <rect x="{hx}" y="{hy + hh + 18}" width="{hw}" height="96" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + hh + 37}" text-anchor="middle" font-size="9.6" font-weight="700" fill="#1d4ed8">Full-Adder XORs</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + hh + 53}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" fill="#334155">s = a ⊕ b ⊕ cᵢₙ</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + hh + 70}" text-anchor="middle" font-size="8.7" fill="#475569">747–2,954 native</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + hh + 83}" text-anchor="middle" font-size="8.7" fill="#475569">XCNF XOR parity</text>')
    p.append(f'    <text x="{hx + hw / 2:.1f}" y="{hy + hh + 96}" text-anchor="middle" font-size="8.7" fill="#475569">clauses / circuit</text>')

    # ================= RIGHT PANEL: EXACT FEASIBILITY INTERVAL + SCALING TABLE =================
    rx, ry, rw = 496, 78, 420

    # Card 1: Exact Number-Line Feasibility Proof on h in [0, 63]
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="178" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#0f172a">2. Exact Feasibility Threshold Proof (at i ≡ 0 mod 5)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 37}" font-size="9.8" fill="#475569">Since x₀ ≥ 20 and y₀ ≤ 40, gadget i = 0 restricts hub h to:</text>')

    # Number line axis h = 0..63
    ax0, ax1, ay = rx + 26, rx + rw - 24, ry + 106
    def hx_pos(v: float) -> float:
        return ax0 + (v / 63.0) * (ax1 - ax0)

    # Shaded regions above axis
    # p0 >= 0: h <= 10 (blue)
    p.append(f'    <rect x="{hx_pos(0):.1f}" y="{ay - 44}" width="{hx_pos(10) - hx_pos(0):.1f}" height="16" rx="3" fill="#dbeafe" stroke="#2563eb" stroke-width="1"/>')
    p.append(f'    <text x="{hx_pos(5):.1f}" y="{ay - 32.5}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#1d4ed8">p₀≥0</text>')
    # r0 >= 0: h <= 30 (purple)
    p.append(f'    <rect x="{hx_pos(0):.1f}" y="{ay - 24}" width="{hx_pos(30) - hx_pos(0):.1f}" height="16" rx="3" fill="#ede9fe" stroke="#7c3aed" stroke-width="1"/>')
    p.append(f'    <text x="{hx_pos(15):.1f}" y="{ay - 12.5}" text-anchor="middle" font-size="8.7" font-weight="700" fill="#5b21b6">r₀ ≥ 0  (h ≤ y₀ − 10 ≤ 30)</text>')

    # SAT window [25, 30] and UNSAT window [31, 63] on the axis
    p.append(f'    <rect x="{hx_pos(25):.1f}" y="{ay + 6}" width="{hx_pos(30) - hx_pos(25):.1f}" height="18" rx="3" fill="#ecfdf5" stroke="#059669" stroke-width="1.3"/>')
    p.append(f'    <rect x="{hx_pos(31):.1f}" y="{ay + 6}" width="{hx_pos(63) - hx_pos(31):.1f}" height="18" rx="3" fill="#fef2f2" stroke="#dc2626" stroke-width="1.3"/>')
    p.append(f'    <text x="{hx_pos(27.5):.1f}" y="{ay + 18.5}" text-anchor="middle" font-size="8.4" font-weight="800" fill="#047857">SAT</text>')
    p.append(f'    <text x="{hx_pos(47):.1f}" y="{ay + 18.5}" text-anchor="middle" font-size="9" font-weight="700" fill="#b91c1c">low = 31 ⇒ UNSAT (both p₀ &lt; 0, r₀ &lt; 0)</text>')

    # Main axis line & ticks
    p.append(f'    <line x1="{ax0}" y1="{ay}" x2="{ax1}" y2="{ay}" stroke="#334155" stroke-width="1.6"/>')
    for tv in (0, 10, 25, 30, 31, 63):
        tx = hx_pos(tv)
        p.append(f'    <line x1="{tx:.1f}" y1="{ay - 4}" x2="{tx:.1f}" y2="{ay + 4}" stroke="#334155" stroke-width="1.4"/>')
        lbl_y = ay + 36 if tv != 31 else ay + 47
        if tv == 31:
            p.append(f'    <line x1="{tx:.1f}" y1="{ay + 24}" x2="{tx:.1f}" y2="{ay + 38}" stroke="#dc2626" stroke-width="1"/>')
        p.append(f'    <text x="{tx:.1f}" y="{lbl_y}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" font-weight="700" fill="{"#dc2626" if tv == 31 else "#334155"}">{tv}</text>')

    # Cliff vertical dashed line at h = 30.5
    cx_cliff = hx_pos(30.5)
    p.append(f'    <line x1="{cx_cliff:.1f}" y1="{ay - 46}" x2="{cx_cliff:.1f}" y2="{ay + 28}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 168}" font-size="9.3" fill="#047857" font-weight="600">hub_60_sat (low=25): witness h = 25, yᵢ = 40 ⇒ rᵢ ≥ 5 satisfies all 60 gadgets</text>')

    # Card 2: Exact 6-Instance Scaling Table
    cy2 = ry + 190
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="206" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">3. Corpus Scaling &amp; Structural Profile (6 Instances)</text>')

    th = cy2 + 37
    p.append(f'    <rect x="{rx + 12}" y="{th - 10}" width="{rw - 24}" height="16" rx="4" fill="#e2e8f0"/>')
    for hx_c, hlbl, anc in [
        (rx + 18, "Instance", "start"),
        (rx + 148, "AIG ANDs", "end"),
        (rx + 216, "CNF Cls", "end"),
        (rx + 276, "XORs", "end"),
        (rx + 332, "Deg CV", "end"),
        (rx + 392, "1C Best", "end"),
    ]:
        p.append(f'    <text x="{hx_c}" y="{th + 1}" text-anchor="{anc}" font-size="8.4" font-weight="700" fill="#334155">{hlbl}</text>')

    rows = [
        ("hub_20_unsat", "4,268", "8,209", "747", "1.16", "8.2 ms", False),
        ("hub_24_unsat", "5,106", "9,820", "893", "1.27", "—", False),
        ("hub_30_unsat", "6,373", "12,249", "1,114", "1.42", "—", False),
        ("hub_60_sat", "12,698", "24,385", "2,219", "2.00", "26.9 ms", True),
        ("hub_60_unsat", "12,701", "24,391", "2,219", "2.00", "23.4 ms", False),
        ("hub_80_unsat", "16,915", "32,478", "2,954", "2.31", "—", False),
    ]
    for i, (nm, ands, cls, xors, cv, best, is_sat) in enumerate(rows):
        ry_r = th + 16 + i * 20.5
        if is_sat:
            p.append(f'    <rect x="{rx + 12}" y="{ry_r - 10.5}" width="{rw - 24}" height="18" rx="3" fill="#ecfdf5"/>')
        p.append(f'    <text x="{rx + 18}" y="{ry_r + 1.5}" font-family="{FONT_MONO}" font-size="8.5" font-weight="700" fill="{"#047857" if is_sat else "#0f172a"}">{nm}</text>')
        p.append(f'    <text x="{rx + 148}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.5" fill="#475569">{ands}</text>')
        p.append(f'    <text x="{rx + 216}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.5" fill="#475569">{cls}</text>')
        p.append(f'    <text x="{rx + 276}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.5" font-weight="600" fill="#7c3aed">{xors}</text>')
        p.append(f'    <text x="{rx + 332}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.5" font-weight="700" fill="#b45309">{cv}</text>')
        p.append(f'    <text x="{rx + 392}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.5" font-weight="700" fill="#1d4ed8">{best}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy2 + 178}" font-size="9.1" fill="#334155">'
        f'Constant ρ{sub("crit")} = 1.42× (Over) · κ = 0.84 · 10,146 total native XOR clauses</text>'
    )
    p.append(
        f'    <text x="{rx + 14}" y="{cy2 + 195}" font-size="9.1" fill="#475569">'
        '4 Formats: AIG (60.5 KB) · CNF (269.7 KB) · XCNF (214.7 KB) · ANF (214.9 KB, deg ≤ 2)</text>'
    )

    p.append("  </g>")
    p.append("</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT_SVG.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
