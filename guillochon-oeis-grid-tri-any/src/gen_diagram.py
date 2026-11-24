#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-grid-tri-any.

Renders the independently verified side-16 triangular-grid frontier lower-bound configuration
with 36 painted points and ZERO equilateral triangles of ANY orientation (upward, downward,
or tilted), decoded directly from `solutions/tri-any_n16_m36.model.xz` (independently solved
from scratch by Frobenius in 17.05 s).
"""
from __future__ import annotations

import json
import lzma
import math
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


def count_any_equilateral(painted: set[tuple[int, int]]) -> int:
    pl = sorted(painted)
    bad = set()
    for i, p in enumerate(pl):
        for q in pl[i + 1 :]:
            a, b = q[0] - p[0], q[1] - p[1]
            for ra, rb in ((-b, a + b), (a + b, -a)):
                r = (p[0] + ra, p[1] + rb)
                if r in painted:
                    bad.add(tuple(sorted((p, q, r))))
    return len(bad)


def count_all_tris(n: int) -> int:
    P = {(x, y) for y in range(n) for x in range(n - y)}
    pl = sorted(P)
    out = set()
    for i, p in enumerate(pl):
        for q in pl[i + 1 :]:
            a, b = q[0] - p[0], q[1] - p[1]
            for ra, rb in ((-b, a + b), (a + b, -a)):
                r = (p[0] + ra, p[1] + rb)
                if r in P:
                    out.add(frozenset((p, q, r)))
    return len(out)


def build_svg() -> str:
    meta = json.loads(
        (ROOT / "src/upstream/sequences/point-patterns/cnf/tri-any_n16_m36.cnf.map.json").read_text(encoding="utf-8")
    )
    tv = read_true_vars(ROOT / "solutions/tri-any_n16_m36.model.xz")
    pts = [tuple(p) for p in meta["points"]]
    painted = {p for i, p in enumerate(pts) if (i + 1) in tv}
    n = meta["n"]
    assert n == 16 and len(painted) == 36 and count_any_equilateral(painted) == 0, "Invalid tri-any model!"
    n_forb_16 = count_all_tris(16)

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
    add('  <text x="24" y="33" class="title">OEIS A240114 / A319159 — Triangular Grid Avoiding Any Equilateral Triangle (tri-any)</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum painted points on a side-N triangular lattice avoiding every equilateral triangle (upward, downward, or tilted)</text>')
    add('  <rect x="764" y="14" width="172" height="24" rx="12" fill="#dc2626"/>')
    add('  <text x="850" y="30" text-anchor="middle" class="badge">OPEN: N=16, m=37?</text>')

    # Left Card: Verified Side-16 Frontier Lower Bound (36 painted points)
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius Side-16 Frontier LB: 36 Painted Points (17.05 s)</text>')
    add('  <text x="36" y="106" class="psub">solutions/tri-any_n16_m36.model.xz | 136 grid points | 0 equilateral triangles</text>')

    step_x = 26.2
    step_y = step_x * math.sqrt(3) / 2.0
    base_w = (n - 1) * step_x
    ox = 20 + (496 - base_w) / 2.0
    oy = 460.0

    def pt_xy(x: int, y: int) -> tuple[float, float]:
        return ox + (x + 0.5 * y) * step_x, oy - y * step_y

    # Subtle triangular boundary & lattice mesh lines
    top_x, top_y = pt_xy(0, n - 1)
    add(f'  <polygon points="{ox:.1f},{oy:.1f} {ox+base_w:.1f},{oy:.1f} {top_x:.1f},{top_y:.1f}" fill="#fff1f2" fill-opacity="0.45" stroke="#fda4af" stroke-width="1.1"/>')
    for k in range(n):
        p1, p2 = pt_xy(0, k), pt_xy(n - 1 - k, k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')
        p1, p2 = pt_xy(k, 0), pt_xy(k, n - 1 - k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')
        p1, p2 = pt_xy(k, 0), pt_xy(0, k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')

    for (x, y) in pts:
        px, py = pt_xy(x, y)
        if (x, y) in painted:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="6.3" fill="#e11d48" stroke="#881337" stroke-width="1.3"/>')
        else:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.7" fill="#cbd5e1"/>')

    add('  <circle cx="88" cy="485" r="5.5" fill="#e11d48" stroke="#881337" stroke-width="1.2"/>')
    add('  <text x="99" y="489" class="cap"><tspan class="cap-b">36 painted points</tspan> (26.5% of 136)</text>')
    add('  <circle cx="310" cy="485" r="3.2" fill="#cbd5e1"/>')
    add('  <text x="320" y="489" class="cap"><tspan class="cap-b">100 unpainted</tspan> (zero eq. triangles)</text>')

    # Right Top Card: All Three Orientations Forbidden
    add('  <rect x="532" y="68" width="408" height="214" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Forbidden Shapes: ALL Equilateral Triangles</text>')
    add('  <text x="548" y="106" class="psub">Upward, downward, and tilted (+/-60 deg axial rotation) all forbidden</text>')

    mn = 6
    msx = 24.5
    msy = msx * math.sqrt(3) / 2.0
    mox, moy = 554.0, 250.0

    def mpt(x: int, y: int) -> tuple[float, float]:
        return mox + (x + 0.5 * y) * msx, moy - y * msy

    # Draw three disjoint forbidden equilateral triangles on side-6 mini grid:
    # 1. Upward: (0,0),(1,0),(0,1)
    # 2. Downward: (1,3),(0,4),(1,4)
    # 3. Tilted: (3,0),(4,1),(2,2) -> vector (1,1), rot +60 (-1,2) => (2,2)
    tris = [
        [(0, 0), (1, 0), (0, 1)],
        [(1, 3), (0, 4), (1, 4)],
        [(3, 0), (4, 1), (2, 2)],
    ]
    t_cols = [("#fee2e2", "#dc2626"), ("#fee2e2", "#dc2626"), ("#fecdd3", "#be123c")]
    bad_pts = set()
    for tri, (fc, sc) in zip(tris, t_cols):
        pts_s = " ".join(f"{mpt(x, y)[0]:.1f},{mpt(x, y)[1]:.1f}" for x, y in tri)
        add(f'  <polygon points="{pts_s}" fill="{fc}" fill-opacity="0.62" stroke="{sc}" stroke-width="2" stroke-dasharray="4,2"/>')
        bad_pts.update(tri)

    for y in range(mn):
        for x in range(mn - y):
            px, py = mpt(x, y)
            if (x, y) in bad_pts:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.2" fill="#dc2626" stroke="#7f1d1d" stroke-width="1"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#94a3b8"/>')

    tx = 706
    add(f'  <text x="{tx}" y="138" class="cap-b" fill="#dc2626">All 3 Orientations Forbidden:</text>')
    add(f'  <text x="{tx}" y="156" class="cap">- Upward grid-aligned</text>')
    add(f'  <text x="{tx}" y="173" class="cap">- Downward grid-aligned</text>')
    add(f'  <text x="{tx}" y="190" class="cap">- Tilted (any vector (a,b) rot</text>')
    add(f'  <text x="{tx}" y="205" class="cap">  +60 deg -&gt; (-b, a+b))</text>')
    add(f'  <text x="{tx}" y="229" class="cap-b">Forbidden 3-Clause Count:</text>')
    add(f'  <text x="{tx}" y="246" class="cap">{n_forb_16:,} equilateral triangles on</text>')
    add(f'  <text x="{tx}" y="261" class="cap">side N = 16 (136 grid points).</text>')

    # Right Bottom Card: OEIS A240114 / A319159 Ladder
    add('  <rect x="532" y="294" width="408" height="206" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="316" class="ptitle">OEIS A240114 / A319159 Ladder &amp; Open Frontier (8 CNFs)</text>')
    add('  <text x="548" y="332" class="psub">Known optimal N &lt;= 15; N = 16 LB 36 via SA &amp; Frobenius (17.05 s)</text>')

    rungs = [
        ("N=13", "28", "28 SAT / 29 UNSAT", "#059669", "#ecfdf5"),
        ("N=14", "31", "31 SAT / 32 UNSAT", "#2563eb", "#eff6ff"),
        ("N=15", "34", "34 SAT / 35 UNSAT", "#059669", "#ecfdf5"),
        ("N=16", "36+", "36 SAT / 37 OPEN", "#dc2626", "#fef2f2"),
    ]
    rx0, rw, rg = 548, 90, 6
    for i, (nl, ml, sub, sc, fc) in enumerate(rungs):
        x = rx0 + i * (rw + rg)
        add(f'  <rect x="{x}" y="348" width="{rw}" height="74" rx="7" fill="{fc}" stroke="{sc}" stroke-width="1.3"/>')
        add(f'  <text x="{x+rw/2:.1f}" y="368" text-anchor="middle" class="mono" fill="{sc}">{nl}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="393" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700" fill="{sc}">{ml}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="413" text-anchor="middle" font-family="ui-monospace,monospace" font-size="7.8" fill="#475569">{sub}</text>')

    add('  <text x="548" y="446" class="cap">- <tspan class="cap-b">Complementary A319159(N-1)</tspan> = N(N+1)/2 - A240114(N).</text>')
    add('  <text x="548" y="464" class="cap">- <tspan class="cap-b">Verified models:</tspan> N=13 (28), N=15 (34), N=16 (36) in solutions/.</text>')
    add('  <text x="548" y="482" class="cap">- <tspan class="cap-b">Open target:</tspan> tri-any_n16_m37.cnf (13,501 vars, 29,826 clauses).</text>')

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
