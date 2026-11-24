#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `zed-adversarial-hub-php` benchmark collection.

Illustrates both adversarial AIG circuit families constructed in `src/main.rs`:
  1. Left: High-Fanout Bit-Vector Hub Disjunctions (`hub_20..80`, 5 UNSAT / 1 SAT)
     where a single shared 10-bit hub integer h in [low, 63] fans out to
     n in {20..80} satellite bit-blasted two's-complement adder/shift gadgets
     enforcing (-x_i - 2h + 40 + (i mod 7) >= 0) OR (y_i - h - 10 + (i mod 5) >= 0),
     pinning the exact low=31 (UNSAT) vs low=25 (SAT) threshold
  2. Right: Scaled Tseitin AIG Pigeonhole Bottleneck (`php_9_8` .. `php_50_49`,
     10 UNSAT + 2 SAT bijection controls `php_20_20`, `php_30_30`) showing the
     AIG gate miter structure and CDCL >600 s timeout cliff by PHP^16_15.

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
    W, H = 920, 496
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Adversarial high-fanout 10-bit bit-vector hub disjunctions and scaled AIG pigeonhole circuits">',
        "<defs>",
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
        # Explicit white card canvas
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Adversarial Bit-Vector Hub &amp; Scaled Pigeonhole Circuits (zed-adversarial-hub-php)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Two bit-level AIGER 1.9 stress families (18 instances): high-fanout 10-bit shared-hub arithmetic "
        "disjunctions + scaled Tseitin PHPᵐₙ circuits</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: BIT-VECTOR HUB DISJUNCTIONS =====================
    px1, py1, pw1, ph1 = 24, 76, 434, 352
    parts.append(
        f'<rect x="{px1}" y="{py1}" width="{pw1}" height="{ph1}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    # Blue header banner
    parts.append(f'<rect x="{px1}" y="{py1}" width="{pw1}" height="28" rx="10" fill="#2563eb"/>')
    parts.append(f'<rect x="{px1}" y="{py1 + 16}" width="{pw1}" height="12" fill="#2563eb"/>')
    parts.append(
        f'<text x="{px1 + pw1/2:.1f}" y="{py1 + 19}" text-anchor="middle" '
        'font-size="11.6" font-weight="700" fill="#ffffff">'
        "1. High-Fanout Bit-Vector Hub (hub_20..80 · 5 UNSAT / 1 SAT)</text>"
    )

    # Central Shared 10-bit Hub Register h
    hx, hy, hw, hh = px1 + 16, py1 + 102, 118, 84
    parts.append(
        f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="9" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.7"/>'
    )
    parts.append(f'<text x="{hx + hw/2:.1f}" y="{hy + 20}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#b45309">Shared Hub h</text>')
    parts.append(f'<text x="{hx + hw/2:.1f}" y="{hy + 36}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.5" font-weight="700" fill="#0f172a">10-bit signed</text>')
    parts.append(f'<text x="{hx + hw/2:.1f}" y="{hy + 52}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.5" font-weight="600" fill="#92400e">h ∈ [low, 63]</text>')
    parts.append(f'<text x="{hx + hw/2:.1f}" y="{hy + 71}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#d97706">Deg CV: 1.16→2.31</text>')

    # Satellite Arithmetic Disjunction Gadgets (right of Hub)
    sat_x, sat_w = px1 + 178, 240
    # Gadget 0 (expanded detail)
    g0y, g0h = py1 + 42, 112
    parts.append(f'<rect x="{sat_x}" y="{g0y}" width="{sat_w}" height="{g0h}" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="1.3"/>')
    parts.append(f'<text x="{sat_x + 10}" y="{g0y + 16}" font-size="9.8" font-weight="700" fill="#1d4ed8">Satellite Gadget i = 0 (critical witness)</text>')
    parts.append(f'<text x="{sat_x + 10}" y="{g0y + 30}" font-size="8.7" fill="#475569">Local 10-bit vars:  xᵢ ∈ [20, 63],  yᵢ ∈ [0, 40]</text>')
    # Two arithmetic branch pills inside Gadget 0
    parts.append(f'<rect x="{sat_x + 10}" y="{g0y + 38}" width="{sat_w - 20}" height="22" rx="4" fill="#eff6ff" stroke="#93c5fd" stroke-width="0.9"/>')
    parts.append(f'<text x="{sat_x + sat_w/2:.1f}" y="{g0y + 52.5}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.9" font-weight="600" fill="#1e3a8a">pᵢ = −xᵢ − 2h + 40 + (i mod 7) ≥ 0</text>')
    parts.append(f'<rect x="{sat_x + 10}" y="{g0y + 64}" width="{sat_w - 20}" height="22" rx="4" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="0.9"/>')
    parts.append(f'<text x="{sat_x + sat_w/2:.1f}" y="{g0y + 78.5}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.9" font-weight="600" fill="#5b21b6">rᵢ = yᵢ − h − 10 + (i mod 5) ≥ 0</text>')
    parts.append(f'<text x="{sat_x + sat_w/2:.1f}" y="{g0y + 102}" text-anchor="middle" font-size="9" font-weight="700" fill="#0f172a">Assert OR( ¬sign(pᵢ), ¬sign(rᵢ) ) = 1</text>')

    # Compact stacked satellite cards i = 1, ..., n-1
    mini_sats = [
        (py1 + 164, "Satellite Gadget i = 1  (mod 7, mod 5)"),
        (py1 + 196, "⋯  n ∈ {20, 24, 30, 60, 80} copies  ⋯"),
        (py1 + 228, "Satellite Gadget i = n−1  (10-bit adders)"),
    ]
    for sy_m, slbl in mini_sats:
        is_dots = "⋯" in slbl
        parts.append(
            f'<rect x="{sat_x}" y="{sy_m}" width="{sat_w}" height="24" rx="5" '
            f'fill="{"#f1f5f9" if is_dots else "#ffffff"}" stroke="#cbd5e1" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{sat_x + sat_w/2:.1f}" y="{sy_m + 15.5}" text-anchor="middle" '
            f'font-size="9" font-weight="{"600" if not is_dots else "700"}" fill="#334155">{slbl}</text>'
        )

    # High-fanout bus arrows from Hub h -> all satellite gadgets
    for ty_a in (g0y + 56, py1 + 176, py1 + 208, py1 + 240):
        parts.append(
            f'<path d="M {hx + hw} {hy + hh/2:.1f} C {hx + hw + 22} {hy + hh/2:.1f}, {sat_x - 22} {ty_a:.1f}, {sat_x - 2} {ty_a:.1f}" '
            'fill="none" stroke="#d97706" stroke-width="1.5" marker-end="url(#arr-amber)"/>'
        )
    parts.append(f'<text x="{hx + hw/2:.1f}" y="{hy + hh + 18}" text-anchor="middle" font-size="8.7" fill="#475569">Bit-blasted 2′s-comp.</text>')
    parts.append(f'<text x="{hx + hw/2:.1f}" y="{hy + hh + 30}" text-anchor="middle" font-size="8.7" fill="#475569">full-adder ripple chains</text>')

    # SAT vs UNSAT Exact Arithmetic Threshold Box (bottom of Left Panel)
    parts.append(f'<rect x="{px1 + 14}" y="{py1 + 264}" width="{pw1 - 28}" height="76" rx="7" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{px1 + 24}" y="{py1 + 281}" font-size="9.8" font-weight="700" fill="#0f172a">Exact Threshold Proof (at i ≡ 0 mod 5, e.g. i = 0):</text>')
    parts.append(f'<rect x="{px1 + 22}" y="{py1 + 288}" width="190" height="42" rx="5" fill="#fef2f2" stroke="#dc2626" stroke-width="0.95"/>')
    parts.append(f'<text x="{px1 + 117}" y="{py1 + 302}" text-anchor="middle" font-size="9" font-weight="700" fill="#b91c1c">low = 31 ⇒ UNSAT (5 inst.)</text>')
    parts.append(f'<text x="{px1 + 117}" y="{py1 + 315}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.1" fill="#7f1d1d">p₀ ≤ −42 &lt; 0, r₀ ≤ −1 &lt; 0</text>')
    parts.append(f'<text x="{px1 + 117}" y="{py1 + 326}" text-anchor="middle" font-size="8" fill="#475569">both branches fail for h ≥ 31</text>')

    parts.append(f'<rect x="{px1 + 222}" y="{py1 + 288}" width="190" height="42" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="0.95"/>')
    parts.append(f'<text x="{px1 + 317}" y="{py1 + 302}" text-anchor="middle" font-size="9" font-weight="700" fill="#047857">low = 25 ⇒ SAT (hub_60_sat)</text>')
    parts.append(f'<text x="{px1 + 317}" y="{py1 + 315}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.1" fill="#065f46">h = 25, yᵢ = 40 ⇒ rᵢ ≥ 5</text>')
    parts.append(f'<text x="{px1 + 317}" y="{py1 + 326}" text-anchor="middle" font-size="8" fill="#475569">satisfies all n = 60 gadgets</text>')

    # ===================== RIGHT PANEL: SCALED AIG PIGEONHOLE BOTTLENECK =====================
    px2, py2, pw2, ph2 = 474, 76, 422, 352
    parts.append(
        f'<rect x="{px2}" y="{py2}" width="{pw2}" height="{ph2}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    # Purple header banner
    parts.append(f'<rect x="{px2}" y="{py2}" width="{pw2}" height="28" rx="10" fill="#7c3aed"/>')
    parts.append(f'<rect x="{px2}" y="{py2 + 16}" width="{pw2}" height="12" fill="#7c3aed"/>')
    parts.append(
        f'<text x="{px2 + pw2/2:.1f}" y="{py2 + 19}" text-anchor="middle" '
        'font-size="11.6" font-weight="700" fill="#ffffff">'
        "2. Scaled Tseitin AIG PHPᵐₙ (10 UNSAT + 2 SAT Controls)</text>"
    )

    # Top Schematic: AIG Miter Pipeline for PHP^m_n
    my_p = py2 + 40
    parts.append(f'<rect x="{px2 + 14}" y="{my_p}" width="{pw2 - 28}" height="106" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{px2 + 24}" y="{my_p + 17}" font-size="10.2" font-weight="700" fill="#0f172a">Bit-Level AIG Miter Construction (build_zed_php)</text>')

    # 3 stages left-to-right inside AIG Miter card
    st_y = my_p + 28
    # Stage 1: m x n inputs
    parts.append(f'<rect x="{px2 + 24}" y="{st_y}" width="88" height="62" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.1"/>')
    parts.append(f'<text x="{px2 + 68}" y="{st_y + 18}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#1d4ed8">m × n Inputs</text>')
    parts.append(f'<text x="{px2 + 68}" y="{st_y + 34}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" fill="#334155">x[p·n + h]</text>')
    parts.append(f'<text x="{px2 + 68}" y="{st_y + 50}" text-anchor="middle" font-size="8.2" fill="#475569">up to 50×49</text>')

    # Stage 2: ALO OR-chains + AMO pairwise OR-gates
    parts.append(f'<rect x="{px2 + 132}" y="{st_y}" width="152" height="28" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
    parts.append(f'<text x="{px2 + 208}" y="{st_y + 12}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#047857">m ALO OR-chains</text>')
    parts.append(f'<text x="{px2 + 208}" y="{st_y + 23}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.1" fill="#334155">∨ₕ x[p, h] = 1</text>')

    parts.append(f'<rect x="{px2 + 132}" y="{st_y + 34}" width="152" height="28" rx="5" fill="#fef2f2" stroke="#dc2626" stroke-width="1"/>')
    parts.append(f'<text x="{px2 + 208}" y="{st_y + 46}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#b91c1c">n·C(m,2) AMO gates</text>')
    parts.append(f'<text x="{px2 + 208}" y="{st_y + 57}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.1" fill="#334155">¬x[p,h] ∨ ¬x[q,h]</text>')

    # Stage 3: Global AND miter PO_0
    parts.append(f'<rect x="{px2 + 304}" y="{st_y + 8}" width="92" height="46" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>')
    parts.append(f'<text x="{px2 + 350}" y="{st_y + 26}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#6d28d9">AND Miter</text>')
    parts.append(f'<text x="{px2 + 350}" y="{st_y + 41}" text-anchor="middle" font-size="8.4" fill="#475569">PO₀ = ALO∧AMO</text>')

    # Connecting arrows between AIG stages
    parts.append(f'<line x1="{px2 + 112}" y1="{st_y + 18}" x2="{px2 + 130}" y2="{st_y + 14}" stroke="#2563eb" stroke-width="1.3" marker-end="url(#arr-blue)"/>')
    parts.append(f'<line x1="{px2 + 112}" y1="{st_y + 44}" x2="{px2 + 130}" y2="{st_y + 48}" stroke="#2563eb" stroke-width="1.3" marker-end="url(#arr-blue)"/>')
    parts.append(f'<line x1="{px2 + 284}" y1="{st_y + 14}" x2="{px2 + 302}" y2="{st_y + 24}" stroke="#7c3aed" stroke-width="1.3" marker-end="url(#arr-purple)"/>')
    parts.append(f'<line x1="{px2 + 284}" y1="{st_y + 48}" x2="{px2 + 302}" y2="{st_y + 38}" stroke="#7c3aed" stroke-width="1.3" marker-end="url(#arr-purple)"/>')

    # Bottom Card inside Right Panel: PHP Scaling Table & CDCL Timeout Wall
    ty_p = py2 + 158
    parts.append(f'<rect x="{px2 + 14}" y="{ty_p}" width="{pw2 - 28}" height="182" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    parts.append(f'<text x="{px2 + 24}" y="{ty_p + 18}" font-size="10.4" font-weight="700" fill="#0f172a">PHPᵐₙ Scaling &amp; CDCL &gt;600 s Cliff (Haken 1985)</text>')

    th_y = ty_p + 34
    parts.append(f'<rect x="{px2 + 22}" y="{th_y - 10}" width="{pw2 - 44}" height="16" rx="4" fill="#e2e8f0"/>')
    for cx_h, lbl_h, anc in [
        (px2 + 28, "Instance", "start"),
        (px2 + 142, "AIG ANDs", "middle"),
        (px2 + 218, "CNF Cls", "middle"),
        (px2 + 296, "CDCL", "middle"),
        (px2 + 368, "Frob.", "middle"),
    ]:
        parts.append(f'<text x="{cx_h}" y="{th_y + 1}" text-anchor="{anc}" font-size="8.6" font-weight="700" fill="#334155">{lbl_h}</text>')

    php_rows = [
        ("php_9_8_unsat", "647", "1,350", "27–438 ms", "1.8 ms", False),
        ("php_16_15_unsat", "3,839", "7,888", ">600 s T/O", "4.5 ms", True),
        ("php_20_19_unsat", "7,599", "15,540", ">600 s T/O", "8.2 ms", True),
        ("php_31_30_unsat", "28,829", "58,528", ">600 s T/O", "—", True),
        ("php_50_49_unsat", "122,499", "247,350", ">600 s T/O", "119 ms", True),
        ("php_20_20 / 30_30", "8k / 27k", "16k / 55k", "SAT controls", "bijection", False),
    ]
    for i, (nm, ands, cls, cdcl, frob, is_hard) in enumerate(php_rows):
        ry_r = th_y + 17 + i * 21
        if is_hard and nm == "php_50_49_unsat":
            parts.append(f'<rect x="{px2 + 22}" y="{ry_r - 11}" width="{pw2 - 44}" height="19" rx="3" fill="#fef2f2"/>')
        elif nm.startswith("php_20_20"):
            parts.append(f'<rect x="{px2 + 22}" y="{ry_r - 11}" width="{pw2 - 44}" height="19" rx="3" fill="#ecfdf5"/>')
        parts.append(f'<text x="{px2 + 28}" y="{ry_r + 1.5}" font-family="{FONT_MONO}" font-size="8.4" font-weight="600" fill="#0f172a">{nm}</text>')
        parts.append(f'<text x="{px2 + 142}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.4" fill="#475569">{ands}</text>')
        parts.append(f'<text x="{px2 + 218}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.4" fill="#475569">{cls}</text>')
        cdcl_c = "#b91c1c" if is_hard else ("#047857" if "SAT" in cdcl else "#334155")
        parts.append(f'<text x="{px2 + 296}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.4" font-weight="700" fill="{cdcl_c}">{cdcl}</text>')
        parts.append(f'<text x="{px2 + 368}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.4" font-weight="700" fill="#047857">{frob}</text>')

    parts.append(
        f'<text x="{px2 + 24}" y="{ty_p + 173}" font-size="8.4" fill="#475569">'
        "php_9_8 &amp; php_13_12 LRAT proofs formally verified in HOL4 / cake_lpr.</text>"
    )

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 440
    pills = [
        (24, 210, "#eff6ff", "#2563eb", "#1d4ed8", "18 Inst.: 3 SAT / 15 UNSAT"),
        (244, 212, "#fffbeb", "#d97706", "#b45309", "hub: 10,146 XORs · Deg CV ≤ 2.31"),
        (466, 206, "#f5f3ff", "#7c3aed", "#6d28d9", "php: 95–99% Horn · ρ_c ≤ 3.08×"),
        (682, 214, "#ecfdf5", "#059669", "#047857", "4 Formats: AIG · CNF · XCNF · ANF"),
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
