#!/usr/bin/env python3
"""Generate a standalone vector illustration (`diagram.svg`) for
`rsa-ntt-factoring` (O(n log n) Fermat-Prime NTT RSA Factoring Circuits).

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


def build_svg() -> str:
    W, H = 960, 520
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Fermat-Prime F_65537 NTT RSA Factoring Circuit Architecture and O(n log n) vs O(n^2) Gate-Count Crossover">',
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
        '    <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="33" font-size="17" font-weight="700" fill="#0f172a">'
        'O(n log n) Fermat-Prime NTT RSA Factoring Circuits (rsa-ntt-factoring)</text>',
        '    <text x="28" y="51" font-size="11.3" fill="#475569">'
        'Exact 𝔽₆₅₅₃₇ (F₄ = 2¹⁶ + 1) NTT multiplier circuits from 24 bits through RSA-896 (2026 record) to RSA-280 &amp; RSA-1024</text>',
        '    <rect x="780" y="17" width="154" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="857" y="33" text-anchor="middle" font-size="10.8" font-weight="700" fill="#047857">16 SAT · 1 UNSAT</text>',
        '    <line x1="24" y1="63" x2="936" y2="63" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # =========================================================================
    # TOP PANEL (a): EXACT F_65537 NTT FACTORING PIPELINE
    # =========================================================================
    px, py, pw, ph = 24, 74, 912, 166
    p.append(f'    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{px + 14}" y="{py + 21}" font-size="12.5" font-weight="700" fill="#0f172a">(a) Exact 𝔽₆₅₅₃₇ Number Theoretic Transform (NTT) Factoring Pipeline (Zero Wraparound: max cₖ ≤ 28,800 &lt; 65,537)</text>')

    # Stage 1: Inputs p, q -> 4-bit limbs
    sub_p = '<tspan baseline-shift="sub" font-size="72%">p</tspan>'
    sub_q = '<tspan baseline-shift="sub" font-size="72%">q</tspan>'
    b1x, b1y, b1w, b1h = px + 14, py + 34, 134, 118
    p.append(f'    <rect x="{b1x}" y="{b1y}" width="{b1w}" height="52" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
    p.append(f'    <text x="{b1x + b1w/2:.1f}" y="{b1y + 18}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1d4ed8">Factor p (b{sub_p} = ⌈B/2⌉)</text>')
    p.append(f'    <text x="{b1x + b1w/2:.1f}" y="{b1y + 33}" text-anchor="middle" font-family="{mono}" font-size="8.8" fill="#0f172a">m{sub_p} 4-bit limbs [0..15]</text>')
    p.append(f'    <text x="{b1x + b1w/2:.1f}" y="{b1y + 46}" text-anchor="middle" font-size="8.4" fill="#475569">p₀=1, p≥3, pad L zeros</text>')

    p.append(f'    <rect x="{b1x}" y="{b1y + 62}" width="{b1w}" height="52" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
    p.append(f'    <text x="{b1x + b1w/2:.1f}" y="{b1y + 80}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1d4ed8">Factor q (b{sub_q} ≤ 516)</text>')
    p.append(f'    <text x="{b1x + b1w/2:.1f}" y="{b1y + 95}" text-anchor="middle" font-family="{mono}" font-size="8.8" fill="#0f172a">m{sub_q} 4-bit limbs [0..15]</text>')
    p.append(f'    <text x="{b1x + b1w/2:.1f}" y="{b1y + 108}" text-anchor="middle" font-size="8.4" fill="#475569">q₀=1, 3≤p≤q, pad L</text>')

    # Stage 2: Forward DIF NTT
    b2x, b2y, b2w = b1x + b1w + 26, b1y, 152
    p.append(f'    <line x1="{b1x + b1w}" y1="{b1y + 26}" x2="{b2x - 2}" y2="{b1y + 26}" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-blue)"/>')
    p.append(f'    <line x1="{b1x + b1w}" y1="{b1y + 88}" x2="{b2x - 2}" y2="{b1y + 88}" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-blue)"/>')

    p.append(f'    <rect x="{b2x}" y="{b2y}" width="{b2w}" height="52" rx="7" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.4"/>')
    p.append(f'    <text x="{b2x + b2w/2:.1f}" y="{b2y + 18}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#6d28d9">Forward DIF NTT (p)</text>')
    p.append(f'    <text x="{b2x + b2w/2:.1f}" y="{b2y + 33}" text-anchor="middle" font-family="{mono}" font-size="8.7" fill="#0f172a">P̂ = NTT_L(p) mod F₄</text>')
    p.append(f'    <text x="{b2x + b2w/2:.1f}" y="{b2y + 46}" text-anchor="middle" font-size="8.3" fill="#475569">4b Stage-0 · CSD/2ᵏ twiddles</text>')

    p.append(f'    <rect x="{b2x}" y="{b2y + 62}" width="{b2w}" height="52" rx="7" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.4"/>')
    p.append(f'    <text x="{b2x + b2w/2:.1f}" y="{b2y + 80}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#6d28d9">Forward DIF NTT (q)</text>')
    p.append(f'    <text x="{b2x + b2w/2:.1f}" y="{b2y + 95}" text-anchor="middle" font-family="{mono}" font-size="8.7" fill="#0f172a">Q̂ = NTT_L(q) mod F₄</text>')
    p.append(f'    <text x="{b2x + b2w/2:.1f}" y="{b2y + 108}" text-anchor="middle" font-size="8.3" fill="#475569">L ∈ {{8,16,32,64,128,256}}</text>')

    # Stage 3: Pointwise Product mod 65537
    b3x, b3y, b3w = b2x + b2w + 26, b1y + 12, 148
    p.append(f'    <path d="M {b2x + b2w} {b2y + 26} C {b2x + b2w + 13} {b2y + 26}, {b2x + b2w + 13} {b3y + 26}, {b3x - 2} {b3y + 26}" fill="none" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')
    p.append(f'    <path d="M {b2x + b2w} {b2y + 88} C {b2x + b2w + 13} {b2y + 88}, {b2x + b2w + 13} {b3y + 64}, {b3x - 2} {b3y + 64}" fill="none" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')

    p.append(f'    <rect x="{b3x}" y="{b3y}" width="{b3w}" height="90" rx="8" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>')
    p.append(f'    <text x="{b3x + b3w/2:.1f}" y="{b3y + 20}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#b45309">Pointwise 𝔽₆₅₅₃₇ Mul</text>')
    p.append(f'    <text x="{b3x + b3w/2:.1f}" y="{b3y + 39}" text-anchor="middle" font-family="{mono}" font-size="9.0" font-weight="700" fill="#0f172a">Ĉ[k] = P̂[k]·Q̂[k]</text>')
    p.append(f'    <text x="{b3x + b3w/2:.1f}" y="{b3y + 56}" text-anchor="middle" font-size="8.6" fill="#475569">L parallel 16×16 Wallace</text>')
    p.append(f'    <text x="{b3x + b3w/2:.1f}" y="{b3y + 70}" text-anchor="middle" font-size="8.6" fill="#475569">+ exact F₄ negacyclic fold</text>')
    p.append(f'    <text x="{b3x + b3w/2:.1f}" y="{b3y + 83}" text-anchor="middle" font-family="{mono}" font-size="8.2" fill="#92400e">Z_lo − Z_hi mod (2¹⁶+1)</text>')

    # Stage 4: Inverse DIT NTT + L^-1 scaling
    b4x, b4y, b4w = b3x + b3w + 26, b3y, 152
    p.append(f'    <line x1="{b3x + b3w}" y1="{b3y + 45}" x2="{b4x - 2}" y2="{b3y + 45}" stroke="#7c3aed" stroke-width="1.7" marker-end="url(#arr-purp)"/>')
    p.append(f'    <rect x="{b4x}" y="{b4y}" width="{b4w}" height="90" rx="8" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.4"/>')
    p.append(f'    <text x="{b4x + b4w/2:.1f}" y="{b4y + 20}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#6d28d9">Inverse DIT NTT</text>')
    p.append(f'    <text x="{b4x + b4w/2:.1f}" y="{b4y + 39}" text-anchor="middle" font-family="{mono}" font-size="8.8" font-weight="700" fill="#0f172a">cₖ = L⁻¹·INTT(Ĉ)[k]</text>')
    p.append(f'    <text x="{b4x + b4w/2:.1f}" y="{b4y + 56}" text-anchor="middle" font-size="8.5" fill="#475569">L⁻¹ ≡ 2³²⁻ˡᵒᵍ²ᴸ (1 shift-sub)</text>')
    p.append(f'    <text x="{b4x + b4w/2:.1f}" y="{b4y + 70}" text-anchor="middle" font-size="8.5" fill="#475569">Exact integer ∑ pᵢqⱼ</text>')
    p.append(f'    <text x="{b4x + b4w/2:.1f}" y="{b4y + 83}" text-anchor="middle" font-family="{mono}" font-size="8.2" fill="#6d28d9">0 ≤ cₖ ≤ 28,800 &lt; 2¹⁵</text>')

    # Stage 5: Base-2^4 Carry Propagation + Clamp N
    b5x, b5y, b5w = b4x + b4w + 26, b3y, 198
    p.append(f'    <line x1="{b4x + b4w}" y1="{b4y + 45}" x2="{b5x - 2}" y2="{b4y + 45}" stroke="#059669" stroke-width="1.7" marker-end="url(#arr-grn)"/>')
    p.append(f'    <rect x="{b5x}" y="{b5y}" width="{b5w}" height="90" rx="8" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>')
    p.append(f'    <text x="{b5x + b5w/2:.1f}" y="{b5y + 20}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#047857">Base-2⁴ Carries &amp; Clamp N</text>')
    p.append(f'    <text x="{b5x + b5w/2:.1f}" y="{b5y + 39}" text-anchor="middle" font-family="{mono}" font-size="8.9" font-weight="700" fill="#0f172a">∑ cₖ·2⁴ᵏ == N (B bits)</text>')
    p.append(f'    <text x="{b5x + b5w/2:.1f}" y="{b5y + 56}" text-anchor="middle" font-size="8.5" fill="#047857">All upper product bits = 0</text>')
    p.append(f'    <text x="{b5x + b5w/2:.1f}" y="{b5y + 71}" text-anchor="middle" font-size="8.5" font-weight="600" fill="#047857">14/14 factored: AIG sim 1/0/0</text>')
    p.append(f'    <text x="{b5x + b5w/2:.1f}" y="{b5y + 84}" text-anchor="middle" font-size="8.3" fill="#dc2626">24b prime 2²⁴−3: UNSAT</text>')

    # =========================================================================
    # BOTTOM-LEFT PANEL (b): LOG-LOG GATE SCALING & EMPIRICAL CROSSOVER
    # =========================================================================
    gx, gy, gw, gh = 24, 252, 578, 250
    p.append(f'    <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{gx + 14}" y="{gy + 21}" font-size="12.5" font-weight="700" fill="#0f172a">(b) Exact AIGER AND-Gate Scaling: O(n log n) 𝔽₆₅₅₃₇ NTT vs. O(n²) Wallace</text>')
    p.append(f'    <text x="{gx + 14}" y="{gy + 36}" font-size="9.6" fill="#475569">Empirical crossover at B = 934 bits (just past RSA-896 record &amp; RSA-280); NTT saves 391,627 ANDs at RSA-1024</text>')

    # Plot coordinates (log10 x: 20..1200, log10 y: 1200..4_500_000)
    px0, py0, plot_w, plot_h = gx + 62, gy + 50, 492, 162
    xmin, xmax = math.log10(20.0), math.log10(1300.0)
    ymin, ymax = math.log10(1200.0), math.log10(4_500_000.0)

    def map_x(b: float) -> float:
        return px0 + (math.log10(b) - xmin) / (xmax - xmin) * plot_w

    def map_y(g: float) -> float:
        return py0 + plot_h - (math.log10(g) - ymin) / (ymax - ymin) * plot_h

    # Grid lines
    for ytick, ylbl in [(2_000, "2K"), (10_000, "10K"), (100_000, "100K"), (1_000_000, "1M"), (3_000_000, "3M")]:
        yy = map_y(ytick)
        p.append(f'    <line x1="{px0}" y1="{yy:.1f}" x2="{px0 + plot_w}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')
        p.append(f'    <text x="{px0 - 7}" y="{yy + 3.2:.1f}" text-anchor="end" font-family="{mono}" font-size="8.8" fill="#64748b">{ylbl}</text>')

    for xtick in [24, 32, 64, 128, 256, 512, 896, 1024]:
        xx = map_x(xtick)
        p.append(f'    <line x1="{xx:.1f}" y1="{py0}" x2="{xx:.1f}" y2="{py0 + plot_h}" stroke="#f1f5f9" stroke-width="0.9"/>')
        lbl = "896" if xtick == 896 else str(xtick)
        dy_off = 13 if xtick != 896 else 13
        col = "#dc2626" if xtick == 896 else "#64748b"
        fw = "700" if xtick == 896 else "400"
        if xtick == 896:
            # Put 896 label slightly left to avoid touching 1024
            p.append(f'    <text x="{xx - 4:.1f}" y="{py0 + plot_h + dy_off}" text-anchor="middle" font-family="{mono}" font-size="8.5" font-weight="{fw}" fill="{col}">896</text>')
        elif xtick == 1024:
            p.append(f'    <text x="{xx + 9:.1f}" y="{py0 + plot_h + dy_off}" text-anchor="middle" font-family="{mono}" font-size="8.5" font-weight="700" fill="#0f172a">1024</text>')
        else:
            p.append(f'    <text x="{xx:.1f}" y="{py0 + plot_h + dy_off}" text-anchor="middle" font-family="{mono}" font-size="8.5" fill="{col}">{lbl}</text>')

    # Axes box
    p.append(f'    <rect x="{px0}" y="{py0}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#94a3b8" stroke-width="1"/>')
    p.append(f'    <text x="{px0 + plot_w/2:.1f}" y="{py0 + plot_h + 29}" text-anchor="middle" font-size="9.8" font-weight="600" fill="#334155">Modulus Bit-Width B (log scale)</text>')
    p.append(f'    <text x="{gx + 16}" y="{py0 + plot_h/2:.1f}" text-anchor="middle" font-size="9.8" font-weight="600" fill="#334155" transform="rotate(-90 {gx + 16} {py0 + plot_h/2:.1f})">AIGER AND Gates (log)</text>')

    # Exact measured data points (Bits, NTT_ANDs, Wallace_ANDs)
    pts = [
        (24, 24390, 1704),
        (32, 26298, 2907),
        (40, 59884, 4420),
        (48, 61868, 6196),
        (64, 65244, 10714),
        (128, 154686, 40893),
        (256, 361728, 159461),
        (330, 819594, 263454),
        (512, 869555, 629684),
        (663, 1984637, 1056208),
        (829, 2043913, 1646760),
        (862, 2055538, 1775673),
        (896, 2066510, 1917894),
        (928, 2078686, 2056760),
        (934, 2081496, 2083349),
        (1024, 2111632, 2503259),
    ]

    # Shade NTT < Wallace region (B >= 934)
    x_cross = map_x(934)
    x_end = map_x(1024)
    p.append(f'    <rect x="{x_cross:.1f}" y="{py0}" width="{px0 + plot_w - x_cross:.1f}" height="{plot_h}" fill="#ecfdf5" opacity="0.65"/>')

    # Vertical dashed marker at RSA-896 record
    x896 = map_x(896)
    p.append(f'    <line x1="{x896:.1f}" y1="{py0}" x2="{x896:.1f}" y2="{py0 + plot_h}" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="4,3"/>')
    p.append(f'    <text x="{x896 - 6:.1f}" y="{py0 + 11.5}" text-anchor="end" font-size="8.6" font-weight="700" fill="#dc2626">RSA-896 (2026 Record)</text>')

    # Polylines
    wal_poly = " ".join(f"{map_x(b):.1f},{map_y(w):.1f}" for b, _, w in pts)
    ntt_poly = " ".join(f"{map_x(b):.1f},{map_y(n):.1f}" for b, n, _ in pts)
    p.append(f'    <polyline points="{wal_poly}" fill="none" stroke="#ea580c" stroke-width="2.2" stroke-dasharray="6,3"/>')
    p.append(f'    <polyline points="{ntt_poly}" fill="none" stroke="#2563eb" stroke-width="2.4"/>')

    # Data point markers
    for b, n, w in pts:
        if b == 934:
            continue
        p.append(f'    <circle cx="{map_x(b):.1f}" cy="{map_y(w):.1f}" r="2.7" fill="#ea580c"/>')
        p.append(f'    <circle cx="{map_x(b):.1f}" cy="{map_y(n):.1f}" r="3.0" fill="#2563eb"/>')

    # Crossover highlight marker (934b, 2.08M) — callout placed in clean lower-right empty space!
    xc, yc = map_x(934), map_y(2082000)
    bx, by = xc - 160, py0 + plot_h - 46
    p.append(f'    <circle cx="{xc:.1f}" cy="{yc:.1f}" r="5.0" fill="#059669" stroke="#ffffff" stroke-width="1.5"/>')
    p.append(f'    <path d="M {xc - 1:.1f} {yc + 5:.1f} L {bx + 128:.1f} {by:.1f}" fill="none" stroke="#059669" stroke-width="1.2"/>')
    p.append(f'    <rect x="{bx:.1f}" y="{by:.1f}" width="144" height="34" rx="5.5" fill="#ecfdf5" stroke="#059669" stroke-width="1.15"/>')
    p.append(f'    <text x="{bx + 72:.1f}" y="{by + 14:.1f}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#047857">Crossover: B = 934 bits</text>')
    p.append(f'    <text x="{bx + 72:.1f}" y="{by + 27:.1f}" text-anchor="middle" font-size="8.2" fill="#065f46">1024b: 2.11M vs 2.50M (−15.6%)</text>')

    # Legend inside top-left of plot
    p.append(f'    <rect x="{px0 + 10}" y="{py0 + 8}" width="186" height="42" rx="6" fill="#ffffff" fill-opacity="0.92" stroke="#cbd5e1" stroke-width="0.9"/>')
    p.append(f'    <line x1="{px0 + 18}" y1="{py0 + 21}" x2="{px0 + 40}" y2="{py0 + 21}" stroke="#2563eb" stroke-width="2.4"/>')
    p.append(f'    <text x="{px0 + 46}" y="{py0 + 24.5}" font-size="9.0" font-weight="600" fill="#0f172a">𝔽₆₅₅₃₇ NTT — O(n log n)</text>')
    p.append(f'    <line x1="{px0 + 18}" y1="{py0 + 38}" x2="{px0 + 40}" y2="{py0 + 38}" stroke="#ea580c" stroke-width="2.2" stroke-dasharray="5,2.5"/>')
    p.append(f'    <text x="{px0 + 46}" y="{py0 + 41.5}" font-size="9.0" font-weight="600" fill="#0f172a">Wallace Tree — O(n²)</text>')

    # =========================================================================
    # BOTTOM-RIGHT PANEL (c): RSA FRONTIER & 24b SOLVER BARRIER
    # =========================================================================
    rx, ry, rw, rh = 616, 252, 320, 250
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.5" font-weight="700" fill="#0f172a">(c) 2026 RSA Frontier (17 Instances)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 35}" font-size="9.2" fill="#475569">4 formats (AIG/CNF/XCNF/ANF), max 9.11 MB (&lt;95 MB)</text>')

    milestones = [
        ("ntt_prime_24b_unsat", "UNSAT", "#dc2626", "#fef2f2", "2²⁴−3 · 24K AND · Frob 2.22s (CDCL T/O)"),
        ("ntt_semiprime_24b", "SAT", "#059669", "#ecfdf5", "4091×4093 · 24K AND · Frob 1.31s (CDCL T/O)"),
        ("rsa155_512b_ntt", "1999", "#2563eb", "#eff6ff", "512b · L=128 · 870K AND · sim 1/0/0"),
        ("rsa250 / rsa260", "20–26", "#2563eb", "#eff6ff", "829–862b · L=256 · 2.04–2.06M AND"),
        ("rsa270_895b_ntt", "Nov26", "#2563eb", "#eff6ff", "895b · L=256 · 2.07M AND · sim 1/0/0"),
        ("rsa896_896b_ntt", "REC", "#dc2626", "#fef2f2", "896b Record (Sep 2026) · 2.07M · 1/0/0"),
        ("rsa280_928b_ntt", "OPEN", "#d97706", "#fffbeb", "928b First Unfactored · 2.08M (1.01× Wal)"),
        ("rsa1024_1024b_ntt", "OPEN", "#059669", "#ecfdf5", "1,024b Frontier · 2.11M (0.84× Wallace!)"),
    ]
    for i, (nm, tag, col, bg, desc) in enumerate(milestones):
        yy = ry + 45 + i * 24.5
        p.append(f'    <rect x="{rx + 10}" y="{yy:.1f}" width="{rw - 20}" height="21.5" rx="4.5" fill="#ffffff" stroke="#e2e8f0" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + 16}" y="{yy + 10.2:.1f}" font-family="{mono}" font-size="8.6" font-weight="700" fill="#0f172a">{esc(nm)}</text>')
        p.append(f'    <rect x="{rx + rw - 52}" y="{yy + 3.2:.1f}" width="36" height="14.5" rx="7" fill="{bg}" stroke="{col}" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + rw - 34}" y="{yy + 13.0:.1f}" text-anchor="middle" font-size="7.6" font-weight="700" fill="{col}">{tag}</text>')
        p.append(f'    <text x="{rx + 16}" y="{yy + 19.2:.1f}" font-size="7.7" fill="#475569">{esc(desc)}</text>')

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
