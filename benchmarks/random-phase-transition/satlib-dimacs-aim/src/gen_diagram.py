#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-dimacs-aim."""
from __future__ import annotations

import collections
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_aim() -> dict[tuple[int, str], dict[str, int]]:
    grid: dict[tuple[int, str], dict[str, int]] = collections.defaultdict(lambda: {"SAT": 0, "UNSAT": 0})
    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            fn, v = line.split("\t")[:2]
            parts = fn.replace(".cnf", "").split("-")
            n = int(parts[1])
            ratio = parts[2].replace("_", ".")
            grid[(n, ratio)][v.strip()] += 1
    return grid


def psat_uniform(alpha: float) -> float:
    return 1.0 / (1.0 + math.exp((alpha - 4.267) / 0.12))


def main() -> None:
    grid = parse_aim()
    total_sat = sum(d["SAT"] for d in grid.values())
    total_unsat = sum(d["UNSAT"] for d in grid.values())
    total = total_sat + total_unsat

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB AIM artificial random 3-SAT diagram">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB Artificial Random 3-SAT — Iwama–Miyano–Asahiro (AIM)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">Planted unique-model SAT ("yes1") &amp; minimal-UNSAT ("no") far below &amp; above α_c ≈ 4.267 · {total} instances ({total_sat} SAT / {total_unsat} UNSAT)</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: Phase-Space Contrast against Uniform Random 3-SAT
    lx, ly, lw, lh = 24, 78, 524, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">The AIM Paradox: Defying the Uniform 3-SAT Phase Transition</text>')
    a(f'<text x="{lx+16}" y="{ly+40}" font-size="10.5" fill="#475569">Artificial constructions place UNSATs at α = 1.6, 2.0 and unique SATs up to α = 6.0</text>')

    px0, py0, px1, py1 = 76, 134, 526, 294
    pw, ph = px1 - px0, py1 - py0
    a_min, a_max = 1.0, 6.5

    def ax(al: float) -> float:
        return px0 + (al - a_min) / (a_max - a_min) * pw

    def ay(v: float) -> float:
        return py1 - v * ph

    # Shaded regions: Uniform SAT side vs Uniform UNSAT side
    xc = ax(4.267)
    a(f'<rect x="{px0}" y="{py0}" width="{xc-px0:.1f}" height="{ph}" fill="#eff6ff" fill-opacity="0.55"/>')
    a(f'<rect x="{xc:.1f}" y="{py0}" width="{px1-xc:.1f}" height="{ph}" fill="#fef2f2" fill-opacity="0.45"/>')

    # Grid lines
    for frac in (0.0, 0.5, 1.0):
        yy = ay(frac)
        a(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px1}" y2="{yy:.1f}" stroke="#cbd5e1" stroke-width="0.7" stroke-dasharray="3,3"/>')
        a(f'<text x="{px0-8}" y="{yy+3.5:.1f}" text-anchor="end" font-size="9.5" fill="#475569">{frac:.1f}</text>')

    for tick in (1.0, 1.6, 2.0, 3.0, 3.4, 4.27, 5.0, 6.0):
        xx = ax(tick)
        a(f'<line x1="{xx:.1f}" y1="{py1}" x2="{xx:.1f}" y2="{py1+5}" stroke="#64748b" stroke-width="1"/>')
        lbl = "4.27" if abs(tick - 4.27) < 0.05 else f"{tick:.1f}"
        fw = "700" if tick in (1.6, 2.0, 3.4, 6.0) else "400"
        col = "#0f172a" if tick in (1.6, 2.0, 3.4, 6.0) else "#64748b"
        a(f'<text x="{xx:.1f}" y="{py1+17}" text-anchor="middle" font-size="9.2" font-weight="{fw}" fill="{col}">{lbl}</text>')

    a(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="none" stroke="#94a3b8" stroke-width="1.2"/>')
    a(f'<line x1="{xc:.1f}" y1="{py0+22}" x2="{xc:.1f}" y2="{py1}" stroke="#d97706" stroke-width="1.5" stroke-dasharray="5,3"/>')
    a(f'<rect x="{xc-52:.1f}" y="{py0+5}" width="104" height="17" rx="4" fill="#fffbeb" stroke="#f59e0b" stroke-width="0.9"/>')
    a(f'<text x="{xc:.1f}" y="{py0+16.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#b45309">Uniform α_c ≈ 4.27</text>')

    # Uniform 3-SAT reference curve (dashed gray-blue)
    pts = [(ax(a_min + (a_max - a_min) * i / 80.0), ay(psat_uniform(a_min + (a_max - a_min) * i / 80.0))) for i in range(81)]
    d_path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    a(f'<path d="{d_path}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6,3"/>')
    a(f'<text x="{ax(2.68):.1f}" y="{ay(0.90):.1f}" text-anchor="middle" font-size="9.5" fill="#64748b">Uniform 3-SAT P(SAT) ≈ 1</text>')
    a(f'<text x="{ax(5.35):.1f}" y="{ay(0.11):.1f}" text-anchor="middle" font-size="9.5" fill="#64748b">Uniform ≈ 0</text>')

    # AIM markers at exact ratios (staggered label offsets at 1.6 vs 2.0 so labels never touch)
    aim_markers = [
        (1.6, 0.72, "SAT", "yes1 (12)", -10, "middle"),
        (1.6, 0.28, "UNSAT", "no (12)", -10, "middle"),
        (2.0, 0.72, "SAT", "yes1 (12)", 10, "middle"),
        (2.0, 0.28, "UNSAT", "no (12)", 10, "middle"),
        (3.4, 0.72, "SAT", "yes1 (12)", 0, "middle"),
        (6.0, 0.72, "SAT", "yes1 (12)", 0, "middle"),
    ]
    for al, yv, kind, tag, dx_lbl, anc in aim_markers:
        xx, yy = ax(al), ay(yv)
        a(f'<line x1="{xx:.1f}" y1="{py0}" x2="{xx:.1f}" y2="{py1}" stroke="#cbd5e1" stroke-width="0.8" stroke-dasharray="2,2"/>')
        if kind == "SAT":
            a(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="6.5" fill="#059669" stroke="#ffffff" stroke-width="1.6"/>')
            a(f'<text x="{xx+dx_lbl:.1f}" y="{yy-11:.1f}" text-anchor="{anc}" font-size="8.8" font-weight="700" fill="#047857">{tag}</text>')
        else:
            r = 6.8
            a(f'<polygon points="{xx:.1f},{yy-r:.1f} {xx+r:.1f},{yy:.1f} {xx:.1f},{yy+r:.1f} {xx-r:.1f},{yy:.1f}" fill="#dc2626" stroke="#ffffff" stroke-width="1.5"/>')
            a(f'<text x="{xx+dx_lbl:.1f}" y="{yy+17:.1f}" text-anchor="{anc}" font-size="8.8" font-weight="700" fill="#b91c1c">{tag}</text>')

    # Callout boxes explaining the two anomalies
    a(f'<rect x="{ax(1.22):.1f}" y="{ay(0.55):.1f}" width="112" height="24" rx="4" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
    a(f'<text x="{ax(1.22)+56:.1f}" y="{ay(0.55)+15:.1f}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#b91c1c">Low-α UNSAT (0.37×)</text>')

    a(f'<rect x="{ax(4.65):.1f}" y="{ay(0.55):.1f}" width="124" height="24" rx="4" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="0.9"/>')
    a(f'<text x="{ax(4.65)+62:.1f}" y="{ay(0.55)+15:.1f}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#047857">High-α Unique SAT (1.4×)</text>')

    a(f'<text x="42" y="{(py0+py1)/2:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#475569" transform="rotate(-90 42 {(py0+py1)/2:.1f})">Uniform P(SAT)</text>')
    a(f'<text x="{(px0+px1)/2:.1f}" y="{py1+32}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e293b">Clause-to-Variable Ratio α = m / n</text>')

    # Bottom Mechanism Box inside Left Panel
    mx, my, mw, mh = lx + 14, 336, lw - 28, 90
    a(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{mx+12}" y="{my+19}" font-size="11.5" font-weight="700" fill="#0f172a">How Iwama–Miyano–Asahiro Plant Unique SAT &amp; Low-α UNSAT</text>')
    a(f'<text x="{mx+12}" y="{my+36}" font-size="10" fill="#334155">• <tspan font-weight="700" fill="#059669">yes1 (48 SAT):</tspan> Pick a unique target assignment σ*, iteratively add 3-clauses eliminating</text>')
    a(f'<text x="{mx+22}" y="{my+50}" font-size="10" fill="#334155">all other models until |Sol(F)| = 1 with ultra-uniform variable degrees (Deg CV ≈ 0.03!).</text>')
    a(f'<text x="{mx+12}" y="{my+67}" font-size="10" fill="#334155">• <tspan font-weight="700" fill="#dc2626">no (24 UNSAT):</tspan> Plant a hidden contradictory core at α = 1.6–2.0 (ρ_crit = 0.37–0.47×)</text>')
    a(f'<text x="{mx+22}" y="{my+81}" font-size="10" fill="#334155">so local search stalls while CDCL learns the sparse contradiction in 1–5 ms.</text>')

    # Right Panel: Parsed 3 × 4 Instance Grid (n ∈ {50, 100, 200} × α ∈ {1.6, 2.0, 3.4, 6.0})
    rx, ry, rw, rh = 562, 78, 334, 360
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+24}" font-size="13" font-weight="700" fill="#0f172a">Parsed 3 × 4 Corpus Matrix (72 CNFs)</text>')
    a(f'<text x="{rx+14}" y="{ry+40}" font-size="10.5" fill="#475569">Exact counts from expected.tsv by (n, α)</text>')

    ns = [50, 100, 200]
    ratios = ["1.6", "2.0", "3.4", "6.0"]
    col_x = [rx + 74, rx + 160, rx + 246]
    row_y0 = ry + 78
    row_h = 56

    # Column headers
    for ci, n in enumerate(ns):
        a(f'<text x="{col_x[ci]+36}" y="{ry+64}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="#0f172a">n = {n}</text>')

    for ri, rat in enumerate(ratios):
        yy = row_y0 + ri * row_h
        a(f'<text x="{rx+14}" y="{yy+20}" font-family="{MONO}" font-size="11" font-weight="700" fill="#1e293b">α={rat}</text>')
        rho = float(rat) / 4.267
        a(f'<text x="{rx+14}" y="{yy+34}" font-size="9" fill="#64748b">{rho:.2f}× α_c</text>')

        for ci, n in enumerate(ns):
            cx = col_x[ci]
            d = grid.get((n, rat), {"SAT": 0, "UNSAT": 0})
            nsat, nunsat = d["SAT"], d["UNSAT"]
            m_est = int(round(n * float(rat)))
            a(f'<rect x="{cx}" y="{yy}" width="74" height="44" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
            a(f'<text x="{cx+37}" y="{yy+13}" text-anchor="middle" font-family="{MONO}" font-size="8.8" fill="#64748b">m≈{m_est}</text>')
            if nunsat > 0:
                a(f'<rect x="{cx+5}" y="{yy+18}" width="30" height="19" rx="3" fill="#ecfdf5" stroke="#059669" stroke-width="0.7"/>')
                a(f'<text x="{cx+20}" y="{yy+31}" text-anchor="middle" font-size="9" font-weight="700" fill="#047857">{nsat} S</text>')
                a(f'<rect x="{cx+39}" y="{yy+18}" width="30" height="19" rx="3" fill="#fef2f2" stroke="#dc2626" stroke-width="0.7"/>')
                a(f'<text x="{cx+54}" y="{yy+31}" text-anchor="middle" font-size="9" font-weight="700" fill="#b91c1c">{nunsat} U</text>')
            else:
                a(f'<rect x="{cx+11}" y="{yy+18}" width="52" height="19" rx="3" fill="#ecfdf5" stroke="#059669" stroke-width="0.7"/>')
                a(f'<text x="{cx+37}" y="{yy+31}" text-anchor="middle" font-size="9" font-weight="700" fill="#047857">{nsat} SAT</text>')

    # Legend & structural fingerprint footer inside right panel
    fy = ry + 308
    a(f'<rect x="{rx+14}" y="{fy}" width="{rw-28}" height="40" rx="7" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
    a(f'<text x="{rx+rw/2:.1f}" y="{fy+16}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1e40af">Structural Fingerprint: Near-Regular 3-SAT</text>')
    a(f'<text x="{rx+rw/2:.1f}" y="{fy+31}" text-anchor="middle" font-size="9.4" fill="#1e3a8a">Deg CV = 0.03–0.04 (vs. 0.28 uniform) · 48 SAT / 24 UNSAT</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
