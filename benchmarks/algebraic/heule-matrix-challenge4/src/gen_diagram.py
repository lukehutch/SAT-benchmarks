#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram (`diagram.svg`) for
`heule-matrix-challenge4` (`MM-22`: the famous open R = 22 frontier for 3x3
matrix multiplication over F_2).

Audits `cnf-orig/MM-22.cnf.xz` directly and renders a publication-grade
light-card SVG illustrating:
  1. The 3x3 matrix multiplication tensor rank scale (R = 19 lower bound through
     R = 22 open frontier, R = 23 Laderman/Heule, and R = 27 naive schoolbook)
     and the 729 Brent equations over F_2.
  2. The complete plain 2-AND + 4-XOR Brent-equation SAT circuit architecture
     (594 matrix bits -> 1,782 pairs -> 16,038 cubes -> 7,290 4-XOR blocks).
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
    n_vars = 0
    n_clauses = 0
    lens: collections.Counter[int] = collections.Counter()
    with lzma.open(cnf_xz, "rt", encoding="ascii", errors="ignore") as f:
        for line in f:
            if not line or line[0] == "c":
                continue
            if line[0] == "p":
                parts = line.split()
                n_vars, n_clauses = int(parts[2]), int(parts[3])
                continue
            lits = line.split()[:-1]
            lens[len(lits)] += 1
    return n_vars, n_clauses, dict(lens)


def build_svg(n_vars: int, n_clauses: int, lens: dict[int, int]) -> str:
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Heule 3x3 Matrix Multiplication Challenge 4: Open R=22 Brent equation frontier">',
        "  <defs>",
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT}">',
    ]

    # Header
    out.append(
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Heule 3×3 Matrix Multiplication — Challenge 4 (MM-22: Open R = 22 Frontier)"
        "</text>"
    )
    out.append(
        '    <text x="26" y="53" font-size="11.5" fill="#475569">'
        "Plain unstreamlined Brent-equation CNF over 𝔽₂ testing whether 3×3 matrix "
        "multiplication admits a rank-22 bilinear scheme (open since 1976)"
        "</text>"
    )
    out.append(
        '    <rect x="744" y="18" width="152" height="26" rx="13" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>'
    )
    out.append(
        '    <text x="820" y="35" text-anchor="middle" font-size="10.8" '
        'font-weight="700" fill="#b45309">OPEN FRONTIER (R = 22)</text>'
    )
    out.append(
        '    <line x1="22" y1="64" x2="898" y2="64" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # ================= LEFT PANEL: TENSOR RANK FRONTIER =================
    lx, ly, lw, lh = 22, 76, 424, 384
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="28" rx="9" fill="#0f172a"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly + 16}" width="{lw}" height="12" fill="#0f172a"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "1. Algebraic Complexity Frontier for rank(T₃,₃,₃) over 𝔽₂</text>"
    )

    # Rank scale card
    ry1 = ly + 40
    out.append(
        f'    <rect x="{lx + 14}" y="{ry1}" width="{lw - 28}" height="136" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ry1 + 19}" font-size="10.8" font-weight="700" fill="#0f172a">'
        "Number of Rank-1 Multiplications R for 3×3 Matrix Product C = A · B:</text>"
    )
    # Horizontal rank track (R = 18 .. 27)
    ranks = [
        (18, "UNSAT", "#fee2e2", "#dc2626", "#b91c1c"),
        (19, "LB", "#fef2f2", "#ef4444", "#b91c1c"),
        (20, "?", "#f1f5f9", "#94a3b8", "#64748b"),
        (21, "?", "#f1f5f9", "#94a3b8", "#64748b"),
        (22, "MM-22", "#fef3c7", "#d97706", "#b45309"),
        (23, "SAT", "#ecfdf5", "#059669", "#047857"),
        (24, "SAT", "#ecfdf5", "#10b981", "#047857"),
        (25, "SAT", "#ecfdf5", "#10b981", "#047857"),
        (26, "SAT", "#ecfdf5", "#10b981", "#047857"),
        (27, "3³", "#eff6ff", "#2563eb", "#1d4ed8"),
    ]
    rx0 = lx + 24
    rw_cell = 37.6
    for idx, (rval, tag, bg, bd, fg) in enumerate(ranks):
        bx = rx0 + idx * rw_cell
        is_target = rval == 22
        sw = "2.2" if is_target else "1.0"
        by_box = ry1 + (30 if is_target else 34)
        bh_box = 48 if is_target else 40
        out.append(
            f'    <rect x="{bx:.1f}" y="{by_box}" width="{rw_cell - 3:.1f}" height="{bh_box}" '
            f'rx="5" fill="{bg}" stroke="{bd}" stroke-width="{sw}"/>'
        )
        out.append(
            f'    <text x="{bx + (rw_cell - 3) / 2:.1f}" y="{by_box + (21 if is_target else 18)}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="{12 if is_target else 11}" '
            f'font-weight="700" fill="{fg}">{rval}</text>'
        )
        out.append(
            f'    <text x="{bx + (rw_cell - 3) / 2:.1f}" y="{by_box + (38 if is_target else 32)}" '
            f'text-anchor="middle" font-size="8.2" font-weight="700" fill="{fg}">{tag}</text>'
        )
    # Annotations under rank scale
    out.append(
        f'    <text x="{lx + 24}" y="{ry1 + 98}" font-size="9.5" fill="#b91c1c">'
        "• R ≤ 18 impossible; R ≥ 19 lower bound (Bläser 2003, all fields)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ry1 + 113}" font-size="9.5" font-weight="700" fill="#b45309">'
        "• R = 22 (MM-22): Famous open threshold — SAT breaks Laderman's 1976 record!</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ry1 + 128}" font-size="9.5" fill="#047857">'
        "• R = 23: Laderman (1976) &amp; 17,000+ schemes (Heule–Kauers–Seidl SAT 2019)</text>"
    )

    # Bilinear tensor visual card
    ty = ry1 + 146
    out.append(
        f'    <rect x="{lx + 14}" y="{ty}" width="{lw - 28}" height="108" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ty + 18}" font-size="10.8" font-weight="700" fill="#0f172a">'
        "Unconstrained Bilinear Tensor System over 𝔽₂:</text>"
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ty + 39}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="10.4" font-weight="700" fill="#1d4ed8">'
        "T₃,₃,₃ = ∑ A⁽ℓ⁾ ⊗ B⁽ℓ⁾ ⊗ C⁽ℓ⁾  (ℓ = 1…22, mod 2)</text>"
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ty + 59}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="8.9" fill="#334155">'
        "⨁ a⁽ℓ⁾ᵢⱼ b⁽ℓ⁾ₖₘ c⁽ℓ⁾ₚₙ  ≡  δ(j=k, m=p, n=i)  [729 eqs, ℓ=1..22]</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ty + 80}" font-size="9.6" fill="#475569">'
        "• 22 × 27 = 594 binary decision variables define all 22 bilinear products.</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ty + 96}" font-size="9.6" fill="#475569">'
        "• Huge symmetry group: S₂₂ layer permutations × (GL₃(𝔽₂))³ × C₃ transpose.</text>"
    )

    # Bottom left card: Why MM-22 resists both CDCL & SLS
    wy = ty + 118
    out.append(
        f'    <rect x="{lx + 14}" y="{wy}" width="{lw - 28}" height="68" rx="7" '
        'fill="#fffbeb" stroke="#fcd34d" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{wy + 18}" font-size="10.4" font-weight="700" fill="#b45309">'
        "Pure Open Benchmark (Zero Units, Zero Symmetry Breaking):</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{wy + 35}" font-size="9.4" fill="#334155">'
        "• Unlike Challenges 1–3, no type-3 terms are pinned or forbidden.</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{wy + 50}" font-size="9.4" fill="#334155">'
        "• Degree-3 non-linear ANF (60,750 eqs) coupled via 7,290 4-XOR parity chains.</text>"
    )

    # ================= RIGHT PANEL: 4-STAGE PLAIN CNF CIRCUIT =================
    rx, ry, rw, rh = 460, 76, 438, 384
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
        f"2. Plain 2-AND + 4-XOR Circuit ({n_vars:,} Vars · {n_clauses:,} Cls)</text>"
    )

    # 4 vertical pipeline stage boxes with arrows
    stages = [
        ("#eff6ff", "#2563eb", "#1d4ed8", "Stage 1 — Factor Matrix Entries (orig)",
         "594 vars (1..594)", "22 layers × (9 A + 9 B + 9 C) bits ∈ {0, 1}"),
        ("#f5f3ff", "#7c3aed", "#6d28d9", "Stage 2 — Bilinear 2-AND Pairs:  p = a ∧ b",
         "1,782 vars (22×81)", "3 cls/gate: (p∨¬a∨¬b), (¬p∨a), (¬p∨b) → 5,346 cls"),
        ("#ecfdf5", "#059669", "#047857", "Stage 3 — Trilinear 2-AND Cubes:  s = p ∧ c",
         "16,038 vars (22×729)", "3 cls/gate: (s∨¬p∨¬c), (¬s∨p), (¬s∨c) → 48,114 cls"),
        ("#fffbeb", "#d97706", "#b45309", "Stage 4 — 729 Brent 22-Term Parity Chains (4-XOR)",
         "6,561 aux (729×9)", "10 4-XORs/eq = 7,290 XORs × 8 cls = 58,320 4-clauses"),
    ]
    sy = ry + 40
    for idx, (bg, bd, tc, title, badge, desc) in enumerate(stages):
        out.append(
            f'    <rect x="{rx + 14}" y="{sy}" width="{rw - 28}" height="52" rx="6" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1.1"/>'
        )
        out.append(
            f'    <text x="{rx + 24}" y="{sy + 19}" font-size="10.6" font-weight="700" fill="{tc}">'
            f"{esc(title)}</text>"
        )
        out.append(
            f'    <text x="{rx + rw - 24}" y="{sy + 19}" text-anchor="end" '
            f'font-family="{MONO}" font-size="9.4" font-weight="700" fill="#1e293b">{esc(badge)}</text>'
        )
        out.append(
            f'    <text x="{rx + 24}" y="{sy + 38}" font-size="9.5" fill="#334155">'
            f"{esc(desc)}</text>"
        )
        if idx < 3:
            out.append(
                f'    <line x1="{rx + rw / 2:.1f}" y1="{sy + 52}" x2="{rx + rw / 2:.1f}" y2="{sy + 63}" '
                'stroke="#475569" stroke-width="1.4" marker-end="url(#arr)"/>'
            )
        sy += 65

    # Exact Clause Budget Bar + Structural Summary
    fy = sy + 2
    out.append(
        f'    <rect x="{rx + 14}" y="{fy}" width="{rw - 28}" height="74" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 16}" font-size="9.7" font-weight="700" fill="#0f172a">'
        f"Exact Clause Spectrum ({n_clauses:,} cls; cf. 6pooled3and-c4: 19,548 vars):</text>"
    )
    bar_x, bar_y, bar_w = rx + 24, fy + 23, rw - 48
    c_segs = [
        (lens.get(2, 0), "#2563eb", f"2-cl: {lens.get(2, 0):,} (32%)"),
        (lens.get(3, 0), "#7c3aed", f"3-cl: {lens.get(3, 0):,}"),
        (lens.get(4, 0), "#d97706", f"4-cl (4-XORs): {lens.get(4, 0):,} (52%)"),
    ]
    cur_x = float(bar_x)
    for cnt, col, lbl in c_segs:
        seg_w = bar_w * (cnt / n_clauses)
        out.append(
            f'    <rect x="{cur_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="19" '
            f'fill="{col}" stroke="#ffffff" stroke-width="0.9"/>'
        )
        out.append(
            f'    <text x="{cur_x + seg_w / 2:.1f}" y="{bar_y + 13}" text-anchor="middle" '
            f'font-size="8.6" font-weight="700" fill="#ffffff">{lbl}</text>'
        )
        cur_x += seg_w
    out.append(
        f'    <text x="{rx + 24}" y="{fy + 58}" font-size="9.4" fill="#475569">'
        "α = 4.48 · ρ_crit = 1.83× (Over) · κ = 0.95 · k̄ = 3.20 · 74% Horn · 299,699 AIG ANDs</text>"
    )

    out.append("  </g>")
    out.append("</svg>\n")
    return "\n".join(out)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cnf_path = root / "cnf-orig" / "MM-22.cnf.xz"
    n_vars, n_clauses, lens = audit_cnf(cnf_path)
    svg = build_svg(n_vars, n_clauses, lens)
    out_svg = root / "diagram.svg"
    out_svg.write_text(svg, encoding="utf-8")
    ET.parse(out_svg)
    print(f"Wrote and validated {out_svg} ({out_svg.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
