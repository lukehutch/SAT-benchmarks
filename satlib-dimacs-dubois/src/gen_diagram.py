#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `satlib-dimacs-dubois` benchmark collection.

Illustrates Olivier Dubois's exact mirror-rung cyclic 3-XOR parity chain
verified directly against `xcnf-converted/dubois20.xcnf.xz`:
  - n = 3d variables (d in {20..30, 50, 100}) partitioned into a top leg
    (x_1..x_{d-1}), mirror bottom leg (x_d..x_{2d-2}), shared vertical rungs
    (y_1..y_{d-2}), right cap pair (y_{d-1}, y_d), and left cap pair
    (x_{2d-1}, x_{2d})
  - 2d - 1 odd 3-XOR blocks (rhs = 1) + 1 twisted closing block (¬x_{2d-2}
    giving rhs = 0), where every variable appears in exactly 2 blocks
    (Deg CV = 0.00), so summing all 2d blocks yields 0 ≡ 2d - 1 ≡ 1 (mod 2)
  - Exact 4-clause CNF 3-XOR block anatomy (74% Horn) + dubois100 quirk note.

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
    W, H = 920, 480
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Dubois cyclic 3-XOR parity ladder with odd closing twist and 4-clause CNF XOR blocks">',
        # Explicit white card canvas
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Dubois Cyclic 3-XOR Parity Chain with Odd Twist (satlib-dimacs-dubois)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        "Mirror-rung 3-XOR loop on n = 3d variables (dubois20..100): 2d−1 odd blocks + 1 twisted "
        "closing block ⇒ 0 ≡ 1 (mod 2) UNSAT</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: EXACT DUBOIS CYCLIC 3-XOR LADDER =====================
    px, py, pw, ph = 24, 76, 570, 332
    parts.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px + 14}" y="{py + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "Exact Dubois Mirror-Rung 3-XOR Topology (n = 3d vars · 2d blocks · deg = 2)</text>"
    )
    parts.append(
        f'<text x="{px + 14}" y="{py + 35}" font-size="9.4" fill="#475569">'
        "Every spine variable xᵢ and vertical rung variable yₖ appears in exactly TWO 3-XOR blocks</text>"
    )

    # Geometry for mirror ladder:
    # 5 columns of 3-XOR blocks on top row (y_top) and bottom row (y_bot)
    # Col 0: Left closing cap (top: x1^x_{2d-1}^x_{2d}=1, bottom RED TWIST: ~x_{2d-2}^x_{2d-1}^x_{2d}=1 <=> =0)
    # Col 1..3: Shared rungs y_1, y_2, ..., y_{d-2}
    # Col 4: Right turnaround cap (top: x_{d-1}^y_{d-1}^y_d=1, bottom: x_d^y_{d-1}^y_d=1)
    y_top = py + 96
    y_bot = py + 216
    y_mid = (y_top + y_bot) / 2
    xs_col = [px + 68, px + 174, px + 280, px + 394, px + 502]

    # Horizontal spine connections along top leg (x_1, x_2, ..., x_{d-1})
    top_edges = [(0, 1, "x₁"), (1, 2, "x₂"), (2, 3, "…"), (3, 4, "x_{d−1}")]
    top_edges_clean = [(0, 1, "x₁"), (1, 2, "x₂"), (2, 3, "⋯"), (3, 4, "xᵈ⁻¹")]
    top_edges_sub = [(0, 1, "x₁"), (1, 2, "x₂"), (2, 3, "⋯"), (3, 4, "x₁₉")]
    bot_edges_sub = [(0, 1, "x₃₈"), (1, 2, "x₃₇"), (2, 3, "⋯"), (3, 4, "x₂₀")]

    # Draw horizontal spine wires
    for (c1, c2, lbl), y_line, is_bot in [
        *[(e, y_top, False) for e in top_edges_sub],
        *[(e, y_bot, True) for e in bot_edges_sub],
    ]:
        x1, x2 = xs_col[c1], xs_col[c2]
        dashed = ' stroke-dasharray="4,3"' if lbl == "⋯" else ""
        stroke_c = "#dc2626" if (is_bot and c1 == 0) else "#2563eb"
        parts.append(f'<line x1="{x1}" y1="{y_line}" x2="{x2}" y2="{y_line}" stroke="{stroke_c}" stroke-width="2.1"{dashed}/>')
        mx = (x1 + x2) / 2
        ty_l = y_line - 11 if not is_bot else y_line + 18
        if is_bot and c1 == 0:
            parts.append(
                f'<rect x="{mx - 20:.1f}" y="{ty_l - 11:.1f}" width="40" height="16" rx="4" '
                'fill="#fef2f2" stroke="#dc2626" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{mx:.1f}" y="{ty_l:.1f}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="9.4" font-weight="700" fill="#b91c1c">¬x₃₈</text>'
            )
        else:
            parts.append(
                f'<text x="{mx:.1f}" y="{ty_l:.1f}" text-anchor="middle" '
                f'font-family="{FONT_MONO}" font-size="9.6" font-weight="700" fill="#1d4ed8">{lbl}</text>'
            )

    # Vertical shared rung wires (each connects top block to mirror bottom block!)
    rungs = [
        (0, "x₃₉, x₄₀", True),    # Left cap shares 2 vars (39, 40)
        (1, "x₄₁", False),        # Shared rung 1
        (2, "x₄₂", False),        # Shared rung 2
        (3, "x₅₈", False),        # Shared rung d-2
        (4, "x₅₉, x₆₀", True),    # Right cap shares 2 vars (59, 60)
    ]
    for col_i, rlbl, is_double in rungs:
        xc = xs_col[col_i]
        if is_double:
            # Draw two parallel shared wires for cap pairs
            parts.append(f'<line x1="{xc - 7}" y1="{y_top}" x2="{xc - 7}" y2="{y_bot}" stroke="#7c3aed" stroke-width="1.8"/>')
            parts.append(f'<line x1="{xc + 7}" y1="{y_top}" x2="{xc + 7}" y2="{y_bot}" stroke="#7c3aed" stroke-width="1.8"/>')
            # Pill label centered over double edge
            parts.append(f'<rect x="{xc - 28}" y="{y_mid - 10:.1f}" width="56" height="20" rx="5" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1"/>')
            parts.append(f'<text x="{xc}" y="{y_mid + 3.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.8" font-weight="700" fill="#6d28d9">{rlbl}</text>')
        else:
            parts.append(f'<line x1="{xc}" y1="{y_top}" x2="{xc}" y2="{y_bot}" stroke="#059669" stroke-width="1.9"/>')
            parts.append(f'<rect x="{xc - 18}" y="{y_mid - 10:.1f}" width="36" height="20" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
            parts.append(f'<text x="{xc}" y="{y_mid + 3.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" font-weight="700" fill="#047857">{rlbl}</text>')

    # Ellipsis indicator between col 2 and col 3 in middle
    parts.append(f'<text x="{(xs_col[2] + xs_col[3])/2:.1f}" y="{y_mid + 4:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="#64748b">⋯</text>')

    # Draw 3-XOR gate nodes (top row all blue ⊕=1; bottom row blue ⊕=1 EXCEPT col 0 RED TWIST ⊕=0!)
    for col_i, xc in enumerate(xs_col):
        # Top node (odd parity = 1)
        parts.append(f'<circle cx="{xc}" cy="{y_top}" r="18" fill="#eff6ff" stroke="#2563eb" stroke-width="1.7"/>')
        parts.append(f'<text x="{xc}" y="{y_top + 4}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1d4ed8">⊕=1</text>')

        # Bottom node
        if col_i == 0:
            # TWISTED CLOSING BLOCK!
            parts.append(f'<circle cx="{xc}" cy="{y_bot}" r="20" fill="#dc2626" stroke="#ffffff" stroke-width="2.2"/>')
            parts.append(f'<text x="{xc}" y="{y_bot + 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff">⊕=0</text>')
            parts.append(
                f'<text x="{xc}" y="{y_bot + 33}" text-anchor="middle" font-size="9" font-weight="700" fill="#b91c1c">'
                "ODD TWIST!</text>"
            )
        else:
            parts.append(f'<circle cx="{xc}" cy="{y_bot}" r="18" fill="#eff6ff" stroke="#2563eb" stroke-width="1.7"/>')
            parts.append(f'<text x="{xc}" y="{y_bot + 4}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1d4ed8">⊕=1</text>')

    # Annotation under ladder (dubois20 concrete indexing)
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + 62}" text-anchor="middle" font-size="9.2" font-weight="600" fill="#475569">'
        "Exact dubois20 indexing (d = 20, n = 60 vars, 40 3-XOR blocks): top leg x₁..x₁₉, bottom leg x₂₀..x₃₈</text>"
    )

    # Bottom cancellation proof bar inside Left Panel
    parts.append(f'<rect x="{px + 14}" y="{py + 266}" width="{pw - 28}" height="52" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.15"/>')
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + 286}" text-anchor="middle" '
        f'font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="#b91c1c">'
        "∑ (all 2d blocks):  2·(∑ xᵢ + ∑ yₖ) ≡ 0  ≠  (2d − 1)·1 + 0 ≡ 1 (mod 2)  ⇒  UNSAT</text>"
    )
    parts.append(
        f'<text x="{px + pw/2:.1f}" y="{py + 305}" text-anchor="middle" font-size="9.2" fill="#334155">'
        "2d−1 = 39 odd blocks + 1 twisted block (¬x₃₈ ⊕ x₃₉ ⊕ x₄₀ = 1) → odd total parity!</text>"
    )

    # ===================== RIGHT PANEL: 4-CLAUSE CNF BLOCK & QUIRK =====================
    rx, rw = 610, 286
    # Card 1: 4-Clause CNF XOR Block Expansion
    parts.append(
        f'<rect x="{rx}" y="76" width="{rw}" height="162" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="96" font-size="11.6" font-weight="700" fill="#0f172a">'
        "4-Clause CNF 3-XOR Block Anatomy</text>"
    )
    parts.append(
        f'<text x="{rx + 12}" y="111" font-size="9.2" fill="#475569">'
        "Normal block (a ⊕ b ⊕ c = 1) — 3 of 4 are Horn:</text>"
    )
    cnf_clauses = [
        ("(  a ∨  b ∨  c )", "non-Horn (3 pos)", "#eff6ff", "#2563eb"),
        ("( ¬a ∨ ¬b ∨  c )", "Horn (1 pos)", "#ecfdf5", "#059669"),
        ("(  a ∨ ¬b ∨ ¬c )", "Horn (1 pos)", "#ecfdf5", "#059669"),
        ("( ¬a ∨  b ∨ ¬c )", "Horn (1 pos)", "#ecfdf5", "#059669"),
    ]
    for i, (cl, tag, bg, bd) in enumerate(cnf_clauses):
        cy_c = 120 + i * 22
        parts.append(f'<rect x="{rx + 12}" y="{cy_c}" width="{rw - 24}" height="18" rx="4" fill="{bg}" stroke="{bd}" stroke-width="0.9"/>')
        parts.append(f'<text x="{rx + 22}" y="{cy_c + 12.5}" font-family="{FONT_MONO}" font-size="9" font-weight="700" fill="#0f172a">{cl}</text>')
        parts.append(f'<text x="{rx + rw - 20}" y="{cy_c + 12.5}" text-anchor="end" font-size="8.5" font-weight="600" fill="{bd}">{tag}</text>')

    parts.append(
        f'<text x="{rx + 12}" y="222" font-size="8.8" fill="#475569">'
        "Every normal block has 75% Horn clauses (overall 74%</text>"
    )
    parts.append(
        f'<text x="{rx + 12}" y="233" font-size="8.8" fill="#475569">'
        "with the final negated twist block x₃₈ → ¬x₃₈).</text>"
    )

    # Card 2: Scaling & Historical dubois100 Quirk
    parts.append(
        f'<rect x="{rx}" y="248" width="{rw}" height="160" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="268" font-size="11.6" font-weight="700" fill="#0f172a">'
        "Corpus Scaling (dubois20 .. dubois100)</text>"
    )
    rows_db = [
        ("dubois20..30", "60–90v", "160–240c", "UNSAT", "#fef2f2", "#dc2626"),
        ("dubois50", "150v", "400c", "UNSAT", "#fef2f2", "#dc2626"),
        ("dubois100*", "300v", "598c*", "SAT*", "#fffbeb", "#d97706"),
    ]
    for i, (nm, vs, cs, ans, pbg, pfg) in enumerate(rows_db):
        ry_r = 288 + i * 24
        parts.append(f'<text x="{rx + 14}" y="{ry_r + 2}" font-family="{FONT_MONO}" font-size="9.2" font-weight="600" fill="#0f172a">{nm}</text>')
        parts.append(f'<text x="{rx + 126}" y="{ry_r + 2}" text-anchor="middle" font-size="9" fill="#334155">{vs}</text>')
        parts.append(f'<text x="{rx + 186}" y="{ry_r + 2}" text-anchor="middle" font-size="9" fill="#334155">{cs}</text>')
        parts.append(f'<rect x="{rx + 224}" y="{ry_r - 10}" width="50" height="16" rx="4" fill="{pbg}" stroke="{pfg}" stroke-width="0.9"/>')
        parts.append(f'<text x="{rx + 249}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.6" font-weight="700" fill="{pfg}">{ans}</text>')

    parts.append(f'<rect x="{rx + 10}" y="354" width="{rw - 20}" height="46" rx="6" fill="#fffbeb" stroke="#fcd34d" stroke-width="1"/>')
    parts.append(f'<text x="{rx + 18}" y="368" font-size="8.7" font-weight="700" fill="#b45309">*Preserved 1993 SATLIB Quirk (dubois100):</text>')
    parts.append(f'<text x="{rx + 18}" y="381" font-size="8.3" fill="#475569">Missing trailing 0 on 202/800 lines fuses clauses into</text>')
    parts.append(f'<text x="{rx + 18}" y="393" font-size="8.3" fill="#475569">tautologies (598 cls) → breaks chain → SAT on all solvers.</text>')

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 422
    pills = [
        (24, 210, "#fef2f2", "#dc2626", "#b91c1c", "13 Inst.: 12 UNSAT / 1 SAT*"),
        (244, 212, "#eff6ff", "#2563eb", "#1d4ed8", "749 Extracted Native 3-XORs"),
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
