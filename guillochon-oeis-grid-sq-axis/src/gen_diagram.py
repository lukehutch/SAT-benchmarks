#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-grid-sq-axis.

Renders the independently verified 11x11 square-grid configuration with 73 painted points
and ZERO axis-aligned squares (while explicitly highlighting a legal tilted square present
in the configuration), decoded directly from `solutions/sq-axis_n11_m73.model.xz`.
"""
from __future__ import annotations

import json
import lzma
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_true_vars(path: Path) -> set[int]:
    opener = lzma.open if path.suffix == ".xz" else open
    true_vars: set[int] = set()
    with opener(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ("c", "s"):
                continue
            toks = s.split()
            if toks[0] == "v":
                toks = toks[1:]
            for tok in toks:
                lit = int(tok)
                if lit > 0:
                    true_vars.add(lit)
    return true_vars


def count_axis_squares(painted: set[tuple[int, int]], n: int) -> int:
    bad = 0
    for x, y in painted:
        for s in range(1, n):
            if (x + s, y) in painted and (x, y + s) in painted and (x + s, y + s) in painted:
                bad += 1
    return bad


def find_tilted_squares(painted: set[tuple[int, int]], n: int) -> list[list[tuple[int, int]]]:
    found: list[tuple[int, list[tuple[int, int]]]] = []
    seen: set[tuple[tuple[int, int], ...]] = set()
    for x, y in sorted(painted):
        for a in range(1, n):
            for b in range(1, n):
                sq = [(x, y), (x + a, y + b), (x + a - b, y + b + a), (x - b, y + a)]
                if all(p in painted for p in sq):
                    key = tuple(sorted(sq))
                    if key not in seen:
                        seen.add(key)
                        found.append((a * a + b * b, sq))
    found.sort(key=lambda t: (-t[0], t[1]))
    return [sq for _, sq in found]


def build_svg() -> str:
    meta = json.loads(
        (ROOT / "src/upstream/sequences/point-patterns/cnf/sq-axis_n11_m73.cnf.map.json").read_text(encoding="utf-8")
    )
    tv = read_true_vars(ROOT / "solutions/sq-axis_n11_m73.model.xz")
    pts = [tuple(p) for p in meta["points"]]
    painted = {p for i, p in enumerate(pts) if (i + 1) in tv}
    n = meta["n"]
    assert n == 11 and len(painted) == 73 and count_axis_squares(painted, n) == 0, "Invalid sq-axis model!"
    tilted_all = find_tilted_squares(painted, n)
    assert tilted_all, "Expected at least one legal tilted square in sq-axis_n11_m73"
    # Pick a crisp medium-sized tilted square near the center (side^2 in [4..13] if available)
    sample_tilted = next((sq for sq in tilted_all if 4 <= ((sq[1][0] - sq[0][0]) ** 2 + (sq[1][1] - sq[0][1]) ** 2) <= 13), tilted_all[0])

    n_forb_11 = sum((11 - s) ** 2 for s in range(1, 11))
    n_forb_14 = sum((14 - s) ** 2 for s in range(1, 14))

    W, H = 960, 520
    els: list[str] = []
    add = els.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    add("""  <defs>
    <style>
      .title { font: 700 17.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .subtitle { font: 400 11.8px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .ptitle { font: 700 13px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .psub { font: 400 11px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .mono { font: 700 9.8px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #334155; }
      .mono-sm { font: 600 8.8px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #64748b; }
      .badge { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .cap { font: 400 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #334155; }
      .cap-b { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
    </style>
  </defs>""")

    add(f'  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    add('  <text x="24" y="33" class="title">OEIS A227133 / A152125 — Square Grid Avoiding Axis-Aligned Squares (sq-axis)</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum painted points on an N x N square grid with no axis-parallel square (tilted squares remain legal)</text>')
    add('  <rect x="764" y="14" width="172" height="24" rx="12" fill="#0284c7"/>')
    add('  <text x="850" y="30" text-anchor="middle" class="badge">OPEN: N=14, m=113?</text>')

    # Left Card: Verified 11x11 Grid (73 painted points)
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius 11x11 Certificate: 73 Painted Points</text>')
    add(f'  <text x="36" y="106" class="psub">solutions/sq-axis_n11_m73.model.xz | A227133(11) = 73 | 0 axis squares ({len(tilted_all)} legal tilted)</text>')

    step = 32.0
    gw = (n - 1) * step
    gx0 = 20 + (496 - gw) / 2.0
    gy0 = 134.0

    for i in range(n):
        px = gx0 + i * step
        py = gy0 + i * step
        add(f'  <line x1="{px:.1f}" y1="{gy0:.1f}" x2="{px:.1f}" y2="{gy0+gw:.1f}" stroke="#cbd5e1" stroke-width="1"/>')
        add(f'  <line x1="{gx0:.1f}" y1="{py:.1f}" x2="{gx0+gw:.1f}" y2="{py:.1f}" stroke="#cbd5e1" stroke-width="1"/>')
        add(f'  <text x="{px:.1f}" y="{gy0+gw+19:.1f}" text-anchor="middle" class="mono-sm">{i}</text>')
        add(f'  <text x="{gx0-13:.1f}" y="{gy0+(n-1-i)*step+3.2:.1f}" text-anchor="end" class="mono-sm">{i}</text>')

    # Highlight one real legal tilted square on the 11x11 grid
    poly_pts = " ".join(f"{gx0 + x * step:.1f},{gy0 + (n - 1 - y) * step:.1f}" for x, y in sample_tilted)
    add(f'  <polygon points="{poly_pts}" fill="#10b981" fill-opacity="0.16" stroke="#059669" stroke-width="2.2" stroke-dasharray="5,3"/>')

    sample_set = set(sample_tilted)
    for (x, y) in pts:
        px = gx0 + x * step
        py = gy0 + (n - 1 - y) * step
        if (x, y) in painted:
            if (x, y) in sample_set:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="8.2" fill="#059669" stroke="#064e3b" stroke-width="1.6"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="7.4" fill="#0284c7" stroke="#0c4a6e" stroke-width="1.4"/>')
        else:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1"/>')

    # Legend
    add('  <circle cx="52" cy="485" r="5.5" fill="#0284c7" stroke="#0c4a6e" stroke-width="1.2"/>')
    add('  <text x="63" y="489" class="cap"><tspan class="cap-b">73 painted</tspan> (60.3%)</text>')
    add('  <circle cx="195" cy="485" r="5.5" fill="#059669" stroke="#064e3b" stroke-width="1.2"/>')
    add('  <text x="206" y="489" class="cap"><tspan class="cap-b">Legal tilted square</tspan> (allowed in sq-axis)</text>')

    # Right Top Card: Forbidden Axis vs Allowed Tilted
    add('  <rect x="532" y="68" width="408" height="214" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Forbidden vs. Allowed Square Orientations</text>')
    add('  <text x="548" y="106" class="psub">Only axis-parallel squares {(x,y),(x+s,y),(x,y+s),(x+s,y+s)} forbidden</text>')

    ms = 28.0
    mx0, my0 = 556.0, 126.0
    for i in range(5):
        add(f'  <line x1="{mx0+i*ms:.1f}" y1="{my0:.1f}" x2="{mx0+i*ms:.1f}" y2="{my0+4*ms:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        add(f'  <line x1="{mx0:.1f}" y1="{my0+i*ms:.1f}" x2="{mx0+4*ms:.1f}" y2="{my0+i*ms:.1f}" stroke="#e2e8f0" stroke-width="1"/>')

    def mp(x: int, y: int) -> tuple[float, float]:
        return mx0 + x * ms, my0 + (4 - y) * ms

    # Forbidden axis-aligned square (0,3)-(1,3)-(1,4)-(0,4)
    f_sq = [mp(0, 3), mp(1, 3), mp(1, 4), mp(0, 4)]
    add(f'  <polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in f_sq)}" fill="#fee2e2" fill-opacity="0.6" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,2"/>')
    # Allowed tilted square (2,0)-(4,1)-(3,3)-(1,2)
    a_sq = [mp(2, 0), mp(4, 1), mp(3, 3), mp(1, 2)]
    add(f'  <polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in a_sq)}" fill="#d1fae5" fill-opacity="0.55" stroke="#059669" stroke-width="2"/>')

    bad_v = {(0, 3), (1, 3), (1, 4), (0, 4)}
    ok_v = {(2, 0), (4, 1), (3, 3), (1, 2)}
    for x in range(5):
        for y in range(5):
            px, py = mp(x, y)
            if (x, y) in bad_v:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.6" fill="#dc2626" stroke="#7f1d1d" stroke-width="1"/>')
            elif (x, y) in ok_v:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.6" fill="#059669" stroke="#064e3b" stroke-width="1"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#94a3b8"/>')

    tx = 696
    add(f'  <text x="{tx}" y="140" class="cap-b" fill="#dc2626">FORBIDDEN (red dashed):</text>')
    add(f'  <text x="{tx}" y="157" class="cap">Axis-parallel s x s squares.</text>')
    add(f'  <text x="{tx}" y="177" class="cap-b" fill="#059669">ALLOWED (green solid):</text>')
    add(f'  <text x="{tx}" y="194" class="cap">All tilted squares (a,b &gt; 0).</text>')
    add(f'  <text x="{tx}" y="218" class="cap-b">Forbidden Clause Count:</text>')
    add(f'  <text x="{tx}" y="235" class="cap">Sum (N-s)^2 = N(N-1)(2N-1)/6:</text>')
    add(f'  <text x="{tx}" y="252" class="cap">{n_forb_11} at N=11; {n_forb_14} at N=14.</text>')

    # Right Bottom Card: OEIS A227133 / A152125 Ladder
    add('  <rect x="532" y="294" width="408" height="206" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="316" class="ptitle">OEIS A227133 / A152125 Ladder &amp; Open Frontier (8 CNFs)</text>')
    add('  <text x="548" y="332" class="psub">Known optimal through N = 13; N = 14 lower bound 112 (Karpov 2016)</text>')

    rungs = [
        ("N=11", "73", "73 SAT / 74 UNSAT", "#059669", "#ecfdf5"),
        ("N=12", "85", "85 SAT / 86 UNSAT", "#0284c7", "#f0f9ff"),
        ("N=13", "98", "98 SAT / 99 UNSAT", "#0284c7", "#f0f9ff"),
        ("N=14", "112+", "112 SAT / 113 OPEN", "#dc2626", "#fef2f2"),
    ]
    rx0, rw, rg = 548, 90, 6
    for i, (nl, ml, sub, sc, fc) in enumerate(rungs):
        x = rx0 + i * (rw + rg)
        add(f'  <rect x="{x}" y="348" width="{rw}" height="74" rx="7" fill="{fc}" stroke="{sc}" stroke-width="1.3"/>')
        add(f'  <text x="{x+rw/2:.1f}" y="368" text-anchor="middle" class="mono" fill="{sc}">{nl}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="393" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700" fill="{sc}">{ml}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="413" text-anchor="middle" font-family="ui-monospace,monospace" font-size="7.6" fill="#475569">{sub}</text>')

    add('  <text x="548" y="446" class="cap">- <tspan class="cap-b">Complementary A152125(N)</tspan> = N^2 - A227133(N) (min hitting set).</text>')
    add('  <text x="548" y="464" class="cap">- <tspan class="cap-b">Encoding:</tspan> N^2 point vars + 4-clauses + Sinz counter (&gt;= m); no symbreak.</text>')
    add('  <text x="548" y="482" class="cap">- <tspan class="cap-b">Open target:</tspan> sq-axis_n14_m113.cnf (16,381 vars, 33,301 clauses).</text>')

    add("</svg>")
    return "\n".join(els) + "\n"


def main() -> None:
    svg = build_svg()
    out = ROOT / "diagram.svg"
    out.write_text(svg, encoding="utf-8")
    ET.parse(out)
    print(f"Wrote and XML-validated {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
