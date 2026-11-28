#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `f2-frobenius-circulants` benchmark collection.

Illustrates the exact cyclic-shift circulant matrices over F_2 constructed in
`src/counterexamples.rs` (shown at n = 16, s = 4 illustrative scale):
  - Left: Invertible 3-XOR circulant C_3 with tap polynomial 1 + t + t^s
    in F_2[t]/(t^{2^k} - 1), Frobenius identity (1 + t + t^s)^{2^k} = 1,
    rank = n, unique planted witness x* (SAT: n = 64, 256, 1024, 4096)
  - Right: Rank-deficient 4-XOR circulant C_4 with factorized tap polynomial
    (1 + t)(1 + t^s), 1^T C_4 = 0 in left kernel, row-0 flip b_0 -> 0 = 1
    global parity contradiction (UNSAT: n = 256, 1024).

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


def draw_circulant_matrix(
    parts: list[str],
    x0: float,
    y0: float,
    n: int,
    taps: list[int],
    cell: float,
    tap_colors: dict[int, str],
    highlight_row0: bool = False,
) -> float:
    size = n * cell
    parts.append(
        f'<rect x="{x0 - 2}" y="{y0 - 2}" width="{size + 4}" height="{size + 4}" '
        'rx="5" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>'
    )
    # Row 0 highlight band if UNSAT flip
    if highlight_row0:
        parts.append(
            f'<rect x="{x0}" y="{y0}" width="{size}" height="{cell}" '
            'fill="#fee2e2" stroke="#dc2626" stroke-width="0.9"/>'
        )
    # Subtle grid lines every 4 cells (stride s = 4)
    for k in range(4, n, 4):
        parts.append(f'<line x1="{x0 + k*cell:.1f}" y1="{y0}" x2="{x0 + k*cell:.1f}" y2="{y0 + size}" stroke="#e2e8f0" stroke-width="0.8"/>')
        parts.append(f'<line x1="{x0}" y1="{y0 + k*cell:.1f}" x2="{x0 + size}" y2="{y0 + k*cell:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')

    for r in range(n):
        for off in taps:
            c = (r + off) % n
            col = "#dc2626" if (highlight_row0 and r == 0) else tap_colors[off]
            parts.append(
                f'<rect x="{x0 + c*cell + 1.0:.1f}" y="{y0 + r*cell + 1.0:.1f}" '
                f'width="{cell - 2.0:.1f}" height="{cell - 2.0:.1f}" rx="1.8" fill="{col}"/>'
            )
    return size


def build_svg() -> str:
    W, H = 920, 480
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="F2-Frobenius circulant matrices: invertible 3-XOR SAT vs rank-deficient 4-XOR UNSAT kernel">',
        # White card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "𝔽₂-Frobenius Circulant Parity Systems (f2-frobenius-circulants)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Strictly balanced n×n cyclic-shift matrices over 𝔽₂ (n = 2ᵏ, stride s = 2^⌊k/2⌋): "
        "invertible 3-XOR SAT vs. rank-deficient 4-XOR UNSAT</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: INVERTIBLE 3-XOR CIRCULANT (SAT) =====================
    px1, py1, pw1, ph1 = 24, 76, 428, 336
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    # Green header banner
    parts.append(f'<rect x="{px1}" y="{py1}" width="{pw1}" height="28" rx="10" fill="#059669"/>')
    parts.append(f'<rect x="{px1}" y="{py1 + 16}" width="{pw1}" height="12" fill="#059669"/>')
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 19}" text-anchor="middle" '
        'font-size="11.8" font-weight="700" fill="#ffffff">'
        "1. Invertible 3-XOR Circulant Ψₖ,b — Unique SAT (4 inst.)</text>"
    )

    # 16x16 Matrix C3 (s = 4)
    m1x, m1y = px1 + 18, py1 + 48
    cell = 11.0
    m_sz = draw_circulant_matrix(
        parts, m1x, m1y, 16, [0, 1, 4], cell,
        {0: "#2563eb", 1: "#059669", 4: "#7c3aed"},
        highlight_row0=False,
    )
    parts.append(
        f'<text x="{m1x + m_sz/2:.1f}" y="{m1y - 6}" text-anchor="middle" '
        'font-size="10" font-weight="700" fill="#1e293b">C₃ (n = 16, s = 4 shown)</text>'
    )

    # Tap legend under matrix 1
    ly1 = m1y + m_sz + 14
    for i, (col, lbl) in enumerate([("#2563eb", "+0"), ("#059669", "+1"), ("#7c3aed", "+s")]):
        lx_i = m1x + 14 + i * 54
        parts.append(f'<rect x="{lx_i}" y="{ly1 - 8}" width="10" height="10" rx="2" fill="{col}"/>')
        parts.append(f'<text x="{lx_i + 14}" y="{ly1}" font-family="{FONT_MONO}" font-size="9.3" font-weight="600" fill="#334155">{lbl}</text>')

    # Right algebraic column inside Left Panel
    ax1 = m1x + m_sz + 18
    aw1 = px1 + pw1 - ax1 - 14
    parts.append(f'<rect x="{ax1}" y="{m1y - 2}" width="{aw1}" height="82" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 15}" font-size="10.2" font-weight="700" fill="#047857">Tap Polynomial (𝔽₂[t]/(tⁿ−1))</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 32}" font-family="{FONT_MONO}" font-size="10.4" font-weight="700" fill="#0f172a">p(t) = 1 + t + tˢ</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 49}" font-size="9.4" fill="#334155">Frobenius (char 2, n = 2ᵏ):</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 64}" font-family="{FONT_MONO}" font-size="9.6" font-weight="700" fill="#2563eb">p(t)ⁿ = 1 + tⁿ + tˢⁿ ≡ 1</text>')

    parts.append(f'<rect x="{ax1}" y="{m1y + 90}" width="{aw1}" height="88" rx="7" fill="#ecfdf5" stroke="#059669" stroke-width="1.1"/>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 107}" font-size="10.2" font-weight="700" fill="#047857">Full Rank &amp; Unique Witness</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 123}" font-size="9.4" fill="#1e293b">• det(C₃) = 1,  rank(C₃) = n</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 138}" font-size="9.4" fill="#1e293b">• ker(C₃) = {esc("{0}")}</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 153}" font-size="9.4" fill="#1e293b">• Unique x★ = C₃⁻¹·b (SAT)</text>')
    parts.append(f'<text x="{ax1 + 10}" y="{m1y + 168}" font-size="9" font-weight="600" fill="#047857">n ∈ {esc("{64, 256, 1024, 4096}")}</text>')

    # Bottom row equation box in Left Panel
    parts.append(f'<rect x="{px1 + 14}" y="{py1 + ph1 - 74}" width="{pw1 - 28}" height="60" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + ph1 - 54}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="10.2" font-weight="700" fill="#0f172a">'
        "Row i:  xᵢ ⊕ x₍ᵢ₊₁₎ mod n ⊕ x₍ᵢ₊ₛ₎ mod n = bᵢ</text>"
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + ph1 - 36}" text-anchor="middle" font-size="9.3" fill="#475569">'
        "2D torus-like stride s = √n forces ≥ 2^(√n / 3√2) merge-tree blowup;</text>"
    )
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + ph1 - 22}" text-anchor="middle" font-size="9.3" font-weight="600" fill="#1d4ed8">'
        "at n = 4,096: Kissat 364 s · CaDiCaL 211 s vs. 𝔽₂-Gauss 16.1 ms!</text>"
    )

    # ===================== RIGHT PANEL: RANK-DEFICIENT 4-XOR CIRCULANT (UNSAT) =====================
    px2, py2, pw2, ph2 = 468, 76, 428, 336
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="{ph2}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    # Red header banner
    parts.append(f'<rect x="{px2}" y="{py2}" width="{pw2}" height="28" rx="10" fill="#dc2626"/>')
    parts.append(f'<rect x="{px2}" y="{py2 + 16}" width="{pw2}" height="12" fill="#dc2626"/>')
    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{py2 + 19}" text-anchor="middle" '
        'font-size="11.8" font-weight="700" fill="#ffffff">'
        "2. Rank-Deficient 4-XOR Circulant — Min. UNSAT (2 inst.)</text>"
    )

    # 16x16 Matrix C4 (s = 4) with row 0 highlighted red (flipped b_0)
    m2x, m2y = px2 + 18, py2 + 48
    draw_circulant_matrix(
        parts, m2x, m2y, 16, [0, 1, 4, 5], cell,
        {0: "#2563eb", 1: "#059669", 4: "#7c3aed", 5: "#d97706"},
        highlight_row0=True,
    )
    parts.append(
        f'<text x="{m2x + m_sz/2:.1f}" y="{m2y - 6}" text-anchor="middle" '
        'font-size="10" font-weight="700" fill="#1e293b">C₄ (row 0 flipped b₀ in red)</text>'
    )

    # Tap legend under matrix 2
    for i, (col, lbl) in enumerate([("#2563eb", "+0"), ("#059669", "+1"), ("#7c3aed", "+s"), ("#d97706", "+s+1")]):
        lx_i = m2x + 2 + i * 44
        parts.append(f'<rect x="{lx_i}" y="{ly1 - 8}" width="9" height="9" rx="2" fill="{col}"/>')
        parts.append(f'<text x="{lx_i + 12}" y="{ly1}" font-family="{FONT_MONO}" font-size="8.7" font-weight="600" fill="#334155">{lbl}</text>')

    # Right algebraic column inside Right Panel
    ax2 = m2x + m_sz + 18
    aw2 = px2 + pw2 - ax2 - 14
    parts.append(f'<rect x="{ax2}" y="{m2y - 2}" width="{aw2}" height="82" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 15}" font-size="10.2" font-weight="700" fill="#b91c1c">Singular Tap Polynomial</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 32}" font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="#0f172a">q(t) = (1+t)(1+tˢ)</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 49}" font-size="9.4" fill="#334155">Zero root at t = 1:</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 64}" font-family="{FONT_MONO}" font-size="9.6" font-weight="700" fill="#dc2626">q(1) = 0 ⇒ 𝟏ᵀ·C₄ = 𝟎</text>')

    parts.append(f'<rect x="{ax2}" y="{m2y + 90}" width="{aw2}" height="88" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.1"/>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 107}" font-size="10.2" font-weight="700" fill="#b91c1c">Left-Kernel Obstruction</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 123}" font-size="9.3" fill="#1e293b">• Every col has even wt 4</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 138}" font-size="9.3" fill="#1e293b">• ∑ᵢ (C₄x)ᵢ = 4∑ xⱼ ≡ 0</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 153}" font-size="9.3" fill="#1e293b">• Flip b₀ ⇒ ∑ᵢ bᵢ ≡ 1</text>')
    parts.append(f'<text x="{ax2 + 10}" y="{m2y + 168}" font-size="9.2" font-weight="700" fill="#b91c1c">0 ≡ 1 (mod 2) ⇒ UNSAT!</text>')

    # Bottom row equation box in Right Panel
    parts.append(f'<rect x="{px2 + 14}" y="{py2 + ph2 - 74}" width="{pw2 - 28}" height="60" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{py2 + ph2 - 54}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="9.8" font-weight="700" fill="#0f172a">'
        "Row i:  xᵢ ⊕ xᵢ₊₁ ⊕ xᵢ₊ₛ ⊕ xᵢ₊ₛ₊₁ = bᵢ  (b₀ flipped)</text>"
    )
    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{py2 + ph2 - 36}" text-anchor="middle" font-size="9.3" fill="#475569">'
        "Minimally unsatisfiable: dropping ANY single row makes the system SAT;</text>"
    )
    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{py2 + ph2 - 22}" text-anchor="middle" font-size="9.3" font-weight="600" fill="#b91c1c">'
        "n ∈ {256, 1,024}: CaDiCaL &gt;30 s T/O at n=1,024 vs. 𝔽₂-Gauss 3.5 ms.</text>"
    )

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 424
    pills = [
        (24, 210, "#ecfdf5", "#059669", "#047857", "6 Instances: 4 SAT / 2 UNSAT"),
        (244, 212, "#eff6ff", "#2563eb", "#1d4ed8", "8,000 Native XORs (deg-1 ANF)"),
        (466, 206, "#fffbeb", "#d97706", "#b45309", "ρ_c = 0.90×–0.91× (Near-crit)"),
        (682, 214, "#f5f3ff", "#7c3aed", "#6d28d9", "4 Formats: AIG · CNF · XCNF · ANF"),
    ]
    for px, pw, bg, bd, fg, lbl in pills:
        parts.append(f'<rect x="{px}" y="{by_s}" width="{pw}" height="34" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        parts.append(f'<text x="{px + pw/2:.1f}" y="{by_s + 21}" text-anchor="middle" font-size="10.1" font-weight="700" fill="{fg}">{esc(lbl)}</text>')

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
