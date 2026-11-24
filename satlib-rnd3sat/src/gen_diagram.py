#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-rnd3sat."""
from __future__ import annotations

import lzma
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_instances() -> list[tuple[int, int, str, str]]:
    """Return sorted list of (n, m, sat_name, unsat_name) grouped by n."""
    by_n: dict[int, dict[str, tuple[int, str]]] = {}
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
            kind = "UNSAT" if stem.startswith("uuf") else "SAT"
            by_n.setdefault(n, {})[kind] = (m, stem)
    out = []
    for n in sorted(by_n):
        m_sat, s_name = by_n[n].get("SAT", (0, f"uf{n}-01"))
        m_unsat, u_name = by_n[n].get("UNSAT", (m_sat, f"uuf{n}-01"))
        out.append((n, m_sat or m_unsat, s_name, u_name))
    return out


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def main() -> None:
    groups = parse_instances()
    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB Uniform Random 3-SAT diagram">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB Uniform Random 3-SAT (uf / uuf 50..250)</text>')
    a('<text x="26" y="54" font-size="12" fill="#475569">Bipartite uniform 3-SAT factor graph &amp; critical finite-size scaling (α = 4.26–4.36) · 10 samples (5 SAT / 5 UNSAT) from 6,600 formulas</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: Uniform 3-SAT Bipartite Factor Graph + Poisson Degree Inset
    lx, ly, lw, lh = 24, 78, 444, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">Uniform Random 3-SAT Bipartite Factor Graph</text>')
    a(f'<text x="{lx+16}" y="{ly+40}" font-size="10.5" fill="#475569">Each clause picks 3 distinct vars uniformly; solid = positive, dashed = negated</text>')

    # Variables row (8 nodes) & Clauses row (6 nodes)
    var_xs = [lx + 42 + i * 51.5 for i in range(8)]
    var_y = ly + 74
    cls_xs = [lx + 58 + j * 65.6 for j in range(6)]
    cls_y = ly + 178

    # Deterministic 3-uniform random-looking bipartite incidence (each clause degree 3)
    clauses = [
        [(0, True), (1, False), (3, True)],
        [(0, False), (2, True), (4, True)],
        [(1, True), (3, False), (5, False)],
        [(2, False), (4, False), (6, True)],
        [(3, True), (5, True), (7, False)],
        [(4, True), (6, False), (7, True)],
    ]
    for ci, lits in enumerate(clauses):
        cx = cls_xs[ci]
        for vi, is_pos in lits:
            vx = var_xs[vi]
            col = "#2563eb" if is_pos else "#dc2626"
            dash = "" if is_pos else ' stroke-dasharray="5,3"'
            a(f'<line x1="{vx:.1f}" y1="{var_y+14}" x2="{cx:.1f}" y2="{cls_y-13}" stroke="{col}" stroke-width="1.5" stroke-opacity="0.88"{dash}/>')

    for i, vx in enumerate(var_xs):
        a(f'<circle cx="{vx:.1f}" cy="{var_y}" r="14" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>')
        a(f'<text x="{vx:.1f}" y="{var_y+4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1e3a8a">x{chr(0x2081+i)}</text>')

    for j, cx in enumerate(cls_xs):
        a(f'<rect x="{cx-16:.1f}" y="{cls_y-13}" width="32" height="26" rx="5" fill="#ffffff" stroke="#334155" stroke-width="1.5"/>')
        a(f'<text x="{cx:.1f}" y="{cls_y+4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0f172a">C{chr(0x2081+j)}</text>')

    # Factor graph legend
    ly_leg = ly + 216
    a(f'<line x1="{lx+20}" y1="{ly_leg}" x2="{lx+48}" y2="{ly_leg}" stroke="#2563eb" stroke-width="2"/>')
    a(f'<text x="{lx+54}" y="{ly_leg+3.5}" font-size="10" fill="#1e293b">Positive literal (xᵢ)</text>')
    a(f'<line x1="{lx+166}" y1="{ly_leg}" x2="{lx+194}" y2="{ly_leg}" stroke="#dc2626" stroke-width="2" stroke-dasharray="5,3"/>')
    a(f'<text x="{lx+200}" y="{ly_leg+3.5}" font-size="10" fill="#1e293b">Negated literal (¬xᵢ)</text>')
    a(f'<text x="{lx+428}" y="{ly_leg+3.5}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="#475569">|Cⱼ| = 3 ∀ j</text>')

    # Inset box: Variable Degree Distribution ~ Poisson(3α ≈ 12.8)
    ix, iy, iw, ih = lx + 16, ly + 234, lw - 32, 112
    a(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{ix+12}" y="{iy+18}" font-size="11" font-weight="700" fill="#0f172a">Variable Degree Distribution: deg(x) ~ Poisson(3α ≈ 12.8)</text>')
    a(f'<text x="{ix+12}" y="{iy+32}" font-size="9.5" fill="#64748b">Near-uniform degree (CV ≈ 0.27), 0% binary, 0 native XORs, no structural hubs</text>')

    # Mini Poisson bar chart k=5..22
    lam = 12.8
    bx0, by0, bw, bh = ix + 18, iy + 42, iw - 36, 48
    ks = list(range(5, 22))
    probs = [poisson_pmf(k, lam) for k in ks]
    pmax = max(probs)
    bar_step = bw / len(ks)
    for idx_k, (k, pr) in enumerate(zip(ks, probs)):
        bh_k = pr / pmax * bh
        bx = bx0 + idx_k * bar_step + 2
        by = by0 + bh - bh_k
        fill = "#2563eb" if 11 <= k <= 14 else "#93c5fd"
        a(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_step-4:.1f}" height="{bh_k:.1f}" rx="2" fill="{fill}"/>')
        if k in (6, 9, 12, 15, 18, 21):
            a(f'<text x="{bx + (bar_step-4)/2:.1f}" y="{by0+bh+12}" text-anchor="middle" font-size="8.8" fill="#64748b">{k}</text>')
    a(f'<line x1="{bx0}" y1="{by0+bh}" x2="{bx0+bw}" y2="{by0+bh}" stroke="#cbd5e1" stroke-width="1"/>')

    # Right Panel: Critical Scaling uf/uuf n = 50..250
    rx, ry, rw, rh = 482, 78, 414, 360
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+16}" y="{ry+24}" font-size="13" font-weight="700" fill="#0f172a">Critical-Threshold Scaling (uf / uuf 50 → 250)</text>')
    a(f'<text x="{rx+16}" y="{ry+40}" font-size="10.5" fill="#475569">Finite-size threshold α(n) converges downward toward α_c ≈ 4.267</text>')

    # Horizontal bar chart of clause count m + exact α and uf/uuf paired badges
    max_m = max(g[1] for g in groups) if groups else 1065
    row_top = ry + 62
    row_gap = 46
    bar_x0 = rx + 68
    bar_max_w = 188

    for idx, (n, m, s_name, u_name) in enumerate(groups):
        yy = row_top + idx * row_gap
        alpha = m / n
        bw_m = (m / max_m) * bar_max_w

        # n label
        a(f'<text x="{rx+16}" y="{yy+14}" font-family="{MONO}" font-size="11.5" font-weight="700" fill="#0f172a">n={n}</text>')
        a(f'<text x="{rx+16}" y="{yy+27}" font-size="9" fill="#64748b">α={alpha:.2f}</text>')

        # Dual split bar: upper half green (uf SAT), lower half red (uuf UNSAT)
        a(f'<rect x="{bar_x0}" y="{yy+1}" width="{bw_m:.1f}" height="12" rx="3" fill="#059669" fill-opacity="0.88"/>')
        a(f'<rect x="{bar_x0}" y="{yy+15}" width="{bw_m:.1f}" height="12" rx="3" fill="#dc2626" fill-opacity="0.85"/>')

        # Clause count text right of bar
        a(f'<text x="{bar_x0 + bw_m + 7:.1f}" y="{yy+17}" font-family="{MONO}" font-size="10" font-weight="700" fill="#1e293b">m={m:,}</text>')

        # Right-aligned paired SAT/UNSAT pills
        a(f'<rect x="{rx+316}" y="{yy+1}" width="84" height="12.5" rx="3" fill="#ecfdf5" stroke="#059669" stroke-width="0.7"/>')
        a(f'<text x="{rx+358}" y="{yy+10.5}" text-anchor="middle" font-family="{MONO}" font-size="8.5" font-weight="700" fill="#047857">{s_name}</text>')
        a(f'<rect x="{rx+316}" y="{yy+15.5}" width="84" height="12.5" rx="3" fill="#fef2f2" stroke="#dc2626" stroke-width="0.7"/>')
        a(f'<text x="{rx+358}" y="{yy+25}" text-anchor="middle" font-family="{MONO}" font-size="8.5" font-weight="700" fill="#b91c1c">{u_name}</text>')

    # Bottom callout card inside right panel: Asymptotic threshold & exponential scaling
    cy = ry + 296
    a(f'<rect x="{rx+14}" y="{cy}" width="{rw-28}" height="52" rx="8" fill="#fffbeb" stroke="#fcd34d" stroke-width="1"/>')
    a(f'<text x="{rx+26}" y="{cy+19}" font-size="11" font-weight="700" fill="#92400e">Why uuf250-1065 Dominates Runtime</text>')
    a(f'<text x="{rx+26}" y="{cy+34}" font-size="10" fill="#78350f">UNSAT proofs scale as ~2^(c·n): uuf50 takes ~2 ms while uuf250 takes</text>')
    a(f'<text x="{rx+26}" y="{cy+46}" font-size="10" fill="#78350f">~1.9–3.6 s (nearly 1,000× harder) across all 5 modern CDCL solvers.</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
