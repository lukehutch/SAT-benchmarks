#!/usr/bin/env python3
"""Generate a bespoke illustrative SVG diagram (`diagram.svg`) for
`zed-adversarial-php` (Scaled Bit-Level AIGER Pigeonhole Principle Circuits).

Illustrates the single problem family constructed in `src/main.rs`:
  1. Left: Bit-level AIGER 1.9 miter architecture (`build_php_direct` &
     `build_zed_php`) mapping m x n inputs through m ALO OR-chains and
     n*C(m,2) pairwise NAND exclusion gates into a single global AND output
     PO_0, plus UNSAT deficiency vs. SAT bijection controls (php_20_20, 30_30).
  2. Right: Log-scale cubic growth plot of AIG AND gates (647..122,499) and
     Tseitin CNF clauses (1,350..247,350) across n=8..49 showing the uniform
     T_max = 5,000 s baseline timeout wall at PHP^{20}_{19} (Haken 1985) and LRAT proof
     certification in HOL4/cake_lpr.

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import math
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


def sup(s: str) -> str:
    return f'<tspan baseline-shift="super" font-size="72%">{esc(s)}</tspan>'


def build_svg() -> str:
    W, H = 940, 496
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Scaled Bit-Level AIGER Pigeonhole Principle Circuits and CDCL Timeout Wall">',
        "  <defs>",
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '    <marker id="arr-purp" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>',
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        # Header
        f'    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        f'Scaled AIGER Pigeonhole Principle Circuits (zed-adversarial-php)</text>',
        f'    <text x="26" y="53" font-size="11.8" fill="#475569">'
        f'12 native AIGER 1.9 PHP{sup("m")}{sub("n")} circuits: 10 UNSAT scaling PHP{sup("9")}{sub("8")} → PHP{sup("50")}{sub("49")} '
        f'+ 2 SAT bijection controls (PHP{sup("20")}{sub("20")}, PHP{sup("30")}{sub("30")})</text>',
        '    <rect x="774" y="18" width="142" height="24" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>',
        '    <text x="845" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#6d28d9">2 SAT · 10 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: AIGER 1.9 MITER ARCHITECTURE =================
    lx, ly, lw, lh = 24, 78, 434, 396
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">1. Bit-Level AIGER 1.9 Miter Circuit (src/main.rs)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">Pure AND-Inverter graph exported to Tseitin CNF, XCNF &amp; degree-≤2 ANF</text>')

    # Stage diagram card
    mx, my, mw, mh = lx + 14, ly + 48, lw - 28, 174
    p.append(f'    <rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')

    # Stage 1: Primary inputs x[p, h]
    s1x, s1y, s1w, s1h = mx + 12, my + 24, 88, 126
    p.append(f'    <rect x="{s1x}" y="{s1y}" width="{s1w}" height="{s1h}" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
    p.append(f'    <text x="{s1x + s1w / 2:.1f}" y="{s1y + 20}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#1d4ed8">m×n Inputs</text>')
    p.append(f'    <text x="{s1x + s1w / 2:.1f}" y="{s1y + 36}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" font-weight="600" fill="#0f172a">x[p·n + h]</text>')
    # Mini 4x3 grid of variable dots
    for rr in range(4):
        for cc in range(3):
            dx = s1x + 22 + cc * 22
            dy = s1y + 52 + rr * 15
            p.append(f'    <circle cx="{dx}" cy="{dy}" r="3.2" fill="#2563eb" fill-opacity="0.75"/>')
    p.append(f'    <text x="{s1x + s1w / 2:.1f}" y="{s1y + 116}" text-anchor="middle" font-size="8.4" fill="#475569">72 .. 2,450 PIs</text>')

    # Stage 2 Top: ALO OR-chains (De Morgan inverted-input AND cascade)
    s2x, s2w = mx + 126, 152
    p.append(f'    <rect x="{s2x}" y="{my + 18}" width="{s2w}" height="62" rx="7" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
    p.append(f'    <text x="{s2x + s2w / 2:.1f}" y="{my + 35}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#047857">m ALO OR-Chains</text>')
    p.append(f'    <text x="{s2x + s2w / 2:.1f}" y="{my + 50}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.8" fill="#0f172a">¬(¬x[p,0] ∧ … ∧ ¬x[p,n−1])</text>')
    p.append(f'    <text x="{s2x + s2w / 2:.1f}" y="{my + 68}" text-anchor="middle" font-size="8.5" fill="#475569">m(n−1) ANDs · each pigeon ≥1</text>')

    # Stage 2 Bottom: Pairwise AMO exclusion gates
    p.append(f'    <rect x="{s2x}" y="{my + 94}" width="{s2w}" height="62" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>')
    p.append(f'    <text x="{s2x + s2w / 2:.1f}" y="{my + 111}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#b91c1c">n·C(m,2) AMO Gates</text>')
    p.append(f'    <text x="{s2x + s2w / 2:.1f}" y="{my + 126}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.8" fill="#0f172a">¬(x[p,h] ∧ x[q,h])</text>')
    p.append(f'    <text x="{s2x + s2w / 2:.1f}" y="{my + 144}" text-anchor="middle" font-size="8.5" fill="#475569">O(m²n) ANDs · ≤1 per hole</text>')

    # Stage 3: Global AND Miter PO_0
    s3x, s3y, s3w, s3h = mx + 302, my + 48, 92, 78
    p.append(f'    <rect x="{s3x}" y="{s3y}" width="{s3w}" height="{s3h}" rx="8" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/>')
    p.append(f'    <text x="{s3x + s3w / 2:.1f}" y="{s3y + 23}" text-anchor="middle" font-size="10" font-weight="700" fill="#6d28d9">AND Miter</text>')
    p.append(f'    <text x="{s3x + s3w / 2:.1f}" y="{s3y + 40}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.2" font-weight="700" fill="#0f172a">PO₀ = 1</text>')
    p.append(f'    <text x="{s3x + s3w / 2:.1f}" y="{s3y + 56}" text-anchor="middle" font-size="8.3" fill="#475569">Tseitin CNF</text>')
    p.append(f'    <text x="{s3x + s3w / 2:.1f}" y="{s3y + 69}" text-anchor="middle" font-size="8.3" fill="#475569">95–99% Horn</text>')

    # Arrows connecting stages
    p.append(f'    <path d="M {s1x + s1w} {my + 60} L {s2x - 2} {my + 49}" fill="none" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-blue)"/>')
    p.append(f'    <path d="M {s1x + s1w} {my + 114} L {s2x - 2} {my + 125}" fill="none" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-blue)"/>')
    p.append(f'    <path d="M {s2x + s2w} {my + 49} L {s3x - 2} {s3y + 26}" fill="none" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')
    p.append(f'    <path d="M {s2x + s2w} {my + 125} L {s3x - 2} {s3y + 52}" fill="none" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')

    # Bottom Left: Two regime boxes (UNSAT Deficiency vs SAT Bijection Controls) + Four-format box
    by1 = my + mh + 12
    p.append(f'    <rect x="{mx}" y="{by1}" width="198" height="84" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.1"/>')
    p.append(f'    <text x="{mx + 10}" y="{by1 + 19}" font-size="10.4" font-weight="700" fill="#b91c1c">10 UNSAT Instances (m = n+1)</text>')
    p.append(f'    <text x="{mx + 10}" y="{by1 + 36}" font-family="{FONT_MONO}" font-size="8.6" fill="#7f1d1d">php_9_8 .. php_50_49</text>')
    p.append(f'    <text x="{mx + 10}" y="{by1 + 52}" font-size="8.8" fill="#475569">Haken (1985): every pure</text>')
    p.append(f'    <text x="{mx + 10}" y="{by1 + 65}" font-size="8.8" fill="#475569">Resolution proof needs 2{sup("Ω(n)")}</text>')
    p.append(f'    <text x="{mx + 10}" y="{by1 + 78}" font-size="8.8" fill="#475569">steps (up to 247,350 clauses).</text>')

    p.append(f'    <rect x="{mx + 208}" y="{by1}" width="198" height="84" rx="8" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.1"/>')
    p.append(f'    <text x="{mx + 218}" y="{by1 + 19}" font-size="10.4" font-weight="700" fill="#047857">2 SAT Controls (m = n)</text>')
    p.append(f'    <text x="{mx + 218}" y="{by1 + 36}" font-family="{FONT_MONO}" font-size="8.6" fill="#065f46">php_20_20_sat, php_30_30_sat</text>')
    p.append(f'    <text x="{mx + 218}" y="{by1 + 52}" font-size="8.8" fill="#475569">Exact bijection controls (n!</text>')
    p.append(f'    <text x="{mx + 218}" y="{by1 + 65}" font-size="8.8" fill="#475569">valid permutations) guarding</text>')
    p.append(f'    <text x="{mx + 218}" y="{by1 + 78}" font-size="8.8" fill="#475569">against false-UNSAT bugs.</text>')

    # Formal Certification & Format Strip
    by2 = by1 + 94
    p.append(f'    <rect x="{mx}" y="{by2}" width="{mw}" height="56" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{mx + 12}" y="{by2 + 19}" font-size="10.2" font-weight="700" fill="#0f172a">Formal LRAT Certification &amp; 4-Format Footprint</text>')
    p.append(f'    <text x="{mx + 12}" y="{by2 + 34}" font-size="8.9" fill="#334155">• php_9_8 &amp; php_13_12 LRAT proofs verified in HOL4/cake_lpr &amp; lrat-check</text>')
    p.append(f'    <text x="{mx + 12}" y="{by2 + 48}" font-size="8.9" fill="#475569">• AIG (193.7 KB) · CNF (477.0 KB) · XCNF (477.0 KB, 0 XORs) · ANF (203.5 KB, deg≤2)</text>')

    # ================= RIGHT PANEL: LOG-SCALE CUBIC GROWTH + 1-CORE BENCHMARK TABLE =================
    rx, ry, rw = 474, 78, 442

    # Card 1: Log-Scale Cubic Growth Plot (AIG ANDs & CNF Clauses vs hole count n)
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="214" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#0f172a">2. Cubic O(n³) Gate/Clause Scaling &amp; &gt;5,000 s Wall</text>')

    # Plot area
    px0, py0, pw0, ph0 = rx + 54, ry + 34, rw - 72, 134
    p.append(f'    <rect x="{px0}" y="{py0}" width="{pw0}" height="{ph0}" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>')

    # Data points: (holes n, aig_ands, cnf_clauses) for the 10 UNSAT instances
    pts = [
        (8, 647, 1350),
        (12, 2027, 4186),
        (13, 2547, 5250),
        (14, 3149, 6480),
        (15, 3839, 7888),
        (16, 4623, 9486),
        (18, 6497, 13300),
        (19, 7599, 15540),
        (30, 28829, 58528),
        (49, 122499, 247350),
    ]
    n_min, n_max = 6.0, 52.0
    ly_min, ly_max = math.log10(400), math.log10(400000)

    def x_n(n_val: float) -> float:
        return px0 + (n_val - n_min) / (n_max - n_min) * pw0

    def y_v(val: float) -> float:
        return py0 + ph0 - (math.log10(val) - ly_min) / (ly_max - ly_min) * ph0

    # Shaded uniform all-5-baselines timeout zone (n >= 19)
    x_cliff = x_n(19.0)
    p.append(f'    <rect x="{x_cliff:.1f}" y="{py0 + 1}" width="{px0 + pw0 - x_cliff - 1:.1f}" height="{ph0 - 2}" fill="#fef2f2" fill-opacity="0.78"/>')
    p.append(f'    <line x1="{x_cliff:.1f}" y1="{py0}" x2="{x_cliff:.1f}" y2="{py0 + ph0}" stroke="#dc2626" stroke-width="1.6" stroke-dasharray="4,2"/>')
    p.append(f'    <text x="{x_cliff + 6:.1f}" y="{py0 + 15}" font-size="8.8" font-weight="700" fill="#b91c1c">All 5 baselines &gt;5,000 s (n ≥ 19)</text>')

    # Horizontal log grid lines
    for ytick, ylbl in [(1000, "1k"), (10000, "10k"), (100000, "100k")]:
        yy = y_v(ytick)
        p.append(f'    <line x1="{px0}" y1="{yy:.1f}" x2="{px0 + pw0}" y2="{yy:.1f}" stroke="#cbd5e1" stroke-width="0.8" stroke-dasharray="3,2"/>')
        p.append(f'    <text x="{px0 - 6}" y="{yy + 3:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.4" fill="#64748b">{ylbl}</text>')

    # X axis ticks
    for nv in (8, 15, 19, 30, 40, 49):
        xx = x_n(nv)
        p.append(f'    <line x1="{xx:.1f}" y1="{py0 + ph0}" x2="{xx:.1f}" y2="{py0 + ph0 + 4}" stroke="#475569" stroke-width="1"/>')
        p.append(f'    <text x="{xx:.1f}" y="{py0 + ph0 + 15}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.5" fill="#475569">{nv}</text>')
    p.append(f'    <text x="{px0 + pw0 / 2:.1f}" y="{py0 + ph0 + 28}" text-anchor="middle" font-size="9" font-weight="600" fill="#334155">Number of holes n  (m = n + 1 pigeons)</text>')

    # Polylines for CNF Clauses (purple) and AIG AND gates (blue)
    cnf_poly = " ".join(f"{x_n(n):.1f},{y_v(c):.1f}" for n, _, c in pts)
    aig_poly = " ".join(f"{x_n(n):.1f},{y_v(a):.1f}" for n, a, _ in pts)
    p.append(f'    <polyline points="{cnf_poly}" fill="none" stroke="#7c3aed" stroke-width="2.2"/>')
    p.append(f'    <polyline points="{aig_poly}" fill="none" stroke="#2563eb" stroke-width="2.2"/>')

    for n, a, c in pts:
        p.append(f'    <circle cx="{x_n(n):.1f}" cy="{y_v(c):.1f}" r="3.2" fill="#7c3aed" stroke="#ffffff" stroke-width="1"/>')
        p.append(f'    <circle cx="{x_n(n):.1f}" cy="{y_v(a):.1f}" r="3.2" fill="#2563eb" stroke="#ffffff" stroke-width="1"/>')

    # Inline legend inside plot (bottom-right)
    p.append(f'    <rect x="{px0 + pw0 - 150}" y="{py0 + ph0 - 40}" width="142" height="34" rx="5" fill="#ffffff" fill-opacity="0.92" stroke="#cbd5e1" stroke-width="0.9"/>')
    p.append(f'    <line x1="{px0 + pw0 - 142}" y1="{py0 + ph0 - 28}" x2="{px0 + pw0 - 124}" y2="{py0 + ph0 - 28}" stroke="#7c3aed" stroke-width="2.2"/>')
    p.append(f'    <text x="{px0 + pw0 - 118}" y="{py0 + ph0 - 25}" font-size="8.6" font-weight="600" fill="#5b21b6">CNF Clauses (≤247k)</text>')
    p.append(f'    <line x1="{px0 + pw0 - 142}" y1="{py0 + ph0 - 14}" x2="{px0 + pw0 - 124}" y2="{py0 + ph0 - 14}" stroke="#2563eb" stroke-width="2.2"/>')
    p.append(f'    <text x="{px0 + pw0 - 118}" y="{py0 + ph0 - 11}" font-size="8.6" font-weight="600" fill="#1d4ed8">AIG ANDs (≤122k)</text>')

    # Card 2: Exact 1-Core Benchmark Scaling Table (Promoted UNSAT Ladder)
    cy2 = ry + 226
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="170" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">3. 1-Core Benchmark Ladder (Flat CNF, T{sub("max")} = 5,000 s)</text>')

    th = cy2 + 37
    p.append(f'    <rect x="{rx + 12}" y="{th - 10}" width="{rw - 24}" height="16" rx="4" fill="#e2e8f0"/>')
    for hx_c, hlbl, anc in [
        (rx + 18, "Instance", "start"),
        (rx + 150, "CNF Vars", "end"),
        (rx + 216, "Clauses", "end"),
        (rx + 292, "Baselines (5)", "middle"),
        (rx + 388, "Frob. 1C", "middle"),
    ]:
        p.append(f'    <text x="{hx_c}" y="{th + 1}" text-anchor="{anc}" font-size="8.5" font-weight="700" fill="#334155">{hlbl}</text>')

    b_rows = [
        ("php_9_8_unsat", "423", "1,350", "15–474 ms", "1.81 ms", False),
        ("php_16_15_unsat", "2,264", "7,888", "109 s–>5,000 s", "4.54 ms", True),
        ("php_20_19_unsat", "4,350", "15,540", "all 5 >5,000 s", "8.15 ms", True),
        ("php_50_49_unsat", "64,875", "247,350", "all 5 >5,000 s", "119.04 ms", True),
    ]
    for i, (nm, vs, cs, oth, fr, is_to) in enumerate(b_rows):
        ry_r = th + 18 + i * 24
        if is_to:
            p.append(f'    <rect x="{rx + 12}" y="{ry_r - 11.5}" width="{rw - 24}" height="21" rx="3" fill="#fef2f2"/>')
        p.append(f'    <text x="{rx + 18}" y="{ry_r + 1.5}" font-family="{FONT_MONO}" font-size="8.7" font-weight="700" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{rx + 150}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.7" fill="#475569">{vs}</text>')
        p.append(f'    <text x="{rx + 216}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.7" fill="#475569">{cs}</text>')
        p.append(f'    <text x="{rx + 292}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.6" font-weight="700" fill="{"#b91c1c" if is_to else "#334155"}">{esc(oth)}</text>')
        p.append(f'    <text x="{rx + 388}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#047857">{fr}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy2 + 158}" font-size="9" fill="#475569">'
        f'Structural regime: all 12 Over-constrained (ρ{sub("crit")} = 2.56×–3.08× · 95–99% Horn · 0 XORs)</text>'
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
