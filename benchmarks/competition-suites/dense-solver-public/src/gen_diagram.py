#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for dense-solver-public."""
from __future__ import annotations

import csv
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 480
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_public() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    csv_path = COL / "src" / "public-inputs.csv"
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rows.append(r)
    return rows


def map_domain(r: dict[str, str]) -> str:
    fam = r["family"]
    if fam == "random-3sat":
        return "Random 3-SAT (uf/uuf50)"
    if fam in ("pigeonhole", "pigeon-hole", "subset-cardinality", "mutilated-chessboard"):
        return "Counting: PHP / Chess / Card."
    if fam in ("parity-learning", "tseitin-formulas"):
        return "Parity & Tseitin XOR"
    if fam in ("planning", "scheduling"):
        return "Planning & Scheduling"
    if fam == "graph-coloring":
        return "Graph Coloring (flat30)"
    if fam in ("hamiltonian", "hgen"):
        return "Hamiltonian & hgen"
    return "FPGA Routing (SC25)"


def main() -> None:
    rows = parse_public()
    n_tot = len(rows)
    n_sat = sum(1 for r in rows if r["answer"] == "SAT")
    n_unsat = sum(1 for r in rows if r["answer"] == "UNSAT")
    n_satlib = sum(1 for r in rows if r["suite"] == "SATLIB")
    n_sc25 = sum(1 for r in rows if r["suite"] == "SC2025")

    domain_order = [
        ("Random 3-SAT (uf/uuf50)", "#2563eb", "uf50-01..04, uuf50-01..04"),
        ("Counting: PHP / Chess / Card.", "#dc2626", "hole6..10, sc25-php/mchess/card"),
        ("Parity & Tseitin XOR", "#7c3aed", "par8-1..3-c, sc25-tseitin (323 XORs)"),
        ("Planning & Scheduling", "#059669", "anomaly, medium, bw_large.a, sc25-sch"),
        ("Graph Coloring (flat30)", "#d97706", "flat30-1..3 (3-coloring)"),
        ("Hamiltonian & hgen", "#0891b2", "sc25-hamiltonian, sc25-hgen"),
        ("FPGA Routing (SC25)", "#475569", "sc25-fpga-routing (homer11)"),
    ]
    dom_counts: dict[str, list[int]] = {d[0]: [0, 0] for d in domain_order}
    for r in rows:
        dm = map_domain(r)
        dom_counts[dm][0 if r["answer"] == "SAT" else 1] += 1

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="dense-solver-public 30-instance multi-domain map">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(f'<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">dense-solver Public Multi-Domain Benchmark Suite ({n_tot} Instances)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">{n_satlib} SATLIB classics + {n_sc25} SAT Competition 2025 Main Track representatives across 7 domains · {n_sat} SAT / {n_unsat} UNSAT</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: Multi-Domain Breakdown (Parsed from public-inputs.csv)
    lx, ly, lw, lh = 24, 78, 492, 380
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="#0f172a">Domain &amp; Verdict Map (Parsed from public-inputs.csv)</text>')
    a(f'<text x="{lx+16}" y="{ly+40}" font-size="10.5" fill="#475569">Each bar splits SAT (green) vs. UNSAT (red) across all 30 committed CNFs</text>')

    bar_x = lx + 224
    max_bar = 190
    max_cnt = 8
    for idx, (dom, col, ex_txt) in enumerate(domain_order):
        ns, nu = dom_counts[dom]
        tot = ns + nu
        yy = ly + 62 + idx * 42
        # Domain title + members
        dom_xml = dom.replace("&", "&amp;")
        a(f'<circle cx="{lx+18}" cy="{yy+7}" r="4.5" fill="{col}"/>')
        a(f'<text x="{lx+29}" y="{yy+11}" font-size="10.8" font-weight="700" fill="#0f172a">{dom_xml}</text>')
        a(f'<text x="{lx+29}" y="{yy+24}" font-family="{MONO}" font-size="8.4" fill="#64748b">{ex_txt}</text>')

        # Stacked SAT / UNSAT bar
        w_s = (ns / max_cnt) * max_bar
        w_u = (nu / max_cnt) * max_bar
        a(f'<rect x="{bar_x}" y="{yy+2}" width="{max_bar}" height="16" rx="4" fill="#e2e8f0"/>')
        if ns > 0:
            a(f'<rect x="{bar_x}" y="{yy+2}" width="{w_s:.1f}" height="16" rx="4" fill="#059669"/>')
        if nu > 0:
            a(f'<rect x="{bar_x+w_s:.1f}" y="{yy+2}" width="{w_u:.1f}" height="16" rx="4" fill="#dc2626"/>')

        # Count label right of bar
        a(f'<text x="{bar_x + max_bar + 8}" y="{yy+14}" font-family="{MONO}" font-size="9.5" font-weight="700" fill="#1e293b">{tot} ({ns}S/{nu}U)</text>')

    # Legend strip inside bottom of left panel
    lby = ly + 358
    a(f'<rect x="{lx+16}" y="{lby-9}" width="12" height="12" rx="2" fill="#059669"/>')
    a(f'<text x="{lx+33}" y="{lby+1}" font-size="10" fill="#334155">SAT ({n_sat})</text>')
    a(f'<rect x="{lx+102}" y="{lby-9}" width="12" height="12" rx="2" fill="#dc2626"/>')
    a(f'<text x="{lx+119}" y="{lby+1}" font-size="10" fill="#334155">UNSAT ({n_unsat})</text>')
    a(f'<text x="{lx+lw-16}" y="{lby+1}" text-anchor="end" font-size="9.8" fill="#475569">Total: 323 native XORs · 4 formats</text>')

    # Right Panel: Real Vars vs. Clauses Log-Log Scatter Plot
    rx, ry, rw, rh = 530, 78, 366, 380
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+24}" font-size="13" font-weight="700" fill="#0f172a">Instance Footprint: Vars vs. Clauses (Log–Log)</text>')
    a(f'<text x="{rx+14}" y="{ry+40}" font-size="10" fill="#475569">Circles = SATLIB (22) · Diamonds = SC 2025 (8) · Green = SAT, Red = UNSAT</text>')

    px0, py0, px1, py1 = rx + 54, ry + 56, rx + rw - 20, ry + 318
    pw, ph = px1 - px0, py1 - py0
    # Log10 bounds: vars in [30, 1000] -> [1.48, 3.0], clauses in [100, 7000] -> [2.0, 3.85]
    lv_min, lv_max = math.log10(32), math.log10(1050)
    lc_min, lc_max = math.log10(100), math.log10(6500)

    def sx_v(v: int) -> float:
        return px0 + (math.log10(max(v, 32)) - lv_min) / (lv_max - lv_min) * pw

    def sy_c(c: int) -> float:
        return py1 - (math.log10(max(c, 100)) - lc_min) / (lc_max - lc_min) * ph

    a(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1"/>')

    # Reference alpha=4.27 diagonal line (m = 4.27 * n)
    x_d0, y_d0 = sx_v(35), sy_c(int(35 * 4.27))
    x_d1, y_d1 = sx_v(950), sy_c(int(950 * 4.27))
    a(f'<line x1="{x_d0:.1f}" y1="{y_d0:.1f}" x2="{x_d1:.1f}" y2="{y_d1:.1f}" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="5,3"/>')
    a(f'<text x="{sx_v(620):.1f}" y="{sy_c(3200):.1f}" font-size="8.6" fill="#64748b" transform="rotate(-38 {sx_v(620):.1f} {sy_c(3200):.1f})">α = 4.27</text>')

    # Grid lines
    for v_tick in (50, 100, 200, 500, 1000):
        xx = sx_v(v_tick)
        a(f'<line x1="{xx:.1f}" y1="{py0}" x2="{xx:.1f}" y2="{py1}" stroke="#e2e8f0" stroke-width="0.7"/>')
        a(f'<text x="{xx:.1f}" y="{py1+14}" text-anchor="middle" font-size="9" fill="#475569">{v_tick}</text>')
    for c_tick in (100, 300, 1000, 3000, 6000):
        yy = sy_c(c_tick)
        a(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px1}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="0.7"/>')
        lbl = f"{c_tick//1000}k" if c_tick >= 1000 else str(c_tick)
        a(f'<text x="{px0-6}" y="{yy+3:.1f}" text-anchor="end" font-size="9" fill="#475569">{lbl}</text>')

    # Plot all 30 points (slight deterministic jitter only for exact duplicates uf50/uuf50/flat30)
    seen_pos: dict[tuple[int, int], int] = {}
    label_specs = {
        "hole6": (9, 3, "start", "hole6"),
        "hole10": (-8, -7, "end", "hole10"),
        "bw_large.a": (-8, -5, "end", "bw_large.a"),
        "sc25-pigeon-hole": (-8, -4, "end", "sc25-php"),
        "sc25-mutilated-chessboard": (-4, 16, "end", "sc25-mchess"),
        "sc25-hamiltonian": (8, -5, "start", "sc25-ham"),
        "sc25-tseitin-formulas": (9, 11, "start", "sc25-tseitin"),
        "sc25-subset-cardinality": (9, 10, "start", "sc25-card"),
        "uf50-01": (-10, -29, "start", "uf/uuf50 (8)"),
    }
    for r in rows:
        nv, nc = int(r["vars"]), int(r["clauses"])
        key = (nv, nc)
        idx_dup = seen_pos.get(key, 0)
        seen_pos[key] = idx_dup + 1
        # Small fan-out for identical (nv, nc)
        ang = idx_dup * 1.1
        jx = (3.0 * math.cos(ang)) if idx_dup > 0 else 0.0
        jy = (3.0 * math.sin(ang)) if idx_dup > 0 else 0.0
        xx = sx_v(nv) + jx
        yy = sy_c(nc) + jy
        col = "#059669" if r["answer"] == "SAT" else "#dc2626"
        if r["suite"] == "SC2025":
            rad = 5.6
            a(f'<polygon points="{xx:.1f},{yy-rad:.1f} {xx+rad:.1f},{yy:.1f} {xx:.1f},{yy+rad:.1f} {xx-rad:.1f},{yy:.1f}" fill="{col}" fill-opacity="0.9" stroke="#ffffff" stroke-width="1.2"/>')
        else:
            a(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4.5" fill="{col}" fill-opacity="0.88" stroke="#ffffff" stroke-width="1.1"/>')

        rid = r["id"]
        if rid in label_specs:
            dx, dy_l, anc, txt = label_specs[rid]
            a(f'<text x="{xx+dx:.1f}" y="{yy+dy_l:.1f}" text-anchor="{anc}" font-family="{MONO}" font-size="8.4" font-weight="700" fill="#1e293b">{txt}</text>')

    a(f'<text x="{(px0+px1)/2:.1f}" y="{py1+30}" text-anchor="middle" font-size="10.2" font-weight="600" fill="#1e293b">Variables n (log scale)</text>')
    a(f'<text x="{rx+18}" y="{(py0+py1)/2:.1f}" text-anchor="middle" font-size="10.2" font-weight="600" fill="#1e293b" transform="rotate(-90 {rx+18} {(py0+py1)/2:.1f})">Clauses m (log scale)</text>')

    # Legend inside bottom of right panel
    rly = ry + 362
    a(f'<circle cx="{rx+24}" cy="{rly-3}" r="4.5" fill="#475569"/>')
    a(f'<text x="{rx+34}" y="{rly+1}" font-size="9.5" fill="#334155">SATLIB (22)</text>')
    a(f'<polygon points="{rx+114},{rly-8} {rx+119},{rly-3} {rx+114},{rly+2} {rx+109},{rly-3}" fill="#475569"/>')
    a(f'<text x="{rx+124}" y="{rly+1}" font-size="9.5" fill="#334155">SC25 (8)</text>')
    a(f'<text x="{rx+rw-14}" y="{rly+1}" text-anchor="end" font-size="9.2" fill="#475569">42–760 v · 133–4,675 c</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
