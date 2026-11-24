#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `sigal-aes256-xcnf` benchmark collection.

Illustrates Victor Sigal's exact full 14-round NIST FIPS 197 AES-256
known-plaintext key-recovery XCNF instances (`w5.solved` & `w126.unsolved`):
  - Dual 14-round encryption copies E_1(K, P_1) = C_1 and E_2(K, P_2) = C_2
    sharing a single 256-bit key schedule (0 key bits fixed)
  - 500 Boyar-Peralta AES S-boxes (52 key-schedule + 2 x 224 round S-boxes)
    decomposed into 42,812 native XORs + 16,000 ANDs + 90,500 Grobner bins
  - Key Hamming-weight contrast: w5.solved (wt=5, C(256,5) ~ 2^33) vs
    w126.unsolved (wt=126, C(256,126) ~ 2^252), with 165,312/165,824 lines
    byte-identical across both files.

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
    W, H = 920, 504
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Dual 14-round AES-256 known-plaintext key recovery XCNF with Boyar-Peralta S-boxes and w5 vs w126 key weights">',
        "<defs>",
        '  <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>',
        '  <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '  <marker id="arr-amber" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/></marker>',
        '  <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>',
        "</defs>",
        # White card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Full 14-Round AES-256 Known-Plaintext Key-Recovery XCNF (sigal-aes256-xcnf)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Dual FIPS 197 encryption copies E₁(K, P₁) = C₁ ∧ E₂(K, P₂) = C₂ sharing a 256-bit key schedule · "
        "59,324 vars · 500 Boyar–Peralta S-boxes</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: DUAL AES-256 ARCHITECTURE =====================
    px, py, pw, ph = 24, 74, 566, 286
    parts.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px + 12}" y="{py + 19}" font-size="12" font-weight="700" fill="#0f172a">'
        "Dual Known-Plaintext Miter (165,312 / 165,824 Lines Byte-Identical Across w5 &amp; w126)</text>"
    )

    # Top Center: Unknown 256-bit Secret Key K
    kx, ky, kw, kh = px + 188, py + 30, 190, 34
    parts.append(
        f'<rect x="{kx}" y="{ky}" width="{kw}" height="{kh}" rx="7" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.4"/>'
    )
    parts.append(
        f'<text x="{kx + kw/2:.1f}" y="{ky + 14}" text-anchor="middle" '
        'font-size="10.4" font-weight="700" fill="#b45309">Unknown 256-Bit Key K</text>'
    )
    parts.append(
        f'<text x="{kx + kw/2:.1f}" y="{ky + 27}" text-anchor="middle" '
        'font-size="8.8" fill="#475569">vars 1..256 (0 key bits fixed)</text>'
    )

    # Center Column: Shared 14-Round Key Schedule
    ksx, ksy, ksw, ksh = px + 206, py + 82, 154, 156
    parts.append(
        f'<rect x="{ksx}" y="{ksy}" width="{ksw}" height="{ksh}" rx="8" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{ksx + ksw/2:.1f}" y="{ksy + 17}" text-anchor="middle" '
        'font-size="10.3" font-weight="700" fill="#b45309">AES-256 Key Schedule</text>'
    )
    parts.append(
        f'<text x="{ksx + ksw/2:.1f}" y="{ksy + 30}" text-anchor="middle" '
        'font-size="8.6" fill="#475569">52 S-boxes · 9,412 bins</text>'
    )
    parts.append(
        f'<line x1="{kx + kw/2:.1f}" y1="{ky + kh}" x2="{ksx + ksw/2:.1f}" y2="{ksy - 2}" '
        'stroke="#d97706" stroke-width="1.5" marker-end="url(#arr-amber)"/>'
    )

    # Round keys rk0..rk14 inside Key Schedule box
    rk_labels = ["rk₀, rk₁ (256b)", "rk₂ .. rk₇", "rk₈ .. rk₁₃", "rk₁₄ (final)"]
    rk_ys: list[float] = []
    for idx, rkl in enumerate(rk_labels):
        ry_k = ksy + 42 + idx * 27
        rk_ys.append(ry_k + 10)
        parts.append(
            f'<rect x="{ksx + 12}" y="{ry_k}" width="{ksw - 24}" height="20" rx="4" '
            'fill="#ffffff" stroke="#fcd34d" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{ksx + ksw/2:.1f}" y="{ry_k + 13.5}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="8.8" font-weight="600" fill="#92400e">{rkl}</text>'
        )

    # Left Copy E1(K, P1) = C1 and Right Copy E2(K, P2) = C2
    copies = [
        (px + 16, "E₁(K, P₁) = C₁", "P₁ (128 unit cls)", "vars 7293..7420", "C₁ (128 unit cls)", "vars 7421..7548"),
        (px + 394, "E₂(K, P₂) = C₂", "P₂ (128 unit cls)", "vars 7549..7676", "C₂ (128 unit cls)", "vars 7677..7804"),
    ]
    cw = 156
    for cx, title, pt, pt_v, ct, ct_v in copies:
        # Plaintext unit box
        parts.append(f'<rect x="{cx}" y="{py + 30}" width="{cw}" height="34" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
        parts.append(f'<text x="{cx + cw/2:.1f}" y="{py + 44}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#047857">{pt}</text>')
        parts.append(f'<text x="{cx + cw/2:.1f}" y="{py + 57}" text-anchor="middle" font-size="8.4" fill="#475569">{pt_v}</text>')

        # Arrow P -> AES-256 stack
        parts.append(f'<line x1="{cx + cw/2:.1f}" y1="{py + 64}" x2="{cx + cw/2:.1f}" y2="{ksy - 2}" stroke="#2563eb" stroke-width="1.4" marker-end="url(#arr-blue)"/>')

        # 14-Round Encryption Stack
        parts.append(f'<rect x="{cx}" y="{ksy}" width="{cw}" height="{ksh}" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
        parts.append(f'<text x="{cx + cw/2:.1f}" y="{ksy + 17}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#1d4ed8">{title}</text>')
        parts.append(f'<text x="{cx + cw/2:.1f}" y="{ksy + 30}" text-anchor="middle" font-size="8.6" fill="#475569">14 Rounds · 224 S-boxes</text>')

        steps = [
            ("SubBytes (16 × BP S-box)", "#f5f3ff", "#7c3aed"),
            ("ShiftRows (byte perm)", "#ffffff", "#2563eb"),
            ("MixColumns (GF(2⁸) XOR)", "#ffffff", "#2563eb"),
            ("AddRoundKey (⊕ rkᵣ)", "#fffbeb", "#d97706"),
        ]
        for s_i, (stxt, sbg, sbd) in enumerate(steps):
            sy_s = ksy + 42 + s_i * 27
            parts.append(f'<rect x="{cx + 8}" y="{sy_s}" width="{cw - 16}" height="21" rx="4" fill="{sbg}" stroke="{sbd}" stroke-width="0.95"/>')
            parts.append(f'<text x="{cx + cw/2:.1f}" y="{sy_s + 14}" text-anchor="middle" font-size="8.6" font-weight="600" fill="#1e293b">{stxt}</text>')

        # Arrow AES-256 stack -> Ciphertext unit box
        ct_y = ksy + ksh + 14
        parts.append(f'<line x1="{cx + cw/2:.1f}" y1="{ksy + ksh}" x2="{cx + cw/2:.1f}" y2="{ct_y - 2}" stroke="#2563eb" stroke-width="1.4" marker-end="url(#arr-blue)"/>')
        parts.append(f'<rect x="{cx}" y="{ct_y}" width="{cw}" height="28" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
        parts.append(f'<text x="{cx + cw/2:.1f}" y="{ct_y + 12}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#047857">{ct}</text>')
        parts.append(f'<text x="{cx + cw/2:.1f}" y="{ct_y + 23}" text-anchor="middle" font-size="8.2" fill="#475569">{ct_v}</text>')

    # Horizontal dashed round-key distribution arrows from Key Schedule to E1 & E2
    for ry_a in rk_ys:
        parts.append(
            f'<line x1="{ksx}" y1="{ry_a:.1f}" x2="{px + 16 + cw + 2}" y2="{ry_a:.1f}" '
            'stroke="#d97706" stroke-width="1.2" stroke-dasharray="3,2" marker-end="url(#arr-amber)"/>'
        )
        parts.append(
            f'<line x1="{ksx + ksw}" y1="{ry_a:.1f}" x2="{px + 394 - 2}" y2="{ry_a:.1f}" '
            'stroke="#d97706" stroke-width="1.2" stroke-dasharray="3,2" marker-end="url(#arr-amber)"/>'
        )

    # NIST verification pill centered under Key Schedule
    parts.append(f'<rect x="{ksx}" y="{ksy + ksh + 14}" width="{ksw}" height="28" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{ksx + ksw/2:.1f}" y="{ksy + ksh + 26}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#0f172a">NIST FIPS 197 Verified</text>')
    parts.append(f'<text x="{ksx + ksw/2:.1f}" y="{ksy + ksh + 37}" text-anchor="middle" font-size="8" fill="#475569">AES(0,0) matches 128/128 bits</text>')

    # ===================== RIGHT PANEL: BOYAR-PERALTA S-BOX XCNF/CNF SPLIT =====================
    rx, rw = 604, 292
    # Card 1: Boyar-Peralta S-Box Decomposition
    parts.append(
        f'<rect x="{rx}" y="74" width="{rw}" height="184" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="94" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Boyar–Peralta S-Box Split (×500 total)</text>"
    )

    # 3 stacked layers of Boyar-Peralta S-box
    bp_layers = [
        (104, "#eff6ff", "#2563eb", "#1d4ed8", "Top &amp; Bottom Linear Maps (U, W)",
         "42,812 native x-clauses (len 3..15, mean 6.02)"),
        (146, "#f5f3ff", "#7c3aed", "#6d28d9", "Nonlinear Core: 32 ANDs / S-box (16,000)",
         "Compact: (¬z∨b), (¬b∨¬d) + 3-XOR d = a⊕z"),
        (188, "#fffbeb", "#d97706", "#b45309", "Gröbner-Basis Implied Binary Clauses",
         "181 bins / S-box = 90,500 redundant propagators"),
    ]
    for ly_b, bg, bd, fg, t1, t2 in bp_layers:
        parts.append(f'<rect x="{rx + 12}" y="{ly_b}" width="{rw - 24}" height="34" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1.15"/>')
        parts.append(f'<text x="{rx + 22}" y="{ly_b + 14}" font-size="9.7" font-weight="700" fill="{fg}">{t1}</text>')
        parts.append(f'<text x="{rx + 22}" y="{ly_b + 27}" font-size="8.7" fill="#334155">{t2}</text>')

    parts.append(
        f'<text x="{rx + 14}" y="238" font-size="9" font-weight="600" fill="#0f172a">'
        "Total XCNF: 123,012 CNF + 42,812 XOR = 165,824 cls</text>"
    )
    parts.append(
        f'<text x="{rx + 14}" y="251" font-size="8.7" fill="#475569">'
        "Max depth 215 · AND-depth 84 · 1 connected component</text>"
    )

    # Card 2: Four-Format Expansion Stats
    parts.append(
        f'<rect x="{rx}" y="268" width="{rw}" height="92" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="287" font-size="11.4" font-weight="700" fill="#0f172a">'
        "Exact Four-Format Representation</text>"
    )
    fmt_lines = [
        ("XCNF (orig):", "59,324 vars · 165,824 cls (489 KB .xz)"),
        ("Tseitin CNF:", "119,644 vars · 811,268 cls · ρ_c = 1.76×"),
        ("AIGER 1.9:", "256 PIs · 460,647–460,695 ANDs"),
        ("DIMACS-ANF:", "59,324 vars · 165,824 eqs (deg ≤ 2)"),
    ]
    for f_i, (fk, fv) in enumerate(fmt_lines):
        fy_f = 304 + f_i * 14.5
        parts.append(f'<text x="{rx + 14}" y="{fy_f:.1f}" font-size="8.9" font-weight="700" fill="#1e293b">{fk}</text>')
        parts.append(f'<text x="{rx + 84}" y="{fy_f:.1f}" font-size="8.9" fill="#475569">{fv}</text>')

    # ===================== BOTTOM PANEL: w5 vs w126 HAMMING-WEIGHT SIDE INFO =====================
    bx, by, bw, bh = 24, 372, 872, 114
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{bx + 14}" y="{by + 19}" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Why w5.solved vs. w126.unsolved Differ — Unencoded Key Hamming-Weight Side Information</text>"
    )

    # Left Card: w5.solved
    c1x, c1y, c1w, c1h = bx + 14, by + 28, 414, 74
    parts.append(f'<rect x="{c1x}" y="{c1y}" width="{c1w}" height="{c1h}" rx="7" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
    parts.append(f'<text x="{c1x + 12}" y="{c1y + 17}" font-size="10.6" font-weight="700" fill="#047857">w5.solved.xcnf  (SAT — unique known key)</text>')
    # 256-bit key strip with 5 active bits
    strip_x, strip_y, strip_w = c1x + 12, c1y + 25, c1w - 24
    parts.append(f'<rect x="{strip_x}" y="{strip_y}" width="{strip_w}" height="12" rx="3" fill="#ffffff" stroke="#6ee7b7" stroke-width="1"/>')
    for pos in (0.07, 0.24, 0.49, 0.71, 0.91):
        parts.append(f'<rect x="{strip_x + pos * strip_w:.1f}" y="{strip_y + 1.5}" width="5" height="9" rx="1" fill="#059669"/>')
    parts.append(
        f'<text x="{c1x + 12}" y="{c1y + 52}" font-size="9.2" fill="#1e293b">'
        "Secret key weight wt(K) = 5  ⇒  C(256, 5) ≈ 8.8×10⁹ ≈ 2³³ candidates</text>"
    )
    parts.append(
        f'<text x="{c1x + 12}" y="{c1y + 65}" font-size="8.8" fill="#475569">'
        "Reachable ONLY with external weight bound (NO weight constraint in XCNF!)</text>"
    )

    # Right Card: w126.unsolved
    c2x = c1x + c1w + 16
    parts.append(f'<rect x="{c2x}" y="{c1y}" width="{c1w}" height="{c1h}" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>')
    parts.append(f'<text x="{c2x + 12}" y="{c1y + 17}" font-size="10.6" font-weight="700" fill="#b91c1c">w126.unsolved.xcnf  (OPEN — 2-year challenge)</text>')
    # 256-bit key strip with ~50% dense active bits
    strip2_x = c2x + 12
    parts.append(f'<rect x="{strip2_x}" y="{strip_y}" width="{strip_w}" height="12" rx="3" fill="#ffffff" stroke="#fca5a5" stroke-width="1"/>')
    # Deterministic pseudorandom ~126/256 bit pattern across 64 mini-cells
    for k_i in range(64):
        if ((k_i * 37 + 11) % 7) in (0, 2, 4, 5):
            parts.append(
                f'<rect x="{strip2_x + 2 + k_i * (strip_w - 4) / 64:.1f}" y="{strip_y + 1.5}" '
                f'width="{(strip_w - 4) / 64 - 0.8:.1f}" height="9" rx="0.8" fill="#dc2626"/>'
            )
    parts.append(
        f'<text x="{c2x + 12}" y="{c1y + 52}" font-size="9.2" fill="#1e293b">'
        "Balanced key weight wt(K) = 126  ⇒  C(256, 126) ≈ 2²⁵² candidates</text>"
    )
    parts.append(
        f'<text x="{c2x + 12}" y="{c1y + 65}" font-size="8.8" fill="#475569">'
        "Full-strength 14-round AES-256 barrier (≈ 2²⁵⁴·⁴); all 5 solvers T/O at 30 s</text>"
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
