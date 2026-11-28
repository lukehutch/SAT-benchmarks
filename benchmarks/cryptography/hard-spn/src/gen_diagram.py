#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `hard-spn` benchmark collection.

Illustrates the LowMC / SPN-style linear-form + nonlinear circuit architecture
implemented in `src/main.rs`:
  - Shared primary input state x in F_2^n (n in {48, 64, 96, 128})
  - Affine F_2 diffusion layer L x = b (r = n/2 sparse 5-input parity rows)
  - 3-input F_2 linear forms l_a, l_b, l_c = x_i ^ x_j ^ x_k feeding into
    nonlinear S-box gates (And, Maj_3, Mux) with planted secret targets v_g
    (and last-gate flip for spn_unsat_n48_d24)
  - Dual solver barrier & exact 4-instance parameter summary.

Usage:
    python3 src/gen_diagram.py
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


def build_svg() -> str:
    W, H = 920, 468
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Hard SPN / LowMC-style linear-form and nonlinear S-box circuit architecture">',
        "<defs>",
        '  <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>',
        '  <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '  <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>',
        '  <marker id="arr-amber" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/></marker>',
        "</defs>",
        # White card canvas for both GitHub light & dark modes
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Hard SPN / LowMC-Style Linear-Form + Nonlinear Circuits (hard-spn)</text>",
        '<text x="26" y="53" font-size="11.8" fill="#475569">'
        "Affine 𝔽₂ diffusion layer (r = n/2 sparse 5-XOR rows) coupled with 3-bit S-box gates "
        "(And, Maj₃, Mux) evaluated on 3-input linear forms ℓ = xᵢ ⊕ xⱼ ⊕ xₖ</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT/CENTER SPN ARCHITECTURE PANEL =====================
    parts.append(
        '<rect x="24" y="76" width="602" height="320" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        '<text x="38" y="96" font-size="12.5" font-weight="700" fill="#0f172a">'
        "Circuit Topology (src/main.rs — LowMC / SPN Algebraic Round Coupling)</text>"
    )

    # --- Column 1: Input State Vector x in F_2^n ---
    ix, iy, iw, ih = 38, 112, 84, 266
    parts.append(
        f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="8" '
        'fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{ix + iw/2:.1f}" y="{iy + 18}" text-anchor="middle" '
        'font-size="11" font-weight="700" fill="#0f172a">Inputs x</text>'
    )
    parts.append(
        f'<text x="{ix + iw/2:.1f}" y="{iy + 32}" text-anchor="middle" '
        'font-size="9.5" fill="#475569">x ∈ 𝔽₂ⁿ (k⊕x★)</text>'
    )
    bit_labels = ["x₀", "x₁", "x₂", "x₃", "x₄", "⋮", "xₙ₋₂", "xₙ₋₁"]
    bit_ys: list[float] = []
    for idx, lbl in enumerate(bit_labels):
        by = iy + 52 + idx * 27
        bit_ys.append(by)
        if lbl == "⋮":
            parts.append(
                f'<text x="{ix + iw/2:.1f}" y="{by + 4:.1f}" text-anchor="middle" '
                'font-size="13" font-weight="700" fill="#64748b">⋮</text>'
            )
        else:
            parts.append(
                f'<rect x="{ix + 12}" y="{by - 10:.1f}" width="{iw - 24}" height="20" rx="5" '
                'fill="#eff6ff" stroke="#2563eb" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{ix + iw/2:.1f}" y="{by + 4:.1f}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="10.2" font-weight="600" fill="#1d4ed8">{lbl}</text>'
            )

    # --- Upper Path: Affine F_2 Diffusion Matrix L x = b ---
    ux, uy, uw, uh = 158, 112, 452, 108
    parts.append(
        f'<rect x="{ux}" y="{uy}" width="{uw}" height="{uh}" rx="8" '
        'fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{ux + 12}" y="{uy + 18}" font-size="11.2" font-weight="700" fill="#1d4ed8">'
        "1. Affine 𝔽₂ Linear Diffusion Layer:  L · x = b (mod 2)</text>"
    )
    parts.append(
        f'<text x="{ux + uw - 12}" y="{uy + 18}" text-anchor="end" '
        'font-size="9.8" font-weight="600" fill="#2563eb">r = n/2 eqs · d = n/2</text>'
    )

    # Draw compact 5x10 sparse binary diffusion matrix L (5 taps per row)
    mat_x, mat_y = ux + 16, uy + 28
    cw, ch = 13, 12
    # Deterministic 5-tap rows illustrating sparse 5-input parity rows
    l_rows = [
        {0, 2, 4, 7, 9},
        {1, 3, 4, 6, 8},
        {0, 1, 5, 7, 8},
        {2, 3, 5, 6, 9},
        {0, 4, 6, 8, 9},
    ]
    parts.append(
        f'<rect x="{mat_x - 3}" y="{mat_y - 2}" width="{10 * cw + 6}" height="{5 * ch + 4}" '
        'rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>'
    )
    for r_idx, taps in enumerate(l_rows):
        for c_idx in range(10):
            cx = mat_x + c_idx * cw
            cy = mat_y + r_idx * ch
            if c_idx in taps:
                parts.append(
                    f'<rect x="{cx + 1.2:.1f}" y="{cy + 1.2:.1f}" width="{cw - 2.4:.1f}" '
                    f'height="{ch - 2.4:.1f}" rx="2" fill="#2563eb"/>'
                )
            else:
                parts.append(
                    f'<rect x="{cx + 1.2:.1f}" y="{cy + 1.2:.1f}" width="{cw - 2.4:.1f}" '
                    f'height="{ch - 2.4:.1f}" rx="2" fill="#e2e8f0"/>'
                )
    # Matrix label + multiplication = b
    mx_end = mat_x + 10 * cw + 6
    parts.append(
        f'<text x="{mx_end + 10}" y="{mat_y + 34}" font-size="13" font-weight="700" fill="#1d4ed8">· x =</text>'
    )
    # Vector b (5 cells)
    bx_v = mx_end + 48
    b_vals = [1, 0, 1, 1, 0]
    parts.append(
        f'<rect x="{bx_v - 2}" y="{mat_y - 2}" width="18" height="{5 * ch + 4}" '
        'rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>'
    )
    for r_idx, bv in enumerate(b_vals):
        cy = mat_y + r_idx * ch + 9.5
        parts.append(
            f'<text x="{bx_v + 7}" y="{cy:.1f}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="9.5" font-weight="700" '
            f'fill="{"#1d4ed8" if bv else "#64748b"}">{bv}</text>'
        )
    # Explanation right of vector b
    tx_u = bx_v + 28
    parts.append(
        f'<text x="{tx_u}" y="{mat_y + 12}" font-size="10.2" font-weight="600" fill="#0f172a">'
        "Row j:  xᵢ₁ ⊕ xᵢ₂ ⊕ xᵢ₃ ⊕ xᵢ₄ ⊕ xᵢ₅ = bⱼ</text>"
    )
    parts.append(
        f'<text x="{tx_u}" y="{mat_y + 28}" font-size="9.6" fill="#475569">'
        "Planted secret x★ sets b = L·x★ (mod 2).</text>"
    )
    parts.append(
        f'<text x="{tx_u}" y="{mat_y + 43}" font-size="9.6" fill="#475569">'
        "Leaves 2ᵈ affine candidates (d = n/2 ∈ {24..64}).</text>"
    )
    parts.append(
        f'<text x="{tx_u}" y="{mat_y + 58}" font-size="9.4" font-weight="600" fill="#1d4ed8">'
        "Native XOR region: 161–578 extracted XORs</text>"
    )

    # Wires from x bus into Diffusion Layer
    for wy in (bit_ys[0], bit_ys[1], bit_ys[2]):
        parts.append(
            f'<path d="M {ix + iw} {wy:.1f} C {ix + iw + 18} {wy:.1f}, {ux - 18} {uy + 48:.1f}, {ux - 2} {uy + 48:.1f}" '
            'fill="none" stroke="#2563eb" stroke-width="1.3" stroke-opacity="0.75" marker-end="url(#arr-blue)"/>'
        )

    # --- Lower Path: 3-Input Linear Forms -> Nonlinear S-Box Layer ---
    lx, ly, lw, lh = 158, 232, 452, 146
    parts.append(
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{lx + 12}" y="{ly + 18}" font-size="11.2" font-weight="700" fill="#0f172a">'
        "2. Linear-Form Substitution Layer (mₙₗ ∈ {38, 55, 85, 150} S-Box Gates)</text>"
    )

    # Stage A: 3-Input F_2 Linear Forms (Purple boxes)
    fx = lx + 14
    fw = 132
    forms = [
        (ly + 30, "ℓₐ = xₐ₁ ⊕ xₐ₂ ⊕ xₐ₃", "3-XOR form a"),
        (ly + 66, "ℓ_b = x_b₁ ⊕ x_b₂ ⊕ x_b₃", "3-XOR form b"),
        (ly + 102, "ℓ_c = x_c₁ ⊕ x_c₂ ⊕ x_c₃", "3-XOR form c"),
    ]
    # Clean Unicode subscripts without underscores
    forms_clean = [
        (ly + 30, "ℓₐ = xᵢ ⊕ xⱼ ⊕ xₖ", "3-input 𝔽₂ form"),
        (ly + 66, "ℓ_b", "3-input 𝔽₂ form"),
        (ly + 102, "ℓ_c", "3-input 𝔽₂ form"),
    ]
    form_texts = [
        ("ℓ₁ = xᵢ ⊕ xⱼ ⊕ xₖ", "3-input 𝔽₂ form"),
        ("ℓ₂ = xₚ ⊕ x_q ⊕ xᵣ", "3-input 𝔽₂ form"),
        ("ℓ₃ = xᵤ ⊕ xᵥ ⊕ x_w", "3-input 𝔽₂ form"),
    ]
    form_texts_clean = [
        ("ℓ₁ = xₐ ⊕ xᵦ ⊕ xᵧ", "3-input 𝔽₂ form"),
        ("ℓ₂ = xᵢ ⊕ xⱼ ⊕ xₖ", "3-input 𝔽₂ form"),
        ("ℓ₃ = xₚ ⊕ xᵣ ⊕ xₛ", "3-input 𝔽₂ form"),
    ]
    form_ys = [ly + 30, ly + 67, ly + 104]
    for f_y, (ft1, ft2) in zip(form_ys, form_texts_clean):
        parts.append(
            f'<rect x="{fx}" y="{f_y}" width="{fw}" height="30" rx="6" '
            'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>'
        )
        parts.append(
            f'<text x="{fx + fw/2:.1f}" y="{f_y + 13}" text-anchor="middle" '
            f'font-size="10" font-weight="700" fill="#6d28d9">{ft1}</text>'
        )
        parts.append(
            f'<text x="{fx + fw/2:.1f}" y="{f_y + 25}" text-anchor="middle" '
            f'font-size="8.7" fill="#475569">{ft2}</text>'
        )

    # Wires from x bus into 3-XOR linear forms
    for wy, fy_t in [(bit_ys[3], form_ys[0] + 15), (bit_ys[4], form_ys[1] + 15), (bit_ys[6], form_ys[2] + 15), (bit_ys[7], form_ys[2] + 15)]:
        parts.append(
            f'<path d="M {ix + iw} {wy:.1f} C {ix + iw + 24} {wy:.1f}, {fx - 26} {fy_t:.1f}, {fx - 2} {fy_t:.1f}" '
            'fill="none" stroke="#7c3aed" stroke-width="1.25" stroke-opacity="0.75" marker-end="url(#arr-purple)"/>'
        )

    # Stage B: Nonlinear 3-Bit S-Box Gate Bank (Amber cards)
    sx = fx + fw + 34
    sw = 152
    sboxes = [
        (form_ys[0], "g ≡ 0:  And(ℓ₁, ℓ₂)", "deg-2 quadratic", "#fffbeb", "#d97706", "#b45309"),
        (form_ys[1], "g ≡ 1:  Maj₃(ℓ₁, ℓ₂, ℓ₃)", "3-bit majority S-box", "#fffbeb", "#d97706", "#b45309"),
        (form_ys[2], "g ≡ 2:  Mux(ℓ₁, ℓ₂, ℓ₃)", "ite(ℓ₁, ℓ₂, ℓ₃)", "#fffbeb", "#d97706", "#b45309"),
    ]
    for s_y, st1, st2, bg, bd, fg in sboxes:
        parts.append(
            f'<rect x="{sx}" y="{s_y}" width="{sw}" height="30" rx="6" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1.25"/>'
        )
        parts.append(
            f'<text x="{sx + sw/2:.1f}" y="{s_y + 13}" text-anchor="middle" '
            f'font-size="10" font-weight="700" fill="{fg}">{st1}</text>'
        )
        parts.append(
            f'<text x="{sx + sw/2:.1f}" y="{s_y + 25}" text-anchor="middle" '
            f'font-size="8.7" fill="#475569">{st2}</text>'
        )

    # Cross-wiring from linear forms to S-boxes
    for fy_c in [y + 15 for y in form_ys]:
        for sy_c in [y + 15 for y in form_ys]:
            if abs(fy_c - sy_c) <= 40:
                parts.append(
                    f'<line x1="{fx + fw}" y1="{fy_c}" x2="{sx - 2}" y2="{sy_c}" '
                    'stroke="#7c3aed" stroke-width="1.05" stroke-opacity="0.65" marker-end="url(#arr-purple)"/>'
                )

    # Stage C: Target Assertions (SAT planted vs UNSAT flipped last gate)
    ax = sx + sw + 26
    aw = 82
    asserts = [
        (form_ys[0], "= v₀ (SAT)", "#ecfdf5", "#059669", "#047857"),
        (form_ys[1], "= v₁ (SAT)", "#ecfdf5", "#059669", "#047857"),
        (form_ys[2], "= ¬vₘ (UNSAT)", "#fef2f2", "#dc2626", "#b91c1c"),
    ]
    for a_y, at, bg, bd, fg in asserts:
        parts.append(
            f'<line x1="{sx + sw}" y1="{a_y + 15}" x2="{ax - 2}" y2="{a_y + 15}" '
            'stroke="#d97706" stroke-width="1.3" marker-end="url(#arr-amber)"/>'
        )
        parts.append(
            f'<rect x="{ax}" y="{a_y + 2}" width="{aw}" height="26" rx="5" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1.15"/>'
        )
        parts.append(
            f'<text x="{ax + aw/2:.1f}" y="{a_y + 18.5}" text-anchor="middle" '
            f'font-size="9.4" font-weight="700" fill="{fg}">{at}</text>'
        )

    # ===================== RIGHT SIDE PANEL: BARRIER + SUITE TABLE =====================
    rx, rw = 640, 256
    # Card 1: Dual Algebraic-CDCL Hardness Barrier
    parts.append(
        f'<rect x="{rx}" y="76" width="{rw}" height="146" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="96" font-size="12" font-weight="700" fill="#0f172a">'
        "Why Linear Forms Defeat Flat CDCL</text>"
    )
    bullets = [
        ("● Direct inputs masked:", "S-boxes read ℓ = xᵢ ⊕ xⱼ ⊕ xₖ,", "not raw bits xᵢ — blocking BCP."),
        ("● Pure Gauss fails:", "And / Maj₃ / Mux introduce", "degree-2 terms over 𝔽₂."),
        ("● Solver gap (n = 128):", "Kissat 4.33 s · CMS CNF 10.8 s", "vs. 𝔽₂-aware solving 38 ms."),
    ]
    by_b = 115
    for b_h, b_1, b_2 in bullets:
        parts.append(
            f'<text x="{rx + 12}" y="{by_b}" font-size="9.8" font-weight="700" fill="#1e293b">{b_h}</text>'
        )
        parts.append(
            f'<text x="{rx + 22}" y="{by_b + 13}" font-size="9.3" fill="#475569">{b_1}</text>'
        )
        parts.append(
            f'<text x="{rx + 22}" y="{by_b + 25}" font-size="9.3" fill="#475569">{b_2}</text>'
        )
        by_b += 36

    # Card 2: Exact Suite Instances Table
    parts.append(
        f'<rect x="{rx}" y="232" width="{rw}" height="164" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="252" font-size="12" font-weight="700" fill="#0f172a">'
        "Suite Instances (3 SAT / 1 UNSAT)</text>"
    )
    # Table header
    ty = 270
    parts.append(f'<rect x="{rx + 10}" y="{ty - 11}" width="{rw - 20}" height="18" rx="4" fill="#e2e8f0"/>')
    cols_t = [(rx + 15, "Instance", "start"), (rx + 112, "n / d", "middle"), (rx + 156, "S-box", "middle"), (rx + 216, "Ans", "middle")]
    for cx_t, ch_t, anc in cols_t:
        parts.append(
            f'<text x="{cx_t}" y="{ty + 1}" text-anchor="{anc}" font-size="9.2" font-weight="700" fill="#334155">{ch_t}</text>'
        )
    rows_spn = [
        ("n48_d24", "48 / 24", "38*", "UNSAT", "#fef2f2", "#dc2626"),
        ("n64_d32", "64 / 32", "55", "SAT", "#ecfdf5", "#059669"),
        ("n96_d48", "96 / 48", "85", "SAT", "#ecfdf5", "#059669"),
        ("n128_d64", "128 / 64", "150", "SAT", "#ecfdf5", "#059669"),
    ]
    for r_i, (nm, nd, sb, ans, pbg, pfg) in enumerate(rows_spn):
        ry = ty + 20 + r_i * 24
        if r_i % 2 == 1:
            parts.append(f'<rect x="{rx + 10}" y="{ry - 12}" width="{rw - 20}" height="21" rx="3" fill="#ffffff"/>')
        parts.append(
            f'<text x="{rx + 15}" y="{ry + 2}" font-family="{FONT_MONO}" font-size="9.5" font-weight="600" fill="#0f172a">{nm}</text>'
        )
        parts.append(
            f'<text x="{rx + 112}" y="{ry + 2}" text-anchor="middle" font-size="9.5" fill="#334155">{nd}</text>'
        )
        parts.append(
            f'<text x="{rx + 156}" y="{ry + 2}" text-anchor="middle" font-size="9.5" fill="#334155">{sb}</text>'
        )
        parts.append(
            f'<rect x="{rx + 190}" y="{ry - 10}" width="50" height="16" rx="4" fill="{pbg}" stroke="{pfg}" stroke-width="0.9"/>'
        )
        parts.append(
            f'<text x="{rx + 215}" y="{ry + 1.5}" text-anchor="middle" font-size="8.8" font-weight="700" fill="{pfg}">{ans}</text>'
        )
    parts.append(
        f'<text x="{rx + 12}" y="388" font-size="8.8" fill="#64748b">'
        "*n48_d24 flips last S-box target bit v₃₇ → UNSAT</text>"
    )

    # ===================== BOTTOM SUMMARY BAR =====================
    by_bar = 408
    pills = [
        (24, 210, "#eff6ff", "#2563eb", "#1d4ed8", "AIG Origin: 969–3,643 ANDs"),
        (244, 214, "#f5f3ff", "#7c3aed", "#6d28d9", "Native XORs: 161–578 (1,328 total)"),
        (468, 206, "#fffbeb", "#d97706", "#b45309", "ρ_crit = 1.06×–1.11× (Near-crit)"),
        (684, 212, "#ecfdf5", "#059669", "#047857", "4 Formats: AIG · CNF · XCNF · ANF"),
    ]
    for px, pw, bg, bd, fg, lbl in pills:
        # Replace underscore in ρ_crit with crisp subscript
        lbl_u = lbl.replace("ρ_crit", "ρ_c")
        parts.append(
            f'<rect x="{px}" y="{by_bar}" width="{pw}" height="34" rx="7" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{px + pw/2:.1f}" y="{by_bar + 21}" text-anchor="middle" '
            f'font-size="10.2" font-weight="700" fill="{fg}">{esc(lbl_u)}</text>'
        )

    parts.append("</g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
