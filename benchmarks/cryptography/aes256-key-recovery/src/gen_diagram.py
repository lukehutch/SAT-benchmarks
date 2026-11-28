#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `aes256-key-recovery` benchmark collection.

Illustrates the clean-room NIST FIPS 197 AES-256 14-round SPN & KeyExpansion
circuit implemented in `src/gen_aes256.py`:
  - 4x4 byte state datapath (SubBytes -> ShiftRows -> MixColumns -> AddRoundKey)
  - Boyar-Peralta (SEA 2010, Table 1) 32-AND / 81-XOR-XNOR S-box decomposition
  - Algebraic equivalence to fixed-IV Davies-Meyer AES-256 hash preimage
  - Deterministic SHA-256 provenance & 256-bit key free/fixed bit mask
  - Graduated 10-instance (R, k) difficulty ladder (8 SAT / 2 UNSAT).

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"

FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def build_svg() -> str:
    W, H = 920, 536
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="NIST FIPS 197 AES-256 SPN round, Boyar-Peralta S-box, Davies-Meyer equivalence, and graduated (R, k) difficulty ladder">',
        "<defs>",
        '  <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>',
        '  <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '  <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>',
        '  <marker id="arr-amber" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/></marker>',
        "</defs>",
        # Card frame
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.2" font-weight="700" fill="#0f172a">'
        "Synthetic NIST FIPS 197 AES-256 Key-Recovery &amp; Hash-Preimage (aes256-key-recovery)</text>",
        '<text x="26" y="53" font-size="11.4" fill="#475569">'
        "Clean-room Boyar–Peralta S-box (32 AND / 81 XOR-XNOR) · Factored GF(2⁸) MixColumns · "
        "10 calibrated instances (8 SAT / 2 UNSAT), R ∈ {1, 2, 3, 4, 14}</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: AES-256 SPN ROUND & KEY SCHEDULE =====================
    lx, ly, lw, lh = 24, 74, 574, 294
    parts.append(
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{lx + 12}" y="{ly + 19}" font-size="12" font-weight="700" fill="#0f172a">'
        "NIST FIPS 197 AES-256 SPN Round r ∈ {1..R}  &amp;  256-Bit KeyExpansion</text>"
    )

    # 4x4 State Matrix Icon (top-left of left panel)
    mx, my = lx + 16, ly + 36
    cell = 17
    parts.append(
        f'<text x="{mx + 2 * cell}" y="{my - 4}" text-anchor="middle" '
        'font-size="9.2" font-weight="700" fill="#334155">4×4 State (128 b)</text>'
    )
    row_colors = ["#eff6ff", "#f5f3ff", "#ecfdf5", "#fffbeb"]
    for r in range(4):
        for c in range(4):
            cx_cell = mx + c * cell
            cy_cell = my + r * cell
            parts.append(
                f'<rect x="{cx_cell}" y="{cy_cell}" width="{cell - 1}" height="{cell - 1}" rx="2.5" '
                f'fill="{row_colors[r]}" stroke="#94a3b8" stroke-width="0.9"/>'
            )
            parts.append(
                f'<text x="{cx_cell + (cell - 1)/2:.1f}" y="{cy_cell + 11.2}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="7.4" fill="#334155">{4 * c + r:x}</text>'
            )
    parts.append(
        f'<text x="{mx + 2 * cell}" y="{my + 4 * cell + 12}" text-anchor="middle" '
        'font-size="8.2" fill="#475569">P ⊕ RK₀</text>'
    )

    # Four SPN Round Stages across top row
    stages = [
        (lx + 106, ly + 38, 108, 66, "#f5f3ff", "#7c3aed", "#6d28d9", "SubBytes", "16× Boyar–Peralta", "32 AND · 81 XOR"),
        (lx + 230, ly + 38, 92,  66, "#f1f5f9", "#64748b", "#334155", "ShiftRows", "Row r ≪ r", "0 gates (wires)"),
        (lx + 338, ly + 38, 112, 66, "#eff6ff", "#2563eb", "#1d4ed8", "MixColumns*", "GF(2⁸) MDS", "76 XOR/col (w≤4)"),
        (lx + 466, ly + 38, 94,  66, "#ecfdf5", "#059669", "#047857", "AddRoundKey", "State ⊕ RKᵣ", "128 2-XORs"),
    ]
    # Arrow from 4x4 state to SubBytes
    parts.append(
        f'<line x1="{mx + 4 * cell + 2}" y1="{ly + 71}" x2="{stages[0][0] - 3}" y2="{ly + 71}" '
        'stroke="#475569" stroke-width="1.4" marker-end="url(#arr-slate)"/>'
    )
    for idx, (sx, sy, sw, sh, bg, bd, fg, title, l1, l2) in enumerate(stages):
        parts.append(
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="7" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1.3"/>'
        )
        parts.append(
            f'<text x="{sx + sw / 2:.1f}" y="{sy + 20}" text-anchor="middle" '
            f'font-size="10.8" font-weight="700" fill="{fg}">{title}</text>'
        )
        parts.append(
            f'<text x="{sx + sw / 2:.1f}" y="{sy + 38}" text-anchor="middle" '
            'font-size="8.9" font-weight="600" fill="#334155">' + l1 + "</text>"
        )
        parts.append(
            f'<text x="{sx + sw / 2:.1f}" y="{sy + 53}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="8.1" fill="#475569">{l2}</text>'
        )
        if idx < len(stages) - 1:
            nx = stages[idx + 1][0]
            parts.append(
                f'<line x1="{sx + sw}" y1="{sy + sh / 2:.1f}" x2="{nx - 3}" y2="{sy + sh / 2:.1f}" '
                'stroke="#475569" stroke-width="1.4" marker-end="url(#arr-slate)"/>'
            )

    # Note under MixColumns
    parts.append(
        f'<text x="{lx + 394}" y="{ly + 116}" text-anchor="middle" font-size="8.1" fill="#475569">'
        "*omitted on final round R (FIPS 197)</text>"
    )

    # KeyExpansion Row (middle of left panel)
    kx, ky, kw, kh = lx + 16, ly + 130, 544, 74
    parts.append(
        f'<rect x="{kx}" y="{ky}" width="{kw}" height="{kh}" rx="8" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{kx + 12}" y="{ky + 18}" font-size="10.4" font-weight="700" fill="#b45309">'
        "AES-256 KeyExpansion  (Nₖ = 8 words = 256 bits → 4(R+1) words, up to 60 words / 52 S-boxes at R = 14)</text>"
    )
    k_boxes = [
        (kx + 12,  ky + 27, 134, 36, "W[0..7] = Key K", "vars 1..256 (LSB-first)"),
        (kx + 164, ky + 27, 174, 36, "i mod 8 = 0: Sub(Rot)⊕Rcon", "28 S-boxes at R=14"),
        (kx + 356, ky + 27, 176, 36, "i mod 8 = 4: SubWord(Wᵢ₋₁)", "AES-256 extra nonlinear step"),
    ]
    for idx, (bx_i, by_i, bw_i, bh_i, bt, bs) in enumerate(k_boxes):
        parts.append(
            f'<rect x="{bx_i}" y="{by_i}" width="{bw_i}" height="{bh_i}" rx="5" '
            'fill="#ffffff" stroke="#f59e0b" stroke-width="1.1"/>'
        )
        parts.append(
            f'<text x="{bx_i + bw_i / 2:.1f}" y="{by_i + 15}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="8.6" font-weight="700" fill="#0f172a">{bt}</text>'
        )
        parts.append(
            f'<text x="{bx_i + bw_i / 2:.1f}" y="{by_i + 29}" text-anchor="middle" '
            f'font-size="8.2" fill="#475569">{bs}</text>'
        )
        if idx < len(k_boxes) - 1:
            parts.append(
                f'<line x1="{bx_i + bw_i}" y1="{by_i + bh_i / 2:.1f}" x2="{k_boxes[idx + 1][0] - 3}" y2="{by_i + bh_i / 2:.1f}" '
                'stroke="#d97706" stroke-width="1.3" marker-end="url(#arr-amber)"/>'
            )

    # Vertical feed arrow from KeyExpansion up into AddRoundKey
    parts.append(
        f'<line x1="{lx + 513}" y1="{ky}" x2="{lx + 513}" y2="{ly + 106}" '
        'stroke="#d97706" stroke-width="1.5" marker-end="url(#arr-amber)"/>'
    )

    # Davies-Meyer Equivalence + Dual-Plaintext Miter Banner (bottom of left panel)
    dx, dy, dw, dh = lx + 16, ly + 216, 544, 66
    parts.append(
        f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="8" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1.15"/>'
    )
    parts.append(
        f'<text x="{dx + 12}" y="{dy + 19}" font-size="10.4" font-weight="700" fill="#0f172a">'
        "Davies–Meyer AES-256 Hash-Preimage Equivalence  &amp;  Dual-Plaintext Miter</text>"
    )
    parts.append(
        f'<text x="{dx + 12}" y="{dy + 38}" font-family="{FONT_MONO}" font-size="9.2" font-weight="600" fill="#1d4ed8">'
        "H = AES-256(K, P) ⊕ P  ⟺  AES-256(K, P) = C   where C = H ⊕ P   (bit-identical circuit)</text>"
    )
    parts.append(
        f'<text x="{dx + 12}" y="{dy + 55}" font-size="8.9" fill="#475569">'
        "For k = 256 (aes256_r14_k256_dual_sat), two blocks share KeyExpansion: "
        "AES-256(K, P₁)=C₁ ∧ AES-256(K, P₂)=C₂ (unique 256-bit key).</text>"
    )

    # ===================== RIGHT PANEL: 2 STACKED CARDS =====================
    rx, rw = 612, 284

    # Card 1: Key Bit Mask & Transparent Deterministic Provenance
    parts.append(
        f'<rect x="{rx}" y="74" width="{rw}" height="148" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="94" font-size="11.6" font-weight="700" fill="#0f172a">'
        "Key Bit Mask &amp; Deterministic Seeds</text>"
    )
    # Key bar
    kbx, kby, kbw = rx + 14, 104, rw - 28
    parts.append(f'<rect x="{kbx}" y="{kby}" width="{kbw * 0.48:.1f}" height="22" rx="4" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>')
    parts.append(
        f'<text x="{kbx + kbw * 0.24:.1f}" y="{kby + 14.5}" text-anchor="middle" '
        'font-size="9.1" font-weight="700" fill="#b91c1c">k free bits (0..k−1)</text>'
    )
    parts.append(f'<rect x="{kbx + kbw * 0.48 + 4:.1f}" y="{kby}" width="{kbw * 0.52 - 4:.1f}" height="22" rx="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>')
    parts.append(
        f'<text x="{kbx + kbw * 0.74 + 2:.1f}" y="{kby + 14.5}" text-anchor="middle" '
        'font-size="8.9" font-weight="600" fill="#334155">256−k fixed units</text>'
    )
    parts.append(
        f'<text x="{rx + 14}" y="143" font-size="9.0" font-weight="600" fill="#334155">'
        "100% synthetic SHA-256 provenance:</text>"
    )
    parts.append(
        f'<rect x="{rx + 14}" y="149" width="{rw - 28}" height="24" rx="5" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{rx + rw / 2:.1f}" y="164.5" text-anchor="middle" font-family="{FONT_MONO}" '
        'font-size="7.6" font-weight="600" fill="#0f172a">SHA-256("frobenius-aes256-benchmark-v1:name:role")</text>'
    )
    # Verification check badges
    parts.append(f'<rect x="{rx + 14}" y="182" width="124" height="28" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
    parts.append(f'<text x="{rx + 76}" y="195" text-anchor="middle" font-size="8.4" font-weight="700" fill="#047857">FIPS-197 C.3 &amp; (0,0)</text>')
    parts.append(f'<text x="{rx + 76}" y="205.5" text-anchor="middle" font-size="7.9" fill="#065f46">128/128 bits PASS ✓</text>')
    parts.append(f'<rect x="{rx + 146}" y="182" width="124" height="28" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
    parts.append(f'<text x="{rx + 208}" y="195" text-anchor="middle" font-size="8.4" font-weight="700" fill="#047857">BP S-Box &amp; UNSAT</text>')
    parts.append(f'<text x="{rx + 208}" y="205.5" text-anchor="middle" font-size="7.9" fill="#065f46">256/256 &amp; 2¹²=0 ✓</text>')

    # Card 2: Boyar-Peralta S-Box Decomposition & 4-Format Pipeline
    parts.append(
        f'<rect x="{rx}" y="232" width="{rw}" height="136" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="252" font-size="11.4" font-weight="700" fill="#0f172a">'
        "Boyar–Peralta S-Box (113 Gates)</text>"
    )
    bp_stages = [
        (rx + 14, 262, 76, 44, "#eff6ff", "#2563eb", "#1d4ed8", "Top Linear", "23 XORs", "U → y₁..y₂₁"),
        (rx + 104, 262, 76, 44, "#f5f3ff", "#7c3aed", "#6d28d9", "GF(2⁴) Inv", "32 AND", "+ 30 XORs"),
        (rx + 194, 262, 76, 44, "#eff6ff", "#2563eb", "#1d4ed8", "Bot Affine", "28 XOR/XN", "+ 0x63"),
    ]
    for idx, (bx_s, by_s, bw_s, bh_s, bg, bd, fg, st, sl1, sl2) in enumerate(bp_stages):
        parts.append(f'<rect x="{bx_s}" y="{by_s}" width="{bw_s}" height="{bh_s}" rx="5" fill="{bg}" stroke="{bd}" stroke-width="1.15"/>')
        parts.append(f'<text x="{bx_s + bw_s / 2:.1f}" y="{by_s + 14}" text-anchor="middle" font-size="8.8" font-weight="700" fill="{fg}">{st}</text>')
        parts.append(f'<text x="{bx_s + bw_s / 2:.1f}" y="{by_s + 27}" text-anchor="middle" font-size="8.2" font-weight="600" fill="#334155">{sl1}</text>')
        parts.append(f'<text x="{bx_s + bw_s / 2:.1f}" y="{by_s + 38}" text-anchor="middle" font-size="7.8" fill="#475569">{sl2}</text>')
        if idx < 2:
            parts.append(
                f'<line x1="{bx_s + bw_s}" y1="{by_s + bh_s / 2:.1f}" x2="{bp_stages[idx + 1][0] - 2}" y2="{by_s + bh_s / 2:.1f}" '
                'stroke="#475569" stroke-width="1.2" marker-end="url(#arr-slate)"/>'
            )

    # 4-format pill strip
    parts.append(
        f'<text x="{rx + 14}" y="324" font-size="9.0" font-weight="700" fill="#334155">'
        "Lossless 4-Format Export (40 files, 3.92 MB total):</text>"
    )
    fmt_pills = [
        (rx + 14,  "xcnf-orig",  "#fef3c7", "#b45309"),
        (rx + 80,  "cnf-conv",   "#eff6ff", "#1d4ed8"),
        (rx + 144, "aig-conv",   "#ecfdf5", "#047857"),
        (rx + 208, "anf-conv",   "#f5f3ff", "#6d28d9"),
    ]
    for px_f, flbl, fbg, ffg in fmt_pills:
        parts.append(f'<rect x="{px_f}" y="332" width="60" height="22" rx="4.5" fill="{fbg}" stroke="{ffg}" stroke-width="1"/>')
        parts.append(f'<text x="{px_f + 30}" y="346.5" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.0" font-weight="700" fill="{ffg}">{flbl}</text>')

    # ===================== BOTTOM PANEL: GRADUATED 10-INSTANCE (R, k) LADDER =====================
    bx, by, bw, bh = 24, 380, 872, 140
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{bx + 14}" y="{by + 19}" font-size="11.6" font-weight="700" fill="#0f172a">'
        "Graduated 10-Instance Difficulty Ladder:  Reduced-Round Propagation → Full Diffusion → Full 14-Round AES-256</text>"
    )

    # 5 stepped difficulty cards across bottom panel
    ladder = [
        ("Tier 1 · R=1", "r01_k128_sat", "128 free · 2.2k v", "SAT", "#ecfdf5", "#059669", "Trivial 1-round", "S-box inversion"),
        ("Tier 2 · R=2..3", "r02_k16, k32 · r03_k16", "16–32 free · 5–7.8k v", "3 SAT", "#eff6ff", "#2563eb", "Easy → Medium", "Nonlinear key re-entry"),
        ("Tier 3 · R=4", "r04_k12 sat / unsat", "12 free · 10.7k v", "1S / 1U", "#fffbeb", "#d97706", "Full diffusion", "2¹² UNSAT proved"),
        ("Tier 4 · R=14", "r14_k10, k12 sat/uns", "10–12 free · 38.9k v", "2S / 1U", "#fef2f2", "#dc2626", "Full 14-round", "276 S-boxes · 29.8k XOR"),
        ("Tier 5 · Full", "r14_k256_dual_sat", "256 free · 69.9k v", "SAT", "#f5f3ff", "#7c3aed", "Dual P₁,P₂ miter", "500 S-boxes · 53.7k XOR"),
    ]
    cw = 158
    gap = 12
    cx0 = bx + 14
    cy0 = by + 28
    for i, (tier, inst, dims, pill, bg, bd, note1, note2) in enumerate(ladder):
        x_i = cx0 + i * (cw + gap)
        parts.append(f'<rect x="{x_i}" y="{cy0}" width="{cw}" height="82" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1.2"/>')
        parts.append(f'<text x="{x_i + 8}" y="{cy0 + 15}" font-size="9.5" font-weight="700" fill="{bd}">{tier}</text>')
        parts.append(f'<rect x="{x_i + cw - 50}" y="{cy0 + 5}" width="43" height="14" rx="3.5" fill="#ffffff" stroke="{bd}" stroke-width="0.9"/>')
        parts.append(f'<text x="{x_i + cw - 28.5:.1f}" y="{cy0 + 15}" text-anchor="middle" font-size="7.6" font-weight="700" fill="{bd}">{pill}</text>')
        parts.append(f'<text x="{x_i + 8}" y="{cy0 + 32}" font-family="{FONT_MONO}" font-size="8.0" font-weight="700" fill="#0f172a">{inst}</text>')
        parts.append(f'<text x="{x_i + 8}" y="{cy0 + 46}" font-size="8.2" fill="#334155">{dims}</text>')
        parts.append(f'<text x="{x_i + 8}" y="{cy0 + 62}" font-size="8.3" font-weight="600" fill="#1e293b">{note1}</text>')
        parts.append(f'<text x="{x_i + 8}" y="{cy0 + 74}" font-size="7.9" fill="#475569">{note2}</text>')
        if i < len(ladder) - 1:
            parts.append(
                f'<line x1="{x_i + cw}" y1="{cy0 + 41}" x2="{x_i + cw + gap - 2}" y2="{cy0 + 41}" '
                'stroke="#64748b" stroke-width="1.35" marker-end="url(#arr-slate)"/>'
            )

    # Bottom footer strip
    parts.append(
        f'<text x="{bx + 14}" y="{by + 128}" font-size="9.2" fill="#475569">'
        "10 instances (8 SAT / 2 UNSAT)  ·  2,192–69,908 vars  ·  7,488–276,176 CNF clauses  ·  "
        "173,288 native XORs  ·  XCNF / CNF / AIG / ANF  ·  MIT License</text>"
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
