#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `tseitin-expanders` benchmark collection.

Illustrates both 3-regular UNSAT Tseitin parity families implemented in
`src/counterexamples.rs`:
  - Left: Deterministic 3-regular expander graph (Hamiltonian cycle +
    pseudorandom perfect matching, exact Rust LCG construction shown at n=16)
    with odd charge sigma(v_0)=1, sigma(v>0)=0, and expansion cut barrier
  - Right: 3-regular prism graph C_m x K_2 (top cycle t_i, bottom cycle b_i,
    spokes s_i, shown at m=10, n=20) with bounded treewidth tw <= 4
  - Bottom: Global Handshaking Lemma parity obstruction 2*sum(x_e) = 0 != 1.

Usage:
    python3 src/gen_diagram.py
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


def exact_expander_matching(n: int, seed: int) -> list[tuple[int, int]]:
    """Exact Fisher-Yates matching from `src/counterexamples.rs` (wrapping u64 LCG)."""
    mask = (1 << 64) - 1
    perm = list(range(n))
    state = (seed ^ 0xA5A5_5A5A_1234_5678) & mask
    for i in range(n - 1, 0, -1):
        state = (state * 6364136223846793005 + 1) & mask
        j = state % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    return [(perm[2 * k], perm[2 * k + 1]) for k in range(n // 2)]


def build_svg() -> str:
    W, H = 920, 480
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="MOD2-Tseitin formulas on 3-regular expander and prism graphs with odd vertex charge obstruction">',
        # White card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "MOD₂-Tseitin Formulas on 3-Regular Expanders &amp; Prisms (tseitin-expanders)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Edge variables xₑ ∈ {0, 1} with 3-XOR vertex parities ⊕ₑ∋ᵥ xₑ = σ(v) and odd global charge "
        "∑ σ(v) ≡ 1 (mod 2) — 2^Ω(n) Resolution barrier</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: 3-REGULAR EXPANDER GRAPH =====================
    px1, py1, pw1, ph1 = 24, 76, 428, 294
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "1. 3-Regular Expander (tseitin_exp_n60 / 120 / 300)</text>"
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 34}" font-size="9.6" fill="#475569">'
        "Hamiltonian cycle (blue) + pseudorandom perfect matching (purple)</text>"
    )

    # Draw 16-vertex deterministic 3-regular expander centered at (px1 + 132, py1 + 160)
    cx1, cy1, rad1 = px1 + 130, py1 + 162, 92.0
    n_exp = 16
    pts1 = [
        (cx1 + rad1 * math.cos(-math.pi / 2 + 2 * math.pi * i / n_exp),
         cy1 + rad1 * math.sin(-math.pi / 2 + 2 * math.pi * i / n_exp))
        for i in range(n_exp)
    ]

    # Expansion cut dashed loop enclosing left half of vertices
    parts.append(
        f'<ellipse cx="{cx1 - 46:.1f}" cy="{cy1 + 8:.1f}" rx="56" ry="86" '
        'fill="#fef2f2" fill-opacity="0.35" stroke="#dc2626" stroke-width="1.3" stroke-dasharray="5,3"/>'
    )
    parts.append(
        f'<text x="{cx1 - 92:.1f}" y="{cy1 + 104:.1f}" font-size="8.8" font-weight="700" fill="#b91c1c">'
        "Cut S: |∂S| ≥ c·|S|</text>"
    )

    # Matching chords (purple, curved slightly through interior)
    matching = exact_expander_matching(n_exp, 777)
    for u, v in matching:
        x1, y1 = pts1[u]
        x2, y2 = pts1[v]
        # Slight pull toward center so chord overlaps look clean
        mx = 0.5 * (x1 + x2) * 0.72 + cx1 * 0.28
        my = 0.5 * (y1 + y2) * 0.72 + cy1 * 0.28
        parts.append(
            f'<path d="M {x1:.1f} {y1:.1f} Q {mx:.1f} {my:.1f}, {x2:.1f} {y2:.1f}" '
            'fill="none" stroke="#7c3aed" stroke-width="1.45" stroke-opacity="0.8"/>'
        )

    # Hamiltonian cycle edges (blue)
    for i in range(n_exp):
        x1, y1 = pts1[i]
        x2, y2 = pts1[(i + 1) % n_exp]
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            'stroke="#2563eb" stroke-width="2.0"/>'
        )

    # Vertices: v_0 red (sigma=1), v_1..v_15 light blue (sigma=0)
    for i, (vx, vy) in enumerate(pts1):
        if i == 0:
            parts.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="11.5" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>')
            parts.append(f'<text x="{vx:.1f}" y="{vy + 3.8:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#ffffff">1</text>')
            parts.append(f'<text x="{vx + 16:.1f}" y="{vy - 9:.1f}" font-size="9.3" font-weight="700" fill="#b91c1c">v₀: σ=1</text>')
        else:
            parts.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="7.5" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
            parts.append(f'<text x="{vx:.1f}" y="{vy + 3.0:.1f}" text-anchor="middle" font-size="8.2" font-weight="700" fill="#1d4ed8">0</text>')

    # Right info boxes inside Expander Panel
    ix1, iw1 = px1 + 244, 170
    parts.append(f'<rect x="{ix1}" y="{py1 + 52}" width="{iw1}" height="100" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 70}" font-size="10.2" font-weight="700" fill="#0f172a">Vertex 3-XOR Constraint</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 88}" font-family="{FONT_MONO}" font-size="9.6" font-weight="700" fill="#1d4ed8">xₑ₁ ⊕ xₑ₂ ⊕ xₑ₃ = σ(v)</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 105}" font-size="9" fill="#475569">• 4 ternary CNF clauses / v</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 120}" font-size="9" fill="#475569">• σ(v₀) = 1, σ(v&gt;0) = 0</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 135}" font-size="9" fill="#475569">• Every edge in 2 XOR eqs</text>')

    parts.append(f'<rect x="{ix1}" y="{py1 + 164}" width="{iw1}" height="114" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.1"/>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 182}" font-size="10.1" font-weight="700" fill="#b91c1c">High Expansion = Hard</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 198}" font-size="9" fill="#1e293b">• Treewidth tw = Ω(n)</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 213}" font-size="9" fill="#1e293b">• Resolution size 2^Ω(n)</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 228}" font-size="9" fill="#1e293b">• n=120, 300: Kissat &amp;</text>')
    parts.append(f'<text x="{ix1 + 18}" y="{py1 + 241}" font-size="9" font-weight="700" fill="#b91c1c">CaDiCaL &gt;5,000 s (T/O)</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 258}" font-size="9" font-weight="700" fill="#047857">• 𝔽₂-Gauss: 1.2–1.4 ms</text>')
    parts.append(f'<text x="{ix1 + 10}" y="{py1 + 271}" font-size="8.4" fill="#475569">LRAT verified in cake_lpr</text>')

    # ===================== RIGHT PANEL: 3-REGULAR PRISM GRAPH C_m x K_2 =====================
    px2, py2, pw2, ph2 = 468, 76, 428, 294
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="{ph2}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{py2 + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "2. 3-Regular Prism C₂₀₀ × K₂ (tseitin_prism_n400)</text>"
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{py2 + 34}" font-size="9.6" fill="#475569">'
        "Outer cycle tᵢ (blue), inner cycle bᵢ (green), radial spokes sᵢ (amber)</text>"
    )

    # Concentric prism C_10 x K_2 centered at (px2 + 128, py2 + 162)
    cx2, cy2 = px2 + 128, py2 + 162
    r_out, r_in = 90.0, 50.0
    m_pr = 10
    outer_pts = [
        (cx2 + r_out * math.cos(-math.pi / 2 + 2 * math.pi * i / m_pr),
         cy2 + r_out * math.sin(-math.pi / 2 + 2 * math.pi * i / m_pr))
        for i in range(m_pr)
    ]
    inner_pts = [
        (cx2 + r_in * math.cos(-math.pi / 2 + 2 * math.pi * i / m_pr),
         cy2 + r_in * math.sin(-math.pi / 2 + 2 * math.pi * i / m_pr))
        for i in range(m_pr)
    ]

    # Spokes s_i (amber)
    for i in range(m_pr):
        x1, y1 = outer_pts[i]
        x2, y2 = inner_pts[i]
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#d97706" stroke-width="1.9"/>')
    # Outer cycle t_i (blue)
    for i in range(m_pr):
        x1, y1 = outer_pts[i]
        x2, y2 = outer_pts[(i + 1) % m_pr]
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#2563eb" stroke-width="2.1"/>')
    # Inner cycle b_i (emerald green)
    for i in range(m_pr):
        x1, y1 = inner_pts[i]
        x2, y2 = inner_pts[(i + 1) % m_pr]
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#059669" stroke-width="1.9"/>')

    # Small separator cut line across prism illustrating width-4 cut
    parts.append(
        f'<line x1="{cx2 - 100}" y1="{cy2}" x2="{cx2 + 100}" y2="{cy2}" '
        'stroke="#059669" stroke-width="1.3" stroke-dasharray="4,3"/>'
    )
    parts.append(
        f'<text x="{cx2}" y="{cy2 + 14}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#047857">'
        "width-4 cut</text>"
    )

    # Prism vertices
    for i, (vx, vy) in enumerate(outer_pts):
        if i == 0:
            parts.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="11" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>')
            parts.append(f'<text x="{vx:.1f}" y="{vy + 3.6:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#ffffff">1</text>')
            parts.append(f'<text x="{vx + 15:.1f}" y="{vy - 9:.1f}" font-size="9.2" font-weight="700" fill="#b91c1c">top₀: σ=1</text>')
        else:
            parts.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="7.2" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
            parts.append(f'<text x="{vx:.1f}" y="{vy + 2.8:.1f}" text-anchor="middle" font-size="8" font-weight="700" fill="#1d4ed8">0</text>')
    for i, (vx, vy) in enumerate(inner_pts):
        parts.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="6.8" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
        parts.append(f'<text x="{vx:.1f}" y="{vy + 2.7:.1f}" text-anchor="middle" font-size="7.8" font-weight="700" fill="#047857">0</text>')

    # Right info boxes inside Prism Panel
    ix2, iw2 = px2 + 244, 170
    parts.append(f'<rect x="{ix2}" y="{py2 + 52}" width="{iw2}" height="100" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 70}" font-size="10.2" font-weight="700" fill="#0f172a">Prism Ring Equations</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 88}" font-family="{FONT_MONO}" font-size="9.2" font-weight="700" fill="#1d4ed8">tᵢ₋₁ ⊕ tᵢ ⊕ sᵢ = δᵢ,₀</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 105}" font-family="{FONT_MONO}" font-size="9.2" font-weight="700" fill="#047857">bᵢ₋₁ ⊕ bᵢ ⊕ sᵢ = 0</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 123}" font-size="9" fill="#475569">• 400 vertices, 600 edges</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 137}" font-size="9" fill="#475569">• 1,000 CNF vars, 3,600 cls</text>')

    parts.append(f'<rect x="{ix2}" y="{py2 + 164}" width="{iw2}" height="114" rx="7" fill="#ecfdf5" stroke="#059669" stroke-width="1.1"/>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 182}" font-size="10.1" font-weight="700" fill="#047857">Low Treewidth Control</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 198}" font-size="9" fill="#1e293b">• Same UNSAT parity law</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 213}" font-size="9" fill="#1e293b">• Bounded treewidth ≤ 4</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 228}" font-size="9" fill="#1e293b">• CaDiCaL: 9.6 ms</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 243}" font-size="9" fill="#1e293b">• Kissat: 13.6 ms</text>')
    parts.append(f'<text x="{ix2 + 10}" y="{py2 + 258}" font-size="9" font-weight="700" fill="#047857">• Proves expansion—not size</text>')
    parts.append(f'<text x="{ix2 + 18}" y="{py2 + 271}" font-size="8.6" fill="#475569">—causes the CDCL cliff!</text>')

    # ===================== BOTTOM PANEL: GLOBAL PARITY OBSTRUCTION PROOF =====================
    bx, by, bw, bh = 24, 382, 872, 82
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
        'fill="#fef2f2" stroke="#dc2626" stroke-width="1.25"/>'
    )
    parts.append(
        f'<text x="{bx + 16}" y="{by + 21}" font-size="11.6" font-weight="700" fill="#b91c1c">'
        "Global Handshaking Parity Obstruction (Why All 4 Instances Are Provably UNSAT)</text>"
    )
    parts.append(
        f'<rect x="{bx + 16}" y="{by + 29}" width="{bw - 32}" height="26" rx="6" '
        'fill="#ffffff" stroke="#fca5a5" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{bx + bw/2:.1f}" y="{by + 46}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="10.6" font-weight="700" fill="#0f172a">'
        "∑ᵥ ∈ V ( ⊕ₑ ∋ v xₑ )  =  2 · ∑ₑ ∈ E xₑ  ≡  0 (mod 2)   ≠   1  ≡  ∑ᵥ ∈ V σ(v)   ⇒   UNSAT</text>"
    )
    parts.append(
        f'<text x="{bx + bw/2:.1f}" y="{by + 71}" text-anchor="middle" font-size="9.6" fill="#475569">'
        "All 4 UNSAT instances sit deeply under-constrained (ρ_c = 0.72×, α = 3.60, 0% Bin, Deg CV = 0.26) · "
        "880 extracted native XORs · 4 formats: AIG / CNF / XCNF / ANF</text>"
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
