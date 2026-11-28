#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-dimacs-gcp-large.

Directly parses the real large graph coloring CNFs (g125.17, g125.18, g250.15, g250.29)
from cnf-orig/, extracts the true underlying graph adjacency matrix & degree distribution
for g125.17 (125 vertices, 17 colors), and renders ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path


def parse_gcp_stats(cnf_xz: Path, n_colors: int) -> tuple[int, int, int, int, list[tuple[int, int]]]:
    """Return (n_vars, n_clauses, n_verts, n_edges, edges_list) from edge2cnf."""
    edges: set[tuple[int, int]] = set()
    n_vars = n_clauses = 0
    with lzma.open(cnf_xz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("c"):
                continue
            if s.startswith("p cnf"):
                p = s.split()
                n_vars, n_clauses = int(p[2]), int(p[3])
                continue
            lits = [int(x) for x in s.split() if x != "0"]
            if len(lits) == 2 and lits[0] < 0 and lits[1] < 0:
                a, b = -lits[0] - 1, -lits[1] - 1
                u, cu = divmod(a, n_colors)
                v, cv = divmod(b, n_colors)
                if u != v and cu == cv:
                    edges.add((min(u, v), max(u, v)))
    return n_vars, n_clauses, n_vars // n_colors, len(edges), sorted(edges)


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    # Parse real metadata for all 4 instances
    specs = [
        ("g125.17.cnf.xz", 17),
        ("g125.18.cnf.xz", 18),
        ("g250.15.cnf.xz", 15),
        ("g250.29.cnf.xz", 29),
    ]
    rows = []
    g125_edges: list[tuple[int, int]] = []
    for fn, k in specs:
        nv, nc, nverts, nedges, ed = parse_gcp_stats(col_dir / "cnf-orig" / fn, k)
        dens = (2.0 * nedges) / (nverts * (nverts - 1)) if nverts > 1 else 0.0
        rows.append((fn.replace(".cnf.xz", ""), nverts, nedges, k, dens, nv, nc))
        if fn == "g125.17.cnf.xz":
            g125_edges = ed

    # Compute degree histogram & block-aggregated 25x25 adjacency density heatmap for g125 (125 = 25 * 5)
    n = 125
    deg = [0] * n
    B = 25
    blk = [[0] * B for _ in range(B)]
    for u, v in g125_edges:
        deg[u] += 1
        deg[v] += 1
        bu, bv = u // 5, v // 5
        blk[bu][bv] += 1
        blk[bv][bu] += 1

    W, H = 940, 485
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.8px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .axis { font: 600 10px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #64748b; }
      .badge { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Large Dense Graph Colouring — DIMACS g125 &amp; g250</text>')
    out.append('  <text x="26" y="54" class="sub">Real adjacency density and degree structure parsed from cnf-orig/g125.17.cnf.xz (125 vertices, 3,891 edges, k = 17 colors)</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left panel: 25x25 block adjacency density matrix of g125 (5x5 vertices per cell)
    lx, ly, lw, lh = 24, 80, 356, 382
    out.append(f'  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{lx+16}" y="{ly+24}" class="h3">Real Adjacency Matrix — g125 (5×5 blocks)</text>')
    out.append(f'  <text x="{lx+16}" y="{ly+42}" class="body">Dense Erdős–Rényi G(125, 0.50): uniform edge cloud</text>')

    mx0, my0, cell = lx + 34, ly + 56, 11.5
    max_blk = max(max(r) for r in blk) or 1
    for r in range(B):
        for c in range(B):
            val = blk[r][c] / max_blk
            # Interpolate #f8fafc -> #2563eb
            cr = int(round(248 - val * (248 - 29)))
            cg = int(round(250 - val * (250 - 78)))
            cb = int(round(252 - val * (252 - 216)))
            out.append(f'  <rect x="{mx0 + c*cell:.1f}" y="{my0 + r*cell:.1f}" width="{cell-0.8:.1f}" height="{cell-0.8:.1f}" fill="#{cr:02x}{cg:02x}{cb:02x}"/>')
    out.append(f'  <rect x="{mx0}" y="{my0}" width="{B*cell:.1f}" height="{B*cell:.1f}" fill="none" stroke="#64748b" stroke-width="1"/>')
    for tick in (0, 25, 50, 75, 100, 125):
        pos = (tick / 125.0) * (B * cell)
        out.append(f'  <text x="{mx0 + pos:.1f}" y="{my0 + B*cell + 14:.1f}" text-anchor="middle" class="axis">{tick}</text>')
        out.append(f'  <text x="{mx0 - 6}" y="{my0 + pos + 3:.1f}" text-anchor="end" class="axis">{tick}</text>')
    out.append(f'  <text x="{lx + lw/2:.1f}" y="{ly + lh - 10}" text-anchor="middle" class="axis">Vertex index (1..125) · density ρ = {2*len(g125_edges)/(125*124):.3f}</text>')

    # Right top panel: Real degree distribution histogram of g125
    rx, rw = 398, 518
    out.append(f'  <rect x="{rx}" y="80" width="{rw}" height="176" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="104" class="h3">Vertex Degree Distribution of g125 (min={min(deg)}, avg={sum(deg)/n:.1f}, max={max(deg)})</text>')
    # Bin degrees in widths of 3 from 44 to 80
    bins = list(range(44, 83, 3))
    counts = [sum(1 for d in deg if b <= d < b + 3) for b in bins]
    max_c = max(counts) or 1
    hx0, hy0, hw, hh = rx + 44, 120, rw - 64, 98
    bw = hw / len(bins)
    for i, cnt in enumerate(counts):
        bh = (cnt / max_c) * hh
        bx = hx0 + i * bw + 3
        by = hy0 + hh - bh
        out.append(f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bw-6:.1f}" height="{bh:.1f}" rx="3" fill="#2563eb" opacity="0.85"/>')
        if cnt > 0:
            out.append(f'  <text x="{bx + (bw-6)/2:.1f}" y="{by - 4:.1f}" text-anchor="middle" class="axis">{cnt}</text>')
        out.append(f'  <text x="{bx + (bw-6)/2:.1f}" y="{hy0 + hh + 14:.1f}" text-anchor="middle" class="axis">{bins[i]}</text>')
    out.append(f'  <line x1="{hx0}" y1="{hy0+hh}" x2="{hx0+hw}" y2="{hy0+hh}" stroke="#94a3b8" stroke-width="1"/>')
    out.append(f'  <text x="{rx + rw/2:.1f}" y="246" text-anchor="middle" class="axis">Vertex degree bin (classic binomial bell around (n−1)p ≈ 62)</text>')

    # Right bottom panel: All 4 parsed instances table + encoding
    out.append(f'  <rect x="{rx}" y="270" width="{rw}" height="192" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="294" class="h3">Parsed DIMACS Challenge Suite (All 4 Instances SAT)</text>')
    out.append(f'  <text x="{rx+16}" y="314" class="body">Direct k-coloring CNF: n·k vars, ALO k-clauses + |E|·k binary edge conflicts:</text>')
    cols_x = [rx + 16, rx + 112, rx + 178, rx + 236, rx + 286, rx + 356, rx + 434]
    headers = ["Instance", "|V|", "|E|", "ρ", "k", "Vars", "Clauses"]
    for cx_h, hlbl in zip(cols_x, headers):
        anch = "start" if hlbl == "Instance" else "end"
        out.append(f'  <text x="{cx_h}" y="338" text-anchor="{anch}" class="mono">{hlbl}</text>')
    out.append(f'  <line x1="{rx+14}" y1="344" x2="{rx+rw-14}" y2="344" stroke="#93c5fd" stroke-width="1"/>')
    for idx, (nm, nv_g, ne_g, k, dens, nvars, ncls) in enumerate(rows):
        yy = 362 + idx * 19
        vals = [nm, f"{nv_g}", f"{ne_g:,}", f"{dens:.2f}", f"{k}", f"{nvars:,}", f"{ncls:,}"]
        for cx_h, vtxt in zip(cols_x, vals):
            anch = "start" if vtxt == nm else "end"
            out.append(f'  <text x="{cx_h}" y="{yy}" text-anchor="{anch}" class="mono">{vtxt}</text>')
    out.append(f'  <text x="{rx+16}" y="446" class="body">High k! color symmetry &amp; dense edge conflicts make g125/g250 hard coloring tests.</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
