#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram (`diagram.svg`) for
`heule-matrix-challenge2` (R = 23 conjectured-UNSAT skewed type-3 partitions).

Decodes all 10 `cnf-orig/*.cnf.xz` instances to extract exact unit-pinned
type-3 multiplicities across the 23 rank-1 products, contrasting Challenge 2's
skewed over-packed partitions (`2-2-3`, `2-4`, `3-3`, `5`) against balanced
satisfiable partitions and highlighting induced cross-term congestion.
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


def decode_instance(cnf_xz: Path) -> tuple[str, int, list[int], int]:
    """Return (stem, n_units, per_step_t3[23], max_step_terms)."""
    by_step: dict[int, list[str]] = collections.defaultdict(list)
    n_units = 0
    with lzma.open(cnf_xz, "rt", encoding="ascii", errors="ignore") as f:
        for line in f:
            if not line or line[0] in ("c", "p"):
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
    max_vars = 0
    for s in range(23):
        terms = by_step.get(s, [])
        max_vars = max(max_vars, len(terms))
        aa = [t for t in terms if t[0] == "a"]
        bb = [t for t in terms if t[0] == "b"]
        cc = [t for t in terms if t[0] == "c"]
        t3 = sum(
            1
            for a in aa
            for b in bb
            for c in cc
            if a[2] == b[1] and b[2] == c[1] and c[2] == a[1]
        )
        counts.append(t3)
    return cnf_xz.name.removesuffix(".cnf.xz"), n_units, counts, max_vars


def build_svg(records: list[tuple[str, int, list[int], int]]) -> str:
    by_name = {r[0]: r for r in records}
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Heule 3x3 Matrix Multiplication Challenge 2: R=23 conjectured UNSAT skewed type-3 partitions">',
        "  <defs>",
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#b91c1c"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT}">',
    ]

    # Header
    out.append(
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Heule 3×3 Matrix Multiplication — Challenge 2 (Conjectured-UNSAT Skewed Partitions)"
        "</text>"
    )
    out.append(
        '    <text x="26" y="53" font-size="11.5" fill="#475569">'
        "10 R = 23 Brent-equation refutation targets forcing the 27 type-3 monomials "
        "into over-packed skewed clusters (2-2-3, 2-4, 3-3, 5)"
        "</text>"
    )
    out.append(
        '    <rect x="742" y="18" width="154" height="26" rx="13" '
        'fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>'
    )
    out.append(
        '    <text x="819" y="35" text-anchor="middle" font-size="10.8" '
        'font-weight="700" fill="#b91c1c">EXPECTED UNSAT (OPEN)</text>'
    )
    out.append(
        '    <line x1="22" y1="64" x2="898" y2="64" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # ================= LEFT PANEL: PIGEONHOLE PACKING BOTTLENECK =================
    lx, ly, lw, lh = 22, 76, 424, 384
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="28" rx="9" fill="#dc2626"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly + 16}" width="{lw}" height="12" fill="#dc2626"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "1. Pigeonhole Excess (27 Type-3 Terms in 23 Products)</text>"
    )

    # Top box: 27 -> 23 pigeonhole rule
    p1y = ly + 40
    out.append(
        f'    <rect x="{lx + 14}" y="{p1y}" width="{lw - 28}" height="74" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{p1y + 18}" font-size="11" font-weight="700" fill="#0f172a">'
        "Tensor T₃,₃,₃ over 𝔽₂:  27 nonzero triples aᵢⱼbⱼₖcₖᵢ (δ = 1)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{p1y + 35}" font-size="10.1" fill="#334155">'
        "Each of 27 triples must appear an odd number of times across R = 23</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{p1y + 50}" font-size="10.1" fill="#334155">'
        "rank-1 layers u⁽ℓ⁾ ⊗ v⁽ℓ⁾ ⊗ w⁽ℓ⁾ ⇒ excess of "
        '<tspan font-weight="700" fill="#b91c1c">27 − 23 = 4</tspan> shared slots.</text>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{p1y + 65}" font-size="9.6" fill="#64748b">'
        "702 remaining δ = 0 Brent sums must all cancel to 0 mod 2.</text>"
    )

    # Contrast box: Balanced (SAT) vs Skewed (Expected UNSAT)
    c_y = p1y + 84
    out.append(
        f'    <rect x="{lx + 14}" y="{c_y}" width="{lw - 28}" height="122" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{c_y + 18}" font-size="10.8" font-weight="700" fill="#0f172a">'
        "Balanced Packing (Challenge 1 SAT) vs Skewed Packing (Challenge 2):</text>"
    )
    # Row A: Balanced 2-2-2-2
    out.append(
        f'    <rect x="{lx + 24}" y="{c_y + 27}" width="376" height="38" rx="5" '
        'fill="#ecfdf5" stroke="#059669" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 34}" y="{c_y + 43}" font-size="10.3" font-weight="700" fill="#047857">'
        "Challenge 1 (SAT): 2-2-2-2  →  4 pairs + 19 singletons</text>"
    )
    out.append(
        f'    <text x="{lx + 34}" y="{c_y + 58}" font-size="9.4" fill="#334155">'
        "Excess +4 spread over 4 products (low cross-term load; 17,000+ SAT schemes)</text>"
    )
    # Row B: Skewed 2-2-3 / 2-4 / 3-3 / 5
    out.append(
        f'    <rect x="{lx + 24}" y="{c_y + 73}" width="376" height="40" rx="5" '
        'fill="#fef2f2" stroke="#dc2626" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{lx + 34}" y="{c_y + 89}" font-size="10.3" font-weight="700" fill="#b91c1c">'
        "Challenge 2 (Target UNSAT): 2-2-3 · 2-4 · 3-3 · 5</text>"
    )
    out.append(
        f'    <text x="{lx + 34}" y="{c_y + 105}" font-size="9.4" fill="#334155">'
        "Excess +4 crammed into only 1–3 products ⇒ 20–22 rigid singletons!</text>"
    )

    # Bottom left callout: Concrete cross-term explosion in MM-23-5-A step 9
    ey = c_y + 132
    out.append(
        f'    <rect x="{lx + 14}" y="{ey}" width="{lw - 28}" height="122" rx="7" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 18}" font-size="10.6" font-weight="700" fill="#b45309">'
        "Cross-Term Explosion in MM-23-5-A (Pinned Product M₁₀):</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 35}" font-family="{MONO}" font-size="9.2" fill="#1e293b">'
        "A⁽¹⁰⁾ ⊇ {a₁₂,a₂₁,a₂₃,a₃₂,a₃₃}  (5 bits forced = 1)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 49}" font-family="{MONO}" font-size="9.2" fill="#1e293b">'
        "B⁽¹⁰⁾ ⊇ {b₁₃,b₂₁,b₂₂,b₃₁,b₃₂}  (5 bits forced = 1)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 63}" font-family="{MONO}" font-size="9.2" fill="#1e293b">'
        "C⁽¹⁰⁾ ⊇ {c₁₂,c₁₃,c₂₁,c₂₃,c₃₂}  (5 bits forced = 1)</text>"
    )
    out.append(
        f'    <line x1="{lx + 24}" y1="{ey + 72}" x2="{lx + lw - 24}" y2="{ey + 72}" '
        'stroke="#fcd34d" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 88}" font-size="9.8" font-weight="700" fill="#b91c1c">'
        "5 × 5 × 5 = 125 forced outer-product monomials in M₁₀ alone!</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 104}" font-size="9.5" fill="#475569">'
        "Induces 7 type-3 triples + 118 δ = 0 terms that remaining 22 singletons</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{ey + 116}" font-size="9.5" fill="#475569">'
        "must cancel mod 2 — believed impossible, yet hard for CDCL to refute.</text>"
    )

    # ================= RIGHT PANEL: ALL 10 DECODED SKEWED PARTITIONS =================
    rx, ry, rw, rh = 460, 76, 438, 384
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="28" rx="9" fill="#b91c1c"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry + 16}" width="{rw}" height="12" fill="#b91c1c"/>'
    )
    out.append(
        f'    <text x="{rx + rw / 2:.1f}" y="{ry + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "2. Decoded 23-Slot Packing Profiles (All 10 Targets)</text>"
    )

    # Visual 23-slot rows for 4 representative families (sorted descending so cluster stands out)
    reps = [
        ("MM-23-2-2-3-A", "20 single + 2-2-3 (3 clusters)"),
        ("MM-23-2-4-A", "21 single + 2-4 (2 clusters)"),
        ("MM-23-3-3-A", "21 single + 3-3 (2 clusters)"),
        ("MM-23-5-A", "22 single + 5 (1 dense cluster)"),
    ]
    def slot_style(t3: int) -> tuple[str, str, str]:
        if t3 == 1:
            return "#e2e8f0", "#94a3b8", "#475569"
        if t3 == 2:
            return "#dbeafe", "#2563eb", "#1d4ed8"
        if t3 == 3:
            return "#ede9fe", "#7c3aed", "#6d28d9"
        if t3 <= 5:
            return "#fef3c7", "#d97706", "#b45309"
        return "#fee2e2", "#dc2626", "#b91c1c"

    sy = ry + 41
    sw = 17.8
    for name, desc in reps:
        _, _, counts, _ = by_name[name]
        ordered = sorted(counts, reverse=True)
        out.append(
            f'    <text x="{rx + 14}" y="{sy}" font-size="10.2" font-weight="700" '
            f'fill="#0f172a">{esc(name)}</text>'
        )
        out.append(
            f'    <text x="{rx + rw - 14}" y="{sy}" text-anchor="end" '
            f'font-size="9.3" fill="#475569">{esc(desc)}</text>'
        )
        sx0 = rx + 14
        for idx, t3 in enumerate(ordered):
            bx = sx0 + idx * sw
            bg, bd, fg = slot_style(t3)
            out.append(
                f'    <rect x="{bx:.1f}" y="{sy + 5}" width="{sw - 2:.1f}" height="17" '
                f'rx="3" fill="{bg}" stroke="{bd}" stroke-width="0.9"/>'
            )
            out.append(
                f'    <text x="{bx + (sw - 2) / 2:.1f}" y="{sy + 16.5}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="9" '
                f'font-weight="700" fill="{fg}">{t3}</text>'
            )
        sy += 36

    # All-10 summary table
    tby = sy + 6
    out.append(
        f'    <rect x="{rx + 14}" y="{tby}" width="{rw - 28}" height="122" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{tby + 17}" font-size="10.3" font-weight="700" fill="#0f172a">'
        "All 10 Challenge-2 Instances (Sorted Induced Type-3 Multiplicity):</text>"
    )
    for idx, (stem, n_units, counts, _) in enumerate(records):
        col = idx // 5
        row = idx % 5
        tx = rx + 24 + col * 204
        ry_row = tby + 34 + row * 17
        big = [c for c in sorted(counts, reverse=True) if c > 1]
        n1 = counts.count(1)
        sig = "+".join(str(x) for x in big)
        out.append(
            f'    <text x="{tx}" y="{ry_row}" font-family="{MONO}" font-size="9.3" '
            f'font-weight="600" fill="#1e293b">{esc(stem)}</text>'
        )
        out.append(
            f'    <text x="{tx + 194}" y="{ry_row}" text-anchor="end" '
            f'font-size="9.1" fill="#b91c1c">{n1}×1 | [{sig}] ({n_units}u)</text>'
        )

    # Bottom CNF summary strip
    ay = tby + 130
    out.append(
        f'    <rect x="{rx + 14}" y="{ay}" width="{rw - 28}" height="52" rx="7" '
        'fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{ay + 18}" font-size="10.4" font-weight="700" fill="#b91c1c">'
        "Identical Plain Base CNF (26,541 vars · 117,203–117,207 clauses · 8,019 XORs)</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{ay + 34}" font-size="9.4" fill="#334155">'
        "Differs from Challenge 1 ONLY in the 77–81 unit pins!  α = 4.42 · ρ_crit = 1.82× · κ = 0.95</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{ay + 46}" font-size="9.3" fill="#64748b">'
        "All 6 benchmarked solvers (CaDiCaL, Kissat, CMS CNF/XCNF, Frobenius, dense) &gt;10 s</text>"
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
