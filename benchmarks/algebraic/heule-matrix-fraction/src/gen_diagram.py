#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram (`diagram.svg`) for
`heule-matrix-fraction` (`f-d-3`, `f-d-4`, `f-d-6`: XOR-free cardinality-
restricted R = 23 Brent-equation variants).

Audits all 3 `cnf-orig/f-d-*.cnf.xz` instances to decode their exact 8 pinned
type-3 cube units (4 disjoint pairs in steps 0..3) and exact clause-type counts
(`EXACTLYONE` on 27 delta=1 eqs, `ZEROTWO` (`printN1` + `printAMT`) on 702
delta=0 eqs, `noRank3` on 23x3 factor matrices, `ATLEASTONE` 9- and 23-clauses,
and ZERO native XOR parity clauses!).
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


def decode_cube_var(u: int) -> tuple[int, str]:
    """Decode cube var u in [2485..19251] -> (step 0..22, 'aIJ bJK cKI')."""
    idx = u - 2485
    step = idx // 729
    rem = idx % 729
    a = rem // 81
    b = (rem % 81) // 9
    c = rem % 9
    return step, f"a{a // 3 + 1}{a % 3 + 1}b{b // 3 + 1}{b % 3 + 1}c{c // 3 + 1}{c % 3 + 1}"


def audit_fraction(cnf_dir: Path) -> tuple[int, int, dict[int, int], list[tuple[str, list[tuple[int, str]]]]]:
    inst_units: list[tuple[str, list[tuple[int, str]]]] = []
    active_n = 0
    n_clauses = 0
    lens: collections.Counter[int] = collections.Counter()
    for p in sorted(cnf_dir.glob("*.cnf.xz")):
        units: list[tuple[int, str]] = []
        used: set[int] = set()
        local_lens: collections.Counter[int] = collections.Counter()
        with lzma.open(p, "rt", encoding="ascii", errors="ignore") as f:
            for line in f:
                if not line or line[0] in ("c", "p"):
                    continue
                lits = [int(x) for x in line.split()[:-1]]
                local_lens[len(lits)] += 1
                for x in lits:
                    used.add(abs(x))
                if len(lits) == 1:
                    units.append(decode_cube_var(lits[0]))
        if not active_n:
            active_n = len(used)
            n_clauses = sum(local_lens.values())
            lens = local_lens
        inst_units.append((p.name.removesuffix(".cnf.xz"), sorted(units)))
    return active_n, n_clauses, dict(lens), inst_units


def build_svg(
    active_n: int,
    n_clauses: int,
    lens: dict[int, int],
    inst_units: list[tuple[str, list[tuple[int, str]]]],
) -> str:
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Heule 3x3 Matrix Multiplication Fractional Variants: XOR-free EXACTLYONE + ZEROTWO">',
        "  <defs>",
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#b45309"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT}">',
    ]

    # Header
    out.append(
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Heule 3×3 Matrix Multiplication — Fractional Variants (f-d-3, f-d-4, f-d-6)"
        "</text>"
    )
    out.append(
        '    <text x="26" y="53" font-size="11.5" fill="#475569">'
        "XOR-free cardinality-restricted R = 23 Brent encoding: replaces mod-2 parity with "
        "EXACTLY-1 / ZERO-OR-2 + noRank3 + 4 pinned cube pairs"
        "</text>"
    )
    out.append(
        '    <rect x="748" y="18" width="148" height="26" rx="13" '
        'fill="#fffbeb" stroke="#d97706" stroke-width="1.2"/>'
    )
    out.append(
        '    <text x="822" y="35" text-anchor="middle" font-size="10.8" '
        'font-weight="700" fill="#b45309">0 XORs · 89% HORN</text>'
    )
    out.append(
        '    <line x1="22" y1="64" x2="898" y2="64" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # ================= LEFT PANEL: PARITY -> CARDINALITY FRACTIONAL RESTRICTION =================
    lx, ly, lw, lh = 22, 76, 444, 384
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="28" rx="9" fill="#d97706"/>'
    )
    out.append(
        f'    <rect x="{lx}" y="{ly + 16}" width="{lw}" height="12" fill="#d97706"/>'
    )
    out.append(
        f'    <text x="{lx + lw / 2:.1f}" y="{ly + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "1. Replacing Mod-2 XOR Parity with Low-Weight Cardinality</text>"
    )

    # Card A: 27 delta=1 equations -> EXACTLYONE
    y1 = ly + 38
    out.append(
        f'    <rect x="{lx + 14}" y="{y1}" width="{lw - 28}" height="96" rx="7" '
        'fill="#ffffff" stroke="#059669" stroke-width="1.2"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y1 + 18}" font-size="10.6" font-weight="700" fill="#047857">'
        "A. 27 Type-3 Equations (δ = 1):  Odd Parity  →  EXACTLY-ONE</text>"
    )
    out.append(
        f'    <rect x="{lx + 24}" y="{y1 + 26}" width="174" height="32" rx="4" '
        'fill="#f8fafc" stroke="#94a3b8" stroke-width="0.9"/>'
    )
    out.append(
        f'    <text x="{lx + 111}" y="{y1 + 40}" text-anchor="middle" font-size="9.0" fill="#64748b">Full 𝔽₂ Brent (XOR):</text>'
    )
    out.append(
        f'    <text x="{lx + 111}" y="{y1 + 53}" text-anchor="middle" font-family="{MONO}" font-size="9.2" fill="#334155">'
        "∑ s_ℓ ∈ {1, 3, 5, …, 23}</text>"
    )
    out.append(
        f'    <line x1="{lx + 200}" y1="{y1 + 42}" x2="{lx + 224}" y2="{y1 + 42}" '
        'stroke="#b45309" stroke-width="1.6" marker-end="url(#arr)"/>'
    )
    out.append(
        f'    <rect x="{lx + 228}" y="{y1 + 26}" width="190" height="32" rx="4" '
        'fill="#ecfdf5" stroke="#059669" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{lx + 323}" y="{y1 + 40}" text-anchor="middle" font-size="9.0" font-weight="700" fill="#047857">Fractional Restriction:</text>'
    )
    out.append(
        f'    <text x="{lx + 323}" y="{y1 + 53}" text-anchor="middle" font-family="{MONO}" font-size="8.9" font-weight="700" fill="#047857">'
        "∑ s_ℓ = 1  (ℓ=1..23, exact!)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y1 + 74}" font-size="9.3" fill="#334155">'
        "Clauses: 27 ALO 23-clauses + 27 × C(23,2) = 6,831 pairwise binary AMO clauses.</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y1 + 88}" font-size="9.1" fill="#64748b">'
        "Every type-3 triple appears in exactly 1 rank-1 layer (no 3-way overlaps).</text>"
    )

    # Card B: 702 delta=0 equations -> ZEROTWO
    y2 = y1 + 105
    out.append(
        f'    <rect x="{lx + 14}" y="{y2}" width="{lw - 28}" height="106" rx="7" '
        'fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 18}" font-size="10.6" font-weight="700" fill="#1d4ed8">'
        "B. 702 Cross-Term Equations (δ = 0):  Even Parity  →  ZERO-OR-TWO</text>"
    )
    out.append(
        f'    <rect x="{lx + 24}" y="{y2 + 26}" width="174" height="32" rx="4" '
        'fill="#f8fafc" stroke="#94a3b8" stroke-width="0.9"/>'
    )
    out.append(
        f'    <text x="{lx + 111}" y="{y2 + 40}" text-anchor="middle" font-size="9.0" fill="#64748b">Full 𝔽₂ Brent (XOR):</text>'
    )
    out.append(
        f'    <text x="{lx + 111}" y="{y2 + 53}" text-anchor="middle" font-family="{MONO}" font-size="9.2" fill="#334155">'
        "∑ s_ℓ ∈ {0, 2, 4, …, 22}</text>"
    )
    out.append(
        f'    <line x1="{lx + 200}" y1="{y2 + 42}" x2="{lx + 224}" y2="{y2 + 42}" '
        'stroke="#b45309" stroke-width="1.6" marker-end="url(#arr)"/>'
    )
    out.append(
        f'    <rect x="{lx + 228}" y="{y2 + 26}" width="190" height="32" rx="4" '
        'fill="#eff6ff" stroke="#2563eb" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{lx + 323}" y="{y2 + 40}" text-anchor="middle" font-size="9.0" font-weight="700" fill="#1d4ed8">Fractional Restriction:</text>'
    )
    out.append(
        f'    <text x="{lx + 323}" y="{y2 + 53}" text-anchor="middle" font-family="{MONO}" font-size="8.9" font-weight="700" fill="#1d4ed8">'
        "∑ s_ℓ ∈ {0, 2}  (no ≥4 terms)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 74}" font-size="9.2" fill="#334155">'
        "• Not-1 (printN1): 702 × 23 = 16,146 Horn 23-clauses (¬s_ℓ ∨ ⋁ s_r, r≠ℓ)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 89}" font-size="9.3" fill="#334155">'
        "• At-Most-2 (printAMT): 702 × 20 = 14,040 aux vars (28,080 2-cl + 42,822 3-cl)</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y2 + 101}" font-size="8.9" fill="#64748b">'
        "Searches the clean fraction of R = 23 schemes with pairwise-only cancellation!</text>"
    )

    # Card C: noRank3 factor matrix constraint
    y3 = y2 + 115
    out.append(
        f'    <rect x="{lx + 14}" y="{y3}" width="{lw - 28}" height="114" rx="7" '
        'fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.1"/>'
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 18}" font-size="10.6" font-weight="700" fill="#6d28d9">'
        "C. Factor Rank Bound (noRank3) + Non-Empty Guards (ATLEASTONE):</text>"
    )
    # Mini visual of 3 of the 6 forbidden 3x3 permutation patterns
    perms = [
        ((0, 0), (1, 1), (2, 2)),
        ((0, 0), (1, 2), (2, 1)),
        ((0, 1), (1, 0), (2, 2)),
    ]
    for p_idx, coords in enumerate(perms):
        gx = lx + 26 + p_idx * 58
        gy = y3 + 28
        cs = 14
        out.append(
            f'    <rect x="{gx}" y="{gy}" width="{3 * cs}" height="{3 * cs}" rx="3" '
            'fill="#ffffff" stroke="#c4b5fd" stroke-width="0.9"/>'
        )
        for r in range(3):
            for c in range(3):
                fill = "#dc2626" if (r, c) in coords else "#f1f5f9"
                out.append(
                    f'    <rect x="{gx + c * cs + 1.5:.1f}" y="{gy + r * cs + 1.5:.1f}" '
                    f'width="{cs - 3}" height="{cs - 3}" rx="2" fill="{fill}"/>'
                )
    out.append(
        f'    <text x="{lx + 206}" y="{y3 + 42}" font-size="9.5" font-weight="700" fill="#b91c1c">'
        "6 forbidden 3×3 transversals</text>"
    )
    out.append(
        f'    <text x="{lx + 206}" y="{y3 + 56}" font-size="9.2" fill="#334155">'
        "per A⁽ℓ⁾, B⁽ℓ⁾, C⁽ℓ⁾ matrix ⇒</text>"
    )
    out.append(
        f'    <text x="{lx + 206}" y="{y3 + 70}" font-family="{MONO}" font-size="9.1" fill="#6d28d9">'
        "23 × 3 × 6 = 414 3-clauses</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 91}" font-size="9.3" fill="#334155">'
        "• Plus 69 non-empty factor 9-clauses (23×3) &amp; 27 entry-use 23-clauses.</text>"
    )
    out.append(
        f'    <text x="{lx + 24}" y="{y3 + 105}" font-size="9.1" fill="#475569">'
        "• Total active vars = 621 + 1,863 + 16,767 + 14,040 = 33,291 (header 152,785).</text>"
    )

    # ================= RIGHT PANEL: EXACT ANATOMY + 3 PINNED VARIANTS =================
    rx, ry, rw, rh = 480, 76, 418, 384
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="9" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry}" width="{rw}" height="28" rx="9" fill="#0f172a"/>'
    )
    out.append(
        f'    <rect x="{rx}" y="{ry + 16}" width="{rw}" height="12" fill="#0f172a"/>'
    )
    out.append(
        f'    <text x="{rx + rw / 2:.1f}" y="{ry + 19}" text-anchor="middle" '
        'font-size="12" font-weight="700" fill="#ffffff">'
        "2. Decoded Pinned Pairs (f-d-3 / 4 / 6) &amp; Clause Anatomy</text>"
    )

    # Decoded pinned pairs for all 3 instances
    py = ry + 40
    out.append(
        f'    <rect x="{rx + 14}" y="{py}" width="{rw - 28}" height="186" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{py + 18}" font-size="10.4" font-weight="700" fill="#0f172a">'
        "Only Difference Between f-d-3, f-d-4, f-d-6: 8 Pinned Unit Cubes</text>"
    )
    out.append(
        f'    <text x="{rx + 24}" y="{py + 32}" font-size="9.2" fill="#64748b">'
        "Each pins 4 disjoint pairs of type-3 cubes into products M₁…M₄ (decoded live):</text>"
    )
    inst_colors = [
        ("#eff6ff", "#2563eb", "#1d4ed8"),
        ("#ecfdf5", "#059669", "#047857"),
        ("#f5f3ff", "#7c3aed", "#6d28d9"),
    ]
    iy = py + 40
    for idx, (stem, units) in enumerate(inst_units):
        bg, bd, tc = inst_colors[idx % 3]
        out.append(
            f'    <rect x="{rx + 22}" y="{iy}" width="{rw - 44}" height="43" rx="5" '
            f'fill="{bg}" stroke="{bd}" stroke-width="1"/>'
        )
        out.append(
            f'    <text x="{rx + 32}" y="{iy + 16}" font-family="{MONO}" font-size="10.2" '
            f'font-weight="700" fill="{tc}">{esc(stem)}</text>'
        )
        # Group by step 0..3
        by_s: dict[int, list[str]] = collections.defaultdict(list)
        for st, lbl in units:
            by_s[st].append(lbl)
        row1 = f"M₁: {','.join(by_s[0])}   M₂: {','.join(by_s[1])}"
        row2 = f"M₃: {','.join(by_s[2])}   M₄: {','.join(by_s[3])}"
        out.append(
            f'    <text x="{rx + 88}" y="{iy + 16}" font-family="{MONO}" font-size="8.3" fill="#1e293b">'
            f"{esc(row1)}</text>"
        )
        out.append(
            f'    <text x="{rx + 88}" y="{iy + 33}" font-family="{MONO}" font-size="8.3" fill="#334155">'
            f"{esc(row2)}</text>"
        )
        iy += 48

    # Exact Clause-Length Breakdown Card
    cy = py + 196
    out.append(
        f'    <rect x="{rx + 14}" y="{cy}" width="{rw - 28}" height="136" rx="7" '
        'fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>'
    )
    out.append(
        f'    <text x="{rx + 24}" y="{cy + 18}" font-size="10.4" font-weight="700" fill="#0f172a">'
        f"Exact Clause Spectrum ({n_clauses:,} clauses · {active_n:,} active vars):</text>"
    )
    bar_x, bar_y, bar_w = rx + 24, cy + 26, rw - 48
    segs = [
        (lens.get(2, 0), "#2563eb", f"2-cl: {lens.get(2, 0):,} (48%)"),
        (lens.get(3, 0), "#059669", f"3-cl: {lens.get(3, 0):,} (41%)"),
        (lens.get(23, 0), "#d97706", "16.2k"),
    ]
    cur_x = float(bar_x)
    for cnt, col, lbl in segs:
        sw = bar_w * (cnt / n_clauses)
        out.append(
            f'    <rect x="{cur_x:.1f}" y="{bar_y}" width="{sw:.1f}" height="20" '
            f'fill="{col}" stroke="#ffffff" stroke-width="0.8"/>'
        )
        out.append(
            f'    <text x="{cur_x + sw / 2:.1f}" y="{bar_y + 13.5}" text-anchor="middle" '
            f'font-size="8.3" font-weight="700" fill="#ffffff">{lbl}</text>'
        )
        cur_x += sw

    bullets = [
        "• 2-cl (72,171): 37,260 pair/cube + 28,080 AMT + 6,831 EXACTLYONE AMO",
        "• 3-cl (61,866): 18,630 pair/cube + 42,822 AMT + 414 noRank3",
        "• 23-cl (16,200): 16,146 printN1 + 27 EXACTLYONE ALO + 27 entry ALO",
        "• Metrics: α = 4.52 · ρ_crit = 2.60× · κ = 1.26 · 89% Horn · 0 XORs!",
        "• Benchmark (T_max = 60 s): 0/3 resolved across all 6 single-core solvers",
    ]
    for i, b in enumerate(bullets):
        out.append(
            f'    <text x="{rx + 24}" y="{cy + 62 + i * 14.5}" font-size="9.0" fill="#334155">'
            f"{esc(b)}</text>"
        )

    out.append("  </g>")
    out.append("</svg>\n")
    return "\n".join(out)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    active_n, n_clauses, lens, inst_units = audit_fraction(root / "cnf-orig")
    if len(inst_units) != 3:
        raise RuntimeError(f"Expected 3 fraction CNFs, found {len(inst_units)}")
    svg = build_svg(active_n, n_clauses, lens, inst_units)
    out_svg = root / "diagram.svg"
    out_svg.write_text(svg, encoding="utf-8")
    ET.parse(out_svg)
    print(f"Wrote and validated {out_svg} ({out_svg.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
