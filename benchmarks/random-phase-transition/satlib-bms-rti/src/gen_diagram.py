#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-bms-rti."""
from __future__ import annotations

import lzma
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_bms_rti() -> list[tuple[str, str, int, int, float]]:
    rows = []
    cnf_dir = COL / "cnf-orig"
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*.cnf.xz")):
            n = m = 0
            active_vars: set[int] = set()
            with lzma.open(p, "rt", errors="replace") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("c"):
                        continue
                    if s.startswith("p cnf"):
                        parts = s.split()
                        n, m = int(parts[2]), int(parts[3])
                    else:
                        toks = s.split()
                        if toks and toks[-1] == "0":
                            for t in toks[:-1]:
                                active_vars.add(abs(int(t)))
            stem = p.name.replace(".cnf.xz", "")
            fam = "BMS" if stem.startswith("BMS") else "RTI"
            act_n = len(active_vars) or n
            rows.append((stem, fam, act_n, m, m / act_n))
    # Sort RTI first then BMS
    rows.sort(key=lambda r: (0 if r[1] == "RTI" else 1, r[0]))
    return rows


def main() -> None:
    rows = parse_bms_rti()
    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB Backbone-Minimal BMS vs RTI diagram">')
    a('<defs>')
    a('  <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>')
    a('  <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/></marker>')
    a('</defs>')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB Backbone-Minimal (BMS) vs. Random 3-SAT (RTI)</text>')
    a('<text x="26" y="54" font-size="12" fill="#475569">Iterative clause deletion strips redundant clauses until dropping any single clause shatters the frozen backbone · 4 SAT samples (from 1,000)</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: 3-Stage Backbone-Minimal Deletion Process
    lx, ly, lw, lh = 24, 78, 558, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">Backbone-Minimal Subformula Extraction (Singer, Gent &amp; Smaill)</text>')

    # Stage 1 box: RTI (Full forced-SAT random 3-SAT)
    s1x, s1y, bw, bh = lx + 16, ly + 42, 152, 232
    a(f'<rect x="{s1x}" y="{s1y}" width="{bw}" height="{bh}" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="1.4"/>')
    a(f'<rect x="{s1x}" y="{s1y}" width="{bw}" height="28" rx="8" fill="#2563eb"/>')
    a(f'<rect x="{s1x}" y="{s1y+16}" width="{bw}" height="12" fill="#2563eb"/>')
    a(f'<text x="{s1x+bw/2:.1f}" y="{s1y+19}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffffff">1. Full RTI Formula</text>')
    a(f'<text x="{s1x+bw/2:.1f}" y="{s1y+45}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="600" fill="#1e3a8a">n = 100, m = 429</text>')
    a(f'<text x="{s1x+bw/2:.1f}" y="{s1y+59}" text-anchor="middle" font-size="9.5" fill="#64748b">α = 4.29 (Near-crit)</text>')

    # Grid of 20 mini clauses: 12 essential (purple) + 8 redundant (slate)
    ess_set = {0, 1, 2, 4, 5, 7, 8, 10, 12, 13, 15, 17}
    for k in range(20):
        col_i = k % 4
        row_i = k // 4
        cx = s1x + 15 + col_i * 31
        cy = s1y + 72 + row_i * 22
        is_e = k in ess_set
        fill = "#f5f3ff" if is_e else "#f1f5f9"
        strk = "#7c3aed" if is_e else "#94a3b8"
        tc = "#5b21b6" if is_e else "#64748b"
        a(f'<rect x="{cx}" y="{cy}" width="26" height="16" rx="3" fill="{fill}" stroke="{strk}" stroke-width="1"/>')
        a(f'<text x="{cx+13}" y="{cy+11.5}" text-anchor="middle" font-family="{MONO}" font-size="8.2" font-weight="700" fill="{tc}">C{k+1}</text>')

    a(f'<rect x="{s1x+12}" y="{s1y+188}" width="{bw-24}" height="32" rx="5" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="0.9"/>')
    a(f'<text x="{s1x+bw/2:.1f}" y="{s1y+202}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#5b21b6">Backbone B = B₀</text>')
    a(f'<text x="{s1x+bw/2:.1f}" y="{s1y+214}" text-anchor="middle" font-size="8.8" fill="#6d28d9">~35% clauses redundant</text>')

    # Arrow 1 -> 2
    a1x0, a1x1, ay_mid = s1x + bw + 4, s1x + bw + 34, s1y + 116
    a(f'<line x1="{a1x0}" y1="{ay_mid}" x2="{a1x1}" y2="{ay_mid}" stroke="#475569" stroke-width="2" marker-end="url(#arr-slate)"/>')
    a(f'<text x="{(a1x0+a1x1)/2:.1f}" y="{ay_mid-16}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#475569">Prune</text>')
    a(f'<text x="{(a1x0+a1x1)/2:.1f}" y="{ay_mid-6}" text-anchor="middle" font-size="8.2" fill="#64748b">B fixed</text>')

    # Stage 2 box: BMS (Backbone-Minimal Subformula)
    s2x = s1x + bw + 38
    a(f'<rect x="{s2x}" y="{s1y}" width="{bw}" height="{bh}" rx="8" fill="#ffffff" stroke="#7c3aed" stroke-width="1.6"/>')
    a(f'<rect x="{s2x}" y="{s1y}" width="{bw}" height="28" rx="8" fill="#7c3aed"/>')
    a(f'<rect x="{s2x}" y="{s1y+16}" width="{bw}" height="12" fill="#7c3aed"/>')
    a(f'<text x="{s2x+bw/2:.1f}" y="{s1y+19}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffffff">2. Minimal BMS Core</text>')
    a(f'<text x="{s2x+bw/2:.1f}" y="{s1y+45}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="600" fill="#5b21b6">n ≈ 100, m = 272–286</text>')
    a(f'<text x="{s2x+bw/2:.1f}" y="{s1y+59}" text-anchor="middle" font-size="9.5" fill="#64748b">α = 2.72–2.92 (Under)</text>')

    for k in range(20):
        col_i = k % 4
        row_i = k // 4
        cx = s2x + 15 + col_i * 31
        cy = s1y + 72 + row_i * 22
        is_e = k in ess_set
        if is_e:
            a(f'<rect x="{cx}" y="{cy}" width="26" height="16" rx="3" fill="#7c3aed" stroke="#5b21b6" stroke-width="1"/>')
            a(f'<text x="{cx+13}" y="{cy+11.5}" text-anchor="middle" font-family="{MONO}" font-size="8.2" font-weight="700" fill="#ffffff">C{k+1}</text>')
        else:
            a(f'<rect x="{cx}" y="{cy}" width="26" height="16" rx="3" fill="none" stroke="#cbd5e1" stroke-width="0.9" stroke-dasharray="2,2"/>')

    a(f'<rect x="{s2x+12}" y="{s1y+188}" width="{bw-24}" height="32" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="0.9"/>')
    a(f'<text x="{s2x+bw/2:.1f}" y="{s1y+202}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#047857">Exact Same Backbone B₀</text>')
    a(f'<text x="{s2x+bw/2:.1f}" y="{s1y+214}" text-anchor="middle" font-size="8.8" fill="#065f46">100% clauses critical</text>')

    # Arrow 2 -> 3
    a2x0, a2x1 = s2x + bw + 4, s2x + bw + 34
    a(f'<line x1="{a2x0}" y1="{ay_mid}" x2="{a2x1}" y2="{ay_mid}" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,2" marker-end="url(#arr-red)"/>')
    a(f'<text x="{(a2x0+a2x1)/2:.1f}" y="{ay_mid-16}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#dc2626">Drop</text>')
    a(f'<text x="{(a2x0+a2x1)/2:.1f}" y="{ay_mid-6}" text-anchor="middle" font-size="8.2" fill="#b91c1c">any c</text>')

    # Stage 3 box: Shattered Backbone
    s3x = s2x + bw + 38
    a(f'<rect x="{s3x}" y="{s1y}" width="{bw}" height="{bh}" rx="8" fill="#ffffff" stroke="#dc2626" stroke-width="1.4"/>')
    a(f'<rect x="{s3x}" y="{s1y}" width="{bw}" height="28" rx="8" fill="#dc2626"/>')
    a(f'<rect x="{s3x}" y="{s1y+16}" width="{bw}" height="12" fill="#dc2626"/>')
    a(f'<text x="{s3x+bw/2:.1f}" y="{s1y+19}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffffff">3. Backbone Breaks</text>')
    a(f'<text x="{s3x+bw/2:.1f}" y="{s1y+45}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="600" fill="#991b1b">F_BMS \ {{c}}</text>')
    a(f'<text x="{s3x+bw/2:.1f}" y="{s1y+59}" text-anchor="middle" font-size="9.5" fill="#64748b">Minimality certificate</text>')

    for k in range(20):
        col_i = k % 4
        row_i = k // 4
        cx = s3x + 15 + col_i * 31
        cy = s1y + 72 + row_i * 22
        if k == 8:
            # Dropped clause highlighted in red dashed X
            a(f'<rect x="{cx}" y="{cy}" width="26" height="16" rx="3" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="3,2"/>')
            a(f'<text x="{cx+13}" y="{cy+11.5}" text-anchor="middle" font-size="10" font-weight="700" fill="#dc2626">×</text>')
        elif k in ess_set:
            # Partially unfrozen amber/slate
            fill = "#fffbeb" if k in (5, 7, 12, 13) else "#e0e7ff"
            strk = "#d97706" if k in (5, 7, 12, 13) else "#6366f1"
            tc = "#b45309" if k in (5, 7, 12, 13) else "#3730a3"
            a(f'<rect x="{cx}" y="{cy}" width="26" height="16" rx="3" fill="{fill}" stroke="{strk}" stroke-width="0.9"/>')
            a(f'<text x="{cx+13}" y="{cy+11.5}" text-anchor="middle" font-family="{MONO}" font-size="8.2" font-weight="700" fill="{tc}">C{k+1}</text>')
        else:
            a(f'<rect x="{cx}" y="{cy}" width="26" height="16" rx="3" fill="none" stroke="#e2e8f0" stroke-width="0.8" stroke-dasharray="2,2"/>')

    a(f'<rect x="{s3x+12}" y="{s1y+188}" width="{bw-24}" height="32" rx="5" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
    a(f'<text x="{s3x+bw/2:.1f}" y="{s1y+202}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b91c1c">|Backbone| Strictly Drops</text>')
    a(f'<text x="{s3x+bw/2:.1f}" y="{s1y+214}" text-anchor="middle" font-size="8.8" fill="#991b1b">Frozen vars unfreeze</text>')

    # Bottom explanation bar inside left panel
    by_note = ly + 286
    a(f'<rect x="{lx+16}" y="{by_note}" width="{lw-32}" height="58" rx="7" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{lx+28}" y="{by_note+19}" font-size="11" font-weight="700" fill="#0f172a">Why BMS Formulas Are Scientifically Interesting</text>')
    a(f'<text x="{lx+28}" y="{by_note+35}" font-size="10" fill="#334155">Even at α ≈ 2.8 (far below α_c = 4.267, ρ_crit ≈ 0.66×), BMS preserves the full frozen</text>')
    a(f'<text x="{lx+28}" y="{by_note+49}" font-size="10" fill="#334155">backbone of a critical-threshold RTI formula while elevating variable-degree skew (CV: 0.28 → 0.40).</text>')

    # Right Panel: Parsed Data Comparison of all 4 committed files
    rx, ry, rw, rh = 596, 78, 300, 360
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+24}" font-size="13" font-weight="700" fill="#0f172a">Parsed Corpus: RTI vs. BMS</text>')
    a(f'<text x="{rx+14}" y="{ry+40}" font-size="10.5" fill="#475569">Exact clause retention from cnf-orig/ (4 SAT)</text>')

    bar_x = rx + 16
    bar_max_w = rw - 32
    max_m = 450
    for i, (stem, fam, act_n, m, alpha) in enumerate(rows):
        yy = ry + 62 + i * 62
        is_rti = fam == "RTI"
        col = "#2563eb" if is_rti else "#7c3aed"
        bg = "#eff6ff" if is_rti else "#f5f3ff"
        rho = alpha / 4.267
        bw_m = (m / max_m) * (bar_max_w - 64)

        a(f'<text x="{bar_x}" y="{yy+12}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#0f172a">{stem}</text>')
        a(f'<rect x="{rx+rw-60}" y="{yy+1}" width="46" height="14" rx="3" fill="{bg}" stroke="{col}" stroke-width="0.8"/>')
        a(f'<text x="{rx+rw-37}" y="{yy+11.5}" text-anchor="middle" font-size="8.8" font-weight="700" fill="{col}">{fam}</text>')

        # Clause bar
        a(f'<rect x="{bar_x}" y="{yy+20}" width="{bar_max_w-64}" height="15" rx="4" fill="#e2e8f0"/>')
        a(f'<rect x="{bar_x}" y="{yy+20}" width="{bw_m:.1f}" height="15" rx="4" fill="{col}"/>')
        a(f'<text x="{bar_x + bar_max_w - 58}" y="{yy+31.5}" font-family="{MONO}" font-size="10" font-weight="700" fill="#1e293b">m={m}</text>')

        pct = (m / 429.0) * 100.0
        a(f'<text x="{bar_x}" y="{yy+47}" font-size="9.2" fill="#475569">active n={act_n} · α={alpha:.2f} · ρ_crit={rho:.2f}× ({pct:.0f}% of 429)</text>')

    # Bottom summary pill
    sy = ry + 314
    a(f'<rect x="{rx+14}" y="{sy}" width="{rw-28}" height="34" rx="7" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    a(f'<text x="{rx+rw/2:.1f}" y="{sy+14.5}" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">Clause Reduction: 429 → 272–286 (−33% to −37%)</text>')
    a(f'<text x="{rx+rw/2:.1f}" y="{sy+27}" text-anchor="middle" font-size="9.2" fill="#065f46">All 4 instances pure 3-SAT (k = 3), 0 XORs, SAT</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
