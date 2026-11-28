#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`cec-arithmetic-miters` (EDA Arithmetic Combinational Equivalence Checking Miters).

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
    W, H = 920, 485
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Combinational Equivalence Checking Arithmetic Miter Architecture">',
        "  <defs>",
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>',
        "    </marker>",
        '    <marker id="arr-purp" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>',
        "    </marker>",
        '    <marker id="arr-amb" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>',
        "    </marker>",
        '    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'EDA Arithmetic Combinational Equivalence Miters (cec-arithmetic-miters)</text>',
        f'    <text x="28" y="53" font-size="11.8" fill="#475569">'
        f'Hardware verification miters asserting ⋁{sub("k")} (A{sub("k")}(x, y) ⊕ B{sub("k")}(x, y)) = 1 · '
        f'Ripple-Carry vs Kogge–Stone &amp; Array vs Wallace vs Karatsuba</text>',
        '    <rect x="758" y="18" width="136" height="24" rx="12" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>',
        '    <text x="826" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#b91c1c">5 UNSAT · A ≡ B</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: FULL MITER ARCHITECTURE =================
    lx, ly, lw, lh = 24, 78, 586, 385
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Combinational Equivalence Checking (CEC) Miter Topology</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Shared inputs (x, y) drive two structurally divergent circuits; UNSAT proves bit-for-bit functional equivalence</text>'
    )

    # Shared Primary Inputs Box (left)
    ix, iy, iw, ih = lx + 16, ly + 136, 72, 114
    p.append(f'    <rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="8" fill="#ffffff" stroke="#334155" stroke-width="1.6"/>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 24}" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">Shared</text>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 39}" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">Inputs</text>')
    p.append(f'    <rect x="{ix + 10}" y="{iy + 50}" width="52" height="22" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="1"/>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 64.5}" text-anchor="middle" font-family="{mono}" font-size="10" font-weight="700" fill="#1d4ed8">x[0..n)</text>')
    p.append(f'    <rect x="{ix + 10}" y="{iy + 79}" width="52" height="22" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="1"/>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 93.5}" text-anchor="middle" font-family="{mono}" font-size="10" font-weight="700" fill="#1d4ed8">y[0..n)</text>')

    # Branching wires from Shared Inputs to Circuit A (top) and Circuit B (bottom)
    cx_box = lx + 124
    cw_box = 248
    ca_y, ca_h = ly + 52, 126
    cb_y, cb_h = ly + 194, 134

    p.append(f'    <path d="M {ix + iw} {iy + 34} L {ix + iw + 16} {iy + 34} L {ix + iw + 16} {ca_y + ca_h/2:.1f} L {cx_box - 2} {ca_y + ca_h/2:.1f}" fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    p.append(f'    <path d="M {ix + iw} {iy + 80} L {ix + iw + 16} {iy + 80} L {ix + iw + 16} {cb_y + cb_h/2:.1f} L {cx_box - 2} {cb_y + cb_h/2:.1f}" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arr-purp)"/>')

    # --- CIRCUIT A: Ripple-Carry Adder (or Array Mult) ---
    p.append(f'    <rect x="{cx_box}" y="{ca_y}" width="{cw_box}" height="{ca_h}" rx="9" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>')
    p.append(f'    <text x="{cx_box + 12}" y="{ca_y + 19}" font-size="11.5" font-weight="700" fill="#1d4ed8">Circuit A: Ripple-Carry (or Array)</text>')
    p.append(f'    <text x="{cx_box + 12}" y="{ca_y + 33}" font-size="9.4" fill="#475569">O(n) serial carry chain — slow depth, linear gates</text>')

    # Mini 4-bit Ripple-Carry chain inside Circuit A
    fa_y = ca_y + 68
    for i in range(4):
        fx = cx_box + 22 + i * 56
        p.append(f'    <rect x="{fx}" y="{fa_y - 16}" width="38" height="32" rx="5" fill="#ffffff" stroke="#2563eb" stroke-width="1.3"/>')
        p.append(f'    <text x="{fx + 19}" y="{fa_y + 3.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">FA{chr(0x2080 + i)}</text>')
        # Input tick from top
        p.append(f'    <text x="{fx + 19}" y="{fa_y - 21}" text-anchor="middle" font-family="{mono}" font-size="8.2" fill="#475569">x{i},y{i}</text>')
        # Output sum tick below
        p.append(f'    <text x="{fx + 19}" y="{fa_y + 28}" text-anchor="middle" font-family="{mono}" font-size="8.5" font-weight="700" fill="#1d4ed8">A{i}</text>')
        # Serial carry arrow to next FA
        if i < 3:
            p.append(f'    <line x1="{fx + 38}" y1="{fa_y}" x2="{fx + 54}" y2="{fa_y}" stroke="#d97706" stroke-width="1.8" marker-end="url(#arr-amb)"/>')
    p.append(f'    <text x="{cx_box + 124}" y="{ca_y + 115}" text-anchor="middle" font-size="9" font-weight="600" fill="#b45309">c₀ → c₁ → c₂ → … → c{sub("n")} (serial carry)</text>')

    # --- CIRCUIT B: Kogge-Stone Parallel Prefix (or Wallace / Karatsuba) ---
    p.append(f'    <rect x="{cx_box}" y="{cb_y}" width="{cw_box}" height="{cb_h}" rx="9" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/>')
    p.append(f'    <text x="{cx_box + 12}" y="{cb_y + 19}" font-size="11.5" font-weight="700" fill="#6d28d9">Circuit B: Kogge–Stone (or Wallace/Karat.)</text>')
    p.append(f'    <text x="{cx_box + 12}" y="{cb_y + 33}" font-size="9.4" fill="#475569">O(log n) parallel-prefix (G, P) tree — zero shared cuts</text>')

    # Mini 4-bit Kogge-Stone prefix network inside Circuit B (rows: init (g,p), step 1, step 2)
    ks_xs = [cx_box + 40 + i * 56 for i in range(4)]
    ks_ys = [cb_y + 52, cb_y + 82, cb_y + 112]
    # Stride 1 edges (row 0 -> row 1): i -> i and (i-1) -> i
    for i in range(4):
        p.append(f'    <line x1="{ks_xs[i]}" y1="{ks_ys[0]}" x2="{ks_xs[i]}" y2="{ks_ys[1]}" stroke="#a78bfa" stroke-width="1.3"/>')
        if i >= 1:
            p.append(f'    <line x1="{ks_xs[i - 1]}" y1="{ks_ys[0]}" x2="{ks_xs[i]}" y2="{ks_ys[1]}" stroke="#7c3aed" stroke-width="1.5"/>')
    # Stride 2 edges (row 1 -> row 2): i -> i and (i-2) -> i
    for i in range(4):
        p.append(f'    <line x1="{ks_xs[i]}" y1="{ks_ys[1]}" x2="{ks_xs[i]}" y2="{ks_ys[2]}" stroke="#a78bfa" stroke-width="1.3"/>')
        if i >= 2:
            p.append(f'    <line x1="{ks_xs[i - 2]}" y1="{ks_ys[1]}" x2="{ks_xs[i]}" y2="{ks_ys[2]}" stroke="#7c3aed" stroke-width="1.5"/>')
    # Draw KS nodes (row 0: p0..p3, row 1: pass p0 + GP1..3, row 2: pass B0,B1 + GP2,3)
    for r_idx, yy in enumerate(ks_ys):
        for i, xx in enumerate(ks_xs):
            is_op = (r_idx == 1 and i >= 1) or (r_idx == 2 and i >= 2)
            fc = "#7c3aed" if is_op else "#ffffff"
            tc = "#ffffff" if is_op else "#6d28d9"
            if r_idx == 0:
                lbl = f"p{i}"
            elif r_idx == 1:
                lbl = "p0"
            else:
                lbl = f"B{i}"
            p.append(f'    <circle cx="{xx}" cy="{yy}" r="9.5" fill="{fc}" stroke="#6d28d9" stroke-width="1.3"/>')
            if is_op:
                p.append(f'    <text x="{xx}" y="{yy + 3.2}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{tc}">GP</text>')
            else:
                p.append(f'    <text x="{xx}" y="{yy + 3.2}" text-anchor="middle" font-family="{mono}" font-size="8.2" font-weight="700" fill="{tc}">{lbl}</text>')
    p.append(f'    <text x="{cx_box + cw_box - 10}" y="{ks_ys[1] + 3}" text-anchor="end" font-size="8.2" font-weight="600" fill="#6d28d9">±1</text>')
    p.append(f'    <text x="{cx_box + cw_box - 10}" y="{ks_ys[2] + 3}" text-anchor="end" font-size="8.2" font-weight="600" fill="#6d28d9">±2</text>')

    # --- BITWISE XOR COMPARATORS + BIG OR MITER ---
    xor_x = lx + 422
    xor_ys = [ly + 108, ly + 152, ly + 196, ly + 266]
    xor_lbls = ["k = 0", "k = 1", "k = 2", "k = w"]

    # Wires from Circuit A & Circuit B into XOR gates
    for idx_x, xy in enumerate(xor_ys):
        ya_out = ca_y + 30 + idx_x * 24
        yb_out = cb_y + 24 + idx_x * 28
        p.append(f'    <path d="M {cx_box + cw_box} {ya_out} C {xor_x - 24} {ya_out}, {xor_x - 28} {xy - 5}, {xor_x - 15} {xy - 5}" fill="none" stroke="#2563eb" stroke-width="1.4"/>')
        p.append(f'    <path d="M {cx_box + cw_box} {yb_out} C {xor_x - 24} {yb_out}, {xor_x - 28} {xy + 5}, {xor_x - 15} {xy + 5}" fill="none" stroke="#7c3aed" stroke-width="1.4"/>')
        # XOR circle node
        p.append(f'    <circle cx="{xor_x}" cy="{xy}" r="14" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>')
        p.append(f'    <text x="{xor_x}" y="{xy + 5}" text-anchor="middle" font-size="14" font-weight="700" fill="#b45309">⊕</text>')
        p.append(f'    <text x="{xor_x}" y="{xy + 25}" text-anchor="middle" font-family="{mono}" font-size="8.5" fill="#475569">{xor_lbls[idx_x]}</text>')
    # Vertical ellipsis between k=2 and k=w
    p.append(f'    <text x="{xor_x}" y="{ly + 238}" text-anchor="middle" font-size="14" font-weight="700" fill="#64748b">⋮</text>')

    # Big OR gate combining all XOR diffs
    or_x, or_y = lx + 504, ly + 188
    for xy in xor_ys:
        p.append(f'    <path d="M {xor_x + 14} {xy} C {xor_x + 42} {xy}, {or_x - 42} {or_y}, {or_x - 26} {or_y}" fill="none" stroke="#d97706" stroke-width="1.6"/>')
    # Drawn OR gate symbol (clean stylized badge)
    p.append(f'    <path d="M {or_x - 28} {or_y - 26} Q {or_x - 16} {or_y} {or_x - 28} {or_y + 26} L {or_x - 2} {or_y + 26} Q {or_x + 22} {or_y + 18} {or_x + 30} {or_y} Q {or_x + 22} {or_y - 18} {or_x - 2} {or_y - 26} Z" fill="#fef2f2" stroke="#dc2626" stroke-width="1.8"/>')
    p.append(f'    <text x="{or_x - 2}" y="{or_y + 4.5}" text-anchor="middle" font-size="12" font-weight="700" fill="#b91c1c">⋁ OR</text>')

    # Output assertion badge below OR gate
    p.append(f'    <line x1="{or_x + 30}" y1="{or_y}" x2="{or_x + 56}" y2="{or_y}" stroke="#dc2626" stroke-width="2" marker-end="url(#arr-red)"/>')
    p.append(f'    <text x="{or_x + 44}" y="{or_y - 8}" text-anchor="middle" font-family="{mono}" font-size="10.5" font-weight="700" fill="#b91c1c">= 1</text>')

    # Bottom Verdict Banner inside Left Panel
    vb_y = ly + 340
    p.append(f'    <rect x="{lx + 16}" y="{vb_y}" width="{lw - 32}" height="32" rx="7" fill="#ffffff" stroke="#dc2626" stroke-width="1.2"/>')
    p.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{vb_y + 20}" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">'
        f'Miter Formula M(x, y) = ⋁{sub("k")} (A{sub("k")} ⊕ B{sub("k")})  ⇒  '
        '<tspan fill="#dc2626">UNSAT</tspan> ⇔ ∀(x, y): A(x, y) ≡ B(x, y)  (0 counterexamples)'
        '</text>'
    )

    # ================= RIGHT PANEL: ALL 5 BENCHMARKS & HARDNESS =================
    rx, ry, rw = 624, 78, 272

    # Card 1: All 5 Miter Instances
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="244" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 22}" font-size="12" font-weight="700" fill="#0f172a">All 5 CEC Miters (Native AIGER 1.9)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 36}" font-size="9.5" fill="#64748b">0 SAT / 5 UNSAT · 831 total native XORs</text>')

    insts = [
        ("adder_32b_rc_vs_ks", "32b RC vs Kogge–Stone", "871 AND · 2,059 cls", 0.33, "#2563eb"),
        ("mult_6x6_arr_vs_wal", "6×6 Array vs Wallace", "591 AND · 918 cls", 0.22, "#059669"),
        ("mult_8x8_arr_vs_wal", "8×8 Array vs Wallace", "1,148 AND · 1,769 cls", 0.43, "#d97706"),
        ("array_vs_wallace_10x10", "10×10 Array vs Wallace", "1,868 AND · 2,850 cls", 0.70, "#dc2626"),
        ("wallace_vs_karat_12x12", "12×12 Wallace vs Karat.", "2,673 AND · 4,247 cls", 1.00, "#7c3aed"),
    ]
    for i, (nm, desc, stat, frac, col) in enumerate(insts):
        yy = ry + 56 + i * 37
        p.append(f'    <text x="{rx + 14}" y="{yy}" font-family="{mono}" font-size="9.2" font-weight="700" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{rx + 14}" y="{yy + 12}" font-size="9.1" fill="#475569">{desc}</text>')
        p.append(f'    <rect x="{rx + 14}" y="{yy + 16}" width="{rw - 28}" height="7.5" rx="2.5" fill="#f1f5f9"/>')
        p.append(f'    <rect x="{rx + 14}" y="{yy + 16}" width="{(rw - 28) * frac:.1f}" height="7.5" rx="2.5" fill="{col}" fill-opacity="0.85"/>')
        p.append(f'    <text x="{rx + rw - 14}" y="{yy + 12}" text-anchor="end" font-size="8.6" font-weight="600" fill="{col}">{stat}</text>')

    # Card 2: Why Pure CDCL Explodes
    cy2 = ry + 256
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="129" rx="10" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 21}" font-size="12" font-weight="700" fill="#b91c1c">Why Multiplier Miters Are Hard</text>')
    hard_lines = [
        "• Divergent topologies share almost NO",
        "  internal functionally equivalent wires",
        "• 8×8 Arr vs Wal (1,769 cls): Kissat 3.6 s,",
        "  CaDiCaL 5.8 s, CMS 8.1 s — explodes at 10×10",
        "• Algebraic / SCA / Gröbner checks close",
        f'  8×8 in ~1.7 ms; ρ{sub("crit")} = 1.36×–1.64×',
    ]
    for i, ln in enumerate(hard_lines):
        p.append(f'    <text x="{rx + 14}" y="{cy2 + 40 + i * 14.5:.1f}" font-size="9.5" fill="#334155">{ln}</text>')

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
