#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`integer-factoring` (Pure-Logic Integer Factorization & Masked Multiplier Circuits).

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
    W, H = 920, 490
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Karatsuba and Masked Wallace Multiplier Integer Factorization Circuit Diagram">',
        "  <defs>",
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>',
        "    </marker>",
        '    <marker id="arr-purp" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>',
        "    </marker>",
        '    <marker id="arr-grn" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>',
        "    </marker>",
        '    <marker id="arr-amb" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Pure-Logic Integer Factorization &amp; Masked Multipliers (integer-factoring)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Inverting Wallace &amp; Karatsuba AIG multipliers (p × q = N) with symmetry guards &amp; 16 sparse 𝔽₂ parity leaks</text>',
        '    <rect x="752" y="18" width="142" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="823" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">5 SAT · 1 UNSAT</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: KARATSUBA + MASKED MULTIPLIER INVERSION =================
    lx, ly, lw, lh = 24, 78, 558, 390
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Karatsuba Recursive Multiplier Inversion &amp; 𝔽₂ Side-Channel Overlay</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Native AIGER 1.9 circuits asserting p × q = N with odd LSBs p₀ = q₀ = 1 and ordering guard 1 &lt; p ≤ q</text>'
    )

    # Column 1: Unknown Factor Inputs p, q + Guard
    ix = lx + 16
    # Factor p split box
    p.append(f'    <rect x="{ix}" y="{ly + 56}" width="112" height="62" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
    p.append(f'    <text x="{ix + 56}" y="{ly + 73}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">Unknown p (n/2 b)</text>')
    p.append(f'    <rect x="{ix + 8}" y="{ly + 82}" width="44" height="26" rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>')
    p.append(f'    <text x="{ix + 30}" y="{ly + 99}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#0f172a">p_hi</text>')
    p.append(f'    <rect x="{ix + 58}" y="{ly + 82}" width="46" height="26" rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>')
    p.append(f'    <text x="{ix + 81}" y="{ly + 99}" text-anchor="middle" font-family="{mono}" font-size="9.2" font-weight="700" fill="#0f172a">p_lo|1</text>')

    # Factor q split box
    p.append(f'    <rect x="{ix}" y="{ly + 132}" width="112" height="62" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
    p.append(f'    <text x="{ix + 56}" y="{ly + 149}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">Unknown q (n/2 b)</text>')
    p.append(f'    <rect x="{ix + 8}" y="{ly + 158}" width="44" height="26" rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>')
    p.append(f'    <text x="{ix + 30}" y="{ly + 175}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#0f172a">q_hi</text>')
    p.append(f'    <rect x="{ix + 58}" y="{ly + 158}" width="46" height="26" rx="4" fill="#ffffff" stroke="#93c5fd" stroke-width="1"/>')
    p.append(f'    <text x="{ix + 81}" y="{ly + 175}" text-anchor="middle" font-family="{mono}" font-size="9.2" font-weight="700" fill="#0f172a">q_lo|1</text>')

    # Symmetry & Non-Triviality Guard Box
    p.append(f'    <rect x="{ix}" y="{ly + 206}" width="112" height="60" rx="7" fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>')
    p.append(f'    <text x="{ix + 56}" y="{ly + 223}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#b45309">Symmetry Guards</text>')
    p.append(f'    <text x="{ix + 56}" y="{ly + 239}" text-anchor="middle" font-family="{mono}" font-size="9.3" fill="#0f172a">p₀ = q₀ = 1 (odd)</text>')
    p.append(f'    <text x="{ix + 56}" y="{ly + 254}" text-anchor="middle" font-family="{mono}" font-size="9.3" fill="#0f172a">1 &lt; p ≤ q</text>')

    # Column 2: 3 Karatsuba Sub-Multipliers (O(n^1.585) -> Wallace base k <= 8)
    kx = lx + 162
    kw = 176
    kboxes = [
        (ly + 56, "#ffffff", "#2563eb", "#1d4ed8", "z₂ = p_hi × q_hi", "Wallace base (k ≤ 8)"),
        (ly + 124, "#f5f3ff", "#7c3aed", "#6d28d9", "z_mid = (p_lo+p_hi)(q_lo+q_hi)", "z₁ = z_mid − (z₀ + z₂)"),
        (ly + 196, "#ffffff", "#2563eb", "#1d4ed8", "z₀ = p_lo × q_lo", "Wallace base (k ≤ 8)"),
    ]
    # Wires from p, q into Karatsuba sub-multipliers
    p.append(f'    <path d="M {ix + 112} {ly + 82} L {kx - 2} {ly + 82}" fill="none" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-blue)"/>')
    p.append(f'    <path d="M {ix + 112} {ly + 98} C {ix + 136} {ly + 98}, {ix + 136} {ly + 150}, {kx - 2} {ly + 150}" fill="none" stroke="#7c3aed" stroke-width="1.5" marker-end="url(#arr-purp)"/>')
    p.append(f'    <path d="M {ix + 112} {ly + 158} C {ix + 136} {ly + 158}, {ix + 136} {ly + 162}, {kx - 2} {ly + 162}" fill="none" stroke="#7c3aed" stroke-width="1.5" marker-end="url(#arr-purp)"/>')
    p.append(f'    <path d="M {ix + 112} {ly + 178} C {ix + 138} {ly + 178}, {ix + 138} {ly + 224}, {kx - 2} {ly + 224}" fill="none" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-blue)"/>')

    for ky, bg, st, tc, l1, l2 in kboxes:
        p.append(f'    <rect x="{kx}" y="{ky}" width="{kw}" height="56" rx="7" fill="{bg}" stroke="{st}" stroke-width="1.4"/>')
        p.append(f'    <text x="{kx + kw/2:.1f}" y="{ky + 23}" text-anchor="middle" font-size="10.2" font-weight="700" fill="{tc}">{esc(l1)}</text>')
        p.append(f'    <text x="{kx + kw/2:.1f}" y="{ky + 41}" text-anchor="middle" font-size="9.3" fill="#475569">{esc(l2)}</text>')

    # Column 3: 3-Operand Wallace Recombination + Clamped Target N
    rx_box = lx + 372
    rw_box = 170
    # Arrows from z2, z1, z0 into Recombination box
    for ky_mid, col_a, mk in [(ly + 84, "#2563eb", "arr-blue"), (ly + 152, "#7c3aed", "arr-purp"), (ly + 224, "#2563eb", "arr-blue")]:
        p.append(f'    <line x1="{kx + kw}" y1="{ky_mid}" x2="{rx_box - 2}" y2="{ky_mid}" stroke="{col_a}" stroke-width="1.7" marker-end="url(#{mk})"/>')

    p.append(f'    <rect x="{rx_box}" y="{ly + 56}" width="{rw_box}" height="122" rx="8" fill="#ffffff" stroke="#059669" stroke-width="1.5"/>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 76}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#047857">Shift &amp; 3-Row Wallace</text>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 95}" text-anchor="middle" font-family="{mono}" font-size="9.4" font-weight="700" fill="#0f172a">z₀ + (z₁ ≪ m)</text>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 111}" text-anchor="middle" font-family="{mono}" font-size="9.4" font-weight="700" fill="#0f172a">   + (z₂ ≪ 2m)</text>')
    p.append(f'    <line x1="{rx_box + 14}" y1="{ly + 123}" x2="{rx_box + rw_box - 14}" y2="{ly + 123}" stroke="#e2e8f0" stroke-width="1"/>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 140}" text-anchor="middle" font-size="9.5" fill="#475569">Final CPA → product P</text>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 156}" text-anchor="middle" font-size="9.2" fill="#64748b">O(n¹·⁵⁸⁵) AIG gates</text>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 170}" text-anchor="middle" font-size="9.2" fill="#64748b">(coupled carry chains)</text>')

    # Clamped Product Output Assertion Box
    p.append(f'    <line x1="{rx_box + rw_box/2:.1f}" y1="{ly + 178}" x2="{rx_box + rw_box/2:.1f}" y2="{ly + 195}" stroke="#059669" stroke-width="1.8" marker-end="url(#arr-grn)"/>')
    p.append(f'    <rect x="{rx_box}" y="{ly + 198}" width="{rw_box}" height="68" rx="8" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 217}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#047857">Clamp P[i] == bit{sub("i")}(N)</text>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 235}" text-anchor="middle" font-size="9.5" font-weight="600" fill="#047857">SAT: semiprime N = p·q</text>')
    p.append(f'    <text x="{rx_box + rw_box/2:.1f}" y="{ly + 251}" text-anchor="middle" font-size="9.5" font-weight="600" fill="#dc2626">UNSAT: prime N (28b)</text>')

    # Bottom Side-Channel Masked XOR Leakage Overlay Box inside Left Panel
    my = ly + 282
    p.append(f'    <rect x="{lx + 16}" y="{my}" width="{lw - 32}" height="94" rx="8" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.4" stroke-dasharray="5,3"/>')
    p.append(f'    <text x="{lx + 30}" y="{my + 20}" font-size="11.5" font-weight="700" fill="#6d28d9">Masked Multiplier Side-Channel Overlay (masked_mult_32b_xor16)</text>')
    p.append(f'    <text x="{lx + 30}" y="{my + 37}" font-size="10" fill="#334155">Augments 32-bit Wallace factoring (N = 65519 × 65521) with 16 sparse 4-bit 𝔽₂ linear parity leaks:</text>')
    # 3 illustrative XOR4 equations in crisp pill boxes
    eqs = [
        "p₃ ⊕ p₁₁ ⊕ q₅ ⊕ q₁₄ = b₁",
        "p₂ ⊕ p₈ ⊕ q₁ ⊕ q₁₃ = b₂",
        "… (16 sparse XOR₄ leaks)",
    ]
    for idx_e, eq in enumerate(eqs):
        ex = lx + 30 + idx_e * 168
        ew = 158 if idx_e < 2 else 160
        p.append(f'    <rect x="{ex}" y="{my + 47}" width="{ew}" height="24" rx="5" fill="#ffffff" stroke="#a78bfa" stroke-width="1.1"/>')
        p.append(f'    <text x="{ex + ew/2:.1f}" y="{my + 62.5}" text-anchor="middle" font-family="{mono}" font-size="9.1" font-weight="600" fill="#6d28d9">{eq}</text>')
    p.append(f'    <text x="{lx + 30}" y="{my + 86}" font-size="9.4" fill="#475569">Tests hybrid CDCL + GF(2) Gaussian elimination coupling nonlinear carry chains with sparse linear equations</text>')

    # ================= RIGHT PANEL: ALL 6 INSTANCES & METRICS =================
    rx, ry, rw = 598, 78, 298

    # Card 1: Exact 6-Instance Table
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="262" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 22}" font-size="12" font-weight="700" fill="#0f172a">All 6 Instances (5 SAT / 1 UNSAT)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 36}" font-size="9.4" fill="#64748b">Native Binary AIGER 1.9 → CNF / XCNF / ANF (deg ≤ 2)</text>')

    items = [
        ("factor_prime_28b_unsat", "UNSAT", "#dc2626", "#fef2f2", "268,435,399 (prime 2²⁸−57)", "2,076 AND · 635 v · 202 XOR"),
        ("factor_wallace_32b", "SAT", "#059669", "#ecfdf5", "65,519 × 65,521 (Wallace)", "2,732 AND · 825 v · 264 XOR"),
        ("factor_wallace_36b", "SAT", "#059669", "#ecfdf5", "262,133 × 262,139 (Wallace)", "3,480 AND · 1,041 v · 335 XOR"),
        ("factor_karatsuba_36b", "SAT", "#7c3aed", "#f5f3ff", "262,133 × 262,139 (Karat.)", "3,289 AND · 999 v · 339 XOR"),
        ("factor_wallace_40b", "SAT", "#2563eb", "#eff6ff", "960,017 × 1,048,573 (40b)", "4,296 AND · 1,271 v · 409 XOR"),
        ("masked_mult_32b_xor16", "SAT", "#d97706", "#fffbeb", "65,519 × 65,521 + 16 XOR₄", "2,886 AND · 856 v · 295 XOR"),
    ]
    for i, (nm, st, col, bg, fac, dim) in enumerate(items):
        yy = ry + 48 + i * 35
        p.append(f'    <rect x="{rx + 10}" y="{yy}" width="{rw - 20}" height="31" rx="5" fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + 18}" y="{yy + 13}" font-family="{mono}" font-size="9.2" font-weight="700" fill="#0f172a">{nm}</text>')
        p.append(f'    <rect x="{rx + rw - 58}" y="{yy + 4}" width="42" height="14" rx="7" fill="{bg}" stroke="{col}" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + rw - 37}" y="{yy + 14}" text-anchor="middle" font-size="8.2" font-weight="700" fill="{col}">{st}</text>')
        p.append(f'    <text x="{rx + 18}" y="{yy + 25.5}" font-size="8.6" fill="#475569">{fac} · {dim}</text>')

    # Card 2: Structural & Phase-Transition Metrics
    cy2 = ry + 274
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="116" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">Structural Profile (Flat CNF)</text>')
    s_lines = [
        ("Regime:", f'Over (ρ{sub("crit")} = 1.48×–1.51×, κ = 0.98)'),
        ("Clauses:", f'3,264–6,717 · k̄ = 3.27 (k{sub("max")} = 4)'),
        ("Native XORs:", "1,844 total across 6 instances"),
        ("ANF Degree:", "Exact degree ≤ 2 (10,286 eqs total)"),
        ("Pure Logic:", "Zero number-theoretic shortcuts"),
    ]
    for i, (k, v) in enumerate(s_lines):
        yy = cy2 + 39 + i * 16.2
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.6" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 88}" y="{yy:.1f}" font-size="9.5" fill="#334155">{v}</text>')

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
