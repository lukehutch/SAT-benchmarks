#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`aloul-dac02-bench` (Aloul DAC 2002 Symmetry Benchmarks).

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


def sup(text: str) -> str:
    return f'<tspan baseline-shift="super" font-size="72%">{esc(text)}</tspan>'


def build_svg() -> str:
    W, H = 920, 488
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Aloul DAC 2002 Symmetry-Rich SAT Benchmark Suite and Orbit Pruning">',
        "  <defs>",
        '    <marker id="arr-purp" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Aloul DAC 2002 Symmetry-Rich SAT Suite (aloul-dac02-bench)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        '5 classic EDA &amp; combinatorial families (32 instances: 14 SAT / 18 UNSAT) · '
        'Automorphism groups Aut(F) &amp; Lex-Leader Symmetry Breaking</text>',
        '    <rect x="752" y="18" width="142" height="24" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>',
        '    <text x="823" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#6d28d9">14 SAT · 18 UNSAT</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: 5 STRUCTURAL FAMILIES =================
    lx, ly, lw, lh = 24, 78, 536, 388
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Five Benchmark Families in aloul-dac02-bench (32 Instances)</text>'
    )

    families = [
        (
            "Urq3_5 .. Urq8_5",
            "6 UNSAT",
            "#7c3aed",
            "#f5f3ff",
            "Urquhart Bipartite Expander Parity (𝔽₂)",
            f'm² × m² bipartite graph, odd total charge ∑ c{sub("v")} ≡ 1 (mod 2) · 312 native XORs',
            "urq",
        ),
        (
            "hole7 .. hole12",
            "6 UNSAT",
            "#dc2626",
            "#fef2f2",
            f'Pigeonhole Principle PHP{sub("n")}{sup("n+1")}',
            f'n+1 pigeons into n holes (56–156 vars) · Full S{sub("n+1")} × S{sub("n")} symmetry',
            "hole",
        ),
        (
            "chnl10_11 .. chnl11_20",
            "6 UNSAT",
            "#d97706",
            "#fffbeb",
            "Over-Subscribed FPGA Channel Routing",
            f'N &gt; W nets through W tracks on 2 sides (220–440 vars) · 2 × PHP{sub("W")}{sup("N")} core',
            "chnl",
        ),
        (
            "fpga10_8 .. fpga13_12",
            "9 SAT",
            "#059669",
            "#ecfdf5",
            "Routable FPGA Switch-Box Channels",
            "N ≤ W disjoint net-to-track routing (120–234 vars) · Rich track symmetry",
            "fpga",
        ),
        (
            "s3-3-3-1 .. s3-3-3-10",
            "5 SAT",
            "#2563eb",
            "#eff6ff",
            "3×3 FPGA Global Routing Grids (18 Nets)",
            "Multi-channel grid routing (864–1,056 vars, 7.6k–10.9k cls) · 306 native XORs",
            "grid",
        ),
    ]

    fy = ly + 34
    card_h = 62
    for name, badge, accent, bg, title, desc, icon in families:
        p.append(
            f'    <rect x="{lx + 14}" y="{fy}" width="{lw - 28}" height="{card_h}" rx="8" '
            f'fill="#ffffff" stroke="{accent}" stroke-width="1.2"/>'
        )
        # Left mini-icon container
        ix, iy, iw, ih = lx + 22, fy + 8, 56, 46
        p.append(f'    <rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="6" fill="{bg}" stroke="{accent}" stroke-width="0.9"/>')

        if icon == "urq":
            # Bipartite graph with parity charges 0/1
            ls = [(ix + 14, iy + 11), (ix + 14, iy + 23), (ix + 14, iy + 35)]
            rs = [(ix + 42, iy + 11), (ix + 42, iy + 23), (ix + 42, iy + 35)]
            for a, b in [(0, 0), (0, 1), (1, 0), (1, 2), (2, 1), (2, 2)]:
                p.append(f'    <line x1="{ls[a][0]}" y1="{ls[a][1]}" x2="{rs[b][0]}" y2="{rs[b][1]}" stroke="#a78bfa" stroke-width="1.2"/>')
            for idx_n, (nx, ny) in enumerate(ls + rs):
                fc = "#7c3aed" if idx_n in (0, 2, 4) else "#ffffff"
                p.append(f'    <circle cx="{nx}" cy="{ny}" r="3.8" fill="{fc}" stroke="#6d28d9" stroke-width="1.1"/>')
        elif icon == "hole":
            # 4 pigeons -> 3 holes
            for i in range(4):
                p.append(f'    <circle cx="{ix + 12}" cy="{iy + 8 + i*10}" r="3" fill="#dc2626"/>')
            for j in range(3):
                p.append(f'    <rect x="{ix + 38}" y="{iy + 9 + j*12}" width="9" height="8" rx="1.5" fill="#ffffff" stroke="#b91c1c" stroke-width="1.1"/>')
            for i in range(3):
                p.append(f'    <line x1="{ix + 15}" y1="{iy + 8 + i*10}" x2="{ix + 38}" y2="{iy + 13 + i*12}" stroke="#dc2626" stroke-width="1.2"/>')
            p.append(f'    <line x1="{ix + 15}" y1="{iy + 38}" x2="{ix + 36}" y2="{iy + 37}" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="2,2"/>')
        elif icon == "chnl":
            # Narrow bottleneck channel
            for k in range(3):
                p.append(f'    <line x1="{ix + 6}" y1="{iy + 12 + k*10}" x2="{ix + 50}" y2="{iy + 12 + k*10}" stroke="#d97706" stroke-width="1.8"/>')
            p.append(f'    <line x1="{ix + 6}" y1="{iy + 39}" x2="{ix + 25}" y2="{iy + 39}" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="3,2"/>')
            p.append(f'    <text x="{ix + 34}" y="{iy + 42}" font-size="9.5" font-weight="800" fill="#dc2626">×</text>')
        elif icon == "fpga":
            # Clean switch box with 2 routed nets
            p.append(f'    <rect x="{ix + 16}" y="{iy + 11}" width="24" height="24" rx="3" fill="#ffffff" stroke="#059669" stroke-width="1.2"/>')
            p.append(f'    <path d="M {ix+6} {iy+18} L {ix+50} {iy+18}" stroke="#059669" stroke-width="1.8" fill="none"/>')
            p.append(f'    <path d="M {ix+6} {iy+28} L {ix+28} {iy+28} L {ix+28} {iy+6}" stroke="#2563eb" stroke-width="1.8" fill="none"/>')
        elif icon == "grid":
            # 3x3 global routing grid
            for r in range(3):
                for c in range(3):
                    gx, gy = ix + 10 + c * 14, iy + 9 + r * 12
                    p.append(f'    <rect x="{gx}" y="{gy}" width="8" height="7" rx="1.2" fill="#dbeafe" stroke="#2563eb" stroke-width="0.9"/>')
            p.append(f'    <path d="M {ix+14} {iy+12} L {ix+42} {iy+12} L {ix+42} {iy+36}" fill="none" stroke="#1d4ed8" stroke-width="1.6"/>')

        # Text inside family card
        tx = lx + 88
        p.append(f'    <text x="{tx}" y="{fy + 18}" font-size="11.5" font-weight="700" fill="#0f172a">{title}</text>')
        p.append(f'    <text x="{tx}" y="{fy + 34}" font-family="{mono}" font-size="9.8" font-weight="600" fill="{accent}">{esc(name)}</text>')
        p.append(f'    <text x="{tx}" y="{fy + 50}" font-size="9.6" fill="#475569">{desc}</text>')

        # Right status pill
        p.append(f'    <rect x="{lx + lw - 86}" y="{fy + 8}" width="64" height="19" rx="9.5" fill="{bg}" stroke="{accent}" stroke-width="0.9"/>')
        p.append(f'    <text x="{lx + lw - 54}" y="{fy + 21}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{accent}">{badge}</text>')

        fy += card_h + 7

    # ================= RIGHT PANEL: SYMMETRY ORBITS & SBP =================
    rx, ry, rw = 576, 78, 320

    # Top card: Automorphism Orbit Quotient & Search Tree Pruning
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="248" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 22}" font-size="12.5" font-weight="700" fill="#0f172a">Symmetry Orbits &amp; Tree Pruning</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 38}" font-size="10" fill="#475569">Automorphism σ ∈ Aut(F) maps F(σ(x)) = F(x)</text>')

    # Root decision node
    rcx, rcy = rx + rw / 2, ry + 64
    p.append(f'    <circle cx="{rcx:.1f}" cy="{rcy}" r="13" fill="#eff6ff" stroke="#2563eb" stroke-width="1.6"/>')
    p.append(f'    <text x="{rcx:.1f}" y="{rcy + 4}" text-anchor="middle" font-size="10" font-weight="700" fill="#1d4ed8">root</text>')

    # Three symmetric subtrees: Canonical (kept) vs 2 isomorphic orbits (pruned!)
    bxs = [rx + 56, rx + 160, rx + 264]
    by_mid = ry + 114
    for idx_b, bx in enumerate(bxs):
        is_canon = idx_b == 0
        stroke_c = "#059669" if is_canon else "#cbd5e1"
        dash = "" if is_canon else ' stroke-dasharray="4,3"'
        p.append(f'    <line x1="{rcx:.1f}" y1="{rcy + 13}" x2="{bx}" y2="{by_mid - 14}" stroke="{stroke_c}" stroke-width="1.8"{dash}/>')
        # Wider subtree triangle so labels fit with generous margin inside!
        fill_tri = "#ecfdf5" if is_canon else "#f1f5f9"
        p.append(f'    <polygon points="{bx},{by_mid - 14} {bx - 42},{by_mid + 52} {bx + 42},{by_mid + 52}" fill="{fill_tri}" stroke="{stroke_c}" stroke-width="1.5"{dash}/>')
        if is_canon:
            p.append(f'    <text x="{bx}" y="{by_mid + 29}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#047857">T₁ (keep)</text>')
            p.append(f'    <text x="{bx}" y="{by_mid + 44}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#059669">Canonical</text>')
        else:
            # Clean red X in upper apex region, label comfortably below
            p.append(f'    <line x1="{bx - 8}" y1="{by_mid + 1}" x2="{bx + 8}" y2="{by_mid + 15}" stroke="#dc2626" stroke-width="2"/>')
            p.append(f'    <line x1="{bx + 8}" y1="{by_mid + 1}" x2="{bx - 8}" y2="{by_mid + 15}" stroke="#dc2626" stroke-width="2"/>')
            p.append(f'    <text x="{bx}" y="{by_mid + 31}" text-anchor="middle" font-size="10" font-weight="700" fill="#64748b">σ{sup(str(idx_b))}(T₁)</text>')
            p.append(f'    <text x="{bx}" y="{by_mid + 45}" text-anchor="middle" font-size="9.1" font-weight="700" fill="#dc2626">PRUNED</text>')

    # Curved purple automorphism arrows σ connecting T1 -> T2 -> T3
    p.append(f'    <path d="M {bxs[0] + 20} {by_mid - 6} Q {(bxs[0]+bxs[1])/2:.1f} {by_mid - 26} {bxs[1] - 20} {by_mid - 6}" fill="none" stroke="#7c3aed" stroke-width="1.4" marker-end="url(#arr-purp)"/>')
    p.append(f'    <text x="{(bxs[0]+bxs[1])/2:.1f}" y="{by_mid - 19}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#6d28d9">σ₁</text>')
    p.append(f'    <path d="M {bxs[1] + 20} {by_mid - 6} Q {(bxs[1]+bxs[2])/2:.1f} {by_mid - 26} {bxs[2] - 20} {by_mid - 6}" fill="none" stroke="#7c3aed" stroke-width="1.4" marker-end="url(#arr-purp)"/>')
    p.append(f'    <text x="{(bxs[1]+bxs[2])/2:.1f}" y="{by_mid - 19}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#6d28d9">σ₂</text>')

    # Lex-leader SBP formula box
    p.append(f'    <rect x="{rx + 14}" y="{ry + 180}" width="{rw - 28}" height="56" rx="7" fill="#ffffff" stroke="#c4b5fd" stroke-width="1.1"/>')
    p.append(f'    <text x="{rx + 24}" y="{ry + 198}" font-size="10.2" font-weight="700" fill="#6d28d9">Lex-Leader Symmetry-Breaking Predicate (SBP):</text>')
    p.append(f'    <text x="{rx + 24}" y="{ry + 214}" font-family="{mono}" font-size="9.8" fill="#0f172a">SBP(F) = ⋀{sub("σ∈G")} [ x ≤{sub("lex")} σ(x) ]</text>')
    p.append(f'    <text x="{rx + 24}" y="{ry + 228}" font-size="9.4" fill="#475569">Retains ≥ 1 model per orbit; preserves SAT/UNSAT</text>')

    # Bottom Card: Suite Impact & Structural Metrics
    by2 = ry + 260
    p.append(f'    <rect x="{rx}" y="{by2}" width="{rw}" height="128" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{by2 + 21}" font-size="12" font-weight="700" fill="#0f172a">Suite Impact &amp; Format Metrics</text>')
    metrics = [
        ("Dimensions:", "46–1,056 vars · 204–10,862 clauses"),
        ("Regime:", f'6 Under (Urq) / 26 Over · Med ρ{sub("crit")} = 4.50×'),
        ("Native XORs:", "618 total (312 Urq + 306 s3-3 grids)"),
        ("Pure CDCL:", "17–24 / 32 solved in 5 s (chokes on PHP/Urq)"),
        ("Sym/Alg SAT:", "32 / 32 solved in 0.36–0.45 s combined"),
    ]
    for i, (k, v) in enumerate(metrics):
        yy = by2 + 41 + i * 17.5
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.8" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 92}" y="{yy:.1f}" font-size="9.7" fill="#334155">{v}</text>')

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
