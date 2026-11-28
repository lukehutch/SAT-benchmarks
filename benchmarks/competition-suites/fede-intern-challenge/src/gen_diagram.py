#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`fede-intern-challenge` (`@fede_intern` 12-Instance Hard SAT Challenge Pack).

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import math
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
    W, H = 920, 512
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Forensic Taxonomy of the 12-Instance fede-intern Hard SAT Challenge Pack">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        '@fede_intern 12-Instance Hard SAT Challenge Pack (fede-intern-challenge)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Forensic structural map of c01–c12 spanning 5 hard mathematical barrier families '
        '(6 SAT / 4 UNSAT / 2 Open TBD)</text>',
        '    <rect x="720" y="18" width="174" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="807" y="34" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">12 Instances · 5 Families</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= TOP ROW: 3 STRUCTURAL FAMILIES (c01-05, c06-07, c08-10) =================
    y1 = 78
    h1 = 148
    w3 = 282
    xs3 = [24, 319, 614]

    # --- Card 1: Uniform Random 3-SAT (c01-c05) ---
    x = xs3[0]
    p.append(f'    <rect x="{x}" y="{y1}" width="{w3}" height="{h1}" rx="9" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
    p.append(f'    <text x="{x + 12}" y="{y1 + 20}" font-size="11.8" font-weight="700" fill="#1d4ed8">1. Critical Random 3-SAT</text>')
    p.append(f'    <rect x="{x + w3 - 68}" y="{y1 + 7}" width="56" height="18" rx="9" fill="#ffffff" stroke="#2563eb" stroke-width="1"/>')
    p.append(f'    <text x="{x + w3 - 40}" y="{y1 + 19.5}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#1d4ed8">c01–c05</text>')
    # Mini 3-SAT factor graph visual on right of card
    fg_x, fg_y = x + 194, y1 + 36
    p.append(f'    <rect x="{fg_x}" y="{fg_y}" width="76" height="62" rx="6" fill="#ffffff" stroke="#bfdbfe" stroke-width="1"/>')
    v_pts = [(fg_x + 16, fg_y + 14), (fg_x + 16, fg_y + 31), (fg_x + 16, fg_y + 48)]
    c_pts = [(fg_x + 58, fg_y + 19), (fg_x + 58, fg_y + 44)]
    for vi, ci, dash in [(0, 0, False), (1, 0, True), (2, 0, False), (0, 1, True), (1, 1, False), (2, 1, True)]:
        d_attr = ' stroke-dasharray="3,2"' if dash else ""
        p.append(f'    <line x1="{v_pts[vi][0] + 5}" y1="{v_pts[vi][1]}" x2="{c_pts[ci][0] - 6}" y2="{c_pts[ci][1]}" stroke="#2563eb" stroke-width="1.1"{d_attr}/>')
    for vx, vy in v_pts:
        p.append(f'    <circle cx="{vx}" cy="{vy}" r="4.5" fill="#dbeafe" stroke="#2563eb" stroke-width="1.2"/>')
    for cx, cy in c_pts:
        p.append(f'    <rect x="{cx - 5}" y="{cy - 5}" width="10" height="10" rx="2" fill="#2563eb"/>')
    # Bullet specs
    c1_lines = [
        "• Pure 3-CNF at α = 4.2600",
        "• n ∈ {300, 350, 400, 450, 500}",
        "• Exact Poisson deg μ = 12.78",
        f'• Right on threshold α{sub("c")} ≈ 4.267',
        f'• Barrier: 2{sup("Ω(n)")} UNSAT refutation',
    ]
    for i, ln in enumerate(c1_lines):
        p.append(f'    <text x="{x + 12}" y="{y1 + 42 + i * 16.5:.1f}" font-size="9.5" fill="#334155">{ln}</text>')
    p.append(f'    <text x="{x + 12}" y="{y1 + 136}" font-size="9.3" font-weight="700" fill="#1d4ed8">c01 UNSAT · c02–c03 TBD · c04–c05 SAT</text>')

    # --- Card 2: Quiet/Balanced Planted 3-SAT (c06-c07) ---
    x = xs3[1]
    p.append(f'    <rect x="{x}" y="{y1}" width="{w3}" height="{h1}" rx="9" fill="#ecfdf5" stroke="#059669" stroke-width="1.3"/>')
    p.append(f'    <text x="{x + 12}" y="{y1 + 20}" font-size="11.8" font-weight="700" fill="#047857">2. Quiet Planted 3-SAT</text>')
    p.append(f'    <rect x="{x + w3 - 68}" y="{y1 + 7}" width="56" height="18" rx="9" fill="#ffffff" stroke="#059669" stroke-width="1"/>')
    p.append(f'    <text x="{x + w3 - 40}" y="{y1 + 19.5}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#047857">c06–c07</text>')
    # Mini balanced polarity histogram visual
    hg_x, hg_y = x + 194, y1 + 36
    p.append(f'    <rect x="{hg_x}" y="{hg_y}" width="76" height="62" rx="6" fill="#ffffff" stroke="#a7f3d0" stroke-width="1"/>')
    # Symmetric bell bars around 0 bias
    bh = [10, 22, 36, 36, 22, 10]
    for idx_b, h_val in enumerate(bh):
        p.append(f'    <rect x="{hg_x + 8 + idx_b * 10}" y="{hg_y + 48 - h_val}" width="7.5" height="{h_val}" rx="1.5" fill="#059669" fill-opacity="0.8"/>')
    p.append(f'    <text x="{hg_x + 38}" y="{hg_y + 58}" text-anchor="middle" font-size="7.6" font-weight="700" fill="#047857">0 polarity bias</text>')

    c2_lines = [
        "• Large 3-CNF at α = 4.2500",
        "• c06: 20k v / 85k c; c07: 50k / 212.5k",
        "• E[|pos−neg|/√d] = 0.796 / 0.798",
        "• Indistinguishable from random 3-SAT",
        "• Barrier: foils greedy CDCL/WalkSAT",
    ]
    for i, ln in enumerate(c2_lines):
        p.append(f'    <text x="{x + 12}" y="{y1 + 42 + i * 16.5:.1f}" font-size="9.5" fill="#334155">{esc(ln)}</text>')
    p.append(f'    <text x="{x + 12}" y="{y1 + 136}" font-size="9.3" font-weight="700" fill="#047857">Both SAT (SID / Survey Prop solves in ~1 s)</text>')

    # --- Card 3: Scrambled Schoolbook Array Factoring (c08-c10) ---
    x = xs3[2]
    p.append(f'    <rect x="{x}" y="{y1}" width="{w3}" height="{h1}" rx="9" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.3"/>')
    p.append(f'    <text x="{x + 12}" y="{y1 + 20}" font-size="11.8" font-weight="700" fill="#6d28d9">3. Scrambled Array Factoring</text>')
    p.append(f'    <rect x="{x + w3 - 68}" y="{y1 + 7}" width="56" height="18" rx="9" fill="#ffffff" stroke="#7c3aed" stroke-width="1"/>')
    p.append(f'    <text x="{x + w3 - 40}" y="{y1 + 19.5}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#6d28d9">c08–c10</text>')
    # Mini 3x3 parallelogram multiplier grid icon
    mg_x, mg_y = x + 194, y1 + 36
    p.append(f'    <rect x="{mg_x}" y="{mg_y}" width="76" height="62" rx="6" fill="#ffffff" stroke="#ddd6fe" stroke-width="1"/>')
    for rr in range(3):
        for cc in range(3):
            gx = mg_x + 28 + cc * 13 - rr * 8
            gy = mg_y + 11 + rr * 14
            p.append(f'    <rect x="{gx}" y="{gy}" width="9" height="9" rx="2" fill="#ede9fe" stroke="#7c3aed" stroke-width="1"/>')
    p.append(f'    <text x="{mg_x + 38}" y="{mg_y + 57}" text-anchor="middle" font-size="7.6" font-weight="700" fill="#6d28d9">3k² vars (A·B=N)</text>')

    c3_lines = [
        "• k×k ripple array (k ∈ {39, 47, 63})",
        "• c10 (40b), c08 (48b), c09 (64b)",
        "• Exact 3k² vars &amp; k(k−1) XOR sums",
        "• 7,550 native XORs recovered in XCNF",
        "• Vars renamed, signs flipped, shuffled",
    ]
    for i, ln in enumerate(c3_lines):
        p.append(f'    <text x="{x + 12}" y="{y1 + 42 + i * 16.5:.1f}" font-size="9.5" fill="#334155">{ln}</text>')
    p.append(f'    <text x="{x + 12}" y="{y1 + 136}" font-size="9.3" font-weight="700" fill="#6d28d9">c08, c09 SAT · c10 UNSAT (prime)</text>')

    # ================= MIDDLE ROW: 2 SC 2025 UNSOLVED FAMILIES (c11, c12) =================
    y2 = 238
    h2 = 136
    w2 = 430
    xs2 = [24, 466]

    # --- Card 4: SC 2025 Unsolved — Ramsey R(4,4) = 18 (c11) ---
    x = xs2[0]
    p.append(f'    <rect x="{x}" y="{y2}" width="{w2}" height="{h2}" rx="9" fill="#fef2f2" stroke="#dc2626" stroke-width="1.3"/>')
    p.append(f'    <text x="{x + 14}" y="{y2 + 21}" font-size="12" font-weight="700" fill="#b91c1c">4. SC 2025 Unsolved: Ramsey R(4, 4) = 18</text>')
    p.append(f'    <rect x="{x + w2 - 82}" y="{y2 + 8}" width="70" height="18" rx="9" fill="#ffffff" stroke="#dc2626" stroke-width="1"/>')
    p.append(f'    <text x="{x + w2 - 47}" y="{y2 + 20.5}" text-anchor="middle" font-family="{mono}" font-size="9.3" font-weight="700" fill="#b91c1c">c11 UNSAT</text>')

    # Mini 2-edge-colored K_6 clique schematic (compact radius so bottom caption has crisp clearance!)
    k_cx, k_cy, k_r = x + 363, y2 + 72, 30
    p.append(f'    <rect x="{x + 312}" y="{y2 + 34}" width="102" height="90" rx="7" fill="#ffffff" stroke="#fecaca" stroke-width="1"/>')
    pts = [(k_cx + k_r * math.cos(2 * math.pi * i / 6 - math.pi / 2),
            k_cy + k_r * math.sin(2 * math.pi * i / 6 - math.pi / 2)) for i in range(6)]
    for i in range(6):
        for j in range(i + 1, 6):
            is_red = (j - i) in (1, 3)
            col_e = "#dc2626" if is_red else "#2563eb"
            p.append(f'    <line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[j][0]:.1f}" y2="{pts[j][1]:.1f}" stroke="{col_e}" stroke-width="1.2" stroke-opacity="0.8"/>')
    for px, py in pts:
        p.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="#0f172a"/>')
    p.append(f'    <text x="{k_cx}" y="{y2 + 118}" text-anchor="middle" font-size="8.2" font-weight="700" fill="#b91c1c">K₁₈: no mono K₄</text>')

    c4_lines = [
        "• GBD: ramsey_4_4_18.normalised (unsolved in SC 2025)",
        "• C(18,2) = 153 edge vars · 2·C(18,4) = 6,120 6-clauses",
        "• Exact regular degree 240 (Deg CV = 0.000, pos = neg)",
        "• Massive symmetry |S₁₈ × Z₂| ≈ 1.28 × 10¹⁶ orbits",
        "• Certified UNSAT via lrat-check + cake_lpr",
    ]
    for i, ln in enumerate(c4_lines):
        p.append(f'    <text x="{x + 14}" y="{y2 + 43 + i * 17:.1f}" font-size="9.6" fill="#334155">{esc(ln)}</text>')

    # --- Card 5: SC 2025 Unsolved — Clique-Coloring (15,7,6) (c12) ---
    x = xs2[1]
    p.append(f'    <rect x="{x}" y="{y2}" width="{w2}" height="{h2}" rx="9" fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>')
    p.append(f'    <text x="{x + 14}" y="{y2 + 21}" font-size="12" font-weight="700" fill="#b45309">5. SC 2025 Unsolved: Clique-Coloring (15, 7, 6)</text>')
    p.append(f'    <rect x="{x + w2 - 82}" y="{y2 + 8}" width="70" height="18" rx="9" fill="#ffffff" stroke="#d97706" stroke-width="1"/>')
    p.append(f'    <text x="{x + w2 - 47}" y="{y2 + 20.5}" text-anchor="middle" font-family="{mono}" font-size="9.3" font-weight="700" fill="#b45309">c12 UNSAT</text>')

    # Mini Clique(7) -> Color(6) PHP collision visual (clean bottom margin above caption!)
    cc_x, cc_y = x + 312, y2 + 34
    p.append(f'    <rect x="{cc_x}" y="{cc_y}" width="102" height="90" rx="7" fill="#ffffff" stroke="#fde68a" stroke-width="1"/>')
    c_pal = ["#2563eb", "#059669", "#7c3aed", "#d97706", "#0891b2", "#db2777"]
    for i in range(7):
        qy = cc_y + 10 + i * 9.6
        p.append(f'    <circle cx="{cc_x + 18}" cy="{qy:.1f}" r="3" fill="{"#dc2626" if i == 6 else "#0f172a"}"/>')
        if i < 6:
            p.append(f'    <line x1="{cc_x + 21}" y1="{qy:.1f}" x2="{cc_x + 76}" y2="{cc_y + 14 + i * 10.6:.1f}" stroke="{c_pal[i]}" stroke-width="1.2"/>')
        else:
            p.append(f'    <line x1="{cc_x + 21}" y1="{qy:.1f}" x2="{cc_x + 76}" y2="{cc_y + 67:.1f}" stroke="#dc2626" stroke-width="1.3" stroke-dasharray="2,2"/>')
    for j in range(6):
        cy_j = cc_y + 14 + j * 10.6
        p.append(f'    <rect x="{cc_x + 77}" y="{cy_j - 3.6:.1f}" width="10" height="7.2" rx="1.5" fill="{c_pal[j]}"/>')
    p.append(f'    <text x="{cc_x + 51}" y="{cc_y + 84}" text-anchor="middle" font-size="8.2" font-weight="700" fill="#b45309">7-clique ↛ 6 colors</text>')

    c5_lines = [
        "• GBD: cliquecolouring_n15_k7_c6 (unsolved in SC 2025)",
        "• 300 vars (105 edges + 105 clique + 90 color) · 6,337 cls",
        f'• Indirect PHP₆⁷ via p{sub("r,j")} ↔ ⋁{sub("v")} (q{sub("v,r")} ∧ c{sub("v,j")})',
        "• Exponential Resolution lower bound (Pudlák 1997)",
        "• Extended Resolution closes in 6 ms (cake_lpr verified)",
    ]
    for i, ln in enumerate(c5_lines):
        p.append(f'    <text x="{x + 14}" y="{y2 + 43 + i * 17:.1f}" font-size="9.6" fill="#334155">{ln}</text>')

    # ================= BOTTOM STRIP: COMPLETE 12-INSTANCE MATRIX (c01..c12) =================
    by = 386
    bh = 108
    p.append(f'    <rect x="24" y="{by}" width="872" height="{bh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="38" y="{by + 20}" font-size="11.8" font-weight="700" fill="#0f172a">Complete 12-Instance Challenge Inventory (c01–c12 · 4 Formats: CNF, AIG, XCNF, ANF)</text>')

    tiles = [
        ("c01", "300 v", "UNSAT", "#2563eb", "#dc2626", "#fef2f2"),
        ("c02", "350 v", "TBD", "#2563eb", "#b45309", "#fffbeb"),
        ("c03", "400 v", "TBD", "#2563eb", "#b45309", "#fffbeb"),
        ("c04", "450 v", "SAT", "#2563eb", "#047857", "#ecfdf5"),
        ("c05", "500 v", "SAT", "#2563eb", "#047857", "#ecfdf5"),
        ("c06", "20k v", "SAT", "#059669", "#047857", "#ecfdf5"),
        ("c07", "50k v", "SAT", "#059669", "#047857", "#ecfdf5"),
        ("c08", "6.6k v", "SAT", "#7c3aed", "#047857", "#ecfdf5"),
        ("c09", "11.9k v", "SAT", "#7c3aed", "#047857", "#ecfdf5"),
        ("c10", "4.6k v", "UNSAT", "#7c3aed", "#dc2626", "#fef2f2"),
        ("c11", "153 v", "UNSAT", "#dc2626", "#dc2626", "#fef2f2"),
        ("c12", "300 v", "UNSAT", "#d97706", "#dc2626", "#fef2f2"),
    ]
    tw = 66
    tgap = 5.2
    tx0 = 36
    ty0 = by + 30
    for i, (cid, nstr, verd, fam_c, v_col, v_bg) in enumerate(tiles):
        tx = tx0 + i * (tw + tgap)
        p.append(f'    <rect x="{tx:.1f}" y="{ty0}" width="{tw}" height="56" rx="6" fill="#ffffff" stroke="{fam_c}" stroke-width="1.3"/>')
        p.append(f'    <rect x="{tx:.1f}" y="{ty0}" width="{tw}" height="4.5" rx="2" fill="{fam_c}"/>')
        p.append(f'    <text x="{tx + tw/2:.1f}" y="{ty0 + 20}" text-anchor="middle" font-family="{mono}" font-size="10.5" font-weight="700" fill="#0f172a">{cid}</text>')
        p.append(f'    <text x="{tx + tw/2:.1f}" y="{ty0 + 34}" text-anchor="middle" font-size="8.6" fill="#475569">{nstr}</text>')
        p.append(f'    <rect x="{tx + 8:.1f}" y="{ty0 + 39}" width="{tw - 16}" height="13" rx="6.5" fill="{v_bg}"/>')
        p.append(f'    <text x="{tx + tw/2:.1f}" y="{ty0 + 48.5}" text-anchor="middle" font-size="8.1" font-weight="700" fill="{v_col}">{verd}</text>')

    p.append(
        f'    <text x="38" y="{by + 100}" font-size="9.4" fill="#475569">'
        'Top bar color = family (Blue: Rand 3-SAT · Green: Quiet Planted · Purple: Array Factoring · Red: Ramsey · Amber: Clique-Coloring) · Total: 7,550 XORs</text>'
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
