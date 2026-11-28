#!/usr/bin/env python3
"""Generate a publication-grade SVG diagram for `davies-rectangle-free-27`.

Parses the exact committed `cnf-orig/02-open.cnf.xz` to decode the actual 27x27
147-cell PG(2,5)-derived fixed template T1 and 145-cell movable template T3,
and renders a light-card standalone SVG (`diagram.svg`) illustrating:
  1. The real 27x27 grid with fixed Color 1 (T1, 147 cells, 0 rectangles),
     row-weight distribution (15x5 + 12x6 = 147), pinned host rows 0-2 of
     02-open.cnf, and an illustrative forbidden 2x2 monochromatic rectangle.
  2. The 5-color template decomposition (147 + 147 + 145 + 290 = 729 cells)
     and the Zarankiewicz / bipartite Ramsey frontier 26 <= b_5(2) <= 28.
"""
from __future__ import annotations

import lzma
import xml.etree.ElementTree as ET
from pathlib import Path


def decode_templates(cnf_xz_path: Path) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """Extract exact T1 (=T2, 147 cells) and T3 (145 cells) from binary disjointness clauses."""
    t1: set[tuple[int, int]] = set()
    t3: set[tuple[int, int]] = set()
    with lzma.open(cnf_xz_path, "rt", errors="ignore") as f:
        for line in f:
            if not line or line[0] in ("c", "p"):
                continue
            parts = line.split()
            if len(parts) != 3:  # 2 literals + trailing 0
                continue
            a, b = int(parts[0]), int(parts[1])
            if a < 0 and b < 0:
                u, v = (-a, -b) if -a < -b else (-b, -a)
                if 1 <= u <= 729 and 730 <= v <= 1458:
                    r, _ = divmod(u - 1, 27)
                    c, _ = divmod(v - 730, 27)
                    t1.add((r, c))
                elif 1459 <= u <= 2187 and 2188 <= v <= 2916:
                    _, rp = divmod(u - 1459, 27)
                    _, cp = divmod(v - 2188, 27)
                    t3.add((rp, cp))
    if len(t1) != 147 or len(t3) != 145:
        raise RuntimeError(f"Expected |T1|=147, |T3|=145; got {len(t1)}, {len(t3)}")
    return t1, t3


def build_svg(t1: set[tuple[int, int]], t3: set[tuple[int, int]]) -> str:
    w, h = 920, 560
    cell = 13
    gx, gy = 56, 108  # top-left of 27x27 T1 grid (351 x 351 px)
    grid_px = 27 * cell

    row_deg = [sum(1 for c in range(27) if (r, c) in t1) for r in range(27)]
    col_deg = [sum(1 for r in range(27) if (r, c) in t1) for c in range(27)]

    # Pick a clean illustrative 2x2 rectangle entirely inside non-T1 cells (rows 6, 14; cols 7, 19)
    rect_r1, rect_r2, rect_c1, rect_c2 = 6, 14, 7, 19
    for rr in (rect_r1, rect_r2):
        for cc in (rect_c1, rect_c2):
            if (rr, cc) in t1:
                # Fallback search for any clean non-T1 2x2 rectangle near center
                found = False
                for r1 in range(5, 12):
                    for r2 in range(14, 21):
                        for c1 in range(6, 12):
                            for c2 in range(16, 22):
                                if all((r, c) not in t1 for r in (r1, r2) for c in (c1, c2)):
                                    rect_r1, rect_r2, rect_c1, rect_c2 = r1, r2, c1, c2
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            break
                    if found:
                        break
                break

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif">'
    )
    out.append("  <defs>")
    out.append(
        '    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>'
    )
    out.append("  </defs>")

    # Explicit light canvas for GitHub light & dark modes
    out.append(
        f'  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>'
    )

    # Title banner
    out.append(
        '  <text x="28" y="36" font-size="18" font-weight="700" fill="#0f172a">'
        "Rectangle-Free 5-Coloring of the 27&#215;27 Grid (Jason Davies / Zarankiewicz Frontier)"
        "</text>"
    )
    out.append(
        '  <text x="28" y="56" font-size="12" fill="#475569">'
        "No axis-aligned 2&#215;2 rectangle may have 4 same-colored corners  &#183;  "
        "Conjectured threshold b&#8325;(2) = 28 (26 &#8804; b&#8325;(2) &#8804; 28; a 27&#215;27 5-coloring settles the conjecture)"
        "</text>"
    )
    out.append('  <line x1="24" y1="68" x2="896" y2="68" stroke="#e2e8f0" stroke-width="1"/>')

    # Left panel header
    out.append(
        f'  <text x="{gx}" y="90" font-size="13" font-weight="700" fill="#1e293b">'
        "Actual Fixed Color-1 Template T&#8321; (147 cells, PG(2,5) &#8726; 4&#215;4)"
        "</text>"
    )
    out.append(
        f'  <text x="{gx}" y="103" font-size="10.5" fill="#64748b">'
        "Decoded from cnf-orig/02-open.cnf.xz: 0 monochromatic rectangles, row/col sums &#8712; {5, 6}"
        "</text>"
    )

    # Highlight pinned host rows 0, 1, 2 for 02-open.cnf
    out.append(
        f'  <rect x="{gx - 2}" y="{gy - 1}" width="{grid_px + 4}" height="{3 * cell + 2}" '
        'fill="#fef9c3" fill-opacity="0.7" stroke="#eab308" stroke-width="1" stroke-dasharray="3,2"/>'
    )

    # Grid background and lines (compact vector grid + 147 filled T1 cells)
    out.append(
        f'  <rect x="{gx}" y="{gy}" width="{grid_px}" height="{grid_px}" '
        'fill="#ffffff" fill-opacity="0.35" stroke="#94a3b8" stroke-width="1.2"/>'
    )
    grid_d = []
    for k in range(1, 27):
        grid_d.append(f"M{gx + k * cell},{gy}v{grid_px}")
        grid_d.append(f"M{gx},{gy + k * cell}h{grid_px}")
    out.append(f'  <path d="{" ".join(grid_d)}" stroke="#e2e8f0" stroke-width="0.6" fill="none"/>')
    for r, c in sorted(t1):
        x = gx + c * cell
        y = gy + r * cell
        out.append(
            f'  <rect x="{x + 0.9:.1f}" y="{y + 0.9:.1f}" width="{cell - 1.8:.1f}" '
            f'height="{cell - 1.8:.1f}" rx="2" fill="#2563eb"/>'
        )

    # Row weight marginals (right of grid) & row index labels (left)
    for r in range(27):
        yc = gy + r * cell + cell * 0.76
        if r in (0, 1, 2, 9, 18, 26):
            out.append(
                f'  <text x="{gx - 6}" y="{yc:.1f}" text-anchor="end" font-size="8.5" '
                f'fill="{"#a16207" if r < 3 else "#64748b"}" font-weight="{"700" if r < 3 else "400"}">{r}</text>'
            )
        deg = row_deg[r]
        fill_d = "#1d4ed8" if deg == 6 else "#94a3b8"
        out.append(
            f'  <text x="{gx + grid_px + 7}" y="{yc:.1f}" font-size="8.5" fill="{fill_d}" '
            f'font-weight="{"700" if deg == 6 else "400"}">{deg}</text>'
        )

    out.append(
        f'  <text x="{gx + grid_px + 7}" y="{gy - 3}" font-size="8.5" font-weight="600" fill="#475569">wt</text>'
    )
    out.append(
        f'  <text x="{gx - 6}" y="{gy - 3}" text-anchor="end" font-size="8.5" font-weight="600" fill="#475569">row</text>'
    )

    # Illustrative forbidden monochromatic 2x2 rectangle inside non-T1 cells
    rx1 = gx + rect_c1 * cell + cell / 2
    rx2 = gx + rect_c2 * cell + cell / 2
    ry1 = gy + rect_r1 * cell + cell / 2
    ry2 = gy + rect_r2 * cell + cell / 2
    out.append(
        f'  <rect x="{rx1:.1f}" y="{ry1:.1f}" width="{rx2 - rx1:.1f}" height="{ry2 - ry1:.1f}" '
        'fill="#dc2626" fill-opacity="0.08" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="5,3"/>'
    )
    for cx, cy in ((rx1, ry1), (rx2, ry1), (rx1, ry2), (rx2, ry2)):
        out.append(
            f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="#dc2626" stroke="#ffffff" stroke-width="1.2"/>'
        )
    out.append(
        f'  <rect x="{(rx1 + rx2) / 2 - 74:.1f}" y="{(ry1 + ry2) / 2 - 11:.1f}" width="148" height="22" rx="4" '
        'fill="#ffffff" fill-opacity="0.93" stroke="#fca5a5" stroke-width="1"/>'
    )
    out.append(
        f'  <text x="{(rx1 + rx2) / 2:.1f}" y="{(ry1 + ry2) / 2 + 3.5:.1f}" text-anchor="middle" '
        'font-size="9.5" font-weight="700" fill="#b91c1c">Forbidden 2&#215;2 Rectangle</text>'
    )

    # Legend under left grid
    ly = gy + grid_px + 22
    out.append(f'  <rect x="{gx}" y="{ly - 9}" width="11" height="11" rx="2" fill="#2563eb"/>')
    out.append(
        f'  <text x="{gx + 16}" y="{ly}" font-size="10.5" fill="#334155">'
        "Fixed T&#8321; (147 cells: 12 rows&#215;6 + 15 rows&#215;5)</text>"
    )
    out.append(
        f'  <rect x="{gx}" y="{ly + 10}" width="11" height="11" rx="1" fill="#fef9c3" '
        'stroke="#eab308" stroke-width="1" stroke-dasharray="2,1"/>'
    )
    out.append(
        f'  <text x="{gx + 16}" y="{ly + 19}" font-size="10.5" fill="#334155">'
        "02-open.cnf pinned host rows 0, 1, 2 &#8594; T&#8322; src rows 15, 0, 2</text>"
    )
    out.append(f'  <circle cx="{gx + 5.5}" cy="{ly + 34}" r="4.5" fill="#dc2626"/>')
    out.append(
        f'  <text x="{gx + 16}" y="{ly + 38}" font-size="10.5" fill="#334155">'
        "Monochromatic 4-corner clause (48,108 per free color 4 &amp; 5)</text>"
    )

    # Right panel: 5-Color Template Decomposition & Variable Architecture
    rx = 458
    rw = 434
    out.append(
        f'  <text x="{rx}" y="90" font-size="13" font-weight="700" fill="#1e293b">'
        "5-Color Decomposition &amp; SAT Encoding (5,244 Vars)"
        "</text>"
    )
    out.append(
        f'  <text x="{rx}" y="103" font-size="10.5" fill="#64748b">'
        "Partitioning 27&#178; = 729 cells via 3 PG(2,5) templates + 2 free colors"
        "</text>"
    )

    cards = [
        ("#eff6ff", "#3b82f6", "#1d4ed8", "Color 1 — Fixed Template T&#8321;", "147 cells (fixed)",
         "PG(2,5) &#8726; 4&#215;4 (z(27) = 147), |Aut(T&#8321;)| = 24. Removes 147 cells from grid."),
        ("#ecfdf5", "#10b981", "#047857", "Color 2 — Movable T&#8322; = R&#8322; T&#8321; C&#8322;&#7488;", "147 cells (vars 1..1458)",
         "27&#215;27 row &amp; col bijections R&#8322;, C&#8322;; disjoint from T&#8321; (21,609 bin cls)."),
        ("#f5f3ff", "#8b5cf6", "#6d28d9", "Color 3 — Movable T&#8323; = R&#8323; T&#8323; C&#8323;&#7488;", "145 cells (vars 1459..2916)",
         "PG(2,5) &#8726; 4&#215;4 (10&#215;6 + 17&#215;5), |Aut(T&#8323;)| = 20 &#8773; D&#8321;&#8320; (unbroken in 02-open)."),
        ("#fff7ed", "#f97316", "#c2410c", "Colors 4 &amp; 5 — Free Remainder (G&#8322;, G&#8323;)", "290 cells (vars 2917..5244)",
         "582 non-T&#8321; cells &#215; 4 color vars; 2 &#215; 48,108 4-clauses + 22 row-0 SBP cls."),
    ]
    cy = 114
    for bg, stroke, title_col, title, badge, desc in cards:
        out.append(
            f'  <rect x="{rx}" y="{cy}" width="{rw}" height="62" rx="8" '
            f'fill="{bg}" stroke="{stroke}" stroke-width="1.2"/>'
        )
        out.append(
            f'  <text x="{rx + 12}" y="{cy + 20}" font-size="11.5" font-weight="700" fill="{title_col}">{title}</text>'
        )
        out.append(
            f'  <text x="{rx + rw - 12}" y="{cy + 20}" text-anchor="end" font-size="10.5" font-weight="600" fill="#334155">{badge}</text>'
        )
        out.append(
            f'  <text x="{rx + 12}" y="{cy + 39}" font-size="10" fill="#334155">{desc}</text>'
        )
        # Mini weight bar inside each card
        cy += 70

    # Stacked 729-cell budget bar
    by = 400
    bar_w = rw
    out.append(
        f'  <text x="{rx}" y="{by - 6}" font-size="10.5" font-weight="700" fill="#334155">'
        "Exact 729-Cell Color Partition Budget (147 + 147 + 145 + 290 = 729)"
        "</text>"
    )
    segs = [
        (147, "#2563eb", "C1: 147"),
        (147, "#10b981", "C2: 147"),
        (145, "#8b5cf6", "C3: 145"),
        (145, "#f97316", "C4: ~145"),
        (145, "#e11d48", "C5: ~145"),
    ]
    bx = float(rx)
    for cnt, col, lbl in segs:
        sw = bar_w * (cnt / 729.0)
        out.append(f'  <rect x="{bx:.1f}" y="{by}" width="{sw:.1f}" height="22" fill="{col}" stroke="#ffffff" stroke-width="1"/>')
        out.append(
            f'  <text x="{bx + sw / 2:.1f}" y="{by + 14.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#ffffff">{lbl}</text>'
        )
        bx += sw

    # Clause-structure summary box
    sy = 434
    out.append(
        f'  <rect x="{rx}" y="{sy}" width="{rw}" height="108" rx="8" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    out.append(
        f'  <text x="{rx + 12}" y="{sy + 17}" font-size="11" font-weight="700" fill="#0f172a">'
        "Shared Base CNF (1,067,824 clauses; 99.92% Horn, &#945; = 203.6)"
        "</text>"
    )
    lines = [
        "&#8226; 848,556 ternary (79.5%): bilinear template links (&#8722;R, &#8722;C, &#177;G)",
        "&#8226; 122,233 binary (11.4%): 75,816 perm AMO + 42,924 T&#8321;-disjoint + 3,492 cell",
        "&#8226; 96,799 4-clauses (9.1%): 96,216 C4/C5 rectangles + 582 cell ALO",
        "&#8226; 01-known-unsat: +52 pins (BCP &#8594; 2,238 active vars, 83,252 cls)",
        "&#8226; 02-open: +3 pins on R&#8322; rows 0&#8211;2 (BCP &#8594; 5,007 active vars, 924,915 cls)",
    ]
    for i, ln in enumerate(lines):
        out.append(f'  <text x="{rx + 12}" y="{sy + 35 + i * 15}" font-size="9.6" fill="#334155">{ln}</text>')

    out.append("</svg>\n")
    return "\n".join(out)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cnf_path = root / "cnf-orig" / "02-open.cnf.xz"
    svg_path = root / "diagram.svg"
    t1, t3 = decode_templates(cnf_path)
    svg = build_svg(t1, t3)
    svg_path.write_text(svg, encoding="utf-8")
    # Strict XML well-formedness check
    ET.parse(svg_path)
    print(f"Wrote and validated {svg_path} ({svg_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
