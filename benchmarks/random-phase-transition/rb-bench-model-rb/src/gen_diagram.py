#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for rb-bench-model-rb."""
from __future__ import annotations

import lzma
import math
import re
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 480
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_rb_families() -> tuple[list[tuple[str, int, int, int, int]], tuple[int, int, int]]:
    """Return sorted families (label, n_csp, d, vars_sat, clauses_sat) and frb30-15-1 edge stats."""
    by_fam: dict[str, tuple[int, int, int, int]] = {}
    pat = re.compile(r"(frb(\d+)-(\d+))-\d+")
    cnf_dir = COL / "cnf-orig"
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*-1.cnf.xz")):
            stem = p.name.replace(".cnf.xz", "")
            m = pat.match(stem)
            if not m:
                continue
            fam, n_csp, d = m.group(1), int(m.group(2)), int(m.group(3))
            nv = nc = 0
            with lzma.open(p, "rt", errors="replace") as f:
                for line in f:
                    if line.startswith("p cnf"):
                        parts = line.split()
                        nv, nc = int(parts[2]), int(parts[3])
                        break
            by_fam[fam] = (n_csp, d, nv, nc)

    # Also parse exact binary clause breakdown of frb30-15-1
    amo = nogoods = edges = 0
    f30 = cnf_dir / "frb30-15-1.cnf.xz"
    if f30.exists():
        epairs: set[tuple[int, int]] = set()
        with lzma.open(f30, "rt", errors="replace") as f:
            for line in f:
                st = line.strip()
                if not st or st[0] in "cp":
                    continue
                lits = [int(x) for x in st.split()[:-1]]
                if len(lits) == 2:
                    v1, v2 = (abs(lits[0]) - 1) // 15, (abs(lits[1]) - 1) // 15
                    if v1 == v2:
                        amo += 1
                    else:
                        nogoods += 1
                        epairs.add((min(v1, v2), max(v1, v2)))
        edges = len(epairs)

    fams = [(k, *v) for k, v in sorted(by_fam.items(), key=lambda kv: kv[1][0])]
    return fams, (amo, nogoods, edges)


def main() -> None:
    fams, (amo_30, nog_30, edges_30) = parse_rb_families()
    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Model RB forced-satisfiable CSP to SAT benchmark diagram">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">Model RB Forced-Satisfiable CSP → SAT Benchmarks (frb30-15 .. frb59-26)</text>')
    a('<text x="26" y="54" font-size="12" fill="#475569">Growing domain d = n^α (α = 0.8), hidden planted assignment &amp; exact phase transition p_c = 1 − e^(−α/r) = 0.25 · 40 SAT instances</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: CSP Constraint Graph + Direct SAT Encoding
    lx, ly, lw, lh = 24, 78, 314, 380
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+14}" y="{ly+23}" font-size="12.5" font-weight="700" fill="#0f172a">1. Random Binary CSP Graph (k = 2)</text>')
    a(f'<text x="{lx+14}" y="{ly+38}" font-size="10" fill="#475569">n CSP vars, domain d = n^0.8, m = r·n·ln n edges</text>')

    # Draw 6-node CSP graph
    cx0, cy0, rad = lx + lw / 2, ly + 124, 62
    nodes = []
    for i in range(6):
        ang = -math.pi / 2 + i * 2 * math.pi / 6
        nodes.append((cx0 + rad * math.cos(ang), cy0 + rad * math.sin(ang)))

    csp_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 3), (1, 4), (2, 5)]
    for u, v in csp_edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        is_hl = (u, v) == (1, 2)
        col = "#dc2626" if is_hl else "#94a3b8"
        w_e = "2.4" if is_hl else "1.3"
        a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w_e}"/>')

    # Highlight edge label
    mx = (nodes[1][0] + nodes[2][0]) / 2 + 24
    my = (nodes[1][1] + nodes[2][1]) / 2 + 3
    a(f'<rect x="{mx-18:.1f}" y="{my-10:.1f}" width="44" height="16" rx="3" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.8"/>')
    a(f'<text x="{mx+4:.1f}" y="{my+1:.1f}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#b91c1c">p·d² ✗</text>')

    for i, (nx, ny) in enumerate(nodes):
        hl = i in (1, 2)
        fill = "#eff6ff" if hl else "#ffffff"
        strk = "#2563eb" if hl else "#475569"
        a(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="16" fill="{fill}" stroke="{strk}" stroke-width="1.6"/>')
        a(f'<text x="{nx:.1f}" y="{ny+4:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0f172a">X{chr(0x2081+i)}</text>')

    # Direct SAT Encoding Formula Card inside Left Panel
    ey = ly + 206
    a(f'<rect x="{lx+12}" y="{ey}" width="{lw-24}" height="162" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    a(f'<text x="{lx+22}" y="{ey+19}" font-size="11" font-weight="700" fill="#0f172a">Direct CNF Encoding (n·d Boolean vars)</text>')

    enc_lines = [
        ("ALO (n cls, k=d):", "(x_{i,1} ∨ x_{i,2} ∨ … ∨ x_{i,d})", "#059669"),
        ("AMO (binary):", "(¬x_{i,a} ∨ ¬x_{i,b})  ∀ a &lt; b", "#2563eb"),
        ("Nogoods (binary):", "(¬x_{i,a} ∨ ¬x_{j,b})  forbidden", "#dc2626"),
    ]
    for idx, (hdr, fml, col) in enumerate(enc_lines):
        yy = ey + 38 + idx * 30
        a(f'<text x="{lx+22}" y="{yy}" font-size="9.5" font-weight="700" fill="{col}">{hdr}</text>')
        a(f'<text x="{lx+28}" y="{yy+13}" font-family="{MONO}" font-size="9.2" fill="#334155">{fml}</text>')

    # Parsed frb30-15-1 concrete numbers
    a(f'<line x1="{lx+20}" y1="{ey+127}" x2="{lx+lw-20}" y2="{ey+127}" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{lx+22}" y="{ey+142}" font-size="9.2" font-weight="700" fill="#475569">Parsed frb30-15-1 (30 vars, d=15, {edges_30} edges):</text>')
    a(f'<text x="{lx+22}" y="{ey+155}" font-family="{MONO}" font-size="9" fill="#0f172a">30 ALO + {amo_30:,} AMO + {nog_30:,} nogoods</text>')

    # Center Panel: d x d Forbidden Nogood Pair Matrix + Exact Phase Transition
    cx, cy, cw, ch = 352, 78, 302, 380
    a(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{cx+14}" y="{cy+23}" font-size="12.5" font-weight="700" fill="#0f172a">2. d × d Nogood Table (X₂, X₃)</text>')
    a(f'<text x="{cx+14}" y="{cy+38}" font-size="10" fill="#475569">p = 0.25 pairs forbidden; planted (a*, b*) kept free</text>')

    # 8x8 visual grid representing d x d nogood matrix (16 forbidden = 25%, planted at row 3, col 5)
    gsize = 8
    cell = 20
    gx0 = cx + 72
    gy0 = cy + 62
    planted = (3, 5)
    # Deterministic ~25% nogood cells (16 of 64), strictly excluding planted (3,5)
    nogood_set = {
        (0, 1), (0, 6), (1, 3), (1, 7),
        (2, 0), (2, 4), (3, 2), (3, 7),
        (4, 1), (4, 5), (5, 0), (5, 3),
        (6, 2), (6, 6), (7, 4), (7, 7),
    }

    a(f'<text x="{gx0 + gsize*cell/2:.1f}" y="{gy0-8}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#2563eb">Domain values b ∈ {{1..d}} of X₃</text>')
    a(f'<text x="{gx0-22}" y="{gy0 + gsize*cell/2:.1f}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#2563eb" transform="rotate(-90 {gx0-22} {gy0 + gsize*cell/2:.1f})">Domain a ∈ {{1..d}} of X₂</text>')

    for r in range(gsize):
        for c in range(gsize):
            rx_c = gx0 + c * cell
            ry_c = gy0 + r * cell
            if (r, c) == planted:
                a(f'<rect x="{rx_c}" y="{ry_c}" width="{cell-1.5}" height="{cell-1.5}" rx="3" fill="#059669" stroke="#047857" stroke-width="1.2"/>')
                a(f'<text x="{rx_c+(cell-1.5)/2:.1f}" y="{ry_c+13}" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff">★</text>')
            elif (r, c) in nogood_set:
                a(f'<rect x="{rx_c}" y="{ry_c}" width="{cell-1.5}" height="{cell-1.5}" rx="3" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
                a(f'<text x="{rx_c+(cell-1.5)/2:.1f}" y="{ry_c+13}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#dc2626">×</text>')
            else:
                a(f'<rect x="{rx_c}" y="{ry_c}" width="{cell-1.5}" height="{cell-1.5}" rx="3" fill="#ffffff" stroke="#cbd5e1" stroke-width="0.7"/>')

    # Matrix legend
    mly = gy0 + gsize * cell + 14
    a(f'<rect x="{cx+22}" y="{mly-8}" width="12" height="12" rx="2" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
    a(f'<text x="{cx+28}" y="{mly+1.5}" text-anchor="middle" font-size="9" font-weight="700" fill="#dc2626">×</text>')
    a(f'<text x="{cx+39}" y="{mly+1.5}" font-size="9.5" fill="#334155">Nogood (¬x ∨ ¬y)</text>')
    a(f'<rect x="{cx+152}" y="{mly-8}" width="12" height="12" rx="2" fill="#059669"/>')
    a(f'<text x="{cx+158}" y="{mly+1.5}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#ffffff">★</text>')
    a(f'<text x="{cx+169}" y="{mly+1.5}" font-size="9.5" fill="#047857" font-weight="700">Planted (a*, b*)</text>')

    # Exact Phase Transition Inset inside Center Panel
    pty = cy + 252
    a(f'<rect x="{cx+12}" y="{pty}" width="{cw-24}" height="116" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    a(f'<text x="{cx+22}" y="{pty+18}" font-size="10.8" font-weight="700" fill="#0f172a">Exact Phase Transition (Xu &amp; Li 2000)</text>')
    a(f'<text x="{cx+22}" y="{pty+33}" font-family="{MONO}" font-size="9.8" font-weight="700" fill="#b45309">p_c = 1 − e^(−α/r) = 1 − 3/4 = 0.25</text>')

    # Mini step curve p in [0.05, 0.45]
    mx0, my0, mx1, my1 = cx + 38, pty + 44, cx + cw - 28, pty + 94
    mw, mh = mx1 - mx0, my1 - my0
    a(f'<rect x="{mx0}" y="{my0}" width="{mw}" height="{mh}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="0.8"/>')
    p_pts = []
    for i in range(61):
        pv = 0.05 + 0.40 * i / 60.0
        yv = 1.0 / (1.0 + math.exp((pv - 0.25) / 0.014))
        p_pts.append((mx0 + (pv - 0.05) / 0.40 * mw, my1 - yv * (mh - 6) - 3))
    a(f'<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in p_pts) + '" fill="none" stroke="#2563eb" stroke-width="2.2"/>')
    xpc = mx0 + (0.25 - 0.05) / 0.40 * mw
    a(f'<line x1="{xpc:.1f}" y1="{my0}" x2="{xpc:.1f}" y2="{my1}" stroke="#d97706" stroke-width="1.4" stroke-dasharray="4,2"/>')
    a(f'<circle cx="{xpc:.1f}" cy="{(my0+my1)/2:.1f}" r="4" fill="#059669" stroke="#ffffff" stroke-width="1.2"/>')
    a(f'<text x="{mx0}" y="{my1+12}" font-size="8.5" fill="#64748b">p=0.05</text>')
    a(f'<text x="{xpc:.1f}" y="{my1+12}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#b45309">p_c=0.25</text>')
    a(f'<text x="{mx1}" y="{my1+12}" text-anchor="end" font-size="8.5" fill="#64748b">0.45</text>')

    # Right Panel: Parsed Scaling Ladder (all 8 size classes, 40 SAT instances)
    rx, ry, rw, rh = 668, 78, 228, 380
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+12}" y="{ry+23}" font-size="12.5" font-weight="700" fill="#0f172a">3. Corpus Scaling (40 SAT)</text>')
    a(f'<text x="{rx+12}" y="{ry+38}" font-size="9.8" fill="#475569">8 classes × 5 seeds (cnf-orig/)</text>')

    max_cls = max(f[4] for f in fams) if fams else 132295
    for idx, (fam, n_csp, d, nv, nc) in enumerate(fams):
        yy = ry + 56 + idx * 34
        hard = n_csp >= 45
        bar_col = "#dc2626" if hard else ("#d97706" if n_csp == 40 else "#059669")
        bw_c = (nc / max_cls) * 116
        a(f'<text x="{rx+12}" y="{yy+11}" font-family="{MONO}" font-size="10" font-weight="700" fill="#0f172a">{fam}</text>')
        a(f'<text x="{rx+rw-12}" y="{yy+11}" text-anchor="end" font-family="{MONO}" font-size="9" fill="#475569">{nv:,}v / {nc//1000}k cls</text>')
        a(f'<rect x="{rx+12}" y="{yy+16}" width="140" height="9" rx="3" fill="#e2e8f0"/>')
        a(f'<rect x="{rx+12}" y="{yy+16}" width="{bw_c:.1f}" height="9" rx="3" fill="{bar_col}"/>')
        tag = "&gt;5s wall" if hard else ("mixed" if n_csp == 40 else "solved")
        a(f'<text x="{rx+158}" y="{yy+24}" font-size="8.6" font-weight="700" fill="{bar_col}">{tag}</text>')

    # Bottom hardness note inside Right Panel
    ny = ry + 332
    a(f'<rect x="{rx+10}" y="{ny}" width="{rw-20}" height="38" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ny+15}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#991b1b">CDCL Hardness Wall (frb45–59)</text>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ny+29}" text-anchor="middle" font-size="8.8" fill="#7f1d1d">0/25 solved in 5 s across all 5 solvers</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
