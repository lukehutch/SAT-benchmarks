#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for sat-shortcut-challenge-tier3."""
from __future__ import annotations

import lzma
import re
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_tier3() -> tuple[dict[tuple[int, int], str], dict[int, int]]:
    verdicts: dict[tuple[int, int], str] = {}
    clauses_by_n: dict[int, int] = {}
    pat = re.compile(r"random3sat_n(\d+)_s(\d+)")

    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            fn, v = line.split("\t")[:2]
            m = pat.match(fn.replace(".cnf", ""))
            if m:
                verdicts[(int(m.group(1)), int(m.group(2)))] = v.strip()

    cnf_dir = COL / "cnf-orig"
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*_s1.cnf.xz")):
            m = pat.match(p.name.replace(".cnf.xz", ""))
            if not m:
                continue
            n_val = int(m.group(1))
            with lzma.open(p, "rt", errors="replace") as f:
                for line in f:
                    if line.startswith("p cnf"):
                        clauses_by_n[n_val] = int(line.split()[3])
                        break
    return verdicts, clauses_by_n


def main() -> None:
    verdicts, clauses_by_n = parse_tier3()
    ns = sorted({k[0] for k in verdicts} or {300, 350, 400, 450, 500})
    seeds = [1, 2, 3, 4, 5]
    n_sat = sum(1 for v in verdicts.values() if v == "SAT")
    n_unsat = sum(1 for v in verdicts.values() if v == "UNSAT")
    n_unk = sum(1 for v in verdicts.values() if v == "UNKNOWN")

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SAT Shortcut Challenge Tier 3 critical random 3-SAT suite">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SAT Shortcut Challenge — Tier 3 Critical Random 3-SAT (α = 4.26)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">25 pure unstructured 3-SAT formulas (n ∈ {{300..500}} × 5 seeds) · {n_sat} SAT / {n_unsat} UNSAT / {n_unk} Open (&gt;300 s, exp. UNSAT)</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: 5 x 5 Parsed Scaling & Verdict Matrix
    lx, ly, lw, lh = 24, 78, 494, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">Parsed 5 × 5 Scaling Matrix (expected.tsv, α = 4.260)</text>')
    a(f'<text x="{lx+16}" y="{ly+40}" font-size="10.5" fill="#475569">Exact clause counts m = 4.26·n (ρ_crit = 1.00×) and 300 s 1-core verdict grid</text>')

    # Column headers: Size (n, m) + s1..s5
    gx0 = lx + 114
    col_w = 72
    hy = ly + 64
    a(f'<text x="{lx+16}" y="{hy}" font-size="10" font-weight="700" fill="#475569">Size (n, m)</text>')
    for si, sd in enumerate(seeds):
        a(f'<text x="{gx0 + si*col_w + col_w/2 - 4:.1f}" y="{hy}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#1e293b">seed {sd}</text>')
    a(f'<line x1="{lx+14}" y1="{hy+7}" x2="{lx+lw-14}" y2="{hy+7}" stroke="#cbd5e1" stroke-width="1"/>')

    row_h = 46
    for ri, n in enumerate(ns):
        yy = hy + 18 + ri * row_h
        m = clauses_by_n.get(n, int(round(n * 4.26)))
        a(f'<text x="{lx+16}" y="{yy+16}" font-family="{MONO}" font-size="11" font-weight="700" fill="#0f172a">n = {n}</text>')
        a(f'<text x="{lx+16}" y="{yy+30}" font-family="{MONO}" font-size="9.2" fill="#64748b">m = {m:,}</text>')

        for si, sd in enumerate(seeds):
            v = verdicts.get((n, sd), "UNKNOWN")
            cx = gx0 + si * col_w
            if v == "SAT":
                bg, strk, tc, lbl, sub = "#ecfdf5", "#059669", "#047857", "SAT", "SLS ms"
            elif v == "UNSAT":
                bg, strk, tc, lbl, sub = "#fef2f2", "#dc2626", "#b91c1c", "UNSAT", "LRAT ✓"
            else:
                bg, strk, tc, lbl, sub = "#fffbeb", "#d97706", "#b45309", "OPEN", "&gt;300 s"

            a(f'<rect x="{cx}" y="{yy+2}" width="64" height="36" rx="6" fill="{bg}" stroke="{strk}" stroke-width="1.2"/>')
            a(f'<text x="{cx+32}" y="{yy+17}" text-anchor="middle" font-size="10" font-weight="700" fill="{tc}">{lbl}</text>')
            a(f'<text x="{cx+32}" y="{yy+30}" text-anchor="middle" font-size="8.4" fill="{tc}">{sub}</text>')

    # Legend inside bottom of left panel
    lby = ly + 334
    a(f'<rect x="{lx+16}" y="{lby-9}" width="12" height="12" rx="2" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
    a(f'<text x="{lx+33}" y="{lby+1}" font-size="9.8" fill="#334155">SAT ({n_sat})</text>')
    a(f'<rect x="{lx+106}" y="{lby-9}" width="12" height="12" rx="2" fill="#fef2f2" stroke="#dc2626" stroke-width="1"/>')
    a(f'<text x="{lx+123}" y="{lby+1}" font-size="9.8" fill="#334155">Proved UNSAT ({n_unsat})</text>')
    a(f'<rect x="{lx+246}" y="{lby-9}" width="12" height="12" rx="2" fill="#fffbeb" stroke="#d97706" stroke-width="1"/>')
    a(f'<text x="{lx+263}" y="{lby+1}" font-size="9.8" fill="#334155">Open &gt;300 s, exp. UNSAT ({n_unk})</text>')

    # Right Top Panel: SAT vs. UNSAT Asymmetry at alpha = 4.26
    rx, ry, rw = 532, 78, 364
    rh1 = 212
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh1}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+23}" font-size="12.5" font-weight="700" fill="#0f172a">The SAT vs. UNSAT Asymmetry Wall</text>')
    a(f'<text x="{rx+14}" y="{ry+38}" font-size="10" fill="#475569">Why UNSAT refutation is the real Tier-3 test</text>')

    # Two comparative log-time cards inside right top panel
    # SAT card (green)
    a(f'<rect x="{rx+14}" y="{ry+48}" width="{rw-28}" height="68" rx="8" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.1"/>')
    a(f'<text x="{rx+24}" y="{ry+66}" font-size="11" font-weight="700" fill="#047857">15 SAT Instances (n = 300–500): Easy for SLS</text>')
    a(f'<text x="{rx+24}" y="{ry+82}" font-size="9.6" fill="#065f46">• 60-line probSAT solves all 15 in 0.6–53 ms (229 ms total)</text>')
    a(f'<text x="{rx+24}" y="{ry+96}" font-size="9.6" fill="#065f46">• Single satisfying witness suffices; no completeness needed</text>')
    a(f'<text x="{rx+24}" y="{ry+109}" font-size="9.2" fill="#047857" font-weight="600">• 1-core CDCL/hybrid solves 15/15 in 1.1–200 s</text>')

    # UNSAT card (red)
    a(f'<rect x="{rx+14}" y="{ry+124}" width="{rw-28}" height="78" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.1"/>')
    a(f'<text x="{rx+24}" y="{ry+142}" font-size="11" font-weight="700" fill="#b91c1c">UNSAT Refutations (2 Proved + 8 Open): 2^Ω(n) Wall</text>')
    a(f'<text x="{rx+24}" y="{ry+158}" font-size="9.6" fill="#7f1d1d">• n = 300 (s1, s5): 21–61 s solo; ~500 MB LRAT proofs</text>')
    a(f'<text x="{rx+24}" y="{ry+172}" font-size="9.6" fill="#7f1d1d">• Formally verified by cake_lpr (s VERIFIED UNSAT)</text>')
    a(f'<text x="{rx+24}" y="{ry+186}" font-size="9.6" fill="#991b1b" font-weight="700">• n = 350–500 (8 instances): 0/8 solved in 300 s (all 5 solvers)</text>')

    # Right Bottom Panel: Pure Unstructured 3-SAT Factor Graph Motif
    ry2 = ry + rh1 + 12
    rh2 = 438 - ry2
    a(f'<rect x="{rx}" y="{ry2}" width="{rw}" height="{rh2}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry2+22}" font-size="12" font-weight="700" fill="#0f172a">Unstructured 3-SAT Core (Zero Shortcuts)</text>')

    # Compact bipartite motif on left + stats on right
    vxs = [rx + 28 + i * 32 for i in range(5)]
    vy_n = ry2 + 52
    cxs = [rx + 44, rx + 92, rx + 140]
    cy_n = ry2 + 102
    for vi, ci, pos in [(0,0,True),(1,0,False),(3,0,True),(1,1,True),(2,1,False),(4,1,True),(0,2,False),(2,2,True),(4,2,False)]:
        col = "#2563eb" if pos else "#dc2626"
        dash = "" if pos else ' stroke-dasharray="3,2"'
        a(f'<line x1="{vxs[vi]}" y1="{vy_n+10}" x2="{cxs[ci]}" y2="{cy_n-9}" stroke="{col}" stroke-width="1.3"{dash}/>')
    for i, vx in enumerate(vxs):
        a(f'<circle cx="{vx}" cy="{vy_n}" r="10" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>')
        a(f'<text x="{vx}" y="{vy_n+3.5}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#1e3a8a">x{chr(0x2081+i)}</text>')
    for j, cx in enumerate(cxs):
        a(f'<rect x="{cx-11}" y="{cy_n-9}" width="22" height="18" rx="3" fill="#ffffff" stroke="#334155" stroke-width="1.2"/>')
        a(f'<text x="{cx}" y="{cy_n+3.5}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#0f172a">C{chr(0x2081+j)}</text>')

    # Right stats bullets beside factor graph
    sx_r = rx + 188
    a(f'<text x="{sx_r}" y="{ry2+48}" font-size="9.8" font-weight="700" fill="#0f172a">Structural Audit (All 25):</text>')
    a(f'<text x="{sx_r}" y="{ry2+64}" font-family="{MONO}" font-size="9.2" fill="#334155">• k = 3.00 (0% bin)</text>')
    a(f'<text x="{sx_r}" y="{ry2+79}" font-family="{MONO}" font-size="9.2" fill="#334155">• α = 4.26 (ρ = 1.00×)</text>')
    a(f'<text x="{sx_r}" y="{ry2+94}" font-family="{MONO}" font-size="9.2" fill="#334155">• Deg CV = 0.27–0.30</text>')
    a(f'<text x="{sx_r}" y="{ry2+109}" font-family="{MONO}" font-size="9.2" fill="#334155">• 0 native XORs / gates</text>')
    a(f'<text x="{rx+14}" y="{ry2+128}" font-size="9.2" fill="#64748b">42,600 total clauses across 25 CNFs · 4 formats SHA-256 verified</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
