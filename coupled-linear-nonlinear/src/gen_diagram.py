#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `coupled-linear-nonlinear` benchmark collection.

Illustrates the dual-branch algebraic-Boolean circuit construction in
`src/main.rs`:
  - Shared primary inputs x in F_2^n (n in {128, 256, 512})
  - Branch A: Under-determined F_2 linear parity core A x = b (r sparse 5-XOR
    equations leaving an affine subspace S_lin of dimension d = n - r)
  - Branch B: Direct nonlinear gate layer (Maj_3, And, Mux) wired directly
    to primary inputs x_a, x_b, x_c defining algebraic variety S_nl
  - Geometric intersection: SAT planted witness x* in S_lin ∩ S_nl vs
    UNSAT flipped-gate empty intersection S_lin ∩ S_nl' = ∅.

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
    W, H = 920, 472
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Coupled F2-linear parity core and nonlinear Boolean gate circuit intersection">',
        "<defs>",
        '  <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '  <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>',
        '  <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>',
        "</defs>",
        # Explicit white card background for GitHub light & dark modes
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Coupled 𝔽₂-Linear + Nonlinear Boolean Circuits (coupled-linear-nonlinear)</text>",
        '<text x="26" y="53" font-size="11.8" fill="#475569">'
        "Jointly satisfying an under-determined 𝔽₂ parity subspace (dim d = n − r) and direct nonlinear "
        "Maj₃ / And / Mux constraints on primary inputs</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: DUAL-BRANCH COUPLED CIRCUIT =====================
    px1, py1, pw1, ph1 = 24, 76, 534, 326
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 20}" font-size="12.2" font-weight="700" fill="#0f172a">'
        "Coupled Miter Architecture (src/main.rs)</text>"
    )

    # Top Shared Primary Input Bus
    bx, by, bw, bh = px1 + 18, py1 + 30, pw1 - 36, 36
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" '
        'fill="#ffffff" stroke="#64748b" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{bx + 12}" y="{by + 22}" font-size="10.5" font-weight="700" fill="#0f172a">'
        "Shared Primary Inputs x ∈ 𝔽₂ⁿ:</text>"
    )
    # Draw compact bit pills inside bus
    bus_bits = ["x₀", "x₁", "x₂", "x₃", "…", "xₐ", "x_b", "x_c", "…", "xₙ₋₁"]
    bus_bits_clean = ["x₀", "x₁", "x₂", "x₃", "…", "xᵢ", "xⱼ", "xₖ", "…", "xₙ₋₁"]
    for idx, bl in enumerate(bus_bits_clean):
        qx = bx + 188 + idx * 30
        if bl == "…":
            parts.append(
                f'<text x="{qx + 12}" y="{by + 22}" text-anchor="middle" font-size="11" font-weight="700" fill="#64748b">…</text>'
            )
        else:
            parts.append(
                f'<rect x="{qx}" y="{by + 8}" width="26" height="20" rx="4" fill="#eff6ff" stroke="#93c5fd" stroke-width="0.9"/>'
            )
            parts.append(
                f'<text x="{qx + 13}" y="{by + 21.5}" text-anchor="middle" font-family="{FONT_MONO}" '
                f'font-size="8.8" font-weight="600" fill="#1d4ed8">{bl}</text>'
            )

    # Left Sub-Branch: Linear Core (Blue)
    lx, ly, lw, lh = px1 + 18, py1 + 90, 240, 178
    parts.append(
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" '
        'fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{lx + lw/2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="11.2" font-weight="700" fill="#1d4ed8">Linear 𝔽₂ Core  (A·x = b)</text>'
    )
    parts.append(
        f'<text x="{lx + lw/2:.1f}" y="{ly + 34}" text-anchor="middle" '
        'font-size="9.3" fill="#475569">r sparse 5-input XOR assertions</text>'
    )

    # Mini sparse 5x12 parity matrix inside Linear Core
    mx, my = lx + 16, ly + 44
    mcw, mch = 13, 12
    mat_taps = [
        {0, 2, 5, 8, 11},
        {1, 3, 5, 7, 10},
        {0, 4, 6, 9, 11},
        {2, 3, 6, 8, 9},
        {1, 4, 7, 10, 11},
    ]
    parts.append(
        f'<rect x="{mx - 2}" y="{my - 2}" width="{12 * mcw + 4}" height="{5 * mch + 4}" '
        'rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>'
    )
    for r_i, taps in enumerate(mat_taps):
        for c_i in range(12):
            fill = "#2563eb" if c_i in taps else "#e2e8f0"
            parts.append(
                f'<rect x="{mx + c_i * mcw + 1:.1f}" y="{my + r_i * mch + 1:.1f}" '
                f'width="{mcw - 2:.1f}" height="{mch - 2:.1f}" rx="1.8" fill="{fill}"/>'
            )
    parts.append(
        f'<text x="{mx + 12 * mcw + 10}" y="{my + 34}" font-size="10.5" font-weight="700" fill="#1d4ed8">= b</text>'
    )
    parts.append(
        f'<text x="{lx + 12}" y="{ly + 123}" font-size="9.5" fill="#1e293b">'
        "• Rank r, nullspace dim d = n − r</text>"
    )
    parts.append(
        f'<text x="{lx + 12}" y="{ly + 137}" font-size="9.5" fill="#1e293b">'
        "• Affine subspace |S_lin| = 2ᵈ</text>"
    )
    # Barrier pill inside Linear Core
    parts.append(
        f'<rect x="{lx + 10}" y="{ly + 146}" width="{lw - 20}" height="22" rx="5" '
        'fill="#ffffff" stroke="#2563eb" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{lx + lw/2:.1f}" y="{ly + 160.5}" text-anchor="middle" '
        'font-size="9.1" font-weight="700" fill="#1d4ed8">Gauss alone: 2ᵈ free DOF (under-det.)</text>'
    )

    # Right Sub-Branch: Direct Nonlinear Gates (Purple)
    nx, ny, nw, nh = px1 + 276, py1 + 90, 240, 178
    parts.append(
        f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="8" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{nx + nw/2:.1f}" y="{ny + 19}" text-anchor="middle" '
        'font-size="11.2" font-weight="700" fill="#6d28d9">Direct Nonlinear Layer</text>'
    )
    parts.append(
        f'<text x="{nx + nw/2:.1f}" y="{ny + 34}" text-anchor="middle" '
        'font-size="9.3" fill="#475569">mₙₗ gates wired directly to xᵢ, xⱼ, xₖ</text>'
    )

    # 3 distinct nonlinear gate blocks
    gates = [
        (ny + 44, "Maj₃(xᵢ, xⱼ, xₖ) = v₀", "xᵢxⱼ ⊕ xᵢxₖ ⊕ xⱼxₖ (deg 2)", "#ffffff", "#7c3aed"),
        (ny + 78, "And(xᵢ, xⱼ) = v₁", "xᵢ ∧ xⱼ  (deg 2)", "#ffffff", "#7c3aed"),
        (ny + 112, "Mux(xᵢ, xⱼ, xₖ) = v₂*", "ite(xᵢ, xⱼ, xₖ)  (*flip ⇒ UNSAT)", "#fef2f2", "#dc2626"),
    ]
    for gy, gt1, gt2, gbg, gbd in gates:
        parts.append(
            f'<rect x="{nx + 12}" y="{gy}" width="{nw - 24}" height="28" rx="5" '
            f'fill="{gbg}" stroke="{gbd}" stroke-width="1.05"/>'
        )
        parts.append(
            f'<text x="{nx + nw/2:.1f}" y="{gy + 12}" text-anchor="middle" '
            f'font-size="9.5" font-weight="700" fill="{gbd}">{gt1}</text>'
        )
        parts.append(
            f'<text x="{nx + nw/2:.1f}" y="{gy + 23.5}" text-anchor="middle" '
            f'font-size="8.4" fill="#475569">{gt2}</text>'
        )

    parts.append(
        f'<rect x="{nx + 10}" y="{ny + 146}" width="{nw - 20}" height="22" rx="5" '
        'fill="#ffffff" stroke="#7c3aed" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{nx + nw/2:.1f}" y="{ny + 160.5}" text-anchor="middle" '
        'font-size="9.1" font-weight="700" fill="#6d28d9">CDCL alone: blind to 𝔽₂ parities</text>'
    )

    # Arrows from Shared Bus down to Linear and Nonlinear Branches
    for ax_b in (lx + 65, lx + 120, lx + 175):
        parts.append(
            f'<line x1="{ax_b}" y1="{by + bh}" x2="{ax_b}" y2="{ly - 2}" '
            'stroke="#2563eb" stroke-width="1.35" marker-end="url(#arr-blue)"/>'
        )
    for ax_p in (nx + 65, nx + 120, nx + 175):
        parts.append(
            f'<line x1="{ax_p}" y1="{by + bh}" x2="{ax_p}" y2="{ny - 2}" '
            'stroke="#7c3aed" stroke-width="1.35" marker-end="url(#arr-purple)"/>'
        )

    # Bottom Merge Miter Bar inside Left Panel
    my_m = py1 + 286
    parts.append(
        f'<path d="M {lx + lw/2:.1f} {ly + lh} L {lx + lw/2:.1f} {my_m - 2}" '
        'fill="none" stroke="#2563eb" stroke-width="1.4" marker-end="url(#arr-blue)"/>'
    )
    parts.append(
        f'<path d="M {nx + nw/2:.1f} {ny + nh} L {nx + nw/2:.1f} {my_m - 2}" '
        'fill="none" stroke="#7c3aed" stroke-width="1.4" marker-end="url(#arr-purple)"/>'
    )
    parts.append(
        f'<rect x="{px1 + 18}" y="{my_m}" width="{pw1 - 36}" height="28" rx="6" '
        'fill="#0f172a"/>'
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{my_m + 18}" text-anchor="middle" '
        'font-size="10.4" font-weight="700" fill="#ffffff">'
        "Coupled AIG Miter:  PO₀(x) = [ A·x = b (mod 2) ]  ∧  [ NL(x) = v ]</text>"
    )

    # ===================== RIGHT PANEL: VARIETY INTERSECTION + TABLE =====================
    rx, ry, rw = 574, 76, 322
    # Top Card: Geometric Subspace Intersection (SAT vs UNSAT)
    parts.append(
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="162" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="{ry + 20}" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Solution Space: Affine Plane ∩ Nonlinear Variety</text>"
    )

    # Left mini-diagram: SAT intersection
    sx1, sy1, sw1, sh1 = rx + 12, ry + 30, 144, 120
    parts.append(
        f'<rect x="{sx1}" y="{sy1}" width="{sw1}" height="{sh1}" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{sx1 + sw1/2:.1f}" y="{sy1 + 15}" text-anchor="middle" '
        'font-size="10" font-weight="700" fill="#059669">Planted SAT (3 inst.)</text>'
    )
    # Tilted blue line (affine subspace S_lin)
    parts.append(
        f'<line x1="{sx1 + 14}" y1="{sy1 + 92}" x2="{sx1 + 130}" y2="{sy1 + 32}" '
        'stroke="#2563eb" stroke-width="2.4"/>'
    )
    # Curved purple arc (nonlinear variety S_nl)
    parts.append(
        f'<path d="M {sx1 + 16} {sy1 + 42} Q {sx1 + 72} {sy1 + 96}, {sx1 + 128} {sy1 + 52}" '
        'fill="none" stroke="#7c3aed" stroke-width="2.4"/>'
    )
    # Intersection witness dot x*
    ix_d, iy_d = sx1 + 65, sy1 + 65.5
    parts.append(
        f'<circle cx="{ix_d:.1f}" cy="{iy_d:.1f}" r="5.5" fill="#059669" stroke="#ffffff" stroke-width="1.5"/>'
    )
    parts.append(
        f'<text x="{ix_d + 10:.1f}" y="{iy_d + 14:.1f}" font-size="9.5" font-weight="700" fill="#047857">x★</text>'
    )
    parts.append(
        f'<text x="{sx1 + 14}" y="{sy1 + 72}" font-size="8.6" font-weight="600" fill="#2563eb">S_lin</text>'
    )
    parts.append(
        f'<text x="{sx1 + 104}" y="{sy1 + 76}" font-size="8.6" font-weight="600" fill="#7c3aed">S_nl</text>'
    )
    parts.append(
        f'<text x="{sx1 + sw1/2:.1f}" y="{sy1 + 111}" text-anchor="middle" '
        'font-size="9" font-weight="600" fill="#047857">x★ ∈ S_lin ∩ S_nl</text>'
    )

    # Right mini-diagram: UNSAT disjoint
    sx2 = rx + 166
    parts.append(
        f'<rect x="{sx2}" y="{sy1}" width="{sw1}" height="{sh1}" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{sx2 + sw1/2:.1f}" y="{sy1 + 15}" text-anchor="middle" '
        'font-size="10" font-weight="700" fill="#dc2626">Flipped UNSAT (1 inst.)</text>'
    )
    # Blue affine subspace S_lin (consistent alone)
    parts.append(
        f'<line x1="{sx2 + 14}" y1="{sy1 + 92}" x2="{sx2 + 126}" y2="{sy1 + 42}" '
        'stroke="#2563eb" stroke-width="2.4"/>'
    )
    # Shifted purple nonlinear variety S_nl' (consistent alone, disjoint!)
    parts.append(
        f'<path d="M {sx2 + 16} {sy1 + 52} Q {sx2 + 64} {sy1 + 30}, {sx2 + 128} {sy1 + 26}" '
        'fill="none" stroke="#dc2626" stroke-width="2.4" stroke-dasharray="5,3"/>'
    )
    parts.append(
        f'<text x="{sx2 + 74}" y="{sy1 + 88}" font-size="8.6" font-weight="600" fill="#2563eb">S_lin ≠ ∅</text>'
    )
    parts.append(
        f'<text x="{sx2 + 76}" y="{sy1 + 44}" font-size="8.6" font-weight="600" fill="#dc2626">S_nl′ ≠ ∅</text>'
    )
    parts.append(
        f'<text x="{sx2 + sw1/2:.1f}" y="{sy1 + 111}" text-anchor="middle" '
        'font-size="9" font-weight="700" fill="#b91c1c">S_lin ∩ S_nl′ = ∅</text>'
    )

    # Bottom Card: Suite Parameters Table
    ty_c = ry + 172
    parts.append(
        f'<rect x="{rx}" y="{ty_c}" width="{rw}" height="154" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="{ty_c + 19}" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Benchmark Scaling (n = 128 .. 512)</text>"
    )
    th_y = ty_c + 36
    parts.append(f'<rect x="{rx + 10}" y="{th_y - 11}" width="{rw - 20}" height="17" rx="4" fill="#e2e8f0"/>')
    for cx_h, lbl_h, anc in [
        (rx + 15, "Instance", "start"),
        (rx + 148, "r / d", "middle"),
        (rx + 198, "mₙₗ", "middle"),
        (rx + 238, "XORs", "middle"),
        (rx + 284, "Ans", "middle"),
    ]:
        parts.append(
            f'<text x="{cx_h}" y="{th_y + 1}" text-anchor="{anc}" font-size="9" font-weight="700" fill="#334155">{lbl_h}</text>'
        )
    rows_cpl = [
        ("n128_d64", "64 / 64", "96", "189", "SAT", "#ecfdf5", "#059669"),
        ("n128_d32_u", "96 / 32", "84*", "277", "UNSAT", "#fef2f2", "#dc2626"),
        ("n256_d128", "128 / 128", "180", "377", "SAT", "#ecfdf5", "#059669"),
        ("n512_d128", "384 / 128", "420", "1,144", "SAT", "#ecfdf5", "#059669"),
    ]
    for r_i, (nm, rd, mnl, xrs, ans, pbg, pfg) in enumerate(rows_cpl):
        ry_r = th_y + 19 + r_i * 23
        if r_i % 2 == 1:
            parts.append(f'<rect x="{rx + 10}" y="{ry_r - 12}" width="{rw - 20}" height="20" rx="3" fill="#ffffff"/>')
        parts.append(
            f'<text x="{rx + 15}" y="{ry_r + 2}" font-family="{FONT_MONO}" font-size="9.3" font-weight="600" fill="#0f172a">{nm}</text>'
        )
        parts.append(f'<text x="{rx + 148}" y="{ry_r + 2}" text-anchor="middle" font-size="9.2" fill="#334155">{rd}</text>')
        parts.append(f'<text x="{rx + 198}" y="{ry_r + 2}" text-anchor="middle" font-size="9.2" fill="#334155">{mnl}</text>')
        parts.append(f'<text x="{rx + 238}" y="{ry_r + 2}" text-anchor="middle" font-size="9.2" fill="#2563eb" font-weight="600">{xrs}</text>')
        parts.append(f'<rect x="{rx + 260}" y="{ry_r - 10}" width="46" height="16" rx="4" fill="{pbg}" stroke="{pfg}" stroke-width="0.9"/>')
        parts.append(f'<text x="{rx + 283}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.6" font-weight="700" fill="{pfg}">{ans}</text>')
    parts.append(
        f'<text x="{rx + 12}" y="{ty_c + 145}" font-size="8.8" fill="#64748b">'
        "*coupled_n128_d32_unsat: last gate flipped (both layers consistent alone)</text>"
    )

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 414
    pills = [
        (24, 210, "#eff6ff", "#2563eb", "#1d4ed8", "1,987 Extracted Native XORs"),
        (244, 212, "#f5f3ff", "#7c3aed", "#6d28d9", "2,546 ANF Eqs (deg ≤ 2)"),
        (466, 206, "#fffbeb", "#d97706", "#b45309", "ρ_c = 1.14×–1.22× (Over)"),
        (682, 214, "#ecfdf5", "#059669", "#047857", "Hybrid Gauss+CDCL: 1.8–2.7 ms"),
    ]
    for px, pw, bg, bd, fg, lbl in pills:
        parts.append(
            f'<rect x="{px}" y="{by_s}" width="{pw}" height="34" rx="7" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{px + pw/2:.1f}" y="{by_s + 21}" text-anchor="middle" '
            f'font-size="10.1" font-weight="700" fill="{fg}">{esc(lbl)}</text>'
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
