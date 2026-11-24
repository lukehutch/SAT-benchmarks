#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `sha256-preimage` benchmark collection.

Illustrates the exact FIPS 180-4 SHA-256 Carry-Save-Adder (CSA) compression
round implemented in `src/sha256.rs` & `src/main.rs`:
  - 8 state registers (a..h -> a'..h'), F_2-linear Sigma0 / Sigma1 maps,
    nonlinear Ch (Mux) & Maj3 gates, and mod-2^32 CSA 3:2 adders (⊞)
  - Message schedule W_t and the sharp R=16 -> R=17 preimage cliff where
    W_16 = W_0 ⊞ sigma0(W_1) ⊞ W_9 ⊞ sigma1(W_14) re-injects the k free
    bits of W_0 into deep ARX mixing
  - Inverted target digest constraint (exact "abc" SAT vs bit-0-flipped UNSAT).

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


def draw_adder(parts: list[str], cx: float, cy: float, r: float = 11.0, fill: str = "#fffbeb", stroke: str = "#d97706") -> None:
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    parts.append(
        f'<text x="{cx:.1f}" y="{cy + 4.5:.1f}" text-anchor="middle" '
        f'font-size="13.5" font-weight="700" fill="{stroke}">⊞</text>'
    )


def build_svg() -> str:
    W, H = 920, 514
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="FIPS 180-4 SHA-256 compression round circuit and R=16 to R=17 preimage phase cliff">',
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
        '  <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/></marker>',
        "</defs>",
        # White card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "FIPS 180-4 SHA-256 Compression Round &amp; Preimage Cliff (sha256-preimage)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        'Exact bit-accurate Carry-Save-Adder (CSA) AIG on padded "abc" — k ∈ {16, 20, 32} free bits in W₀, '
        "R ∈ {16, 17, 64} rounds</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT/MAIN PANEL: SHA-256 ROUND DATAPATH =====================
    px, py, pw, ph = 24, 74, 578, 286
    parts.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px + 12}" y="{py + 19}" font-size="12" font-weight="700" fill="#0f172a">'
        "One SHA-256 Compression Round t  (32-bit Words · ⊞ = mod-2³² CSA 3:2 + CPA)</text>"
    )

    # 8 state registers across top (a..h) and bottom (a'..h')
    regs = ["a", "b", "c", "d", "e", "f", "g", "h"]
    reg_x0 = px + 36
    reg_dx = 64
    reg_w, reg_h = 44, 24
    top_y = py + 32
    bot_y = py + 244

    reg_cx = [reg_x0 + i * reg_dx + reg_w / 2 for i in range(8)]
    for i, rname in enumerate(regs):
        rx_i = reg_x0 + i * reg_dx
        # Top register
        fill_t = "#eff6ff" if rname in ("a", "e") else "#ffffff"
        stroke_t = "#2563eb" if rname in ("a", "e") else "#64748b"
        parts.append(
            f'<rect x="{rx_i}" y="{top_y}" width="{reg_w}" height="{reg_h}" rx="5" '
            f'fill="{fill_t}" stroke="{stroke_t}" stroke-width="1.25"/>'
        )
        parts.append(
            f'<text x="{reg_cx[i]:.1f}" y="{top_y + 16}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="11.5" font-weight="700" fill="#0f172a">{rname}</text>'
        )
        # Bottom register
        fill_b = "#ecfdf5" if rname in ("a", "e") else "#ffffff"
        stroke_b = "#059669" if rname in ("a", "e") else "#64748b"
        parts.append(
            f'<rect x="{rx_i}" y="{bot_y}" width="{reg_w}" height="{reg_h}" rx="5" '
            f'fill="{fill_b}" stroke="{stroke_b}" stroke-width="1.25"/>'
        )
        parts.append(
            f'<text x="{reg_cx[i]:.1f}" y="{bot_y + 16}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="11.5" font-weight="700" fill="#0f172a">{rname}′</text>'
        )

    # Diagonal shift wires: a->b', b->c', c->d', e->f', f->g', g->h'
    for src, dst in [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)]:
        x1, y1 = reg_cx[src], top_y + reg_h
        x2, y2 = reg_cx[dst], bot_y
        # Clean polyline shift near bottom so function boxes sit above cleanly
        mid_y1 = bot_y - 34
        mid_y2 = bot_y - 16
        parts.append(
            f'<path d="M {x1:.1f} {y1} L {x1:.1f} {mid_y1} L {x2:.1f} {mid_y2} L {x2:.1f} {y2 - 2}" '
            'fill="none" stroke="#94a3b8" stroke-width="1.35" marker-end="url(#arr-slate)"/>'
        )

    # --- Function Blocks in Middle Band (y = py+72 .. py+198) ---
    # 1) Maj(a,b,c) & Sigma0(a) -> T2 adder (left side)
    maj_x, maj_y, maj_w, maj_h = px + 68, py + 82, 108, 30
    parts.append(
        f'<rect x="{maj_x}" y="{maj_y}" width="{maj_w}" height="{maj_h}" rx="6" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{maj_x + maj_w/2:.1f}" y="{maj_y + 13}" text-anchor="middle" '
        'font-size="10.2" font-weight="700" fill="#6d28d9">Maj₃(a, b, c)</text>'
    )
    parts.append(
        f'<text x="{maj_x + maj_w/2:.1f}" y="{maj_y + 25}" text-anchor="middle" '
        'font-size="8.4" fill="#475569">nonlinear bitwise</text>'
    )

    s0_x, s0_y, s0_w, s0_h = px + 68, py + 124, 108, 32
    parts.append(
        f'<rect x="{s0_x}" y="{s0_y}" width="{s0_w}" height="{s0_h}" rx="6" '
        'fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{s0_x + s0_w/2:.1f}" y="{s0_y + 13}" text-anchor="middle" '
        'font-size="10.2" font-weight="700" fill="#1d4ed8">Σ₀(a)</text>'
    )
    parts.append(
        f'<text x="{s0_x + s0_w/2:.1f}" y="{s0_y + 25.5}" text-anchor="middle" '
        'font-size="8.3" fill="#475569">ROTR²⊕¹³⊕²² (𝔽₂)</text>'
    )

    # T2 Adder (a' = T1 ⊞ T2)
    t2_cx, t2_cy = px + 206, py + 140
    draw_adder(parts, t2_cx, t2_cy, 11)
    parts.append(f'<text x="{t2_cx + 19}" y="{t2_cy + 3.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b45309">T₂</text>')

    # Wires a,b,c -> Maj & Sigma0 -> T2
    parts.append(f'<path d="M {reg_cx[0]:.1f} {top_y + reg_h} L {reg_cx[0]:.1f} {s0_y + 16} L {s0_x - 2} {s0_y + 16}" fill="none" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr-blue)"/>')
    parts.append(f'<path d="M {reg_cx[1]:.1f} {top_y + reg_h} L {reg_cx[1]:.1f} {maj_y - 2}" fill="none" stroke="#7c3aed" stroke-width="1.1"/>')
    parts.append(f'<path d="M {maj_x + maj_w} {maj_y + 15} L {t2_cx} {maj_y + 15} L {t2_cx} {t2_cy - 13}" fill="none" stroke="#d97706" stroke-width="1.25" marker-end="url(#arr-amber)"/>')
    parts.append(f'<line x1="{s0_x + s0_w}" y1="{s0_y + 16}" x2="{t2_cx - 13}" y2="{t2_cy}" stroke="#d97706" stroke-width="1.25" marker-end="url(#arr-amber)"/>')

    # 2) Ch(e,f,g) & Sigma1(e) & K_t & W_t -> T1 CSA Adder (right side)
    ch_x, ch_y, ch_w, ch_h = px + 344, py + 82, 108, 30
    parts.append(
        f'<rect x="{ch_x}" y="{ch_y}" width="{ch_w}" height="{ch_h}" rx="6" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{ch_x + ch_w/2:.1f}" y="{ch_y + 13}" text-anchor="middle" '
        'font-size="10.2" font-weight="700" fill="#6d28d9">Ch(e, f, g)</text>'
    )
    parts.append(
        f'<text x="{ch_x + ch_w/2:.1f}" y="{ch_y + 25}" text-anchor="middle" '
        'font-size="8.4" fill="#475569">Mux(e, f, g)</text>'
    )

    s1_x, s1_y, s1_w, s1_h = px + 344, py + 124, 108, 32
    parts.append(
        f'<rect x="{s1_x}" y="{s1_y}" width="{s1_w}" height="{s1_h}" rx="6" '
        'fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{s1_x + s1_w/2:.1f}" y="{s1_y + 13}" text-anchor="middle" '
        'font-size="10.2" font-weight="700" fill="#1d4ed8">Σ₁(e)</text>'
    )
    parts.append(
        f'<text x="{s1_x + s1_w/2:.1f}" y="{s1_y + 25.5}" text-anchor="middle" '
        'font-size="8.3" fill="#475569">ROTR⁶⊕¹¹⊕²⁵ (𝔽₂)</text>'
    )

    # K_t and W_t input pills on far right of T1
    kw_x, kw_w = px + 474, 88
    parts.append(
        f'<rect x="{kw_x}" y="{py + 82}" width="{kw_w}" height="24" rx="5" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.1"/>'
    )
    parts.append(
        f'<text x="{kw_x + kw_w/2:.1f}" y="{py + 98}" text-anchor="middle" '
        'font-size="9.8" font-weight="700" fill="#b45309">K_t (const)</text>'.replace("K_t", "Kₜ")
    )
    parts.append(
        f'<rect x="{kw_x}" y="{py + 114}" width="{kw_w}" height="26" rx="5" '
        'fill="#fef2f2" stroke="#dc2626" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text x="{kw_x + kw_w/2:.1f}" y="{py + 131}" text-anchor="middle" '
        'font-size="9.8" font-weight="700" fill="#b91c1c">Wₜ (sched.)</text>'
    )

    # T1 Multi-operand CSA Adder Node
    t1_cx, t1_cy = px + 492, py + 178
    draw_adder(parts, t1_cx, t1_cy, 13, fill="#fffbeb", stroke="#d97706")
    parts.append(
        f'<text x="{t1_cx + 22}" y="{t1_cy - 10}" font-size="10" font-weight="700" fill="#b45309">T₁</text>'
    )
    parts.append(
        f'<text x="{t1_cx}" y="{t1_cy + 25}" text-anchor="middle" font-size="8.4" fill="#475569">5-op CSA</text>'
    )

    # Wires into T1: h (routed cleanly outside K_t/W_t right edge), Ch, Sigma1, K_t, W_t
    parts.append(f'<path d="M {reg_cx[7]:.1f} {top_y + reg_h} L {reg_cx[7]:.1f} {py + 68} L {px + pw - 9} {py + 68} L {px + pw - 9} {t1_cy} L {t1_cx + 15} {t1_cy}" fill="none" stroke="#475569" stroke-width="1.2" marker-end="url(#arr-slate)"/>')
    parts.append(f'<line x1="{ch_x + ch_w}" y1="{ch_y + 15}" x2="{t1_cx - 10}" y2="{t1_cy - 10}" stroke="#d97706" stroke-width="1.15" marker-end="url(#arr-amber)"/>')
    parts.append(f'<line x1="{s1_x + s1_w}" y1="{s1_y + 16}" x2="{t1_cx - 14}" y2="{t1_cy - 2}" stroke="#d97706" stroke-width="1.2" marker-end="url(#arr-amber)"/>')
    parts.append(f'<line x1="{kw_x + kw_w/2:.1f}" y1="{py + 140}" x2="{t1_cx}" y2="{t1_cy - 15}" stroke="#dc2626" stroke-width="1.35" marker-end="url(#arr-red)"/>')
    # e -> Sigma1
    parts.append(f'<path d="M {reg_cx[4]:.1f} {top_y + reg_h} L {reg_cx[4]:.1f} {s1_y + 16} L {s1_x - 2} {s1_y + 16}" fill="none" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr-blue)"/>')

    # Adder for e' = d ⊞ T1
    ep_cx, ep_cy = reg_cx[4], py + 194
    draw_adder(parts, ep_cx, ep_cy, 10.5, fill="#ecfdf5", stroke="#059669")
    # d -> e' adder
    parts.append(f'<path d="M {reg_cx[3]:.1f} {top_y + reg_h} L {reg_cx[3]:.1f} {ep_cy} L {ep_cx - 13} {ep_cy}" fill="none" stroke="#475569" stroke-width="1.3" marker-end="url(#arr-slate)"/>')
    # T1 -> e' adder
    parts.append(f'<path d="M {t1_cx - 14} {t1_cy + 4} L {ep_cx + 13} {ep_cy}" fill="none" stroke="#d97706" stroke-width="1.4" marker-end="url(#arr-amber)"/>')
    # e' adder -> e' register
    parts.append(f'<line x1="{ep_cx:.1f}" y1="{ep_cy + 11}" x2="{ep_cx:.1f}" y2="{bot_y - 2}" stroke="#059669" stroke-width="1.5" marker-end="url(#arr-slate)"/>')

    # Adder for a' = T1 ⊞ T2
    ap_cx, ap_cy = reg_cx[0], py + 194
    draw_adder(parts, ap_cx, ap_cy, 10.5, fill="#ecfdf5", stroke="#059669")
    # T2 -> a' adder
    parts.append(f'<path d="M {t2_cx} {t2_cy + 11} L {t2_cx} {ap_cy - 18} L {ap_cx + 12} {ap_cy - 6}" fill="none" stroke="#d97706" stroke-width="1.35" marker-end="url(#arr-amber)"/>')
    # T1 bus across to a' adder
    parts.append(f'<path d="M {t1_cx - 13} {t1_cy + 9} L {px + 256} {py + 214} L {ap_cx + 12} {ap_cy + 5}" fill="none" stroke="#d97706" stroke-width="1.35" stroke-dasharray="4,2.5" marker-end="url(#arr-amber)"/>')
    # a' adder -> a' register
    parts.append(f'<line x1="{ap_cx:.1f}" y1="{ap_cy + 11}" x2="{ap_cx:.1f}" y2="{bot_y - 2}" stroke="#059669" stroke-width="1.5" marker-end="url(#arr-slate)"/>')

    # Compact round equations inside datapath footer
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + ph - 5}" text-anchor="middle" font-size="9.1" fill="#475569">'
        "T₁ = h ⊞ Σ₁(e) ⊞ Ch(e,f,g) ⊞ Kₜ ⊞ Wₜ   ·   T₂ = Σ₀(a) ⊞ Maj(a,b,c)   ·   a′ = T₁ ⊞ T₂,  e′ = d ⊞ T₁</text>"
    )

    # ===================== RIGHT PANEL: W_t FEEDBACK & TARGET DIGEST =====================
    rx, rw = 616, 280
    # Card 1: Message Schedule & W_0 Free Bits
    parts.append(
        f'<rect x="{rx}" y="74" width="{rw}" height="132" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="94" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Message Schedule Wₜ &amp; Free W₀ Bits</text>"
    )
    # Visual 32-bit W_0 register bar
    w0x, w0y, w0w = rx + 14, 104, rw - 28
    parts.append(f'<rect x="{w0x}" y="{w0y}" width="{w0w * 0.56:.1f}" height="20" rx="4" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>')
    parts.append(
        f'<text x="{w0x + w0w * 0.28:.1f}" y="{w0y + 13.5}" text-anchor="middle" '
        'font-size="9.4" font-weight="700" fill="#b91c1c">k free bits (k ∈ {16,20,32})</text>'
    )
    parts.append(f'<rect x="{w0x + w0w * 0.56 + 4:.1f}" y="{w0y}" width="{w0w * 0.44 - 4:.1f}" height="20" rx="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>')
    parts.append(
        f'<text x="{w0x + w0w * 0.78 + 2:.1f}" y="{w0y + 13.5}" text-anchor="middle" '
        'font-size="9.2" font-weight="600" fill="#334155">32−k fixed ("abc")</text>'
    )
    parts.append(
        f'<text x="{rx + 14}" y="142" font-size="9.5" font-weight="600" fill="#1e293b">'
        "Recurrence (t ≥ 16):</text>"
    )
    parts.append(
        f'<rect x="{rx + 14}" y="148" width="{rw - 28}" height="24" rx="5" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{rx + rw/2:.1f}" y="164" text-anchor="middle" font-family="{FONT_MONO}" '
        'font-size="9.1" font-weight="600" fill="#0f172a">Wₜ = Wₜ₋₁₆ ⊞ σ₀(Wₜ₋₁₅) ⊞ Wₜ₋₇ ⊞ σ₁(Wₜ₋₂)</text>'
    )
    parts.append(
        f'<text x="{rx + 14}" y="187" font-size="9.2" fill="#dc2626" font-weight="700">'
        "At t = 16 (R = 17): W₁₆ re-injects W₀!</text>"
    )
    parts.append(
        f'<text x="{rx + 14}" y="199" font-size="8.9" fill="#475569">'
        "Breaks backward inversion → 2ᵏ preimage cliff.</text>"
    )

    # Card 2: Inverted Target Digest & Suite Table
    parts.append(
        f'<rect x="{rx}" y="216" width="{rw}" height="144" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="235" font-size="11.6" font-weight="700" fill="#0f172a">'
        "Inverted Digest: H₀ ⊞ state_R = Target</text>".replace("state_R", "stateᵣ")
    )
    th_y = 252
    parts.append(f'<rect x="{rx + 10}" y="{th_y - 10}" width="{rw - 20}" height="16" rx="4" fill="#e2e8f0"/>')
    for cx_h, t_h, anc in [(rx + 14, "Instance", "start"), (rx + 126, "ANDs", "middle"), (rx + 184, "CDCL", "middle"), (rx + 244, "Ans", "middle")]:
        parts.append(f'<text x="{cx_h}" y="{th_y + 1}" text-anchor="{anc}" font-size="8.8" font-weight="700" fill="#334155">{t_h}</text>')

    sha_rows = [
        ("16r_k32", "30.1k", "10–17 ms", "SAT", "#ecfdf5", "#059669"),
        ("17r_k16", "31.7k", "4.2–7.7 s", "SAT", "#ecfdf5", "#059669"),
        ("64r_k16_sat", "182k", "275–2267 s", "SAT", "#ecfdf5", "#059669"),
        ("64r_k16_uns", "182k", "2396–2594 s", "UNSAT", "#fef2f2", "#dc2626"),
        ("64r_k20_sat", "183k", "2607 s–T/O", "SAT", "#ecfdf5", "#059669"),
    ]
    for i, (nm, ands, cdcl, ans, pbg, pfg) in enumerate(sha_rows):
        ry_r = th_y + 17 + i * 20
        if i % 2 == 1:
            parts.append(f'<rect x="{rx + 10}" y="{ry_r - 11}" width="{rw - 20}" height="18" rx="3" fill="#ffffff"/>')
        parts.append(f'<text x="{rx + 14}" y="{ry_r + 1.5}" font-family="{FONT_MONO}" font-size="8.9" font-weight="600" fill="#0f172a">{nm}</text>')
        parts.append(f'<text x="{rx + 126}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.8" fill="#475569">{ands}</text>')
        parts.append(f'<text x="{rx + 184}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.7" fill="#334155">{cdcl}</text>')
        parts.append(f'<rect x="{rx + 222}" y="{ry_r - 9}" width="44" height="14" rx="3.5" fill="{pbg}" stroke="{pfg}" stroke-width="0.85"/>')
        parts.append(f'<text x="{rx + 244}" y="{ry_r + 1}" text-anchor="middle" font-size="8.1" font-weight="700" fill="{pfg}">{ans}</text>')

    # ===================== BOTTOM PANEL: R = 16 -> 17 PHASE CLIFF TIMELINE =====================
    bx, by, bw, bh = 24, 372, 872, 126
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{bx + 14}" y="{by + 20}" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Sharp Round-Depth Preimage Phase Cliff:  R = 16  →  R = 17  →  Full 64 Rounds</text>"
    )

    # Timeline bar segments
    tx0 = bx + 18
    ty_bar = by + 32
    seg1_w = 244  # R = 0..15 (green)
    seg2_w = 436  # R = 16..63 (red/amber)
    seg3_w = 148  # Final IV + Digest check (purple)

    # Segment 1: R = 0..15
    parts.append(f'<rect x="{tx0}" y="{ty_bar}" width="{seg1_w}" height="34" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>')
    parts.append(f'<text x="{tx0 + seg1_w/2:.1f}" y="{ty_bar + 14}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#047857">Rounds 0 .. 15  (R ≤ 16)</text>')
    parts.append(f'<text x="{tx0 + seg1_w/2:.1f}" y="{ty_bar + 27}" text-anchor="middle" font-size="9" fill="#334155">W₀ enters once → backward prop O(R), k=32 in 17 ms</text>')

    # Cliff vertical divider at R = 16 -> 17
    cx_cliff = tx0 + seg1_w + 10
    parts.append(f'<line x1="{cx_cliff}" y1="{ty_bar - 4}" x2="{cx_cliff}" y2="{ty_bar + 42}" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="4,2"/>')
    parts.append(f'<rect x="{cx_cliff - 46}" y="{ty_bar + 44}" width="92" height="17" rx="4" fill="#dc2626"/>')
    parts.append(f'<text x="{cx_cliff}" y="{ty_bar + 55.5}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#ffffff">W₁₆ Cliff (R=17)</text>')

    # Segment 2: R = 16..63
    tx2 = cx_cliff + 10
    parts.append(f'<rect x="{tx2}" y="{ty_bar}" width="{seg2_w}" height="34" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>')
    parts.append(f'<text x="{tx2 + seg2_w/2:.1f}" y="{ty_bar + 14}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#b91c1c">Rounds 16 .. 63  (W₁₆ Re-Injection &amp; Deep ARX Mixing)</text>')
    parts.append(f'<text x="{tx2 + seg2_w/2:.1f}" y="{ty_bar + 27}" text-anchor="middle" font-size="9" fill="#334155">Coupled Σ₀/Σ₁/σ₀/σ₁ (𝔽₂-linear) + Ch/Maj/⊞ carries → 2ᵏ CDCL barrier (275–2,607 s)</text>')

    # Arrow -> Segment 3: Target Digest
    tx3 = tx2 + seg2_w + 14
    parts.append(f'<line x1="{tx2 + seg2_w}" y1="{ty_bar + 17}" x2="{tx3 - 2}" y2="{ty_bar + 17}" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
    parts.append(f'<rect x="{tx3}" y="{ty_bar}" width="{seg3_w}" height="34" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>')
    parts.append(f'<text x="{tx3 + seg3_w/2:.1f}" y="{ty_bar + 14}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#6d28d9">H₀ ⊞ state₆₄ = D★</text>')
    parts.append(f'<text x="{tx3 + seg3_w/2:.1f}" y="{ty_bar + 27}" text-anchor="middle" font-size="8.6" fill="#475569">exact SAT / bit-0 flip UNSAT</text>')

    # Footer metadata strip inside bottom panel
    parts.append(
        f'<text x="{bx + 18}" y="{by + 114}" font-size="9.4" fill="#475569">'
        "5 instances (4 SAT / 1 UNSAT)  ·  7,438–43,624 CNF vars  ·  47,125–283,828 clauses  ·  "
        "77,329 native XORs  ·  ρ_c = 1.16×–1.23× (Over)  ·  AIG / CNF / XCNF / ANF</text>"
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
