#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram (`diagram.svg`) for
`heule-matrix-challenge1` (R = 23 SAT schemes with hardcoded type-3 pairings).

Decodes the real unit-clause type-3 pairings directly from `cnf-orig/*.cnf.xz`
and renders a publication-grade light-card SVG illustrating:
  1. The 3x3 matrix multiplication tensor T_{3,3,3} over F_2 (A * B = C) and its
     729 Brent parity equations over R = 23 rank-1 outer products.
  2. The decoded type-3 partition signatures across all 10 satisfiable instances
     (with 23-slot visual strips for `MM-23-2-2-2-2-3` and `MM-23-4-4-4-4-1`)
     plus the plain 2-AND + 4-XOR CNF variable/clause architecture.
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


def decode_instance(cnf_xz: Path) -> tuple[str, int, int, list[int], int]:
    """Return (stem, n_vars, n_clauses, per_step_t3_counts[23], n_units)."""
    by_step: dict[int, list[str]] = collections.defaultdict(list)
    n_vars = 0
    n_clauses = 0
    n_units = 0
    with lzma.open(cnf_xz, "rt", encoding="ascii", errors="ignore") as f:
        for line in f:
            if not line or line[0] == "c":
                continue
            if line[0] == "p":
                parts = line.split()
                n_vars, n_clauses = int(parts[2]), int(parts[3])
                continue
            parts = line.split()
            if len(parts) == 2 and parts[1] == "0":
                lit = int(parts[0])
                n_units += 1
                if 1 <= lit <= 23 * 27:
                    step = (lit - 1) // 27
                    off = (lit - 1) % 27
                    mat = "abc"[off // 9]
                    idx = off % 9
                    by_step[step].append(f"{mat}{idx // 3 + 1}{idx % 3 + 1}")
    counts: list[int] = []
    for s in range(23):
        terms = by_step.get(s, [])
        aa = [t for t in terms if t[0] == "a"]
        bb = [t for t in terms if t[0] == "b"]
        cc = [t for t in terms if t[0] == "c"]
        t3 = 0
        for a in aa:
            for b in bb:
                for c in cc:
                    if a[2] == b[1] and b[2] == c[1] and c[2] == a[1]:
                        t3 += 1
        counts.append(t3)
    stem = cnf_xz.name.removesuffix(".cnf.xz")
    return stem, n_vars, n_clauses, counts, n_units


def draw_mini_3x3(
    out: list[str],
    x: float,
    y: float,
    cell: float,
    title: str,
    title_col: str,
    prefix: str,
    hi_cells: dict[tuple[int, int], tuple[str, str]],
) -> float:
    """Draw a clean 3x3 matrix with bracketed grid; return total width."""
    gw = 3 * cell
    out.append(
        f'  <text x="{x + gw / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle" '
        f'font-size="11" font-weight="700" fill="{title_col}">{esc(title)}</text>'
    )
    out.append(
        f'  <rect x="{x:.1f}" y="{y:.1f}" width="{gw:.1f}" height="{gw:.1f}" '
        f'rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.1"/>'
    )
    for r in range(3):
        for c in range(3):
            cx = x + c * cell
            cy = y + r * cell
            bg, fg = hi_cells.get((r, c), ("#f8fafc", "#64748b"))
            sw = "1.2" if (r, c) in hi_cells else "0.6"
            sc = fg if (r, c) in hi_cells else "#e2e8f0"
            out.append(
                f'  <rect x="{cx + 1.5:.1f}" y="{cy + 1.5:.1f}" '
                f'width="{cell - 3:.1f}" height="{cell - 3:.1f}" rx="3" '
                f'fill="{bg}" stroke="{sc}" stroke-width="{sw}"/>'
            )
            lbl = f"{prefix}{r + 1}{c + 1}"
            fw = "700" if (r, c) in hi_cells else "500"
            out.append(
                f'  <text x="{cx + cell / 2:.1f}" y="{cy + cell / 2 + 3.5:.1f}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="9.5" '
                f'font-weight="{fw}" fill="{fg}">{lbl}</text>'
            )
    return gw


def build_svg(records: list[tuple[str, int, int, list[int], int]]) -> str:
    by_name = {r[0]: r for r in records}
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Heule 3x3 Matrix Multiplication Challenge 1: R=23 SAT schemes with type-3 pairings">',
        "  <defs>",
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        "  </defs>",
        # Explicit white light-card canvas for GitHub light & dark modes
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT}">',
    ]

    # Header banner
    out.append(
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Heule 3×3 Matrix Multiplication — Challenge 1 (R = 23 SAT Type-3 Pairings)"
        "</text>"
    )
    out.append(
        '    <text x="26" y="53" font-size="11.5" fill="#475569">'
        "10 satisfiable 𝔽₂ Brent-equation instances with hardcoded type-3 monomial pairings "
        "and zero streamlining constraints (hard for complete CDCL)"
        "</text>"
    )
    # Top-right status pill
    out.append(
        '    <rect x="752" y="18" width="144" height="26" rx="13" '
        'fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>'
    )
    out.append(
        '    <text x="824" y="35" text-anchor="middle" font-size="11" '
        'font-weight="700" fill="#047857">10 / 10 KNOWN SAT</text>'
    )
    out.append(
        '    <line x1="22" y1="64" x2="898" y2="64" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # ================= LEFT PANEL: TENSOR + BRENT EQUATIONS =================
    lx, ly, lw, lh = 22, 76, 424, 384
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="28" rx="9" fill="#2563eb"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly + 16}" width="{lw}" height="12" fill="#2563eb"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "1. 3×3 Tensor T₃,₃,₃ &amp; 729 Brent Equations over 𝔽₂</text>"
    )

    # Three 3x3 matrices highlighting TWO paired type-3 triples from step 20 of MM-23-2-2-2-2-3:
    # (a11, b11, c11) in blue and (a33, b33, c33) in emerald!
    my = ly + 52
    cell = 29.0
    hi_a = {(0, 0): ("#eff6ff", "#1d4ed8"), (2, 2): ("#ecfdf5", "#047857")}
    hi_b = {(0, 0): ("#eff6ff", "#1d4ed8"), (2, 2): ("#ecfdf5", "#047857")}
    hi_c = {(0, 0): ("#eff6ff", "#1d4ed8"), (2, 2): ("#ecfdf5", "#047857")}
    w_m = draw_mini_3x3(out, lx + 22, my, cell, "Factor A⁽ℓ⁾", "#1d4ed8", "a", hi_a)
    out.append(
        f'    <text x="{lx + 22 + w_m + 18:.1f}" y="{my + w_m / 2 + 5:.1f}" '
        'text-anchor="middle" font-size="16" font-weight="700" fill="#475569">⊗</text>'
    )
    draw_mini_3x3(out, lx + 22 + w_m + 36, my, cell, "Factor B⁽ℓ⁾", "#047857", "b", hi_b)
    out.append(
        f'    <text x="{lx + 22 + 2 * w_m + 54:.1f}" y="{my + w_m / 2 + 5:.1f}" '
        'text-anchor="middle" font-size="16" font-weight="700" fill="#475569">⊗</text>'
    )
    draw_mini_3x3(out, lx + 22 + 2 * w_m + 72, my, cell, "Factor C⁽ℓ⁾", "#6d28d9", "c", hi_c)

    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{my + w_m + 18:.1f}" text-anchor="middle" '
        'font-size="10.2" fill="#334155">'
        "Example paired product M₂₁ (MM-23-2-2-2-2-3): pins "
        '<tspan font-weight="700" fill="#1d4ed8">a₁₁b₁₁c₁₁</tspan>'
        " &amp; "
        '<tspan font-weight="700" fill="#047857">a₃₃b₃₃c₃₃</tspan></text>'
    )

    # Rank-1 outer-product layer stack schematic
    sy = my + w_m + 30
    out.append(
        f'    <rect x="{lx + 14}" y="{sy:.1f}" width="{lw - 28}" height="82" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{sy + 17:.1f}" text-anchor="middle" '
        'font-size="10.8" font-weight="700" fill="#0f172a">'
        "Rank-23 Tensor Decomposition:  T₃,₃,₃ = ∑ u⁽ℓ⁾ ⊗ v⁽ℓ⁾ ⊗ w⁽ℓ⁾  (ℓ = 1…23)</text>"
    )
    # Stacked rank-1 mini cards
    card_labels = [
        ("M₁", "#eff6ff", "#2563eb", "1 t3"),
        ("M₂", "#eff6ff", "#2563eb", "1 t3"),
        ("…", "#f8fafc", "#94a3b8", "18×"),
        ("M₆", "#ecfdf5", "#059669", "2 t3"),
        ("M₁₇", "#f5f3ff", "#7c3aed", "3 t3"),
        ("M₂₃", "#eff6ff", "#2563eb", "1 t3"),
    ]
    cx0 = lx + 26
    for idx, (lbl, bg, bd, sub) in enumerate(card_labels):
        bx = cx0 + idx * 62
        out.append(
            f'    <rect x="{bx}" y="{sy + 26:.1f}" width="54" height="44" rx="5" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1.1"/>'
        )
        out.append(
            f'    <text x="{bx + 27}" y="{sy + 44:.1f}" text-anchor="middle" '
            f'font-size="11" font-weight="700" fill="#0f172a">{lbl}</text>'
        )
        out.append(
            f'    <text x="{bx + 27}" y="{sy + 60:.1f}" text-anchor="middle" '
            f'font-size="9.2" font-weight="600" fill="{bd}">{sub}</text>'
        )

    # Brent equations card
    by = sy + 94
    out.append(
        f'    <rect x="{lx + 14}" y="{by:.1f}" width="{lw - 28}" height="108" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 26}" y="{by + 19:.1f}" font-size="11" font-weight="700" fill="#0f172a">'
        "729 Brent Parity Equations (9 × 9 × 9 over 𝔽₂):</text>"
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{by + 40:.1f}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="9.6" font-weight="700" fill="#1d4ed8">'
        "⨁ (a⁽ℓ⁾ᵢⱼ ∧ b⁽ℓ⁾ₖₘ ∧ c⁽ℓ⁾ₚₙ)  ≡  δ(j=k, m=p, n=i)  [ℓ=1..23]</text>"
    )
    # Split badges: 27 type-3 vs 702 cancel
    out.append(
        f'    <rect x="{lx + 24}" y="{by + 51:.1f}" width="182" height="46" rx="5" '
        'fill="#ecfdf5" stroke="#059669" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 115}" y="{by + 68:.1f}" text-anchor="middle" '
        'font-size="10.5" font-weight="700" fill="#047857">27 Type-3 Terms (δ = 1)</text>'
    )
    out.append(
        f'    <text x="{lx + 115}" y="{by + 84:.1f}" text-anchor="middle" '
        'font-size="9.4" fill="#334155">aᵢⱼbⱼₖcₖᵢ — odd parity (≥1 hit)</text>'
    )
    out.append(
        f'    <rect x="{lx + 216}" y="{by + 51:.1f}" width="182" height="46" rx="5" '
        'fill="#f8fafc" stroke="#94a3b8" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 307}" y="{by + 68:.1f}" text-anchor="middle" '
        'font-size="10.5" font-weight="700" fill="#334155">702 Cross Terms (δ = 0)</text>'
    )
    out.append(
        f'    <text x="{lx + 307}" y="{by + 84:.1f}" text-anchor="middle" '
        'font-size="9.4" fill="#475569">Non-trace triples cancel mod 2</text>'
    )

    # ================= RIGHT PANEL: DECODED CHALLENGE 1 PAIRINGS =================
    rx, ry, rw, rh = 460, 76, 438, 384
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="28" rx="9" fill="#059669"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry + 16}" width="{rw}" height="12" fill="#059669"/>'
    )
    out.append(
        f'    <text x="{rx + rw / 2:.1f}" y="{ry + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "2. Hardcoded Type-3 Pairings Across 10 SAT Instances</text>"
    )

    # Visual 23-slot strips for two contrasting decoded Challenge-1 instances
    strip_specs = [
        ("MM-23-2-2-2-2-3", "4 pairs + 1 triple + 18 singletons  (85 unit pins)"),
        ("MM-23-4-4-4-4-1", "4 quadruples + 19 singletons  (93 unit pins)"),
    ]
    color_map = {
        1: ("#e2e8f0", "#475569", "#334155"),
        2: ("#dbeafe", "#2563eb", "#1d4ed8"),
        3: ("#ede9fe", "#7c3aed", "#6d28d9"),
        4: ("#fef3c7", "#d97706", "#b45309"),
    }
    ty = ry + 42
    for name, subtitle in strip_specs:
        _, _, _, counts, _ = by_name[name]
        out.append(
            f'    <text x="{rx + 14}" y="{ty}" font-size="10.5" font-weight="700" '
            f'fill="#0f172a">{esc(name)}</text>'
        )
        out.append(
            f'    <text x="{rx + rw - 14}" y="{ty}" text-anchor="end" '
            f'font-size="9.6" fill="#475569">{esc(subtitle)}</text>'
        )
        sw = 17.8
        sx0 = rx + 14
        for idx, t3 in enumerate(counts):
            bx = sx0 + idx * sw
            bg, bd, fg = color_map.get(t3, ("#fee2e2", "#dc2626", "#b91c1c"))
            out.append(
                f'    <rect x="{bx:.1f}" y="{ty + 6}" width="{sw - 2:.1f}" height="20" '
                f'rx="3" fill="{bg}" stroke="{bd}" stroke-width="0.9"/>'
            )
            out.append(
                f'    <text x="{bx + (sw - 2) / 2:.1f}" y="{ty + 19.5}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="9.5" '
                f'font-weight="700" fill="{fg}">{t3}</text>'
            )
        ty += 42

    # Legend for 23-slot counts
    out.append(
        f'    <text x="{rx + 14}" y="{ty + 2}" font-size="9.4" fill="#64748b">'
        "23 rank-1 slots M₁…M₂₃ colored by pinned type-3 multiplicity:  "
        '<tspan font-weight="700" fill="#475569">1</tspan> single  ·  '
        '<tspan font-weight="700" fill="#1d4ed8">2</tspan> pair  ·  '
        '<tspan font-weight="700" fill="#6d28d9">3</tspan> triple  ·  '
        '<tspan font-weight="700" fill="#b45309">4</tspan> quad</text>'
    )

    # Compact 10-instance table (2 columns x 5 rows) inside white card
    tby = ty + 14
    out.append(
        f'    <rect x="{rx + 14}" y="{tby}" width="{rw - 28}" height="128" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{tby + 17}" font-size="10.5" font-weight="700" fill="#0f172a">'
        "All 10 Challenge-1 Instances (Decoded from cnf-orig/*.cnf.xz):</text>"
    )
    for idx, (stem, nv, nc, counts, n_units) in enumerate(records):
        col = idx // 5
        row = idx % 5
        tx = rx + 24 + col * 204
        ry_row = tby + 35 + row * 18
        tot_t3 = sum(counts)
        out.append(
            f'    <text x="{tx}" y="{ry_row}" font-family="{MONO}" font-size="9.3" '
            f'font-weight="600" fill="#1e293b">{esc(stem)}</text>'
        )
        out.append(
            f'    <text x="{tx + 194}" y="{ry_row}" text-anchor="end" '
            f'font-size="9.2" fill="#047857">{n_units} pins · {tot_t3} t3</text>'
        )

    # Bottom CNF Architecture summary card (Right panel)
    ay = tby + 138
    out.append(
        f'    <rect x="{rx + 14}" y="{ay}" width="{rw - 28}" height="82" rx="7" '
        'fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{ay + 18}" font-size="10.8" font-weight="700" fill="#1d4ed8">'
        "Plain 2-AND + 4-XOR Encoding (26,541 vars · 117,206–117,219 clauses)</text>"
    )
    # Variable budget stacked bar inside card
    bar_x, bar_y, bar_w = rx + 24, ay + 26, rw - 48
    v_segs = [
        (621, "#2563eb", ""),
        (1863, "#7c3aed", ""),
        (16767, "#059669", "16,767 cube vars (23×729)"),
        (7290, "#d97706", "7,290 XOR aux"),
    ]
    tot_v = 26541
    cur_x = float(bar_x)
    for cnt, col, lbl in v_segs:
        seg_w = bar_w * (cnt / tot_v)
        out.append(
            f'    <rect x="{cur_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="18" '
            f'fill="{col}" stroke="#ffffff" stroke-width="0.8"/>'
        )
        if lbl:
            out.append(
                f'    <text x="{cur_x + seg_w / 2:.1f}" y="{bar_y + 12.5}" '
                f'text-anchor="middle" font-size="8.8" font-weight="700" fill="#ffffff">{lbl}</text>'
            )
        cur_x += seg_w
    out.append(
        f'    <text x="{rx + 24}" y="{ay + 59}" font-size="9.5" fill="#334155">'
        "621 A/B/C bits + 1,863 pair (a∧b) + 16,767 cube (p∧c) + 7,290 4-XOR chain aux</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{ay + 73}" font-size="9.5" fill="#475569">'
        "8,019 native XORs/file · α = 4.42 · ρ_crit = 1.82× · YalSAT solves 5 in mins; 1C CDCL &gt;10 s</text>"
    )

    out.append("  </g>")
    out.append("</svg>\n")
    return "\n".join(out)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cnf_dir = root / "cnf-orig"
    records = [decode_instance(p) for p in sorted(cnf_dir.glob("*.cnf.xz"))]
    if len(records) != 10:
        raise RuntimeError(f"Expected 10 CNF files in {cnf_dir}, found {len(records)}")
    svg = build_svg(records)
    out_svg = root / "diagram.svg"
    out_svg.write_text(svg, encoding="utf-8")
    ET.parse(out_svg)
    print(f"Wrote and validated {out_svg} ({out_svg.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
