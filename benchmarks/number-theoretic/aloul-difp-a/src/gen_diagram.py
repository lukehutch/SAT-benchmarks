#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`aloul-difp-a` (Aloul Array-Multiplier Integer Factoring Benchmarks).

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
    W, H = 920, 480
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Aloul Carry-Save Array Multiplier Integer Factoring SAT Architecture">',
        "  <defs>",
        '    <marker id="arr-purp" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>',
        "    </marker>",
        '    <marker id="arr-amb" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>',
        "    </marker>",
        '    <marker id="arr-grn" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Aloul Array-Multiplier Integer Factoring (aloul-difp-a)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Bit-level inversion of a 2D Carry-Save Array Multiplier (p × q = N) · '
        '14 SAT semiprimes (n ∈ {19, 20, 21}-bit primes, randomly reordered)</text>',
        '    <rect x="782" y="18" width="112" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="838" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">14 SAT · Array</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: 4x4 CARRY-SAVE ARRAY MULTIPLIER GRID =================
    lx, ly, lw, lh = 24, 78, 540, 380
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        '2D Carry-Save Array Multiplier Mesh (4×4 Bit-Slice Schematic of n×n)</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        f'Unknown prime bits p{sub("i")}, q{sub("j")} form AND partial products reduced row-by-row in O(n) depth</text>'
    )

    col_x = [lx + 478 - c * 60 for c in range(8)]
    row_y = [ly + 90, ly + 142, ly + 194, ly + 246]
    cpa_y = ly + 300

    # Unknown factor p input badges above row 0 (clean 9px gap!)
    for i in range(4):
        cx = col_x[i]
        p.append(f'    <rect x="{cx - 18}" y="{ly + 47}" width="36" height="19" rx="5" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>')
        p.append(f'    <text x="{cx}" y="{ly + 60}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#1d4ed8">p{chr(0x2080 + i)}?</text>')

    # Unknown factor q input badges on right edge of each row
    for r in range(4):
        ry_r = row_y[r]
        p.append(f'    <rect x="{lx + 502}" y="{ry_r - 10}" width="30" height="20" rx="5" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>')
        p.append(f'    <text x="{lx + 517}" y="{ry_r + 3.5}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#1d4ed8">q{chr(0x2080 + r)}?</text>')
        p.append(f'    <line x1="{col_x[r + 3] - 18}" y1="{ry_r}" x2="{lx + 502}" y2="{ry_r}" stroke="#bfdbfe" stroke-width="1.2" stroke-dasharray="3,2"/>')

    # Draw wires between array cells BEFORE cell boxes
    for i in range(4):
        c = i
        if c == 0:
            p.append(f'    <line x1="{col_x[0]}" y1="{row_y[0] + 14}" x2="{col_x[0]}" y2="{ly + 340}" stroke="#059669" stroke-width="2" marker-end="url(#arr-grn)"/>')
        else:
            p.append(f'    <line x1="{col_x[c]}" y1="{row_y[0] + 14}" x2="{col_x[c]}" y2="{row_y[1] - 16}" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')

    for r in range(1, 4):
        next_y = row_y[r + 1] - 16 if r < 3 else cpa_y - 16
        for i in range(4):
            c = r + i
            x_cur = col_x[c]
            y_cur = row_y[r]
            if i == 0 and r < 3:
                p.append(f'    <line x1="{x_cur}" y1="{y_cur + 14}" x2="{x_cur}" y2="{ly + 340}" stroke="#059669" stroke-width="2" marker-end="url(#arr-grn)"/>')
            elif r < 3:
                p.append(f'    <line x1="{x_cur}" y1="{y_cur + 14}" x2="{x_cur}" y2="{next_y}" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')
            else:
                p.append(f'    <line x1="{x_cur}" y1="{y_cur + 14}" x2="{x_cur}" y2="{cpa_y - 16}" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')
            if c + 1 < 8:
                p.append(f'    <line x1="{x_cur - 12}" y1="{y_cur + 13}" x2="{col_x[c + 1] + 10}" y2="{next_y}" stroke="#d97706" stroke-width="1.5" marker-end="url(#arr-amb)"/>')

    # Final CPA horizontal carry ripple arrows (cols 3 -> 4 -> 5 -> 6 -> 7)
    for c in range(3, 7):
        p.append(f'    <line x1="{col_x[c] - 22}" y1="{cpa_y}" x2="{col_x[c + 1] + 24}" y2="{cpa_y}" stroke="#d97706" stroke-width="1.8" marker-end="url(#arr-amb)"/>')

    # Draw cell boxes
    for i in range(4):
        cx = col_x[i]
        cy = row_y[0]
        p.append(f'    <rect x="{cx - 20}" y="{cy - 13}" width="40" height="26" rx="5" fill="#ffffff" stroke="#2563eb" stroke-width="1.3"/>')
        p.append(f'    <text x="{cx}" y="{cy + 3.5}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#1d4ed8">p{i}∧q0</text>')

    for r in range(1, 4):
        for i in range(4):
            c = r + i
            cx = col_x[c]
            cy = row_y[r]
            cell_type = "HA" if (r == 1 or i == 3) else "FA"
            bg_c = "#f5f3ff" if cell_type == "FA" else "#fffbeb"
            st_c = "#7c3aed" if cell_type == "FA" else "#d97706"
            p.append(f'    <rect x="{cx - 22}" y="{cy - 14}" width="44" height="28" rx="5" fill="{bg_c}" stroke="{st_c}" stroke-width="1.3"/>')
            p.append(f'    <text x="{cx}" y="{cy - 1}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">{cell_type}</text>')
            p.append(f'    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="8.2" fill="#475569">p{i}∧q{r}</text>')

    # CPA row boxes (cols 3..7)
    for c in range(3, 8):
        cx = col_x[c]
        lbl = "CPA" if c < 7 else "MSB"
        p.append(f'    <rect x="{cx - 22}" y="{cpa_y - 13}" width="44" height="26" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1.4"/>')
        p.append(f'    <text x="{cx}" y="{cpa_y + 3.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#047857">{lbl}</text>')

    # Clamped fixed product output bar N_7 .. N_0 (generous vertical clearance below CPA!)
    out_y = ly + 358
    p.append(f'    <text x="{lx + 36}" y="{out_y - 21}" font-size="9.4" font-weight="700" fill="#047857">Clamped Target Bits (unit literals fixing p × q = N):</text>')
    p.append(f'    <rect x="{lx + 24}" y="{out_y - 14}" width="{lw - 48}" height="23" rx="6" fill="#059669"/>')
    for c in range(8):
        p.append(f'    <text x="{col_x[c]}" y="{out_y + 1}" text-anchor="middle" font-family="{mono}" font-size="10" font-weight="700" fill="#ffffff">N{chr(0x2080 + c)}</text>')

    # Legend in empty top-left corner of parallelogram
    leg_x, leg_y = lx + 18, ly + 82
    p.append(f'    <rect x="{leg_x}" y="{leg_y}" width="176" height="86" rx="7" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    p.append(f'    <text x="{leg_x + 10}" y="{leg_y + 16}" font-size="10" font-weight="700" fill="#0f172a">Array Signal Flow</text>')
    p.append(f'    <line x1="{leg_x + 10}" y1="{leg_y + 32}" x2="{leg_x + 32}" y2="{leg_y + 32}" stroke="#7c3aed" stroke-width="2"/>')
    p.append(f'    <text x="{leg_x + 38}" y="{leg_y + 35}" font-size="9.3" fill="#334155">Sum s = a ⊕ b ⊕ c (XOR)</text>')
    p.append(f'    <line x1="{leg_x + 10}" y1="{leg_y + 50}" x2="{leg_x + 32}" y2="{leg_y + 50}" stroke="#d97706" stroke-width="2"/>')
    p.append(f'    <text x="{leg_x + 38}" y="{leg_y + 53}" font-size="9.3" fill="#334155">Carry c = Maj₃(a,b,c)</text>')
    p.append(f'    <line x1="{leg_x + 10}" y1="{leg_y + 68}" x2="{leg_x + 32}" y2="{leg_y + 68}" stroke="#059669" stroke-width="2"/>')
    p.append(f'    <text x="{leg_x + 38}" y="{leg_y + 71}" font-size="9.3" fill="#334155">Clamped product bit N{sub("k")}</text>')

    # ================= RIGHT PANEL: INSTANCE SPOTLIGHT & METRICS =================
    rx, ry, rw = 580, 78, 316

    # Card 1: Real Instance Spotlight
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="120" rx="9" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#1d4ed8">Real Instance: difp_19_0_arr_rcr</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 40}" font-family="{mono}" font-size="10.2" font-weight="700" fill="#0f172a">N = 0x1451990C0F</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 56}" font-family="{mono}" font-size="9.8" fill="#334155">  = 87,268,330,511 (37-bit)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 74}" font-family="{mono}" font-size="10.2" font-weight="700" fill="#047857">p = 283,097 (19-bit prime)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 90}" font-family="{mono}" font-size="10.2" font-weight="700" fill="#047857">q = 308,263 (19-bit prime)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 108}" font-size="9.6" fill="#475569">Vars &amp; clauses randomly shuffled (_rcr)</text>')

    # Card 2: Array vs Wallace Topology Signature (fixed & escaping!)
    cy2 = ry + 130
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="114" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">Array Multiplier Structural Signature</text>')
    sig_lines = [
        ("Adder Depth:", "Linear O(n) sequential carry-save rows"),
        ("Regularity:", "Uniform 2D mesh → low Deg CV = 0.45"),
        ("CNF Clauses:", "Tseitin AND (3 cls), XOR3 (8), Maj₃ (6)"),
        ("XOR Chains:", "380–462 native XORs per file (5,730 total)"),
        ("vs Wallace:", "31% fewer vars & 37% fewer clauses"),
    ]
    for i, (k, v) in enumerate(sig_lines):
        yy = cy2 + 39 + i * 16.2
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.8" font-weight="700" fill="#7c3aed">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 92}" y="{yy:.1f}" font-size="9.6" fill="#334155">{esc(v)}</text>')

    # Card 3: Corpus Breakdown (extra vertical breathing room!)
    cy3 = cy2 + 124
    p.append(f'    <rect x="{rx}" y="{cy3}" width="{rw}" height="126" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy3 + 20}" font-size="12" font-weight="700" fill="#0f172a">Corpus Dimensions (14 SAT Instances)</text>')

    groups = [
        ("difp_19 / 20 (arr)", "9 files", "1,201 v · 6,563 c · 380 XOR", 0.82, "#2563eb"),
        ("difp_21 (arr)", "5 files", "1,453 v · 7,967 c · 462 XOR", 1.00, "#7c3aed"),
    ]
    for i, (g, cnt, stat, frac, col) in enumerate(groups):
        yy = cy3 + 40 + i * 38
        p.append(f'    <text x="{rx + 14}" y="{yy}" font-family="{mono}" font-size="9.5" font-weight="700" fill="#0f172a">{g}</text>')
        p.append(f'    <text x="{rx + rw - 14}" y="{yy}" text-anchor="end" font-size="9.4" font-weight="600" fill="{col}">{cnt}</text>')
        p.append(f'    <rect x="{rx + 14}" y="{yy + 4}" width="{rw - 28}" height="7.5" rx="3" fill="#f1f5f9"/>')
        p.append(f'    <rect x="{rx + 14}" y="{yy + 4}" width="{(rw - 28) * frac:.1f}" height="7.5" rx="3" fill="{col}" fill-opacity="0.82"/>')
        p.append(f'    <text x="{rx + 14}" y="{yy + 22.5}" font-size="9.1" fill="#475569">{stat}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy3 + 118}" font-size="9.4" fill="#475569">'
        f'Regime: Over (ρ{sub("crit")} = 1.48×) · κ = 0.98 · 59% Horn · k̄ = 3.33</text>'
    )

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
