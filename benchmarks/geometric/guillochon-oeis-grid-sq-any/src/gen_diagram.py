#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-grid-sq-any.

Renders the independently verified 8x8 square-grid configuration with 34 painted points
and ZERO squares of ANY orientation (axis-aligned or tilted), decoded directly from
`solutions/sq-any_n8_m34.model.xz` + `sq-any_n8_m34.cnf.map.json`.
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


def count_any_squares(painted: set[tuple[int, int]]) -> int:
    pl = sorted(painted)
    bad = set()
    for i, p in enumerate(pl):
        for q in pl[i + 1 :]:
            a, b = q[0] - p[0], q[1] - p[1]
            for ra, rb in ((-b, a), (b, -a)):
                r, s = (q[0] + ra, q[1] + rb), (p[0] + ra, p[1] + rb)
                if r in painted and s in painted:
                    bad.add(tuple(sorted((p, q, r, s))))
    return len(bad)


def build_svg() -> str:
    meta = json.loads(
        (ROOT / "src/upstream/sequences/point-patterns/cnf/sq-any_n8_m34.cnf.map.json").read_text(encoding="utf-8")
    )
    tv = read_true_vars(ROOT / "solutions/sq-any_n8_m34.model.xz")
    pts = [tuple(p) for p in meta["points"]]
    painted = {p for i, p in enumerate(pts) if (i + 1) in tv}
    n = meta["n"]
    assert n == 8 and len(painted) == 34 and count_any_squares(painted) == 0, "Invalid sq-any model!"

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
    add('  <text x="24" y="33" class="title">OEIS A240443 — Square Grid Avoiding Arbitrary-Orientation Squares (sq-any)</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum painted points on an N x N square lattice containing no 4 corners of ANY square (axis-aligned or tilted)</text>')
    add('  <rect x="768" y="14" width="168" height="24" rx="12" fill="#2563eb"/>')
    add('  <text x="852" y="30" text-anchor="middle" class="badge">OPEN: N=11, m=59?</text>')

    # Left Card: Verified 8x8 Grid (34 painted points)
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius 8x8 Certificate: 34 Painted Points (0.07 s)</text>')
    add('  <text x="36" y="106" class="psub">solutions/sq-any_n8_m34.model.xz | exact optimal A240443(8) = 34 | 0 squares</text>')

    step = 44.0
    gw = (n - 1) * step
    gx0 = 20 + (496 - gw) / 2.0
    gy0 = 140.0

    # Grid lines
    for i in range(n):
        pos_x = gx0 + i * step
        pos_y = gy0 + i * step
        add(f'  <line x1="{pos_x:.1f}" y1="{gy0:.1f}" x2="{pos_x:.1f}" y2="{gy0+gw:.1f}" stroke="#cbd5e1" stroke-width="1.1"/>')
        add(f'  <line x1="{gx0:.1f}" y1="{pos_y:.1f}" x2="{gx0+gw:.1f}" y2="{pos_y:.1f}" stroke="#cbd5e1" stroke-width="1.1"/>')
        add(f'  <text x="{pos_x:.1f}" y="{gy0+gw+22:.1f}" text-anchor="middle" class="mono-sm">{i}</text>')
        add(f'  <text x="{gx0-16:.1f}" y="{gy0+(n-1-i)*step+3.5:.1f}" text-anchor="end" class="mono-sm">{i}</text>')

    # Points (y upward)
    for (x, y) in pts:
        px = gx0 + x * step
        py = gy0 + (n - 1 - y) * step
        if (x, y) in painted:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="10.2" fill="#2563eb" stroke="#1e3a8a" stroke-width="1.6"/>')
            add(f'  <circle cx="{px-2.6:.1f}" cy="{py-2.6:.1f}" r="2.2" fill="#93c5fd" fill-opacity="0.7"/>')
        else:
            add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.0" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>')

    # Legend
    add('  <circle cx="98" cy="485" r="6.5" fill="#2563eb" stroke="#1e3a8a" stroke-width="1.3"/>')
    add('  <text x="111" y="489" class="cap"><tspan class="cap-b">34 painted points</tspan> (53.1% of 64)</text>')
    add('  <circle cx="322" cy="485" r="4.5" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>')
    add('  <text x="333" y="489" class="cap"><tspan class="cap-b">30 unpainted</tspan></text>')

    # Right Top Card: Forbidden Pattern Schematic (Axis + Tilted BOTH forbidden)
    add('  <rect x="532" y="68" width="408" height="214" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Forbidden Shapes: Axis-Aligned AND Tilted Squares</text>')
    add('  <text x="548" y="106" class="psub">Every side vector (a, b) with a &gt; 0, b &gt;= 0 generates a 4-literal clause</text>')

    ms = 28.0
    mx0, my0 = 556.0, 126.0
    for i in range(5):
        add(f'  <line x1="{mx0+i*ms:.1f}" y1="{my0:.1f}" x2="{mx0+i*ms:.1f}" y2="{my0+4*ms:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        add(f'  <line x1="{mx0:.1f}" y1="{my0+i*ms:.1f}" x2="{mx0+4*ms:.1f}" y2="{my0+i*ms:.1f}" stroke="#e2e8f0" stroke-width="1"/>')

    def mp(x: int, y: int) -> tuple[float, float]:
        return mx0 + x * ms, my0 + (4 - y) * ms

    # Forbidden axis square: (0,0)-(1,0)-(1,1)-(0,1)
    sq1 = [mp(0, 0), mp(1, 0), mp(1, 1), mp(0, 1)]
    pts1 = " ".join(f"{x:.1f},{y:.1f}" for x, y in sq1)
    add(f'  <polygon points="{pts1}" fill="#fee2e2" fill-opacity="0.55" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,2"/>')
    # Forbidden tilted square: (2,0)-(4,1)-(3,3)-(1,2), vector (a,b)=(2,1)
    sq2 = [mp(2, 0), mp(4, 1), mp(3, 3), mp(1, 2)]
    pts2 = " ".join(f"{x:.1f},{y:.1f}" for x, y in sq2)
    add(f'  <polygon points="{pts2}" fill="#fecaca" fill-opacity="0.55" stroke="#b91c1c" stroke-width="2" stroke-dasharray="4,2"/>')

    for x in range(5):
        for y in range(5):
            px, py = mp(x, y)
            in_bad = (x, y) in {(0, 0), (1, 0), (1, 1), (0, 1), (2, 0), (4, 1), (3, 3), (1, 2)}
            if in_bad:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="4.8" fill="#dc2626" stroke="#7f1d1d" stroke-width="1.1"/>')
            else:
                add(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#94a3b8"/>')

    tx = 696
    add(f'  <text x="{tx}" y="138" class="cap-b" fill="#dc2626">Both Forbidden (X):</text>')
    add(f'  <text x="{tx}" y="157" class="cap">- Axis-aligned: (a, b) = (s, 0)</text>')
    add(f'  <text x="{tx}" y="174" class="cap">- Tilted: (a, b) = (2, 1), rot 90 deg</text>')
    add(f'  <text x="{tx}" y="191" class="cap">  gives corners +(a,b), +(a-b,a+b),</text>')
    add(f'  <text x="{tx}" y="206" class="cap">  +(-b,a).</text>')
    add(f'  <text x="{tx}" y="228" class="cap-b">Count of Forbidden Squares:</text>')
    add(f'  <text x="{tx}" y="245" class="cap">N^2(N^2 - 1)/12 = 336 at N=8,</text>')
    add(f'  <text x="{tx}" y="261" class="cap">and 1,210 forbidden squares at N=11.</text>')

    # Right Bottom Card: OEIS A240443 Ladder
    add('  <rect x="532" y="294" width="408" height="206" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="316" class="ptitle">OEIS A240443 Calibration Ladder &amp; Open Frontier (8 CNFs)</text>')
    add('  <text x="548" y="332" class="psub">Known optimal through N = 10; N = 11 lower bound 58 (Israel 2016)</text>')

    rungs = [
        ("N=8", "34", "34 SAT / 35 UNSAT", "#059669", "#ecfdf5"),
        ("N=9", "42", "42 SAT / 43 UNSAT", "#2563eb", "#eff6ff"),
        ("N=10", "50", "50 SAT / 51 UNSAT", "#2563eb", "#eff6ff"),
        ("N=11", "58+", "58 SAT / 59 OPEN", "#dc2626", "#fef2f2"),
    ]
    rx0, rw, rg = 548, 90, 6
    for i, (nl, ml, sub, sc, fc) in enumerate(rungs):
        x = rx0 + i * (rw + rg)
        add(f'  <rect x="{x}" y="348" width="{rw}" height="74" rx="7" fill="{fc}" stroke="{sc}" stroke-width="1.3"/>')
        add(f'  <text x="{x+rw/2:.1f}" y="368" text-anchor="middle" class="mono" fill="{sc}">{nl}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="393" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700" fill="{sc}">{ml}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="413" text-anchor="middle" font-family="ui-monospace,monospace" font-size="7.8" fill="#475569">{sub}</text>')

    add('  <text x="548" y="446" class="cap">- <tspan class="cap-b">Encoding:</tspan> N^2 point vars + 4-clauses + Sinz counter (&gt;= m); no symbreak.</text>')
    add('  <text x="548" y="464" class="cap">- <tspan class="cap-b">Calibration:</tspan> Frobenius solves sq-any_n8_m34 in 0.07 s (#1 of 5 solvers).</text>')
    add('  <text x="548" y="482" class="cap">- <tspan class="cap-b">Open target:</tspan> sq-any_n11_m59.cnf (7,561 vars, 16,148 clauses).</text>')

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
