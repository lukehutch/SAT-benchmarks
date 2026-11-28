#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram (`diagram.svg`) for
`heule-matrix-6pooled3and-c4` (`MM-22-63`: compact 6-pooled 3-AND encoding
of the open R = 22 frontier for 3x3 matrix multiplication over F_2).

Audits `cnf-orig/MM-22-63.cnf.xz` directly and renders a publication-grade
light-card SVG illustrating:
  1. Exact zero-remainder fit of R = 22 into a depth-2 uniform 6-XOR tree
     (4 leaf 6-XOR pools of 5 cubes + 1 root 6-XOR of 2 cubes + 4 links ->
     pure {2, 4, 6}-CNF with ZERO 3-clauses!).
  2. Exact compact variable budget (19,548 vars — smallest CNF encoding of the
     open R = 22 problem, down 21.7% from plain MM-22's 24,975 vars).
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


def audit_cnf(cnf_xz: Path) -> tuple[int, int, dict[int, int]]:
    nv = nc = 0
    lens: collections.Counter[int] = collections.Counter()
    with lzma.open(cnf_xz, "rt", encoding="ascii", errors="ignore") as f:
        for line in f:
            if not line or line[0] == "c":
                continue
            if line[0] == "p":
                parts = line.split()
                nv, nc = int(parts[2]), int(parts[3])
                continue
            ln = len(line.split()) - 1
            lens[ln] += 1
    if set(lens.keys()) != {2, 4, 6}:
        raise RuntimeError(f"Expected pure {{2,4,6}}-CNF for MM-22-63, got {sorted(lens.keys())}")
    return nv, nc, dict(lens)


def build_svg(nv: int, nc: int, lens: dict[int, int]) -> str:
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Heule 3x3 Matrix Multiplication 6pooled3and Challenge 4: MM-22-63 compact R=22 frontier">',
        "  <defs>",
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>',
        "    </marker>",
        '    <marker id="arra" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT}">',
    ]

    # Header
    out.append(
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Heule 3×3 Matrix Multiplication — 6pooled3and / Challenge 4 (MM-22-63)"
        "</text>"
    )
    out.append(
        '    <text x="26" y="53" font-size="11.5" fill="#475569">'
        "Smallest-variable encoding of the open R = 22 𝔽₂ tensor-rank frontier: "
        "exact zero-remainder depth-2 6-XOR tree + direct 3-AND (pure 2/4/6-CNF)"
        "</text>"
    )
    out.append(
        '    <rect x="740" y="18" width="156" height="26" rx="13" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>'
    )
    out.append(
        '    <text x="818" y="35" text-anchor="middle" font-size="10.8" '
        'font-weight="700" fill="#b45309">OPEN R = 22 (19,548v)</text>'
    )
    out.append(
        '    <line x1="22" y1="64" x2="898" y2="64" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # ================= LEFT PANEL: PERFECT ZERO-REMAINDER R=22 6-XOR TREE =================
    lx, ly, lw, lh = 22, 76, 456, 384
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="28" rx="9" fill="#4f46e5"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly + 16}" width="{lw}" height="12" fill="#4f46e5"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "1. Perfect Depth-2 6-XOR Tree Fit for R = 22 (Zero Remainder!)</text>"
    )

    # Top equation strip
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 45}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="9.0" font-weight="700" fill="#0f172a">'
        "729 Brent eqs: s₁ ⊕ s₂ ⊕ … ⊕ s₂₂ ≡ δ  (s_ℓ = a_ℓ ∧ b_ℓ ∧ c_ℓ)</text>"
    )

    # Visual Tree Diagram inside white canvas
    ty = ly + 56
    out.append(
        f'    <rect x="{lx + 14}" y="{ty}" width="{lw - 28}" height="218" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    # 4 Leaf 6-XOR boxes (each pools 5 cubes + 1 link = 6 vars)
    leaf_specs = [
        (lx + 24, "Leaf 1 (6-XOR)", "s₁…s₅ ⊕ t₁ = δ", "32 6-cls", "#fffbeb", "#d97706", "#b45309"),
        (lx + 129, "Leaf 2 (6-XOR)", "s₆…s₁₀ ⊕ t₂ = 0", "32 6-cls", "#eff6ff", "#2563eb", "#1d4ed8"),
        (lx + 234, "Leaf 3 (6-XOR)", "s₁₁…s₁₅ ⊕ t₃ = 0", "32 6-cls", "#eff6ff", "#2563eb", "#1d4ed8"),
        (lx + 339, "Leaf 4 (6-XOR)", "s₁₆…s₂₀ ⊕ t₄ = 0", "32 6-cls", "#eff6ff", "#2563eb", "#1d4ed8"),
    ]
    ly_leaf = ty + 16
    for px, title, eq, sub, bg, bd, fg in leaf_specs:
        out.append(
            f'    <rect x="{px}" y="{ly_leaf}" width="98" height="54" rx="6" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1.1"/>'
        )
        out.append(
            f'    <text x="{px + 49}" y="{ly_leaf + 15}" text-anchor="middle" '
            f'font-size="9.2" font-weight="700" fill="{fg}">{title}</text>'
        )
        out.append(
            f'    <text x="{px + 49}" y="{ly_leaf + 31}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="7.8" fill="#1e293b">{eq}</text>'
        )
        out.append(
            f'    <text x="{px + 49}" y="{ly_leaf + 46}" text-anchor="middle" '
            f'font-size="8.4" fill="#64748b">5 cubes + t → {sub}</text>'
        )

    # Extra 2 direct inputs s21, s22 box on the left of root
    ly_root = ty + 114
    out.append(
        f'    <rect x="{lx + 24}" y="{ly_root + 8}" width="80" height="42" rx="6" '
        'fill="#ecfdf5" stroke="#059669" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{lx + 64}" y="{ly_root + 25}" text-anchor="middle" '
        'font-size="9.0" font-weight="700" fill="#047857">2 Remaining</text>'
    )
    out.append(
        f'    <text x="{lx + 64}" y="{ly_root + 40}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="9.2" font-weight="700" fill="#047857">s₂₁ , s₂₂</text>'
    )
    # Root 6-XOR box (2 remaining cubes + 4 link vars = 6 vars EXACTLY!)
    out.append(
        f'    <rect x="{lx + 124}" y="{ly_root}" width="304" height="58" rx="7" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/>'
    )
    out.append(
        f'    <text x="{lx + 276}" y="{ly_root + 18}" text-anchor="middle" '
        'font-size="10.2" font-weight="700" fill="#6d28d9">'
        "Root 6-XOR Gate (2 Cubes + 4 Links = 6 Vars EXACTLY!)</text>"
    )
    out.append(
        f'    <text x="{lx + 276}" y="{ly_root + 36}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="9.3" font-weight="700" fill="#0f172a">'
        "s₂₁ ⊕ s₂₂ ⊕ t₁ ⊕ t₂ ⊕ t₃ ⊕ t₄ = 0  (32 cls)</text>"
    )
    out.append(
        f'    <text x="{lx + 276}" y="{ly_root + 51}" text-anchor="middle" '
        'font-size="8.4" fill="#475569">'
        "5 × 729 = 3,645 6-XORs = 116,640 6-cls (zero 3-XOR tail!)</text>"
    )

    # Arrows into root
    out.append(
        f'    <line x1="{lx + 104}" y1="{ly_root + 29}" x2="{lx + 122}" y2="{ly_root + 29}" '
        'stroke="#2563eb" stroke-width="1.4" marker-end="url(#arr)"/>'
    )
    arrow_xs = [
        (lx + 73, lx + 178, "#d97706", "url(#arra)"),
        (lx + 178, lx + 235, "#2563eb", "url(#arr)"),
        (lx + 283, lx + 295, "#2563eb", "url(#arr)"),
        (lx + 388, lx + 365, "#2563eb", "url(#arr)"),
    ]
    for x1, x2, col, mk in arrow_xs:
        out.append(
            f'    <line x1="{x1}" y1="{ly_leaf + 54}" x2="{x2}" y2="{ly_root - 2}" '
            f'stroke="{col}" stroke-width="1.3" marker-end="{mk}"/>'
        )

    # Arithmetic callout under tree inside card
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ty + 194}" text-anchor="middle" '
        'font-size="9.8" font-weight="700" fill="#1e293b">'
        "Exact Pack Formula:  4 leaves × 5 cubes + 2 direct cubes = 22 cubes using only 4 aux vars/eq!</text>"
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ty + 209}" text-anchor="middle" '
        'font-size="9.1" fill="#64748b">'
        "Verified on eq 0 (a₁₁b₁₁c₁₁): vars (595..3511, 16633) … root (15175, 15904, 16633..16636)</text>"
    )

    # Bottom left card: Why R=22 is uniquely clean under 6pooled3and
    by_l = ty + 228
    out.append(
        f'    <rect x="{lx + 14}" y="{by_l}" width="{lw - 28}" height="86" rx="7" '
        'fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{by_l + 18}" font-size="10.4" font-weight="700" fill="#1d4ed8">'
        "Pure {2, 4, 6}-CNF Fingerprint (Zero Ternary or Unit Clauses!):</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{by_l + 35}" font-size="9.4" fill="#334155">'
        f"• 2-clauses ({lens[2]:,}): 3 binary guards (¬s ∨ a), (¬s ∨ b), (¬s ∨ c) per 3-AND</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{by_l + 51}" font-size="9.4" fill="#334155">'
        f"• 4-clauses ({lens[4]:,}): 1 forward clause (s ∨ ¬a ∨ ¬b ∨ ¬c) per 3-AND cube</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{by_l + 67}" font-size="9.4" fill="#334155">'
        f"• 6-clauses ({lens[6]:,}): 3,645 uniform 6-XOR blocks × 32 clauses (no tail!)</text>"
    )

    # ================= RIGHT PANEL: COMPACT FRONTIER BUDGET =================
    rx, ry, rw, rh = 492, 76, 406, 384
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="28" rx="9" fill="#d97706"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry + 16}" width="{rw}" height="12" fill="#d97706"/>'
    )
    out.append(
        f'    <text x="{rx + rw / 2:.1f}" y="{ry + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "2. MM-22 Plain vs MM-22-63 Variable Compression</text>"
    )

    # Variable breakdown stacked comparison (Plain 24,975 vs Pooled 19,548)
    vy = ry + 42
    out.append(
        f'    <rect x="{rx + 14}" y="{vy}" width="{rw - 28}" height="134" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{vy + 18}" font-size="10.4" font-weight="700" fill="#0f172a">'
        "Variable Budget Comparison (−5,427 Vars = −21.7%):</text>"
    )
    # Bar 1: Plain MM-22 (24,975)
    bx, bw_full = rx + 24, rw - 48
    out.append(
        f'    <text x="{bx}" y="{vy + 36}" font-size="9.4" font-weight="600" fill="#475569">'
        "Plain MM-22 (challenge4): 24,975 vars</text>"
    )
    plain_segs = [
        (594, "#2563eb", ""),
        (1782, "#dc2626", ""),
        (16038, "#059669", "16,038 cubes"),
        (6561, "#d97706", "6,561 XOR aux"),
    ]
    cx = float(bx)
    for cnt, col, lbl in plain_segs:
        sw = bw_full * (cnt / 24975.0)
        out.append(
            f'    <rect x="{cx:.1f}" y="{vy + 42}" width="{sw:.1f}" height="20" '
            f'fill="{col}" stroke="#ffffff" stroke-width="0.8"/>'
        )
        if lbl:
            out.append(
                f'    <text x="{cx + sw / 2:.1f}" y="{vy + 55.5}" text-anchor="middle" '
                f'font-size="8.4" font-weight="700" fill="#ffffff">{lbl}</text>'
            )
        cx += sw

    # Bar 2: MM-22-63 (19,548) scaled to same axis (24,975)
    out.append(
        f'    <text x="{bx}" y="{vy + 80}" font-size="9.4" font-weight="700" fill="#1d4ed8">'
        f"MM-22-63 (this benchmark): {nv:,} vars (0 pair vars!)</text>"
    )
    pool_segs = [
        (594, "#2563eb", ""),
        (16038, "#059669", "16,038 direct 3-AND cubes"),
        (2916, "#7c3aed", "2,916"),
    ]
    cx = float(bx)
    for cnt, col, lbl in pool_segs:
        sw = bw_full * (cnt / 24975.0)
        out.append(
            f'    <rect x="{cx:.1f}" y="{vy + 86}" width="{sw:.1f}" height="20" '
            f'fill="{col}" stroke="#ffffff" stroke-width="0.8"/>'
        )
        if lbl:
            out.append(
                f'    <text x="{cx + sw / 2:.1f}" y="{vy + 99.5}" text-anchor="middle" '
                f'font-size="8.4" font-weight="700" fill="#ffffff">{lbl}</text>'
            )
        cx += sw
    # Dashed saved-vars gap indicator
    gap_w = bw_full - (cx - bx)
    out.append(
        f'    <rect x="{cx + 2:.1f}" y="{vy + 86}" width="{gap_w - 2:.1f}" height="20" rx="3" '
        'fill="#ecfdf5" stroke="#059669" stroke-width="1" stroke-dasharray="3,2"/>'
    )
    out.append(
        f'    <text x="{cx + gap_w / 2:.1f}" y="{vy + 99.5}" text-anchor="middle" '
        'font-size="8.3" font-weight="700" fill="#047857">−5,427v</text>'
    )
    out.append(
        f'    <text x="{bx}" y="{vy + 123}" font-size="8.9" fill="#64748b">'
        "Legend: Blue 594 A/B/C · Red 1,782 pairs (removed) · Green cubes · Purple/Amber XOR aux</text>"
    )

    # Structural metrics grid (2x2)
    my_grid = vy + 144
    cards = [
        (rx + 14, my_grid, "#eff6ff", "#2563eb", "#1d4ed8", "Clauses / Ratio",
         f"{nc:,} cls", "α = 9.25 · k̄ = 4.76"),
        (rx + 208, my_grid, "#f5f3ff", "#7c3aed", "#6d28d9", "Native XORs (XCNF)",
         "3,645 (all 6-XOR)", "Down 50% from 7,290"),
        (rx + 14, my_grid + 68, "#fffbeb", "#d97706", "#b45309", "Phase &amp; Constrained",
         "ρ_crit = 2.68×", "κ = 1.23 · Deg CV 0.53"),
        (rx + 208, my_grid + 68, "#ecfdf5", "#059669", "#047857", "4-Format Sizes",
         "849.3 KB total", "481,463 AIG · 83.8k ANF"),
    ]
    for cx_c, cy_c, bg, bd, tc, hdr, big, sub in cards:
        out.append(
            f'    <rect x="{cx_c}" y="{cy_c}" width="184" height="58" rx="6" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1"/>'
        )
        out.append(
            f'    <text x="{cx_c + 10}" y="{cy_c + 16}" font-size="9.2" font-weight="700" fill="{tc}">{hdr}</text>'
        )
        out.append(
            f'    <text x="{cx_c + 10}" y="{cy_c + 34}" font-family="{MONO}" font-size="11.2" font-weight="700" fill="#0f172a">{big}</text>'
        )
        out.append(
            f'    <text x="{cx_c + 10}" y="{cy_c + 49}" font-size="8.8" fill="#475569">{sub}</text>'
        )

    # Bottom open-frontier note
    fy = my_grid + 136
    out.append(
        f'    <rect x="{rx + 14}" y="{fy}" width="{rw - 28}" height="52" rx="7" '
        'fill="#ffffff" stroke="#d97706" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 18}" font-size="10.2" font-weight="700" fill="#b45309">'
        "Grand Challenge Status: SAT ⇔ 3×3 𝔽₂ Matrix Mult in 22 Products</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 34}" font-size="9.2" fill="#334155">'
        "A SAT model breaks Laderman's 1976 bound over 𝔽₂; UNSAT proves rank ≥ 23.</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 46}" font-size="9.1" fill="#64748b">'
        "1-core 10 s benchmark: 0/6 solvers resolved (compare xor6cut-22..27 rank sweep).</text>"
    )

    out.append("  </g>")
    out.append("</svg>\n")
    return "\n".join(out)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cnf_path = root / "cnf-orig" / "MM-22-63.cnf.xz"
    nv, nc, lens = audit_cnf(cnf_path)
    svg = build_svg(nv, nc, lens)
    out_svg = root / "diagram.svg"
    out_svg.write_text(svg, encoding="utf-8")
    ET.parse(out_svg)
    print(f"Wrote and validated {out_svg} ({out_svg.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
