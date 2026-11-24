#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`mod-circuit-sat` (Exact Synthesis of Optimal MOD_n^{3,r} Boolean Circuits).

Mathematically verifies the rendered optimal 3-gate MOD_3^{3,0} and 4-gate
MOD_3^{3,1} B_2 circuits against all 2^3 = 8 truth-table rows at generation
time. Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
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


def sup(text: str) -> str:
    return f'<tspan baseline-shift="super" font-size="72%">{esc(text)}</tspan>'


def verify_optimal_circuits() -> None:
    """Assert both depicted B_2 circuits compute MOD_3^{3,0} and MOD_3^{3,1} exactly."""
    for x1 in (0, 1):
        for x2 in (0, 1):
            for x3 in (0, 1):
                wt = x1 + x2 + x3
                # Optimal s*=3 circuit for MOD_3^{3,0} (normal B2 + negated_output=1)
                g1 = x1 ^ x2
                g2 = x1 ^ x3
                g3 = g1 | g2
                out0 = 1 - g3
                assert out0 == (1 if wt % 3 == 0 else 0)

                # Optimal s*=4 circuit for MOD_3^{3,1} (normal B2, negated_output=0)
                h1 = x1 ^ x2
                h2 = x1 & x2
                h3 = x3 ^ h1
                h4 = (1 - h2) & h3  # LT(h2, h3) = ~h2 & h3
                assert h4 == (1 if wt % 3 == 1 else 0)


def build_svg() -> str:
    verify_optimal_circuits()
    W, H = 920, 495
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Exact Synthesis of Optimal MOD3 Boolean Circuits over B2">',
        "  <defs>",
        '    <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        '    <marker id="arr-grn" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        f'    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        f'Exact Synthesis of Optimal MOD{sub("n")}{sup("3,r")} Circuits (mod-circuit-sat)</text>',
        f'    <text x="28" y="53" font-size="11.8" fill="#475569">'
        f'Minimum 2-input B₂ gate DAGs computing [(x₁ + … + x{sub("n")}) mod 3 = r] · '
        f'Sharp s* − 1 (UNSAT) vs s* (SAT) thresholds</text>',
        '    <rect x="734" y="18" width="160" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="814" y="34" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">5 SAT · 4 UNSAT · 2 Open</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: TWO VERIFIED OPTIMAL B2 GATE DAGS =================
    lx, ly, lw, lh = 24, 78, 526, 396
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Verified Exact Minimum B₂ Circuits (Decoded from SAT Models)</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Normal 2-input basis B₂ = {AND, OR, XOR, GT (a∧¬b), LT (¬a∧b)} with g(0,0) = 0</text>'
    )

    # --- SUB-BOX A: Optimal s*=3 DAG for MOD_3^{3,0} ---
    ay, ah = ly + 50, 134
    p.append(f'    <rect x="{lx + 14}" y="{ay}" width="{lw - 28}" height="{ah}" rx="8" fill="#ffffff" stroke="#059669" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 26}" y="{ay + 19}" font-size="11.5" font-weight="700" fill="#047857">A. MOD₃{sup("3,0")}(x₁, x₂, x₃) — Optimal s* = 3 Gates (mod3_n3_r0_s3_sat)</text>')

    # Inputs x1, x2, x3
    in_x = lx + 48
    a_in_ys = [ay + 44, ay + 74, ay + 104]
    for i, yy in enumerate(a_in_ys):
        p.append(f'    <circle cx="{in_x}" cy="{yy}" r="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
        p.append(f'    <text x="{in_x}" y="{yy + 4}" text-anchor="middle" font-family="{mono}" font-size="10.2" font-weight="700" fill="#1d4ed8">x{chr(0x2081 + i)}</text>')

    # Gates g1 = x1 ^ x2, g2 = x1 ^ x3, g3 = g1 | g2, out = ~g3
    g1x, g1y = lx + 178, ay + 54
    g2x, g2y = lx + 178, ay + 100
    g3x, g3y = lx + 318, ay + 77
    ox_a, oy_a = lx + 446, ay + 77

    # Wires for DAG A
    p.append(f'    <path d="M {in_x + 12} {a_in_ys[0]} L {g1x - 42} {g1y - 7}" fill="none" stroke="#475569" stroke-width="1.6" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {a_in_ys[1]} L {g1x - 42} {g1y + 7}" fill="none" stroke="#475569" stroke-width="1.6" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {a_in_ys[0] + 4} C {in_x + 56} {a_in_ys[0] + 24}, {in_x + 68} {g2y - 10}, {g2x - 42} {g2y - 7}" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {a_in_ys[2]} L {g2x - 42} {g2y + 7}" fill="none" stroke="#475569" stroke-width="1.6" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {g1x + 40} {g1y} C {g1x + 68} {g1y}, {g3x - 66} {g3y - 8}, {g3x - 42} {g3y - 8}" fill="none" stroke="#7c3aed" stroke-width="1.7" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {g2x + 40} {g2y} C {g2x + 68} {g2y}, {g3x - 66} {g3y + 8}, {g3x - 42} {g3y + 8}" fill="none" stroke="#7c3aed" stroke-width="1.7" marker-end="url(#arr-slate)"/>')
    p.append(f'    <line x1="{g3x + 48}" y1="{g3y}" x2="{ox_a - 44}" y2="{oy_a}" stroke="#059669" stroke-width="2" marker-end="url(#arr-grn)"/>')

    # Gate boxes DAG A
    for gx, gy, glbl, gexpr, gbg, gst, gtc in [
        (g1x, g1y, "g₁: XOR", "x₁ ⊕ x₂", "#f5f3ff", "#7c3aed", "#6d28d9"),
        (g2x, g2y, "g₂: XOR", "x₁ ⊕ x₃", "#f5f3ff", "#7c3aed", "#6d28d9"),
        (g3x, g3y, "g₃: OR", "g₁ ∨ g₂", "#fffbeb", "#d97706", "#b45309"),
    ]:
        p.append(f'    <rect x="{gx - 40}" y="{gy - 17}" width="80" height="34" rx="7" fill="{gbg}" stroke="{gst}" stroke-width="1.4"/>')
        p.append(f'    <text x="{gx}" y="{gy - 2}" text-anchor="middle" font-size="10.2" font-weight="700" fill="{gtc}">{glbl}</text>')
        p.append(f'    <text x="{gx}" y="{gy + 11}" text-anchor="middle" font-family="{mono}" font-size="8.8" fill="#334155">{gexpr}</text>')
    # Negation bubble on g3 output (negated_output=1) — label shifted right cleanly!
    p.append(f'    <circle cx="{g3x + 44}" cy="{g3y}" r="4.2" fill="#ffffff" stroke="#dc2626" stroke-width="1.6"/>')
    p.append(f'    <text x="{g3x + 62}" y="{g3y - 10}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#dc2626">¬out</text>')
    # Output pill A
    p.append(f'    <rect x="{ox_a - 42}" y="{oy_a - 19}" width="84" height="38" rx="7" fill="#ecfdf5" stroke="#059669" stroke-width="1.4"/>')
    p.append(f'    <text x="{ox_a}" y="{oy_a - 2}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#047857">out = ¬g₃</text>')
    p.append(f'    <text x="{ox_a}" y="{oy_a + 12}" text-anchor="middle" font-size="8.8" fill="#334155">wt ∈ {"{0, 3}"}</text>')

    # --- SUB-BOX B: Optimal s*=4 DAG for MOD_3^{3,1} (s=3 UNSAT -> s=4 SAT) ---
    by, bh = ay + ah + 12, 146
    p.append(f'    <rect x="{lx + 14}" y="{by}" width="{lw - 28}" height="{bh}" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 26}" y="{by + 19}" font-size="11.5" font-weight="700" fill="#1d4ed8">B. MOD₃{sup("3,1")}(x₁, x₂, x₃) — s = 3 UNSAT, Optimal s* = 4 Gates (SAT)</text>')

    b_in_ys = [by + 48, by + 82, by + 116]
    for i, yy in enumerate(b_in_ys):
        p.append(f'    <circle cx="{in_x}" cy="{yy}" r="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
        p.append(f'    <text x="{in_x}" y="{yy + 4}" text-anchor="middle" font-family="{mono}" font-size="10.2" font-weight="700" fill="#1d4ed8">x{chr(0x2081 + i)}</text>')

    h1x, h1y = lx + 158, by + 56
    h2x, h2y = lx + 158, by + 104
    h3x, h3y = lx + 278, by + 68
    h4x, h4y = lx + 392, by + 92

    # Wires for DAG B
    p.append(f'    <path d="M {in_x + 12} {b_in_ys[0]} L {h1x - 38} {h1y - 6}" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {b_in_ys[1] - 2} L {h1x - 38} {h1y + 6}" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {b_in_ys[0] + 4} C {in_x + 46} {b_in_ys[0] + 24}, {in_x + 56} {h2y - 12}, {h2x - 38} {h2y - 6}" fill="none" stroke="#475569" stroke-width="1.4" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {b_in_ys[1] + 4} L {h2x - 38} {h2y + 6}" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
    # g1 -> g3 and x3 -> g3
    p.append(f'    <path d="M {h1x + 36} {h1y} L {h3x - 38} {h3y - 6}" fill="none" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {in_x + 12} {b_in_ys[2]} C {in_x + 92} {b_in_ys[2] + 18}, {h3x - 76} {b_in_ys[2] + 10}, {h3x - 38} {h3y + 8}" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
    # g3 -> g4 and g2 -> g4
    p.append(f'    <path d="M {h3x + 36} {h3y} L {h4x - 42} {h4y - 7}" fill="none" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-slate)"/>')
    p.append(f'    <path d="M {h2x + 36} {h2y} L {h4x - 42} {h4y + 7}" fill="none" stroke="#2563eb" stroke-width="1.6" marker-end="url(#arr-slate)"/>')

    # Gate boxes DAG B
    for gx, gy, gw, glbl, gexpr, gbg, gst, gtc in [
        (h1x, h1y, 72, "g₁: XOR", "x₁ ⊕ x₂", "#f5f3ff", "#7c3aed", "#6d28d9"),
        (h2x, h2y, 72, "g₂: AND", "x₁ ∧ x₂", "#eff6ff", "#2563eb", "#1d4ed8"),
        (h3x, h3y, 72, "g₃: XOR", "g₁ ⊕ x₃", "#f5f3ff", "#7c3aed", "#6d28d9"),
        (h4x, h4y, 80, "g₄: LT", "¬g₂ ∧ g₃", "#ecfdf5", "#059669", "#047857"),
    ]:
        p.append(f'    <rect x="{gx - gw/2:.1f}" y="{gy - 17}" width="{gw}" height="34" rx="7" fill="{gbg}" stroke="{gst}" stroke-width="1.4"/>')
        p.append(f'    <text x="{gx}" y="{gy - 2}" text-anchor="middle" font-size="10" font-weight="700" fill="{gtc}">{glbl}</text>')
        p.append(f'    <text x="{gx}" y="{gy + 11}" text-anchor="middle" font-family="{mono}" font-size="8.6" fill="#334155">{gexpr}</text>')

    p.append(f'    <line x1="{h4x + 40}" y1="{h4y}" x2="{lx + lw - 42}" y2="{h4y}" stroke="#059669" stroke-width="2" marker-end="url(#arr-grn)"/>')
    p.append(f'    <text x="{lx + lw - 34}" y="{h4y - 4}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#047857">out</text>')
    p.append(f'    <text x="{lx + lw - 34}" y="{h4y + 10}" text-anchor="middle" font-size="8.2" fill="#475569">wt=1</text>')

    # Mini Truth Table Strip at bottom of Left Panel
    tty = by + bh + 10
    p.append(f'    <rect x="{lx + 14}" y="{tty}" width="{lw - 28}" height="36" rx="6" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 26}" y="{tty + 15}" font-size="9.5" font-weight="700" fill="#0f172a">Symmetric Hamming-Weight Verification (n = 3, m = 3):</text>')
    p.append(f'    <text x="{lx + 26}" y="{tty + 29}" font-family="{mono}" font-size="9.1" fill="#334155">wt(x) ∈ {{0,1,2,3}}  →  MOD₃{sup("3,0")}: [1, 0, 0, 1] (s*=3)   ·   MOD₃{sup("3,1")}: [0, 1, 0, 0] (s*=4)</text>')

    # ================= RIGHT PANEL: THRESHOLD STAIRCASE & SAT ENCODING =================
    rx, ry, rw = 566, 78, 330

    # Card 1: Optimality Threshold Map across all 11 instances
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="244" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#0f172a">Exact Gate-Budget Thresholds (11 Instances)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 36}" font-size="9.5" fill="#64748b">Red = UNSAT lower bound (s*−1) · Green = Optimal SAT (s*)</text>')

    rows = [
        ("n=3, r=0", "s = 3", "SAT", "#059669", "#ecfdf5", "65 v · 435 c"),
        ("n=3, r=1", "s = 3 → 4", "U → S", "#2563eb", "#eff6ff", "65→107 v · 426→903 c"),
        ("n=4, r=2", "s = 5 → 6", "U → S", "#2563eb", "#eff6ff", "250→343 v · 4.1k→6.8k c"),
        ("n=4, r=0", "s = 6 → 7", "U → S", "#2563eb", "#eff6ff", "343→454 v · 6.9k→10.6k c"),
        ("n=5, r=1", "s = 8 → 9", "U → S", "#7c3aed", "#f5f3ff", "825→1,019 v · 33.5k→46.4k c"),
        ("n=6, r=1,2", "s ≤ 12", "OPEN", "#d97706", "#fffbeb", "2,309 v · 185.7k c (×2)"),
    ]
    for i, (fn, rng, tag, col, bg, dim) in enumerate(rows):
        yy = ry + 48 + i * 31
        p.append(f'    <rect x="{rx + 12}" y="{yy}" width="{rw - 24}" height="26" rx="5" fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + 20}" y="{yy + 16.5}" font-family="{mono}" font-size="9.4" font-weight="700" fill="#0f172a">{fn}</text>')
        p.append(f'    <text x="{rx + 92}" y="{yy + 16.5}" font-size="9.4" font-weight="700" fill="{col}">{rng}</text>')
        p.append(f'    <text x="{rx + 156}" y="{yy + 16.5}" font-size="8.7" fill="#475569">{dim}</text>')
        p.append(f'    <rect x="{rx + rw - 54}" y="{yy + 5}" width="38" height="16" rx="8" fill="{bg}" stroke="{col}" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + rw - 35}" y="{yy + 16}" text-anchor="middle" font-size="8.2" font-weight="700" fill="{col}">{tag}</text>')

    # Card 2: SAT Encoding Structure (Kojevnikov-Kulikov-Yaroslavtsev + SB)
    cy2 = ry + 256
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="140" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 21}" font-size="12" font-weight="700" fill="#0f172a">SAT Encoding &amp; Symmetry Breaking (modsat.py)</text>')
    enc_lines = [
        ("sel(i,j,k):", "Exactly-one fan-in pair (j &lt; k &lt; i) per gate i"),
        (f'f{sub("i")} (3 bits):', "Normal B₂ truth table (f₀₁, f₁₀, f₁₁); no const"),
        (f'x{sub("i,t")}:', f'Gate i value on all 2{sup("n")} − 1 non-zero rows t'),
        ("Symmetry:", "lex gate order + noreuse + symmetric inputs"),
        ("Regime:", f'Deep Over (ρ{sub("crit")} = 3.24×–14.2×, α up to 80)'),
        ("Decoder:", "maps/*.map.json decodes SAT → verified B₂"),
    ]
    for i, (k, v) in enumerate(enc_lines):
        yy = cy2 + 40 + i * 16.5
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.6" font-weight="700" fill="#6d28d9">{k}</text>')
        p.append(f'    <text x="{rx + 84}" y="{yy:.1f}" font-size="9.5" fill="#334155">{v}</text>')

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
