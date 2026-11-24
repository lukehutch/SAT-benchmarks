#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-grid-tri-up.

Renders the independently verified side-14 triangular-grid frontier lower-bound configuration
with 46 painted points (+6 jump over side 13 = 40!) and ZERO upward grid-aligned equilateral
triangles, while highlighting a legal downward grid-aligned triangle present in the solution.
Decoded directly from `solutions/tri-up_n14_m46.model.xz` (solved by Frobenius in 57.10 s).
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


def count_upward_tris(painted: set[tuple[int, int]], n: int) -> int:
    P = {(x, y) for y in range(n) for x in range(n - y)}
    bad = 0
    for x, y in P:
        for s in range(1, n):
            if (x, y) in painted and (x + s, y) in painted and (x, y + s) in painted:
                bad += 1
    return bad


def find_downward_tris(painted: set[tuple[int, int]], n: int) -> list[tuple[int, tuple[tuple[int, int], ...]]]:
    P = {(x, y) for y in range(n) for x in range(n - y)}
    found = []
    for x, y in sorted(P):
        for s in range(1, n):
            tri = ((x + s, y), (x, y + s), (x + s, y + s))
            if all(p in painted for p in tri):
                found.append((s, tri))
    found.sort(key=lambda t: (-t[0], t[1]))
    return found


def count_all_upward_tris(n: int) -> int:
    # C(n+1, 3) = (n-1)*n*(n+1)/6
    P = {(x, y) for y in range(n) for x in range(n - y)}
    return sum(1 for x, y in P for s in range(1, n) if (x + s, y) in P and (x, y + s) in P)


def build_svg() -> str:
    meta = json.loads(
        (ROOT / "src/upstream/sequences/point-patterns/cnf/tri-up_n14_m46.cnf.map.json").read_text(encoding="utf-8")
    )
    tv = read_true_vars(ROOT / "solutions/tri-up_n14_m46.model.xz")
    pts = [tuple(p) for p in meta["points"]]
    painted = {p for i, p in enumerate(pts) if (i + 1) in tv}
    n = meta["n"]
    assert n == 14 and len(painted) == 46 and count_upward_tris(painted, n) == 0, "Invalid tri-up model!"
    down_tris = find_downward_tris(painted, n)
    assert down_tris, "Expected legal downward grid-aligned triangles in tri-up_n14_m46"
    # Pick a crisp medium downward triangle (side 2 or 3 if available)
    sample_down = next((t for s, t in down_tris if 2 <= s <= 4), down_tris[0][1])
    n_forb_14 = count_all_upward_tris(14)

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
    add('  <text x="24" y="33" class="title">OEIS A157795 / A319158 — Triangular Grid Avoiding Upward Triangles (tri-up)</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum painted points on a side-N triangular lattice avoiding upward grid-aligned triangles (downward &amp; tilted allowed)</text>')
    add('  <rect x="764" y="14" width="172" height="24" rx="12" fill="#059669"/>')
    add('  <text x="850" y="30" text-anchor="middle" class="badge">OPEN: N=14, m=47?</text>')

    # Left Card: Verified Side-14 Frontier LB (46 painted points)
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius Side-14 Frontier LB: 46 Painted Points (57.10 s)</text>')
    add(f'  <text x="36" y="106" class="psub">solutions/tri-up_n14_m46.model.xz | 0 upward tris ({len(down_tris)} legal downward tris)</text>')

    step_x = 30.2
    step_y = step_x * math.sqrt(3) / 2.0
    base_w = (n - 1) * step_x
    ox = 20 + (496 - base_w) / 2.0
    oy = 460.0

    def pt_xy(x: int, y: int) -> tuple[float, float]:
        return ox + (x + 0.5 * y) * step_x, oy - y * step_y

    top_x, top_y = pt_xy(0, n - 1)
    add(f'  <polygon points="{ox:.1f},{oy:.1f} {ox+base_w:.1f},{oy:.1f} {top_x:.1f},{top_y:.1f}" fill="#ecfdf5" fill-opacity="0.55" stroke="#6ee7b7" stroke-width="1.1"/>')
    for k in range(n):
        p1, p2 = pt_xy(0, k), pt_xy(n - 1 - k, k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')
        p1, p2 = pt_xy(k, 0), pt_xy(k, n - 1 - k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')
        p1, p2 = pt_xy(k, 0), pt_xy(0, k)
        add(f'  <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')

    # Highlight one real legal downward triangle in the solution
    poly_s = " ".join(f"{pt_xy(x, y)[0]:.1f},{pt_xy(x, y)[1]:.1f}" for x, y in sample_down)
    add(f'  <polygon points="{poly_s}" fill="#0ea5e9" fill-opacity="0.18" stroke="#0284c7" stroke-width="2.2" stroke-dasharray="5,3"/>')

    sample_set = set(sample_down)
    for (x, y) in pts:
        px, py = pt_xy(x, y)
        if (x, y) in painted:
            if (x, y) in sample_set:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="7.4" fill="#0284c7" stroke="#0c4a6e" stroke-width="1.5"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="6.8" fill="#059669" stroke="#064e3b" stroke-width="1.3"/>')
        else:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="3.0" fill="#cbd5e1"/>')

    add('  <circle cx="52" cy="485" r="5.5" fill="#059669" stroke="#064e3b" stroke-width="1.1"/>')
    add('  <text x="63" y="489" class="cap"><tspan class="cap-b">46 painted</tspan> (43.8% of 105)</text>')
    add('  <circle cx="222" cy="485" r="5.5" fill="#0284c7" stroke="#0c4a6e" stroke-width="1.1"/>')
    add('  <text x="233" y="489" class="cap"><tspan class="cap-b">Legal downward triangle</tspan> (allowed)</text>')

    # Right Top Card: Forbidden Upward vs Allowed Downward + Tilted
    add('  <rect x="532" y="68" width="408" height="214" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Forbidden vs. Allowed Triangle Orientations</text>')
    add('  <text x="548" y="106" class="psub">ONLY upward grid-aligned triangles forbidden; downward &amp; tilted OK</text>')

    mn = 6
    msx = 24.5
    msy = msx * math.sqrt(3) / 2.0
    mox, moy = 554.0, 250.0

    def mpt(x: int, y: int) -> tuple[float, float]:
        return mox + (x + 0.5 * y) * msx, moy - y * msy

    up_forb = [(0, 0), (2, 0), (0, 2)]
    dn_ok = [(1, 3), (0, 4), (1, 4)]
    tilt_ok = [(3, 0), (5, 0), (4, 1)]  # wait: use true tilted: (3,0)-(5,0) is upward! Fix to true tilted:
    # Check true tilted: p=(3,0), q=(4,1) -> (a,b)=(1,1), rot +60 (-1,2) -> r=(2,2)
    tilt_ok = [(3, 0), (4, 1), (2, 2)]

    pts_f = " ".join(f"{mpt(x, y)[0]:.1f},{mpt(x, y)[1]:.1f}" for x, y in up_forb)
    add(f'  <polygon points="{pts_f}" fill="#fee2e2" fill-opacity="0.65" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,2"/>')
    for tri in (dn_ok, tilt_ok):
        pts_ok = " ".join(f"{mpt(x, y)[0]:.1f},{mpt(x, y)[1]:.1f}" for x, y in tri)
        add(f'  <polygon points="{pts_ok}" fill="#d1fae5" fill-opacity="0.58" stroke="#059669" stroke-width="2"/>')

    bad_pts = set(up_forb)
    ok_pts = set(dn_ok + tilt_ok)
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
    add(f'  <text x="{tx}" y="156" class="cap">- Upward grid-aligned triangles</text>')
    add(f'  <text x="{tx}" y="178" class="cap-b" fill="#059669">ALLOWED (green solid):</text>')
    add(f'  <text x="{tx}" y="196" class="cap">- Downward grid-aligned</text>')
    add(f'  <text x="{tx}" y="213" class="cap">- All tilted equilateral triangles</text>')
    add(f'  <text x="{tx}" y="236" class="cap-b">Forbidden 3-Clause Count:</text>')
    add(f'  <text x="{tx}" y="253" class="cap">C(N+1, 3) = {n_forb_14:,} upward triangles</text>')
    add(f'  <text x="{tx}" y="268" class="cap">on side N = 14 (105 points).</text>')

    # Right Bottom Card: OEIS A157795 / A319158 Ladder
    add('  <rect x="532" y="294" width="408" height="206" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="316" class="ptitle">OEIS A157795(N-1) / A319158(N) Ladder &amp; Frontier (8 CNFs)</text>')
    add('  <text x="548" y="332" class="psub">Known optimal N &lt;= 13; N = 14 LB 46 (+6 jump!) verified via SA &amp; Frobenius</text>')

    rungs = [
        ("N=11", "31", "31 SAT / 32 UNSAT*", "#059669", "#ecfdf5"),
        ("N=12", "35", "35 SAT / 36 UNSAT", "#059669", "#ecfdf5"),
        ("N=13", "40", "40 SAT / 41 UNSAT", "#059669", "#ecfdf5"),
        ("N=14", "46+", "46 SAT / 47 OPEN", "#dc2626", "#fef2f2"),
    ]
    rx0, rw, rg = 548, 90, 6
    for i, (nl, ml, sub, sc, fc) in enumerate(rungs):
        x = rx0 + i * (rw + rg)
        add(f'  <rect x="{x}" y="348" width="{rw}" height="74" rx="7" fill="{fc}" stroke="{sc}" stroke-width="1.3"/>')
        add(f'  <text x="{x+rw/2:.1f}" y="368" text-anchor="middle" class="mono" fill="{sc}">{nl}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="393" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700" fill="{sc}">{ml}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="413" text-anchor="middle" font-family="ui-monospace,monospace" font-size="7.6" fill="#475569">{sub}</text>')

    add('  <text x="548" y="446" class="cap">- <tspan class="cap-b">*Certified proof:</tspan> tri-up_n11_m32.lrat.xz (cake_lpr s VERIFIED UNSAT).</text>')
    add('  <text x="548" y="464" class="cap">- <tspan class="cap-b">Calibration #1:</tspan> Frobenius solves 4/4 in 15.34 s total (fastest of 5).</text>')
    add('  <text x="548" y="482" class="cap">- <tspan class="cap-b">Open target:</tspan> tri-up_n14_m47.cnf (6,137 vars, 12,565 clauses).</text>')

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
