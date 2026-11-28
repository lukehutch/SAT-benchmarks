#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram (`diagram.svg`) for
`heule-matrix-6pooled3and-c3` (`MM-23-63-no-type3`: compact 6-pooled 3-AND
re-encoding of Challenge 3, forbidding all 27 type-3 triples in summand M_1).

Audits `cnf-orig/MM-23-63-no-type3.cnf.xz` directly and illustrates:
  1. Direct propagation shortcut: how the 27 ternary forbidding clauses
     `(-a_ik, -b_kj, -c_ji)` immediately kill cube s_1 inside the direct 3-AND
     gate and Leaf Pool 1 of each delta = 1 6-XOR tree (with zero pair vars).
  2. Exact head-to-head structural comparison against Plain `MM-23-no-type3`
     and exact clause-length breakdown (2/3/4/6-clauses, 4,374 XORs).
"""
from __future__ import annotations

import collections
import lzma
import xml.etree.ElementTree as ET
from pathlib import Path

W, H = 920, 480
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def audit_cnf(cnf_xz: Path) -> tuple[int, int, dict[int, int], int]:
    nv = nc = 0
    lens: collections.Counter[int] = collections.Counter()
    no_type3 = 0
    with lzma.open(cnf_xz, "rt", encoding="ascii", errors="ignore") as f:
        for line in f:
            if not line or line[0] == "c":
                continue
            if line[0] == "p":
                parts = line.split()
                nv, nc = int(parts[2]), int(parts[3])
                continue
            lits = [int(x) for x in line.split()[:-1]]
            lens[len(lits)] += 1
            if len(lits) == 3 and all(x < 0 for x in lits) and max(-x for x in lits) <= 27:
                no_type3 += 1
    if no_type3 != 27:
        raise RuntimeError(f"Expected 27 no-type3 clauses, found {no_type3}")
    return nv, nc, dict(lens), no_type3


def build_svg(nv: int, nc: int, lens: dict[int, int], no_type3: int) -> str:
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Heule 3x3 Matrix Multiplication 6pooled3and Challenge 3: MM-23-63-no-type3">',
        "  <defs>",
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#6d28d9"/>',
        "    </marker>",
        '    <marker id="arrr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT}">',
    ]

    # Header
    out.append(
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Heule 3×3 Matrix Multiplication — 6pooled3and / Challenge 3 (MM-23-63-no-type3)"
        "</text>"
    )
    out.append(
        '    <text x="26" y="53" font-size="11.5" fill="#475569">'
        "Direct 3-AND + 6-pooled XOR re-encoding of the R = 23 no-type-3-in-M₁ challenge "
        "(21,033 vars, 186,651 clauses, 4,374 XORs)"
        "</text>"
    )
    out.append(
        '    <rect x="760" y="18" width="136" height="26" rx="13" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>'
    )
    out.append(
        '    <text x="828" y="35" text-anchor="middle" font-size="11" '
        'font-weight="700" fill="#6d28d9">OPEN / HARD (1 CNF)</text>'
    )
    out.append(
        '    <line x1="22" y1="64" x2="898" y2="64" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # ================= LEFT PANEL: DIRECT 3-AND + NO-TYPE3 PROPAGATION =================
    lx, ly, lw, lh = 22, 76, 444, 384
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="28" rx="9" fill="#7c3aed"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly + 16}" width="{lw}" height="12" fill="#7c3aed"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "1. How no-type3 Eliminates M₁ Inside Direct 3-AND + 6-XOR</text>"
    )

    # Step 1: 27 no-type3 clauses on M1
    y1 = ly + 40
    out.append(
        f'    <rect x="{lx + 14}" y="{y1}" width="{lw - 28}" height="74" rx="7" '
        'fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y1 + 18}" font-size="10.8" font-weight="700" fill="#b91c1c">'
        f"Constraint on Summand M₁: {no_type3} Forbidden Type-3 Triples (δ = 1)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y1 + 37}" font-family="{MONO}" font-size="10.2" '
        'font-weight="700" fill="#1e293b">'
        "(¬a⁽¹⁾ᵢₖ ∨ ¬b⁽¹⁾ₖⱼ ∨ ¬c⁽¹⁾ⱼᵢ)   for all 27 trace triples (i,j,k)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y1 + 56}" font-size="9.5" fill="#475569">'
        "In plain CNF, these sit 2 gates away from XORs (via pair p = a∧b, then s = p∧c).</text>"
    )

    # Arrow down
    out.append(
        f'    <line x1="{lx + lw / 2:.1f}" y1="{y1 + 74}" x2="{lx + lw / 2:.1f}" y2="{y1 + 91}" '
        'stroke="#dc2626" stroke-width="1.6" marker-end="url(#arrr)"/>'
    )

    # Step 2: Direct 3-AND collapse
    y2 = y1 + 94
    out.append(
        f'    <rect x="{lx + 14}" y="{y2}" width="{lw - 28}" height="86" rx="7" '
        'fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 18}" font-size="10.8" font-weight="700" fill="#1d4ed8">'
        "Direct 3-AND Resolution Shortcut (Zero Pair Variables!):</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 37}" font-family="{MONO}" font-size="8.7" fill="#334155">'
        "3-AND: (¬s₁∨a₁), (¬s₁∨b₁), (¬s₁∨c₁), (s₁∨¬a₁∨¬b₁∨¬c₁)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 54}" font-family="{MONO}" font-size="8.9" '
        'font-weight="700" fill="#b91c1c">'
        "Resolve with (¬a₁ ∨ ¬b₁ ∨ ¬c₁) ⇒ Unit (¬s₁)  [s⁽¹⁾ = 0 on δ=1]</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 72}" font-size="9.4" fill="#475569">'
        "1-step binary/ternary resolution kills all 27 δ = 1 cubes of M₁ directly.</text>"
    )

    # Arrow down
    out.append(
        f'    <line x1="{lx + lw / 2:.1f}" y1="{y2 + 86}" x2="{lx + lw / 2:.1f}" y2="{y2 + 103}" '
        'stroke="#6d28d9" stroke-width="1.6" marker-end="url(#arr)"/>'
    )

    # Step 3: Collapsed Leaf Pool 1 for every delta=1 Brent equation
    y3 = y2 + 106
    out.append(
        f'    <rect x="{lx + 14}" y="{y3}" width="{lw - 28}" height="128" rx="7" '
        'fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 18}" font-size="10.8" font-weight="700" fill="#6d28d9">'
        "Impact on the 27 δ = 1 Pooled 6-XOR Trees (M₂…M₂₃ Only):</text>"
    )
    # Show struck-through s1 inside Pool 1
    out.append(
        f'    <rect x="{lx + 24}" y="{y3 + 28}" width="194" height="44" rx="5" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 121}" y="{y3 + 44}" text-anchor="middle" '
        'font-size="9.4" font-weight="700" fill="#6d28d9">Leaf Pool 1 (δ = 1 eqs)</text>'
    )
    out.append(
        f'    <text x="{lx + 121}" y="{y3 + 61}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="9.3" fill="#1e293b">'
        '<tspan fill="#dc2626" text-decoration="line-through">s₁</tspan>'
        " ⊕ s₂ ⊕ s₃ ⊕ s₄ ⊕ s₅ ⊕ t₁ = 1</text>"
    )
    # Arrow to rest of tree
    out.append(
        f'    <line x1="{lx + 220}" y1="{y3 + 50}" x2="{lx + 244}" y2="{y3 + 50}" '
        'stroke="#6d28d9" stroke-width="1.5" marker-end="url(#arr)"/>'
    )
    out.append(
        f'    <rect x="{lx + 248}" y="{y3 + 28}" width="168" height="44" rx="5" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 332}" y="{y3 + 44}" text-anchor="middle" '
        'font-size="9.4" font-weight="700" fill="#b45309">Pools 2–5 + 3-XOR Root</text>'
    )
    out.append(
        f'    <text x="{lx + 332}" y="{y3 + 61}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="9.1" fill="#1e293b">s₆…s₂₃ via t₂…t₅ (5 aux)</text>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 91}" font-size="9.5" fill="#334155">'
        "• On the 27 δ = 1 equations: Leaf Pool 1 shrinks effectively to a 5-XOR over M₂…M₅.</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 107}" font-size="9.5" fill="#334155">'
        "• On the 702 δ = 0 equations: M₁ stays fully active to cancel cross-terms mod 2.</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 121}" font-size="9.2" font-weight="600" fill="#6d28d9">'
        "• Equivalent to Challenge 3, with 5,508 fewer variables and tighter clause locality.</text>"
    )

    # ================= RIGHT PANEL: PLAIN C3 vs 6POOLED3AND C3 =================
    rx, ry, rw, rh = 480, 76, 418, 384
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="28" rx="9" fill="#2563eb"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry + 16}" width="{rw}" height="12" fill="#2563eb"/>'
    )
    out.append(
        f'    <text x="{rx + rw / 2:.1f}" y="{ry + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "2. Structural Comparison: Plain c3 vs 6pooled3and-c3</text>"
    )

    # Side-by-side comparison table card
    ty = ry + 40
    out.append(
        f'    <rect x="{rx + 14}" y="{ty}" width="{rw - 28}" height="178" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    # Table header
    out.append(
        f'    <rect x="{rx + 15}" y="{ty + 1}" width="{rw - 30}" height="24" rx="6" fill="#f1f5f9"/>'
    )
    out.append(
        f'    <text x="{rx + 26}" y="{ty + 16.5}" font-size="9.6" font-weight="700" fill="#0f172a">Metric</text>'
    )
    out.append(
        f'    <text x="{rx + 198}" y="{ty + 16.5}" text-anchor="end" font-size="9.6" font-weight="700" fill="#475569">Plain c3</text>'
    )
    out.append(
        f'    <text x="{rx + 306}" y="{ty + 16.5}" text-anchor="end" font-size="9.6" font-weight="700" fill="#1d4ed8">6pooled3and-c3</text>'
    )
    out.append(
        f'    <text x="{rx + 392}" y="{ty + 16.5}" text-anchor="end" font-size="9.6" font-weight="700" fill="#6d28d9">Change</text>'
    )
    comp_rows = [
        ("CNF Variables (n)", "26,541", f"{nv:,}", "−20.8%"),
        ("Pair Vars (a ∧ b)", "1,863", "0", "−100%"),
        ("XOR Aux Vars", "7,290", "3,645", "−50.0%"),
        ("CNF Clauses (m)", "117,153", f"{nc:,}", "+59.3%"),
        ("Native XOR Blocks", "8,019", "4,374", "−45.5%"),
        ("Avg Length k̄ (max)", "3.18 (4)", "4.70 (6)", "+1.52"),
        ("Phase ρ_crit / κ", "1.82× / 0.94", "2.63× / 1.22", "+44.5%"),
        ("Deg CV / Horn %", "0.96 / 73%", "0.53 / 48%", "flatter"),
    ]
    for i, (m_lbl, v1, v2, chg) in enumerate(comp_rows):
        ry_i = ty + 40 + i * 18
        if i % 2 == 1:
            out.append(
                f'    <rect x="{rx + 18}" y="{ry_i - 12}" width="{rw - 36}" height="17" fill="#f8fafc"/>'
            )
        out.append(
            f'    <text x="{rx + 26}" y="{ry_i}" font-size="9.3" font-weight="600" fill="#334155">{m_lbl}</text>'
        )
        out.append(
            f'    <text x="{rx + 198}" y="{ry_i}" text-anchor="end" font-family="{MONO}" font-size="9.1" fill="#64748b">{v1}</text>'
        )
        out.append(
            f'    <text x="{rx + 306}" y="{ry_i}" text-anchor="end" font-family="{MONO}" font-size="9.1" font-weight="700" fill="#1d4ed8">{v2}</text>'
        )
        out.append(
            f'    <text x="{rx + 392}" y="{ry_i}" text-anchor="end" font-family="{MONO}" font-size="8.9" font-weight="700" fill="#6d28d9">{chg}</text>'
        )

    # Exact Clause Spectrum Bar
    by = ty + 188
    out.append(
        f'    <rect x="{rx + 14}" y="{by}" width="{rw - 28}" height="82" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{by + 17}" font-size="10.2" font-weight="700" fill="#0f172a">'
        f"Exact Clause Anatomy ({nc:,} total clauses, 0 unit pins):</text>"
    )
    bar_x, bar_y, bar_w = rx + 24, by + 24, rw - 48
    segs = [
        (lens.get(2, 0), "#2563eb", f"2-cl: {lens.get(2, 0):,}"),
        (lens.get(3, 0), "#dc2626", ""),
        (lens.get(4, 0), "#059669", "4-cl"),
        (lens.get(6, 0), "#7c3aed", f"6-cl (6-XOR): {lens.get(6, 0):,} (62.5%)"),
    ]
    cur_x = float(bar_x)
    for cnt, col, lbl in segs:
        sw = bar_w * (cnt / nc)
        out.append(
            f'    <rect x="{cur_x:.1f}" y="{bar_y}" width="{sw:.1f}" height="19" '
            f'fill="{col}" stroke="#ffffff" stroke-width="0.8"/>'
        )
        if lbl and sw > 28:
            out.append(
                f'    <text x="{cur_x + sw / 2:.1f}" y="{bar_y + 13}" text-anchor="middle" '
                f'font-size="8.4" font-weight="700" fill="#ffffff">{lbl}</text>'
            )
        cur_x += sw
    out.append(
        f'    <text x="{rx + 24}" y="{by + 58}" font-size="9.2" fill="#334155">'
        f"• 3-cl = {lens.get(3, 0):,}  =  2,916 root 3-XOR clauses + "
        '<tspan font-weight="700" fill="#b91c1c">27 no-type3 clauses</tspan></text>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{by + 73}" font-size="9.2" fill="#475569">'
        f"• 4-cl = {lens.get(4, 0):,} direct 3-ANDs · 2-cl = {lens.get(2, 0):,} (= 3×16,767)</text>"
    )

    # Bottom 4-format pill card
    fy = by + 92
    out.append(
        f'    <rect x="{rx + 14}" y="{fy}" width="{rw - 28}" height="52" rx="7" '
        'fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 18}" font-size="10.2" font-weight="700" fill="#6d28d9">'
        "4-Format Corpus Footprint (933.7 KB total; 0/6 solvers solved in 10 s):</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 34}" font-size="9.2" fill="#334155">'
        "CNF: 21,033v / 186,651c · AIG: 496,907 ANDs · XCNF: 4,374 XORs</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 46}" font-size="9.2" fill="#475569">'
        "ANF: 37,800 vars / 88,236 deg-≤3 equations (100% lossless conversions)</text>"
    )

    out.append("  </g>")
    out.append("</svg>\n")
    return "\n".join(out)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cnf_path = root / "cnf-orig" / "MM-23-63-no-type3.cnf.xz"
    nv, nc, lens, no_type3 = audit_cnf(cnf_path)
    svg = build_svg(nv, nc, lens, no_type3)
    out_svg = root / "diagram.svg"
    out_svg.write_text(svg, encoding="utf-8")
    ET.parse(out_svg)
    print(f"Wrote and validated {out_svg} ({out_svg.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
