#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `satlib-dimacs-phole` benchmark collection.

Illustrates John Hooker's classic DIMACS Pigeonhole Principle UNSAT suite
(`hole6` through `hole10`, encoding PHP^7_6 through PHP^11_10):
  - Left: Complete bipartite graph K_{7,6} (hole6: 7 pigeons P_1..P_7 ->
    6 holes H_1..H_6), highlighting a maximal 5-edge matching plus the forced
    collision on H_6 (P_6, P_7 -> H_6) and Hall's deficiency |P| > |N(P)|
  - Right Top: Exact direct CNF encoding (n+1 ALO positive n-clauses +
    n*C(n+1,2) binary Horn AMO clauses, S_{n+1} x S_n symmetry)
  - Right Bottom: Empirical Haken 2^Omega(n) exponential cliff from the README
    (CaDiCaL 5 ms -> 28 ms -> 267 ms -> 3,117 ms -> >5,000 ms on hole6..10).

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


def build_svg() -> str:
    W, H = 920, 480
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Complete bipartite pigeonhole graph K_{7,6} showing forced collision, Hall deficiency, and exponential Resolution scaling across hole6 to hole10">',
        # White card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Pigeonhole Principle Kₙ₊₁,ₙ: hole6..hole10 (satlib-dimacs-phole)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Classic DIMACS UNSAT suite PHPⁿ⁺¹ₙ (n = 6..10): placing n+1 pigeons into n holes violates "
        "Hall's Marriage Condition — Haken's 2^Ω(n) Resolution lower bound</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: COMPLETE BIPARTITE GRAPH K_{7,6} =====================
    px1, py1, pw1, ph1 = 24, 76, 434, 334
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "Complete Bipartite Graph K₇,₆  (hole6 = PHP⁷₆: 42 Vars)</text>"
    )
    parts.append(
        f'<text x="{px1 + 14}" y="{py1 + 35}" font-size="9.4" fill="#475569">'
        "Each edge (i, j) is Boolean variable xᵢ,ⱼ ∈ {0, 1} (“pigeon i in hole j”)</text>"
    )

    # Column headers
    p_x = px1 + 88
    h_x = px1 + 342
    parts.append(f'<text x="{p_x}" y="{py1 + 54}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1d4ed8">7 Pigeons (n + 1)</text>')
    parts.append(f'<text x="{h_x}" y="{py1 + 54}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#047857">6 Holes (n)</text>')

    p_ys = [py1 + 74 + i * 32 for i in range(7)]
    h_ys = [py1 + 90 + j * 32 for j in range(6)]

    # Draw all 42 background complete bipartite edges faintly
    for py_i in p_ys:
        for hy_j in h_ys:
            parts.append(
                f'<line x1="{p_x + 15}" y1="{py_i}" x2="{h_x - 22}" y2="{hy_j}" '
                'stroke="#cbd5e1" stroke-width="0.85" stroke-opacity="0.65"/>'
            )

    # Highlight 5 valid matched edges (P1->H1 .. P5->H5) in emerald green
    for i in range(5):
        parts.append(
            f'<line x1="{p_x + 15}" y1="{p_ys[i]}" x2="{h_x - 22}" y2="{h_ys[i]}" '
            'stroke="#059669" stroke-width="2.4"/>'
        )

    # Highlight forced COLLISION pair (P6->H6 and P7->H6) in bold red
    parts.append(
        f'<line x1="{p_x + 15}" y1="{p_ys[5]}" x2="{h_x - 22}" y2="{h_ys[5]}" '
        'stroke="#dc2626" stroke-width="2.8"/>'
    )
    parts.append(
        f'<line x1="{p_x + 15}" y1="{p_ys[6]}" x2="{h_x - 22}" y2="{h_ys[5]}" '
        'stroke="#dc2626" stroke-width="2.8" stroke-dasharray="6,3"/>'
    )

    # Collision pill centered near P6/P7 -> H6
    parts.append(
        f'<rect x="{px1 + 148}" y="{p_ys[5] - 3}" width="144" height="32" rx="6" '
        'fill="#fef2f2" stroke="#dc2626" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{px1 + 220}" y="{p_ys[5] + 10}" text-anchor="middle" font-size="9.3" font-weight="700" fill="#b91c1c">'
        "COLLISION ON H₆!</text>"
    )
    parts.append(
        f'<text x="{px1 + 220}" y="{p_ys[5] + 23}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.7" fill="#7f1d1d">'
        "violates (¬x₆,₆ ∨ ¬x₇,₆)</text>"
    )

    # Draw 7 Pigeon nodes
    for i, py_i in enumerate(p_ys):
        is_col = i >= 5
        fill = "#fef2f2" if is_col else "#eff6ff"
        bd = "#dc2626" if is_col else "#2563eb"
        fg = "#b91c1c" if is_col else "#1d4ed8"
        parts.append(f'<circle cx="{p_x}" cy="{py_i}" r="13.5" fill="{fill}" stroke="{bd}" stroke-width="1.6"/>')
        parts.append(f'<text x="{p_x}" y="{py_i + 3.8}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.6" font-weight="700" fill="{fg}">P{chr(0x2081 + i)}</text>')
        if i == 6:
            parts.append(f'<text x="{p_x - 20}" y="{py_i + 3.5}" text-anchor="end" font-size="8.5" font-weight="700" fill="#b91c1c">extra!</text>')

    # Draw 6 Hole nodes
    for j, hy_j in enumerate(h_ys):
        is_col = j == 5
        fill = "#fef2f2" if is_col else "#ecfdf5"
        bd = "#dc2626" if is_col else "#059669"
        fg = "#b91c1c" if is_col else "#047857"
        parts.append(f'<rect x="{h_x - 22}" y="{hy_j - 12}" width="44" height="24" rx="5" fill="{fill}" stroke="{bd}" stroke-width="1.6"/>')
        parts.append(f'<text x="{h_x}" y="{hy_j + 3.8}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.6" font-weight="700" fill="{fg}">H{chr(0x2081 + j)}</text>')

    # Hall deficiency bar at bottom of Left Panel
    parts.append(f'<rect x="{px1 + 14}" y="{py1 + 292}" width="{pw1 - 28}" height="30" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.1"/>')
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 311}" text-anchor="middle" font-size="9.6" font-weight="700" fill="#b91c1c">'
        "Hall Deficiency:  |P| = n + 1  &gt;  n = |N(P)|   ⇒   No Injective Matching (UNSAT)</text>"
    )

    # ===================== RIGHT PANEL: DIRECT CNF ENCODING + HAKEN EXPONENTIAL CLIFF =====================
    px2, py2, pw2, ph2 = 474, 76, 422, 334
    # Card 1: Direct CNF Clause Encoding
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="148" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{py2 + 20}" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Direct CNF Encoding (n(n+1) Variables · Sₙ₊₁ × Sₙ Symmetry)</text>"
    )

    parts.append(f'<rect x="{px2 + 12}" y="{py2 + 30}" width="{pw2 - 24}" height="44" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.15"/>')
    parts.append(f'<text x="{px2 + 22}" y="{py2 + 46}" font-size="9.8" font-weight="700" fill="#047857">At-Least-One (ALO — n+1 positive n-clauses):</text>')
    parts.append(f'<text x="{px2 + 22}" y="{py2 + 63}" font-family="{FONT_MONO}" font-size="9.6" fill="#0f172a">∀ i ∈ {esc("{1..n+1}")}:   xᵢ,₁ ∨ xᵢ,₂ ∨ … ∨ xᵢ,ₙ</text>')

    parts.append(f'<rect x="{px2 + 12}" y="{py2 + 82}" width="{pw2 - 24}" height="44" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.15"/>')
    parts.append(f'<text x="{px2 + 22}" y="{py2 + 98}" font-size="9.8" font-weight="700" fill="#b91c1c">At-Most-One (AMO — n·C(n+1,2) binary Horn clauses, 95–98%):</text>')
    parts.append(f'<text x="{px2 + 22}" y="{py2 + 115}" font-family="{FONT_MONO}" font-size="9.6" fill="#0f172a">∀ j ∈ {esc("{1..n}")}, i &lt; k:   ¬xᵢ,ⱼ ∨ ¬xₖ,ⱼ</text>')

    parts.append(
        f'<text x="{px2 + 14}" y="{py2 + 140}" font-size="8.9" fill="#475569">'
        "Zero XOR clauses · Deg CV = 0.00 (completely symmetric across pigeons &amp; holes)</text>"
    )

    # Card 2: Empirical Haken Exponential Cliff (hole6..hole10, log-scale horizontal bars)
    cy_2 = py2 + 158
    parts.append(
        f'<rect x="{px2}" y="{cy_2}" width="{pw2}" height="176" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{cy_2 + 20}" font-size="11.6" font-weight="700" fill="#0f172a">'
        "Haken's 2^Ω(n) CDCL Blowup vs. Cardinality Solving (Log Scale)</text>"
    )
    parts.append(
        f'<text x="{px2 + 14}" y="{cy_2 + 34}" font-size="8.9" fill="#475569">'
        "1-core wall time from README: CaDiCaL (red, ~10× per pigeon) vs. Frobenius (green, ~1.7 ms)</text>"
    )

    # Exact benchmark timings from README (ms)
    bench = [
        ("hole6", "42v/133c", 5.38, 1.79, False),
        ("hole7", "56v/204c", 28.14, 1.50, False),
        ("hole8", "72v/297c", 266.52, 1.60, False),
        ("hole9", "90v/415c", 3117.30, 1.96, False),
        ("hole10", "110v/561c", 5000.0, 1.85, True),
    ]
    bx0 = px2 + 124
    bmax = 212.0  # maps log10(1 ms) .. log10(5000 ms) -> [0, bmax]
    log_max = math.log10(5000.0)

    for idx, (nm, dim, cad_ms, frob_ms, is_to) in enumerate(bench):
        by_i = cy_2 + 45 + idx * 24
        parts.append(f'<text x="{px2 + 14}" y="{by_i + 12}" font-family="{FONT_MONO}" font-size="9.1" font-weight="700" fill="#0f172a">{nm}</text>')
        parts.append(f'<text x="{px2 + 60}" y="{by_i + 12}" font-size="8.2" fill="#64748b">{dim}</text>')
        parts.append(f'<rect x="{bx0}" y="{by_i}" width="{bmax:.1f}" height="17" rx="3.5" fill="#e2e8f0"/>')
        w_cad = max(6.0, bmax * math.log10(max(1.0, cad_ms)) / log_max)
        w_frob = max(6.0, bmax * math.log10(max(1.0, frob_ms)) / log_max)
        parts.append(f'<rect x="{bx0}" y="{by_i + 1}" width="{w_cad:.1f}" height="8" rx="2" fill="{"#991b1b" if is_to else "#dc2626"}"/>')
        parts.append(f'<rect x="{bx0}" y="{by_i + 9.5}" width="{w_frob:.1f}" height="6.5" rx="2" fill="#059669"/>')
        cad_lbl = ">5,000 ms" if is_to else f"{cad_ms:,.1f} ms"
        parts.append(f'<text x="{bx0 + bmax + 6}" y="{by_i + 12}" font-size="8.6" font-weight="700" fill="{"#991b1b" if is_to else "#dc2626"}">{cad_lbl}</text>')

    # Small legend bottom of Card 2
    parts.append(f'<rect x="{bx0}" y="{cy_2 + 165}" width="10" height="6" rx="1.5" fill="#dc2626"/>')
    parts.append(f'<text x="{bx0 + 14}" y="{cy_2 + 170.5}" font-size="8.3" fill="#475569">CaDiCaL 3.1.0</text>')
    parts.append(f'<rect x="{bx0 + 96}" y="{cy_2 + 165}" width="10" height="6" rx="1.5" fill="#059669"/>')
    parts.append(f'<text x="{bx0 + 110}" y="{cy_2 + 170.5}" font-size="8.3" fill="#475569">Frobenius / dense (1.2–2.0 ms)</text>')

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 424
    pills = [
        (24, 210, "#fef2f2", "#dc2626", "#b91c1c", "5 / 5 UNSAT (hole6 .. hole10)"),
        (244, 212, "#eff6ff", "#2563eb", "#1d4ed8", "95–98% Binary Horn Clauses"),
        (466, 206, "#fffbeb", "#d97706", "#b45309", "ρ_c = 3.00×–5.00× (Over)"),
        (682, 214, "#f5f3ff", "#7c3aed", "#6d28d9", "0 XORs · AIG / CNF / XCNF / ANF"),
    ]
    for px_p, pw_p, bg, bd, fg, lbl in pills:
        parts.append(f'<rect x="{px_p}" y="{by_s}" width="{pw_p}" height="34" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        parts.append(f'<text x="{px_p + pw_p/2:.1f}" y="{by_s + 21}" text-anchor="middle" font-size="10.1" font-weight="700" fill="{fg}">{esc(lbl)}</text>')

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
