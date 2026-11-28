#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-dimacs-lran."""
from __future__ import annotations

import lzma
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_lran() -> list[tuple[str, int, int, float]]:
    rows = []
    cnf_dir = COL / "cnf-orig"
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*.cnf.xz")):
            n = m = 0
            with lzma.open(p, "rt", errors="replace") as f:
                for line in f:
                    if line.startswith("p cnf"):
                        parts = line.split()
                        n, m = int(parts[2]), int(parts[3])
                        break
            stem = p.name.replace(".cnf.xz", "")
            rows.append((stem, n, m, m / n if n else 0.0))
    rows.sort(key=lambda r: r[1])
    return rows


def energy_profile(t: float) -> float:
    """Stylized rugged 3-SAT energy landscape E(sigma) = #unsat clauses on t in [0, 1]."""
    # Deep global minimum E=0 near t=0.78, several metastable local minima E>0 elsewhere
    base = (
        0.52
        + 0.19 * math.sin(6.5 * t + 0.4)
        + 0.14 * math.cos(17.0 * t - 0.6)
        + 0.08 * math.sin(33.0 * t + 1.2)
    )
    # Carve a sharp narrow zero-energy SAT basin at t=0.77
    well = 0.72 * math.exp(-((t - 0.77) / 0.042) ** 2)
    # Carve two deep deceptive local minima (traps) at t=0.24 and t=0.51 (well above E=0 baseline)
    trap1 = 0.24 * math.exp(-((t - 0.24) / 0.045) ** 2)
    trap2 = 0.17 * math.exp(-((t - 0.51) / 0.050) ** 2)
    val = base - well - trap1 - trap2
    return max(0.0, min(0.95, val))


def main() -> None:
    rows = parse_lran()
    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB Large Critical Random 3-SAT diagram">')
    a('<defs>')
    a('  <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/></marker>')
    a('</defs>')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB Large Critical Random 3-SAT (f600, f1000, f2000)</text>')
    a('<text x="26" y="54" font-size="12" fill="#475569">Rugged energy landscape at α = 4.25 (ρ_crit = 1.00×) · WalkSAT / SLS local-minima escape vs. exponential CDCL branching · 3 SAT instances</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: Rugged Energy Landscape + Search Paradigm Contrast
    lx, ly, lw, lh = 24, 78, 550, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">Rugged Unsat-Clause Landscape E(σ) on {{0, 1}}ⁿ (n = 600–2,000)</text>')
    a(f'<text x="{lx+16}" y="{ly+40}" font-size="10.5" fill="#475569">Metastable local minima (E &gt; 0) trap greedy descent; rare narrow funnels reach E = 0</text>')

    px0, py0, px1, py1 = 68, 130, 554, 294
    pw, ph = px1 - px0, py1 - py0

    def ex(t: float) -> float:
        return px0 + t * pw

    def ey(v: float) -> float:
        return py1 - v * ph

    # Energy zero baseline & grid
    a(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1"/>')
    for frac, lbl in [(0.0, "0 (SAT)"), (0.5, "E mid"), (1.0, "E high")]:
        yy = ey(frac)
        a(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px1}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="0.8" stroke-dasharray="3,3"/>')
    a(f'<text x="{px0-6}" y="{ey(0.0)+3:.1f}" text-anchor="end" font-size="9.5" font-weight="700" fill="#059669">E = 0</text>')
    a(f'<text x="{px0-6}" y="{ey(0.88):.1f}" text-anchor="end" font-size="9.5" fill="#475569">E(σ)</text>')
    a(f'<text x="{(px0+px1)/2:.1f}" y="{py1+16}" text-anchor="middle" font-size="10" fill="#475569">Hypercube Configuration Space σ ∈ {{0, 1}}ⁿ (Hamming slice)</text>')

    # Plot rugged energy curve + fill
    samples = 180
    pts = [(ex(i / samples), ey(energy_profile(i / samples))) for i in range(samples + 1)]
    area_d = f"M {px0:.1f},{py1:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts) + f" L {px1:.1f},{py1:.1f} Z"
    curve_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    a(f'<path d="{area_d}" fill="#cbd5e1" fill-opacity="0.35"/>')
    a(f'<path d="{curve_d}" fill="none" stroke="#334155" stroke-width="2.1"/>')

    # Find exact local minima and global SAT well on curve
    t_trap1, t_trap2, t_sat = 0.24, 0.51, 0.77
    y_t1, y_t2, y_sat = ey(energy_profile(t_trap1)), ey(energy_profile(t_trap2)), ey(energy_profile(t_sat))

    # Highlight metastable local minima traps
    for tx, ty, lbl in [(t_trap1, y_t1, "Local min (E &gt; 0)"), (t_trap2, y_t2, "Metastable trap")]:
        xx = ex(tx)
        a(f'<circle cx="{xx:.1f}" cy="{ty:.1f}" r="4.5" fill="#d97706" stroke="#ffffff" stroke-width="1.3"/>')
        a(f'<text x="{xx:.1f}" y="{ty+16:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="#b45309">{lbl}</text>')

    # WalkSAT noisy escape path hopping over barrier from trap1 -> trap2 -> global well
    hop_d = (
        f"M {ex(0.14):.1f},{ey(energy_profile(0.14))-10:.1f} "
        f"Q {ex(0.20):.1f},{y_t1-26:.1f} {ex(t_trap1):.1f},{y_t1-8:.1f} "
        f"Q {ex(0.37):.1f},{ey(0.82):.1f} {ex(t_trap2):.1f},{y_t2-8:.1f} "
        f"Q {ex(0.65):.1f},{ey(0.86):.1f} {ex(t_sat)-5:.1f},{y_sat-12:.1f}"
    )
    a(f'<path d="{hop_d}" fill="none" stroke="#7c3aed" stroke-width="2.2" stroke-dasharray="5,3" marker-end="url(#arr-purple)"/>')
    a(f'<rect x="{ex(0.37)-72:.1f}" y="{py0+8}" width="146" height="20" rx="4" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="0.9"/>')
    a(f'<text x="{ex(0.37)+1:.1f}" y="{py0+21.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#6d28d9">WalkSAT / SLS noisy barrier hops</text>')

    # Global SAT well callout
    a(f'<circle cx="{ex(t_sat):.1f}" cy="{y_sat:.1f}" r="6" fill="#059669" stroke="#ffffff" stroke-width="1.8"/>')
    a(f'<rect x="{ex(t_sat)+12:.1f}" y="{y_sat-34:.1f}" width="84" height="28" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
    a(f'<text x="{ex(t_sat)+54:.1f}" y="{y_sat-21.5:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#047857">SAT Model</text>')
    a(f'<text x="{ex(t_sat)+54:.1f}" y="{y_sat-10.5:.1f}" text-anchor="middle" font-size="8.5" fill="#065f46">E(σ*) = 0</text>')

    # Bottom dual paradigm comparison cards inside Left Panel
    cy = 326
    cw = 252
    # Card A: Pure CDCL Tree
    a(f'<rect x="{lx+14}" y="{cy}" width="{cw}" height="98" rx="8" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
    a(f'<text x="{lx+26}" y="{cy+19}" font-size="11.5" font-weight="700" fill="#1e40af">Pure CDCL Search Tree</text>')
    # Mini branching tree icon on right side of card
    tx0, ty0 = lx + 216, cy + 28
    a(f'<line x1="{tx0}" y1="{ty0}" x2="{tx0-20}" y2="{ty0+24}" stroke="#2563eb" stroke-width="1.4"/>')
    a(f'<line x1="{tx0}" y1="{ty0}" x2="{tx0+20}" y2="{ty0+24}" stroke="#2563eb" stroke-width="1.4"/>')
    a(f'<line x1="{tx0-20}" y1="{ty0+24}" x2="{tx0-30}" y2="{ty0+48}" stroke="#dc2626" stroke-width="1.2"/>')
    a(f'<line x1="{tx0-20}" y1="{ty0+24}" x2="{tx0-10}" y2="{ty0+48}" stroke="#dc2626" stroke-width="1.2"/>')
    a(f'<line x1="{tx0+20}" y1="{ty0+24}" x2="{tx0+10}" y2="{ty0+48}" stroke="#dc2626" stroke-width="1.2"/>')
    a(f'<line x1="{tx0+20}" y1="{ty0+24}" x2="{tx0+30}" y2="{ty0+48}" stroke="#2563eb" stroke-width="1.2"/>')
    a(f'<circle cx="{tx0}" cy="{ty0}" r="3.5" fill="#2563eb"/>')
    for dx in (-30, -10, 10):
        a(f'<text x="{tx0+dx}" y="{ty0+58}" text-anchor="middle" font-size="9" font-weight="700" fill="#dc2626">×</text>')
    a(f'<text x="{lx+26}" y="{cy+38}" font-size="9.8" fill="#1e3a8a">• Branches systematically over</text>')
    a(f'<text x="{lx+34}" y="{cy+52}" font-size="9.8" fill="#1e3a8a">2ⁿ assignments (n up to 2,000)</text>')
    a(f'<text x="{lx+26}" y="{cy+69}" font-size="9.8" fill="#1e3a8a">• Zero gates/XORs → thrashing</text>')
    a(f'<text x="{lx+34}" y="{cy+83}" font-size="9.8" fill="#b91c1c" font-weight="600">• Timeout &gt;5 s on f2000</text>')

    # Card B: SLS / Hybrid WalkSAT
    c2x = lx + 14 + cw + 18
    a(f'<rect x="{c2x}" y="{cy}" width="{cw}" height="98" rx="8" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1"/>')
    a(f'<text x="{c2x+12}" y="{cy+19}" font-size="11.5" font-weight="700" fill="#5b21b6">SLS / Hybrid (WalkSAT / probSAT)</text>')
    a(f'<text x="{c2x+12}" y="{cy+38}" font-size="9.8" fill="#4c1d95">• Flips variables in unsat clauses</text>')
    a(f'<text x="{c2x+20}" y="{cy+52}" font-size="9.8" fill="#4c1d95">with break-count noise bias</text>')
    a(f'<text x="{c2x+12}" y="{cy+69}" font-size="9.8" fill="#4c1d95">• Escapes metastable traps fast</text>')
    a(f'<text x="{c2x+20}" y="{cy+83}" font-size="9.8" fill="#047857" font-weight="600">• Finds f600–f2000 models rapidly</text>')

    # Right Panel: Parsed Corpus Scaling (f600, f1000, f2000)
    rx, ry, rw, rh = 588, 78, 308, 360
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+24}" font-size="13" font-weight="700" fill="#0f172a">Parsed DIMACS LRAN Scaling</text>')
    a(f'<text x="{rx+14}" y="{ry+40}" font-size="10.5" fill="#475569">Exact dimensions from cnf-orig/ (α = 4.25)</text>')

    max_m = max(r[2] for r in rows) if rows else 8500
    for i, (stem, n, m, alpha) in enumerate(rows):
        yy = ry + 64 + i * 76
        bw_m = (m / max_m) * 182
        a(f'<rect x="{rx+14}" y="{yy}" width="{rw-28}" height="64" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
        a(f'<text x="{rx+24}" y="{yy+19}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="#0f172a">{stem}</text>')
        a(f'<rect x="{rx+rw-68}" y="{yy+7}" width="44" height="15" rx="4" fill="#ecfdf5" stroke="#059669" stroke-width="0.8"/>')
        a(f'<text x="{rx+rw-46}" y="{yy+18}" text-anchor="middle" font-size="9" font-weight="700" fill="#047857">SAT</text>')

        # Clause scale bar
        a(f'<rect x="{rx+24}" y="{yy+27}" width="182" height="12" rx="3" fill="#e2e8f0"/>')
        a(f'<rect x="{rx+24}" y="{yy+27}" width="{bw_m:.1f}" height="12" rx="3" fill="#2563eb"/>')
        a(f'<text x="{rx+214}" y="{yy+37}" font-family="{MONO}" font-size="9.5" font-weight="700" fill="#1e293b">m={m:,}</text>')

        a(f'<text x="{rx+24}" y="{yy+54}" font-size="9.5" fill="#475569">n = {n:,} vars · α = {alpha:.2f} · ρ_crit = {alpha/4.267:.2f}× · k = 3</text>')

    # Bottom Stats Box inside Right Panel
    sy = ry + 298
    a(f'<rect x="{rx+14}" y="{sy}" width="{rw-28}" height="48" rx="8" fill="#fffbeb" stroke="#fcd34d" stroke-width="1"/>')
    a(f'<text x="{rx+24}" y="{sy+18}" font-size="10.5" font-weight="700" fill="#92400e">Pure Critical 3-SAT Stress Test</text>')
    a(f'<text x="{rx+24}" y="{sy+32}" font-size="9.5" fill="#78350f">15,300 total clauses · 0 XORs · Deg CV = 0.27–0.28</text>')
    a(f'<text x="{rx+24}" y="{sy+43}" font-size="9.5" fill="#78350f">AIG size: 7.6k → 25.5k AND gates (all 3 SAT)</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
