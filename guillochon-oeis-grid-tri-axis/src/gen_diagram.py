#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-grid-tri-axis.

Renders the independently verified side-16 triangular-grid frontier lower-bound configuration
with 54 painted points and ZERO grid-aligned equilateral triangles (upward or downward), while
highlighting a legal tilted equilateral triangle present in the solution. Decoded directly
from `solutions/tri-axis_n16_m54.model.xz` (solved from scratch by Frobenius in 2.50 s).
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


def count_axis_tris(painted: set[tuple[int, int]], n: int) -> int:
    P = {(x, y) for y in range(n) for x in range(n - y)}
    bad = 0
    for x, y in P:
        for s in range(1, n):
            up = [(x, y), (x + s, y), (x, y + s)]
            if all(p in painted for p in up):
                bad += 1
            down = [(x + s, y), (x, y + s), (x + s, y + s)]
            if all(p in painted for p in down):
                bad += 1
    return bad


def find_tilted_tris(painted: set[tuple[int, int]]) -> list[tuple[tuple[int, int], ...]]:
    pl = sorted(painted)
    found: list[tuple[int, tuple[tuple[int, int], ...]]] = []
    seen = set()
    for i, p in enumerate(pl):
        for q in pl[i + 1 :]:
            a, b = q[0] - p[0], q[1] - p[1]
            for ra, rb in ((-b, a + b), (a + b, -a)):
                r = (p[0] + ra, p[1] + rb)
                if r in painted:
                    tri = tuple(sorted((p, q, r)))
                    if tri in seen:
                        continue
                    sides = [(tri[j][0] - tri[k][0], tri[j][1] - tri[k][1]) for j, k in ((1, 0), (2, 0), (2, 1))]
                    aligned = all(dx == 0 or dy == 0 or dx == -dy for dx, dy in sides)
                    if not aligned:
                        seen.add(tri)
                        d2 = a * a + a * b + b * b
                        found.append((d2, tri))
    found.sort(key=lambda t: (t[0], t[1]))
    return [tri for _, tri in found]


def count_all_axis_tris(n: int) -> int:
    P = {(x, y) for y in range(n) for x in range(n - y)}
    cnt = 0
    for x, y in P:
        for s in range(1, n):
            if (x + s, y) in P and (x, y + s) in P:
                cnt += 1
            if (x + s, y) in P and (x, y + s) in P and (x + s, y + s) in P:
                cnt += 1
    return cnt


def build_svg() -> str:
    meta = json.loads(
        (ROOT / "src/upstream/sequences/point-patterns/cnf/tri-axis_n16_m54.cnf.map.json").read_text(encoding="utf-8")
    )
    tv = read_true_vars(ROOT / "solutions/tri-axis_n16_m54.model.xz")
    pts = [tuple(p) for p in meta["points"]]
    painted = {p for i, p in enumerate(pts) if (i + 1) in tv}
    n = meta["n"]
    assert n == 16 and len(painted) == 54 and count_axis_tris(painted, n) == 0, "Invalid tri-axis model!"
    tilted = find_tilted_tris(painted)
    assert tilted, "Expected legal tilted triangles in tri-axis_n16_m54"
    # Pick a clean medium-sized tilted triangle (d2 == 7 or 13 if available)
    sample_tri = next(
        (t for t in tilted if 7 <= (t[1][0] - t[0][0]) ** 2 + (t[1][0] - t[0][0]) * (t[1][1] - t[0][1]) + (t[1][1] - t[0][1]) ** 2 <= 19),
        tilted[0],
    )
    n_forb_16 = count_all_axis_tris(16)

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
    add('  <text x="24" y="33" class="title">OEIS A227308 / A227116 — Triangular Grid Avoiding Axis-Aligned Triangles (tri-axis)</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum painted points on a side-N triangular lattice avoiding upward and downward grid-aligned equilateral triangles</text>')
    add('  <rect x="764" y="14" width="172" height="24" rx="12" fill="#d97706"/>')
    add('  <text x="850" y="30" text-anchor="middle" class="badge">OPEN: N=16, m=55?</text>')

    # Left Card: Verified Side-16 Frontier LB (54 painted points)
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius Side-16 Frontier LB: 54 Painted Points (2.50 s)</text>')
    add(f'  <text x="36" y="106" class="psub">solutions/tri-axis_n16_m54.model.xz | 0 grid-aligned tris ({len(tilted)} legal tilted tris)</text>')

    step_x = 26.2
    step_y = step_x * math.sqrt(3) / 2.0
    base_w = (n - 1) * step_x
    ox = 20 + (496 - base_w) / 2.0
    oy = 460.0

    def pt_xy(x: int, y: int) -> tuple[float, float]:
        return ox + (x + 0.5 * y) * step_x, oy - y * step_y

    top_x, top_y = pt_xy(0, n - 1)
    add(f'  <polygon points="{ox:.1f},{oy:.1f} {ox+base_w:.1f},{oy:.1f} {top_x:.1f},{top_y:.1f}" fill="#fffbeb" fill-opacity="0.55" stroke="#fcd34d" stroke-width="1.1"/>')
    for k in range(n):
        p1, p2 = pt_xy(0, k), pt_xy(n - 1 - k, k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')
        p1, p2 = pt_xy(k, 0), pt_xy(k, n - 1 - k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')
        p1, p2 = pt_xy(k, 0), pt_xy(0, k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.8"/>')

    # Highlight one real legal tilted equilateral triangle
    poly_s = " ".join(f"{pt_xy(x, y)[0]:.1f},{pt_xy(x, y)[1]:.1f}" for x, y in sample_tri)
    add(f'  <polygon points="{poly_s}" fill="#10b981" fill-opacity="0.18" stroke="#059669" stroke-width="2.2" stroke-dasharray="5,3"/>')

    sample_set = set(sample_tri)
    for (x, y) in pts:
        px, py = pt_xy(x, y)
        if (x, y) in painted:
            if (x, y) in sample_set:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="6.8" fill="#059669" stroke="#064e3b" stroke-width="1.4"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="6.1" fill="#d97706" stroke="#78350f" stroke-width="1.2"/>')
        else:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.6" fill="#cbd5e1"/>')

    add('  <circle cx="52" cy="485" r="5.5" fill="#d97706" stroke="#78350f" stroke-width="1.1"/>')
    add('  <text x="63" y="489" class="cap"><tspan class="cap-b">54 painted</tspan> (39.7%)</text>')
    add('  <circle cx="195" cy="485" r="5.5" fill="#059669" stroke="#064e3b" stroke-width="1.1"/>')
    add('  <text x="206" y="489" class="cap"><tspan class="cap-b">Legal tilted equilateral triangle</tspan> (allowed)</text>')

    # Right Top Card: Forbidden Axis (Up+Down) vs Allowed Tilted
    add('  <rect x="532" y="68" width="408" height="214" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Forbidden vs. Allowed Triangle Orientations</text>')
    add('  <text x="548" y="106" class="psub">Upward and downward grid-aligned forbidden; tilted triangles allowed</text>')

    mn = 6
    msx = 24.5
    msy = msx * math.sqrt(3) / 2.0
    mox, moy = 554.0, 250.0

    def mpt(x: int, y: int) -> tuple[float, float]:
        return mox + (x + 0.5 * y) * msx, moy - y * msy

    up_forb = [(0, 0), (1, 0), (0, 1)]
    dn_forb = [(1, 3), (0, 4), (1, 4)]
    ok_tilt = [(3, 0), (4, 1), (2, 2)]

    for tri in (up_forb, dn_forb):
        pts_s = " ".join(f"{mpt(x, y)[0]:.1f},{mpt(x, y)[1]:.1f}" for x, y in tri)
        add(f'  <polygon points="{pts_s}" fill="#fee2e2" fill-opacity="0.65" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,2"/>')
    pts_ok = " ".join(f"{mpt(x, y)[0]:.1f},{mpt(x, y)[1]:.1f}" for x, y in ok_tilt)
    add(f'  <polygon points="{pts_ok}" fill="#d1fae5" fill-opacity="0.55" stroke="#059669" stroke-width="2"/>')

    bad_pts = set(up_forb + dn_forb)
    ok_pts = set(ok_tilt)
    for y in range(mn):
        for x in range(mn - y):
            px, py = mpt(x, y)
            if (x, y) in bad_pts:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.2" fill="#dc2626" stroke="#7f1d1d" stroke-width="1"/>')
            elif (x, y) in ok_pts:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.2" fill="#059669" stroke="#064e3b" stroke-width="1"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#94a3b8"/>')

    tx = 706
    add(f'  <text x="{tx}" y="138" class="cap-b" fill="#dc2626">FORBIDDEN (red dashed):</text>')
    add(f'  <text x="{tx}" y="156" class="cap">- Upward grid-aligned</text>')
    add(f'  <text x="{tx}" y="173" class="cap">- Downward grid-aligned</text>')
    add(f'  <text x="{tx}" y="195" class="cap-b" fill="#059669">ALLOWED (green solid):</text>')
    add(f'  <text x="{tx}" y="212" class="cap">- Tilted equilateral triangles</text>')
    add(f'  <text x="{tx}" y="234" class="cap-b">Forbidden 3-Clause Count:</text>')
    add(f'  <text x="{tx}" y="251" class="cap">{n_forb_16:,} axis-aligned triangles on</text>')
    add(f'  <text x="{tx}" y="266" class="cap">side N = 16 (vs 3,060 in tri-any).</text>')

    # Right Bottom Card: OEIS A227308 / A227116 Ladder
    add('  <rect x="532" y="294" width="408" height="206" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="316" class="ptitle">OEIS A227308 / A227116 Ladder &amp; Open Frontier (8 CNFs)</text>')
    add('  <text x="548" y="332" class="psub">Known optimal N &lt;= 15; N = 16 LB 54 found via SA &amp; Frobenius (2.50 s)</text>')

    rungs = [
        ("N=13", "39", "39 SAT / 40 UNSAT", "#059669", "#ecfdf5"),
        ("N=14", "44", "44 SAT / 45 UNSAT", "#059669", "#ecfdf5"),
        ("N=15", "49", "49 SAT / 50 UNSAT", "#d97706", "#fffbeb"),
        ("N=16", "54+", "54 SAT / 55 OPEN", "#dc2626", "#fef2f2"),
    ]
    rx0, rw, rg = 548, 90, 6
    for i, (nl, ml, sub, sc, fc) in enumerate(rungs):
        x = rx0 + i * (rw + rg)
        add(f'  <rect x="{x}" y="348" width="{rw}" height="74" rx="7" fill="{fc}" stroke="{sc}" stroke-width="1.3"/>')
        add(f'  <text x="{x+rw/2:.1f}" y="368" text-anchor="middle" class="mono" fill="{sc}">{nl}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="393" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700" fill="{sc}">{ml}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="413" text-anchor="middle" font-family="ui-monospace,monospace" font-size="7.8" fill="#475569">{sub}</text>')

    add('  <text x="548" y="446" class="cap">- <tspan class="cap-b">Complementary A227116(N)</tspan> = N(N+1)/2 - A227308(N).</text>')
    add('  <text x="548" y="464" class="cap">- <tspan class="cap-b">Verified models:</tspan> N=13 (39), N=14 (44), N=16 (54) in solutions/.</text>')
    add('  <text x="548" y="482" class="cap">- <tspan class="cap-b">Open target:</tspan> tri-axis_n16_m55.cnf (11,071 vars, 22,912 clauses).</text>')

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
