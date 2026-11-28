#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for random-3sat-phase-transition."""
from __future__ import annotations

import lzma
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def parse_collection() -> list[tuple[str, int, int, float, str]]:
    verdicts: dict[str, str] = {}
    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            fn, v = line.split("\t")[:2]
            verdicts[fn.strip()] = v.strip()

    rows: list[tuple[str, int, int, float, str]] = []
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
            stem = p.name[:-3]  # strip .xz -> .cnf
            v = verdicts.get(stem, "SAT" if "_sat" in stem else "UNSAT")
            rows.append((stem.replace(".cnf", ""), n, m, m / n if n else 0.0, v))
    rows.sort(key=lambda r: (r[3], 0 if r[4] == "SAT" else 1))
    return rows


def psat_curve(alpha: float) -> float:
    # Smooth finite-size n=200 empirical P(SAT) sigmoid centered at alpha_c = 4.267
    return 1.0 / (1.0 + math.exp((alpha - 4.267) / 0.075))


def hardness_curve(alpha: float) -> float:
    # Asymmetric log-hardness peak centered at alpha_c = 4.267 (steeper left, slower right decay)
    if alpha <= 4.267:
        return math.exp(-((alpha - 4.267) / 0.24) ** 2)
    return math.exp(-((alpha - 4.267) / 0.44) ** 2)


def main() -> None:
    rows = parse_collection()
    sat_cnt = sum(1 for r in rows if r[4] == "SAT")
    unsat_cnt = sum(1 for r in rows if r[4] == "UNSAT")

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Random 3-SAT phase transition diagram">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(f'<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">Random 3-SAT Phase Transition (n = 200, α = m/n Sweep)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">Easy–hard–easy satisfiability cliff at α_c ≈ 4.267 · {len(rows)} committed instances ({sat_cnt} SAT / {unsat_cnt} UNSAT) spanning α ∈ [3.80, 5.00]</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left panel: Phase Transition Chart
    lx, ly, lw, lh = 24, 78, 576, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">Satisfiability Cliff P(SAT) &amp; Search Hardness vs. Clause Ratio α = m/n</text>')

    # Plot bounds inside left panel
    px0, py0, px1, py1 = 80, 126, 548, 362
    pw, ph = px1 - px0, py1 - py0
    a_min, a_max = 3.60, 5.20

    def ax(alpha: float) -> float:
        return px0 + (alpha - a_min) / (a_max - a_min) * pw

    def ay(val: float) -> float:
        return py1 - val * ph

    # Regime bands
    x_under_end = ax(4.12)
    x_crit_end = ax(4.42)
    a(f'<rect x="{px0}" y="{py0}" width="{x_under_end - px0:.1f}" height="{ph}" fill="#ecfdf5" fill-opacity="0.75"/>')
    a(f'<rect x="{x_under_end:.1f}" y="{py0}" width="{x_crit_end - x_under_end:.1f}" height="{ph}" fill="#fffbeb" fill-opacity="0.90"/>')
    a(f'<rect x="{x_crit_end:.1f}" y="{py0}" width="{px1 - x_crit_end:.1f}" height="{ph}" fill="#fef2f2" fill-opacity="0.75"/>')

    # Regime captions (placed in open whitespace clear of curves & data markers)
    a(f'<text x="{(px0 + x_under_end)/2:.1f}" y="{py0+78}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#059669">Under-constrained</text>')
    a(f'<text x="{(px0 + x_under_end)/2:.1f}" y="{py0+91}" text-anchor="middle" font-size="9.5" fill="#047857">Easy SAT (many models)</text>')
    a(f'<text x="{(x_under_end + x_crit_end)/2:.1f}" y="{py0+16}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#b45309">Critical</text>')
    a(f'<text x="{(x_under_end + x_crit_end)/2:.1f}" y="{py0+29}" text-anchor="middle" font-size="9.5" fill="#b45309">Hard peak</text>')
    a(f'<text x="{(x_crit_end + px1)/2:.1f}" y="{py0+16}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#dc2626">Over-constrained</text>')
    a(f'<text x="{(x_crit_end + px1)/2:.1f}" y="{py0+29}" text-anchor="middle" font-size="9.5" fill="#b91c1c">Easier UNSAT (short proofs)</text>')

    # Grid lines
    for frac in (0.0, 0.25, 0.50, 0.75, 1.0):
        yy = ay(frac)
        a(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px1}" y2="{yy:.1f}" stroke="#cbd5e1" stroke-width="0.7" stroke-dasharray="3,3"/>')
        a(f'<text x="{px0-8}" y="{yy+3.5:.1f}" text-anchor="end" font-size="10" fill="#475569">{frac:.2f}</text>')

    for tick in (3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2):
        xx = ax(tick)
        a(f'<line x1="{xx:.1f}" y1="{py1}" x2="{xx:.1f}" y2="{py1+5}" stroke="#64748b" stroke-width="1"/>')
        a(f'<text x="{xx:.1f}" y="{py1+18}" text-anchor="middle" font-size="10" fill="#475569">{tick:.1f}</text>')

    # Plot frame
    a(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="none" stroke="#94a3b8" stroke-width="1.2"/>')

    # Critical threshold line
    xc = ax(4.267)
    a(f'<line x1="{xc:.1f}" y1="{py0+34}" x2="{xc:.1f}" y2="{py1}" stroke="#d97706" stroke-width="1.6" stroke-dasharray="5,4"/>')
    a(f'<rect x="{xc-37:.1f}" y="{py1-20}" width="74" height="17" rx="4" fill="#fffbeb" stroke="#f59e0b" stroke-width="0.9"/>')
    a(f'<text x="{xc:.1f}" y="{py1-8}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b45309">α_c ≈ 4.267</text>')

    # Hardness bell shaded area + stroke
    h_pts = []
    for i in range(81):
        al = a_min + (a_max - a_min) * i / 80.0
        h_pts.append((ax(al), ay(0.84 * hardness_curve(al))))
    poly_d = f"M {px0:.1f},{py1:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in h_pts) + f" L {px1:.1f},{py1:.1f} Z"
    line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in h_pts)
    a(f'<path d="{poly_d}" fill="#f59e0b" fill-opacity="0.16"/>')
    a(f'<path d="{line_d}" fill="none" stroke="#d97706" stroke-width="2.2" stroke-dasharray="6,3"/>')

    # P(SAT) curve
    p_pts = []
    for i in range(81):
        al = a_min + (a_max - a_min) * i / 80.0
        p_pts.append((ax(al), ay(psat_curve(al))))
    p_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in p_pts)
    a(f'<path d="{p_d}" fill="none" stroke="#2563eb" stroke-width="2.6"/>')

    # Right Y-axis label (Hardness)
    a(f'<text x="42" y="{(py0+py1)/2:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="#2563eb" transform="rotate(-90 42 {(py0+py1)/2:.1f})">P(SAT | n = 200)</text>')
    a(f'<text x="582" y="{(py0+py1)/2:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="#b45309" transform="rotate(90 582 {(py0+py1)/2:.1f})">Relative CDCL Hardness</text>')
    a(f'<text x="{(px0+px1)/2:.1f}" y="{py1+35}" text-anchor="middle" font-size="11" font-weight="600" fill="#1e293b">Clause-to-Variable Ratio α = m / n</text>')

    # Overlay all 8 real dataset points cleanly (avoid overlap at alpha=4.26!)
    # SAT points sit near y = 0.92..0.56 on P(SAT), UNSAT points sit on P(SAT) or offset clearly at 4.26
    for idx, (name, n, m, alpha, v) in enumerate(rows):
        xx = ax(alpha)
        p_val = psat_curve(alpha)
        if abs(alpha - 4.26) < 0.01:
            yy = ay(0.58 if v == "SAT" else 0.44)
        else:
            yy = ay(p_val)
        if v == "SAT":
            a(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5.5" fill="#059669" stroke="#ffffff" stroke-width="1.6"/>')
        else:
            # Diamond for UNSAT
            r = 6.2
            a(f'<polygon points="{xx:.1f},{yy-r:.1f} {xx+r:.1f},{yy:.1f} {xx:.1f},{yy+r:.1f} {xx-r:.1f},{yy:.1f}" fill="#dc2626" stroke="#ffffff" stroke-width="1.5"/>')

        # Custom clean label offsets for each of the 8 points
        lbl = f"{alpha:.2f}"
        if abs(alpha - 3.80) < 0.01:
            a(f'<text x="{xx:.1f}" y="{yy+18:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#047857">3.80</text>')
        elif abs(alpha - 4.00) < 0.01:
            a(f'<text x="{xx:.1f}" y="{yy+18:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#047857">4.00</text>')
        elif abs(alpha - 4.10) < 0.01:
            a(f'<text x="{xx-10:.1f}" y="{yy+18:.1f}" text-anchor="end" font-size="9.5" font-weight="700" fill="#047857">4.10</text>')
        elif abs(alpha - 4.26) < 0.01 and v == "SAT":
            a(f'<text x="{xx+10:.1f}" y="{yy+3:.1f}" text-anchor="start" font-size="9.5" font-weight="700" fill="#047857">4.26 SAT</text>')
        elif abs(alpha - 4.26) < 0.01 and v == "UNSAT":
            a(f'<text x="{xx+10:.1f}" y="{yy+3:.1f}" text-anchor="start" font-size="9.5" font-weight="700" fill="#b91c1c">4.26 UNSAT</text>')
        elif abs(alpha - 4.45) < 0.01:
            a(f'<text x="{xx+10:.1f}" y="{yy+3:.1f}" text-anchor="start" font-size="9.5" font-weight="700" fill="#b91c1c">4.45</text>')
        elif abs(alpha - 4.65) < 0.01:
            a(f'<text x="{xx:.1f}" y="{yy-12:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b91c1c">4.65</text>')
        elif abs(alpha - 5.00) < 0.01:
            a(f'<text x="{xx:.1f}" y="{yy-19:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b91c1c">5.00</text>')

    # Legend bar inside bottom of left panel
    leg_y = 418
    a(f'<line x1="44" y1="{leg_y}" x2="66" y2="{leg_y}" stroke="#2563eb" stroke-width="2.6"/>')
    a(f'<text x="72" y="{leg_y+4}" font-size="10.5" fill="#1e293b">P(SAT) curve</text>')
    a(f'<line x1="162" y1="{leg_y}" x2="184" y2="{leg_y}" stroke="#d97706" stroke-width="2.2" stroke-dasharray="5,3"/>')
    a(f'<text x="190" y="{leg_y+4}" font-size="10.5" fill="#1e293b">CDCL hardness peak</text>')
    a(f'<circle cx="326" cy="{leg_y}" r="5" fill="#059669" stroke="#ffffff" stroke-width="1.2"/>')
    a(f'<text x="336" y="{leg_y+4}" font-size="10.5" fill="#1e293b">Committed SAT (4)</text>')
    a(f'<polygon points="458,{leg_y-5.5} 463.5,{leg_y} 458,{leg_y+5.5} 452.5,{leg_y}" fill="#dc2626" stroke="#ffffff" stroke-width="1.2"/>')
    a(f'<text x="469" y="{leg_y+4}" font-size="10.5" fill="#1e293b">Committed UNSAT (4)</text>')

    # Right top panel: Mini 3-SAT Factor Graph
    rx, ry, rw = 612, 78, 284
    rh1 = 178
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh1}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+22}" font-size="12.5" font-weight="700" fill="#0f172a">Uniform 3-SAT Factor Graph</text>')
    a(f'<text x="{rx+14}" y="{ry+37}" font-size="10" fill="#64748b">3 distinct random vars/clause, p(¬) = 1/2</text>')

    # 5 variable circles at top, 3 clause squares at bottom
    var_xs = [rx + 36 + i * 53 for i in range(5)]
    var_y = ry + 66
    cls_xs = [rx + 62, rx + 142, rx + 222]
    cls_y = ry + 126
    edges = [
        (0, 0, True), (1, 0, False), (3, 0, True),
        (1, 1, True), (2, 1, True), (4, 1, False),
        (0, 2, False), (2, 2, False), (4, 2, True),
    ]
    for vi, ci, pos in edges:
        col = "#2563eb" if pos else "#dc2626"
        dash = "" if pos else ' stroke-dasharray="4,3"'
        a(f'<line x1="{var_xs[vi]}" y1="{var_y+12}" x2="{cls_xs[ci]}" y2="{cls_y-11}" stroke="{col}" stroke-width="1.5"{dash}/>')

    for i, vx in enumerate(var_xs):
        a(f'<circle cx="{vx}" cy="{var_y}" r="13" fill="#eff6ff" stroke="#2563eb" stroke-width="1.4"/>')
        a(f'<text x="{vx}" y="{var_y+4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1e3a8a">x{chr(0x2081+i)}</text>')

    for j, cx in enumerate(cls_xs):
        a(f'<rect x="{cx-14}" y="{cls_y-11}" width="28" height="22" rx="4" fill="#ffffff" stroke="#475569" stroke-width="1.4"/>')
        a(f'<text x="{cx}" y="{cls_y+4}" text-anchor="middle" font-size="10" font-weight="700" fill="#0f172a">C{chr(0x2081+j)}</text>')

    # Factor graph mini-legend
    a(f'<line x1="{rx+16}" y1="{ry+159}" x2="{rx+38}" y2="{ry+159}" stroke="#2563eb" stroke-width="1.8"/>')
    a(f'<text x="{rx+43}" y="{ry+163}" font-size="9.5" fill="#475569">pos (x)</text>')
    a(f'<line x1="{rx+92}" y1="{ry+159}" x2="{rx+114}" y2="{ry+159}" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="4,2"/>')
    a(f'<text x="{rx+119}" y="{ry+163}" font-size="9.5" fill="#475569">neg (¬x)</text>')
    a(f'<text x="{rx+272}" y="{ry+163}" text-anchor="end" font-family="{MONO}" font-size="9.2" fill="#0f172a">C₁=(x₁∨¬x₂∨x₄)</text>')

    # Right bottom panel: Parsed Dataset Table (all 8 instances)
    ry2 = ry + rh1 + 12
    rh2 = 438 - ry2
    a(f'<rect x="{rx}" y="{ry2}" width="{rw}" height="{rh2}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry2+21}" font-size="12" font-weight="700" fill="#0f172a">Parsed Sweep Corpus (n = 200)</text>')

    # Column headers
    hy = ry2 + 39
    a(f'<text x="{rx+14}" y="{hy}" font-size="9.5" font-weight="700" fill="#64748b">α = m/n</text>')
    a(f'<text x="{rx+78}" y="{hy}" font-size="9.5" font-weight="700" fill="#64748b">Clauses m</text>')
    a(f'<text x="{rx+152}" y="{hy}" font-size="9.5" font-weight="700" fill="#64748b">ρ_crit</text>')
    a(f'<text x="{rx+226}" y="{hy}" font-size="9.5" font-weight="700" fill="#64748b">Verdict</text>')
    a(f'<line x1="{rx+12}" y1="{hy+5}" x2="{rx+rw-12}" y2="{hy+5}" stroke="#e2e8f0" stroke-width="1"/>')

    for i, (name, n, m, alpha, v) in enumerate(rows):
        row_y = hy + 19 + i * 14.8
        rho = alpha / 4.267
        pill_fill = "#ecfdf5" if v == "SAT" else "#fef2f2"
        pill_str = "#059669" if v == "SAT" else "#dc2626"
        a(f'<text x="{rx+14}" y="{row_y:.1f}" font-family="{MONO}" font-size="10" font-weight="600" fill="#0f172a">{alpha:.2f}</text>')
        a(f'<text x="{rx+78}" y="{row_y:.1f}" font-family="{MONO}" font-size="10" fill="#334155">{m:,}</text>')
        a(f'<text x="{rx+152}" y="{row_y:.1f}" font-family="{MONO}" font-size="10" fill="#475569">{rho:.2f}×</text>')
        a(f'<rect x="{rx+218}" y="{row_y-9.5:.1f}" width="52" height="12.5" rx="3" fill="{pill_fill}" stroke="{pill_str}" stroke-width="0.7"/>')
        a(f'<text x="{rx+244}" y="{row_y:.1f}" text-anchor="middle" font-size="8.8" font-weight="700" fill="{pill_str}">{v}</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
