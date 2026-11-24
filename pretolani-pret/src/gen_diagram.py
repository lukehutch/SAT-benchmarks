#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `pretolani-pret` benchmark collection.

Illustrates Daniele Pretolani's 1990 TRISAT parity-charged 2-coloring UNSAT
formulas (`pret60_*` and `pret150_*`):
  - Left: Hierarchical 3-XOR parity-charged tree/DAG with closed degree-2
    edge pairings (every variable appears in exactly 2 3-XOR nodes, Deg CV=0.00),
    all internal nodes even (charge 0) and a single odd root flip (charge 1)
    forcing global 0 != 1 (mod 2) contradiction and exponential Resolution
  - Right: Exact Horn-clause polarity sweep ({25%, 40%, 60%, 75%}) achieved via
    literal sign renaming without altering the underlying F_2 parity obstruction,
    plus pret60 / pret150 suite parameters.

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
    W, H = 920, 470
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Pretolani parity-charged 2-coloring 3-XOR DAG with odd root charge and Horn percentage sweep">',
        # Explicit white card background
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Pretolani Parity-Charged 2-Coloring Formulas (pretolani-pret)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "TRISAT (1990) 3-regular parity-charged graph: 2k−1 even 3-XOR nodes + 1 odd root charge "
        "⇒ UNSAT across Horn-% polarity sweep</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: PARITY-CHARGED 3-XOR DAG =====================
    px, py, pw, ph = 24, 76, 514, 326
    parts.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px + 14}" y="{py + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "Parity-Charged 3-XOR Graph / DAG (Every Variable Has Exact Degree 2)</text>"
    )
    parts.append(
        f'<text x="{px + 14}" y="{py + 35}" font-size="9.5" fill="#475569">'
        "40 nodes / 60 edges (pret60) or 100 nodes / 150 edges (pret150) — each node = 4 ternary clauses</text>"
    )

    # Draw a clean 8-node 3-regular parity-charged hierarchical DAG (1 odd root + 7 even nodes)
    # Level 0 (Root): R0 at top center -> 3 edges going down to L1_a, L1_b, L1_c
    # Level 1 (3 internal nodes): L1_a, L1_b, L1_c
    # Level 2 (4 leaf/base nodes): B0, B1, B2, B3 connected cleanly so EVERY node has degree 3!
    # Check degrees (8 nodes * 3 / 2 = 12 edges):
    #   R0: (R0, L1_a), (R0, L1_b), (R0, L1_c) -> deg 3
    #   L1_a: (R0, L1_a), (L1_a, B0), (L1_a, B1) -> deg 3
    #   L1_b: (R0, L1_b), (L1_b, B1), (L1_b, B2) -> deg 3
    #   L1_c: (R0, L1_c), (L1_c, B2), (L1_c, B3) -> deg 3
    #   B0: (L1_a, B0), (B0, B1), (B0, B3) -> deg 3
    #   B1: (L1_a, B1), (L1_b, B1), (B0, B1) -> deg 3
    #   B2: (L1_b, B2), (L1_c, B2), (B2, B3) -> deg 3
    #   B3: (L1_c, B3), (B2, B3), (B0, B3) -> deg 3
    # Exact 8-node 3-regular graph! Every edge variable appears in EXACTLY 2 XORs!
    nodes = {
        "R0": (px + 257, py + 76),
        "L1a": (px + 115, py + 142),
        "L1b": (px + 257, py + 142),
        "L1c": (px + 399, py + 142),
        "B0": (px + 75, py + 216),
        "B1": (px + 195, py + 216),
        "B2": (px + 319, py + 216),
        "B3": (px + 439, py + 216),
    }
    edges = [
        ("R0", "L1a", "x₃₈"),
        ("R0", "L1b", "x₅₉"),
        ("R0", "L1c", "x₆₀"),
        ("L1a", "B0", "x₁"),
        ("L1a", "B1", "x₂"),
        ("L1b", "B1", "x₃"),
        ("L1b", "B2", "x₄"),
        ("L1c", "B2", "x₅"),
        ("L1c", "B3", "x₆"),
        ("B0", "B1", "x₇"),
        ("B2", "B3", "x₈"),
    ]
    # Draw straight edges with crisp variable tags
    for u, v, lbl in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        col = "#dc2626" if u == "R0" else "#64748b"
        w_e = "1.9" if u == "R0" else "1.5"
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w_e}"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if u == "R0" and v == "L1b":
            mx += 14
        elif u == "R0" and v == "L1a":
            mx -= 12
            my -= 5
        elif u == "R0" and v == "L1c":
            mx += 12
            my -= 5
        elif y1 == y2:
            my -= 7
        else:
            mx += -11 if x2 < x1 else 11
        parts.append(
            f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="8.6" font-weight="600" '
            f'fill="{"#b91c1c" if u == "R0" else "#475569"}">{lbl}</text>'
        )

    # Closing wrap edge (B0, B3) curving cleanly underneath
    bx0, by0 = nodes["B0"]
    bx3, by3 = nodes["B3"]
    parts.append(
        f'<path d="M {bx0} {by0} Q {px + 257} {by0 + 40}, {bx3} {by3}" '
        'fill="none" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="4,2.5"/>'
    )
    parts.append(
        f'<text x="{px + 257}" y="{by0 + 30}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="8.6" font-weight="600" fill="#6d28d9">x₉ (closing cycle edge)</text>'
    )

    # Draw nodes on top of edges
    for nid, (nx, ny) in nodes.items():
        if nid == "R0":
            parts.append(f'<circle cx="{nx}" cy="{ny}" r="18" fill="#dc2626" stroke="#ffffff" stroke-width="2.2"/>')
            parts.append(f'<text x="{nx}" y="{ny + 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff">⊕=1</text>')
            # Root callout badge
            parts.append(f'<rect x="{nx + 28}" y="{ny - 15}" width="176" height="30" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.1"/>')
            parts.append(f'<text x="{nx + 116}" y="{ny - 2}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#b91c1c">Odd Root Charge (σ = 1)</text>')
            parts.append(f'<text x="{nx + 116}" y="{ny + 10}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.6" fill="#475569">x₃₈ ⊕ x₅₉ ⊕ x₆₀ = 1</text>')
        else:
            parts.append(f'<circle cx="{nx}" cy="{ny}" r="15" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>')
            parts.append(f'<text x="{nx}" y="{ny + 3.8}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1d4ed8">⊕=0</text>')

    # Bottom parity contradiction callout inside Left Panel
    parts.append(
        f'<rect x="{px + 14}" y="{py + 258}" width="{pw - 28}" height="56" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + 276}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="9.8" font-weight="700" fill="#0f172a">'
        "∑ (all 2k nodes):  2 · ∑ xₑ  ≡  0 (mod 2)   ≠   1 (root charge)  ⇒  UNSAT</text>"
    )
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + 294}" text-anchor="middle" font-size="9.2" fill="#475569">'
        "Pure 3-SAT with α = 2.67 (ρ_c = 0.62×, deeply under-constrained), yet Resolution requires 2^Ω(n)!</text>"
    )
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + 307}" text-anchor="middle" font-size="8.9" font-weight="600" fill="#047857">'
        "Zero-copy 𝔽₂ Gaussian elimination collapses all 160–400 clauses to 40–100 XORs in &lt;1.5 ms.</text>"
    )

    # ===================== RIGHT PANEL: HORN-% SWEEP + SUITE TABLE =====================
    rx, rw = 554, 342
    # Card 1: Horn-Clause Polarity Sweep Chart
    parts.append(
        f'<rect x="{rx}" y="76" width="{rw}" height="176" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="96" font-size="11.8" font-weight="700" fill="#0f172a">'
        "Horn-Clause Polarity Sweep (25% → 75%)</text>"
    )
    parts.append(
        f'<text x="{rx + 12}" y="110" font-size="9.1" fill="#475569">'
        "Renaming xᵢ ↔ ¬xᵢ changes Horn-% without altering 𝔽₂ parity:</text>"
    )

    # 4 horizontal bars for exact measured Horn% from README
    bars = [
        ("pret*_25", 26, "#2563eb", "26% Horn"),
        ("pret*_40", 40, "#7c3aed", "40% Horn"),
        ("pret*_60", 60, "#d97706", "60% Horn"),
        ("pret*_75", 74, "#059669", "74% Horn"),
    ]
    bar_x0 = rx + 76
    bar_max = 196
    for idx, (blbl, pct, col, val_txt) in enumerate(bars):
        by_i = 123 + idx * 24
        parts.append(f'<text x="{rx + 12}" y="{by_i + 12}" font-family="{FONT_MONO}" font-size="9.3" font-weight="600" fill="#0f172a">{blbl}</text>')
        parts.append(f'<rect x="{bar_x0}" y="{by_i}" width="{bar_max}" height="16" rx="4" fill="#e2e8f0"/>')
        parts.append(f'<rect x="{bar_x0}" y="{by_i}" width="{bar_max * pct / 100.0:.1f}" height="16" rx="4" fill="{col}"/>')
        parts.append(f'<text x="{bar_x0 + bar_max + 8}" y="{by_i + 12}" font-size="9.1" font-weight="700" fill="{col}">{val_txt}</text>')

    # 4-clause block mini-explanation
    parts.append(
        f'<rect x="{rx + 12}" y="221" width="{rw - 24}" height="22" rx="5" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{rx + rw/2:.1f}" y="235.5" text-anchor="middle" font-size="8.8" fill="#334155">'
        "3-XOR block = 4 ternary clauses: 1 or 3 are Horn (≤1 pos lit) per sign flip</text>"
    )

    # Card 2: Exact Corpus Table
    parts.append(
        f'<rect x="{rx}" y="262" width="{rw}" height="140" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="282" font-size="11.6" font-weight="700" fill="#0f172a">'
        "Benchmark Families (8 / 8 Provably UNSAT)</text>"
    )
    th_y = 299
    parts.append(f'<rect x="{rx + 10}" y="{th_y - 10}" width="{rw - 20}" height="16" rx="4" fill="#e2e8f0"/>')
    for cx_h, lbl_h, anc in [(rx + 16, "Family", "start"), (rx + 132, "Nodes", "middle"), (rx + 178, "Vars", "middle"), (rx + 226, "Clauses", "middle"), (rx + 290, "XORs / Ans", "middle")]:
        parts.append(f'<text x="{cx_h}" y="{th_y + 1}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{lbl_h}</text>')

    pret_rows = [
        ("pret60_{25..75}", "40", "60", "160", "40 · UNSAT"),
        ("pret150_{25..75}", "100", "150", "400", "100 · UNSAT"),
    ]
    for i, (fam, nd, vs, cl, xa) in enumerate(pret_rows):
        ry_r = th_y + 20 + i * 25
        if i % 2 == 1:
            parts.append(f'<rect x="{rx + 10}" y="{ry_r - 12}" width="{rw - 20}" height="21" rx="3" fill="#ffffff"/>')
        parts.append(f'<text x="{rx + 16}" y="{ry_r + 2}" font-family="{FONT_MONO}" font-size="8.7" font-weight="600" fill="#0f172a">{fam}</text>')
        parts.append(f'<text x="{rx + 132}" y="{ry_r + 2}" text-anchor="middle" font-size="9.1" fill="#334155">{nd}</text>')
        parts.append(f'<text x="{rx + 178}" y="{ry_r + 2}" text-anchor="middle" font-size="9.1" fill="#334155">{vs}</text>')
        parts.append(f'<text x="{rx + 226}" y="{ry_r + 2}" text-anchor="middle" font-size="9.1" fill="#334155">{cl}</text>')
        parts.append(f'<text x="{rx + 290}" y="{ry_r + 2}" text-anchor="middle" font-size="8.9" font-weight="700" fill="#b91c1c">{xa}</text>')

    # Historical note inside Card 2
    parts.append(
        f'<rect x="{rx + 10}" y="357" width="{rw - 20}" height="35" rx="6" fill="#fffbeb" stroke="#fcd34d" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{rx + 18}" y="371" font-size="8.6" font-weight="700" fill="#b45309">DIMACS Hygiene &amp; Historical Note:</text>'
    )
    parts.append(
        f'<text x="{rx + 18}" y="384" font-size="8.4" fill="#475569">Trailing EOF sentinel stripped; SATLIB typo fixed (all 8 have Charge=1).</text>'
    )

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 414
    pills = [
        (24, 210, "#fef2f2", "#dc2626", "#b91c1c", "8 / 8 UNSAT (Charge = 1)"),
        (244, 212, "#eff6ff", "#2563eb", "#1d4ed8", "560 Extracted Native 3-XORs"),
        (466, 206, "#fffbeb", "#d97706", "#b45309", "ρ_c = 0.62× · Deg CV = 0.00"),
        (682, 214, "#f5f3ff", "#7c3aed", "#6d28d9", "4 Formats: CNF · AIG · XCNF · ANF"),
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
