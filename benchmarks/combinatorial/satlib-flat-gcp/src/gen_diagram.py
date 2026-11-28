#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-flat-gcp.

Directly parses the real instance `cnf-orig/flat30-1.cnf.xz` (30 vertices, 60 edges),
solves for a verified exact 3-coloring in Python, computes a clean deterministic
force-directed layout, and renders ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
import math
from pathlib import Path
from xml.sax.saxutils import escape


def parse_flat30(cnf_xz: Path) -> tuple[int, list[tuple[int, int]]]:
    """Parse vertices and edges from edge2cnf 3-coloring CNF."""
    edges_set: set[tuple[int, int]] = set()
    n_vars = 0
    with lzma.open(cnf_xz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("c"):
                continue
            if s.startswith("p cnf"):
                n_vars = int(s.split()[2])
                continue
            lits = [int(x) for x in s.split() if x != "0"]
            if len(lits) == 2 and lits[0] < 0 and lits[1] < 0:
                a, b = -lits[0] - 1, -lits[1] - 1
                u, cu = divmod(a, 3)
                v, cv = divmod(b, 3)
                if u != v and cu == cv:
                    edges_set.add((min(u, v), max(u, v)))
    n_verts = n_vars // 3
    return n_verts, sorted(edges_set)


def solve_3coloring(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """Find a verified proper 3-coloring via MRV backtracking."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colors = [-1] * n

    def backtrack(assigned: int) -> bool:
        if assigned == n:
            return True
        # Pick unassigned vertex with fewest legal colors (tie-break by highest degree)
        best_v = -1
        best_opts: list[int] = [0, 1, 2, 3]
        for v in range(n):
            if colors[v] != -1:
                continue
            used = {colors[w] for w in adj[v] if colors[w] != -1}
            opts = [c for c in (0, 1, 2) if c not in used]
            if not opts:
                return False
            if len(opts) < len(best_opts) or (len(opts) == len(best_opts) and len(adj[v]) > len(adj[best_v])):
                best_v = v
                best_opts = opts
        for c in best_opts:
            colors[best_v] = c
            if backtrack(assigned + 1):
                return True
            colors[best_v] = -1
        return False

    if not backtrack(0):
        raise RuntimeError("flat30-1 should be 3-colorable")
    for u, v in edges:
        assert colors[u] != colors[v]
    return colors


def force_layout(n: int, edges: list[tuple[int, int]], colors: list[int]) -> list[tuple[float, float]]:
    """Deterministic Fruchterman-Reingold layout seeded by color class ring."""
    # Seed vertices in 3 sectors around a circle for crisp visual separation
    by_col = [[v for v in range(n) if colors[v] == c] for c in range(3)]
    xs = [0.0] * n
    ys = [0.0] * n
    for c in range(3):
        grp = by_col[c]
        for i, v in enumerate(grp):
            ang = 2 * math.pi * (c / 3.0 + (i + 0.5) / (3.0 * len(grp)))
            rad = 0.72 + 0.20 * ((i % 2) * 2 - 1)
            xs[v] = rad * math.cos(ang)
            ys[v] = rad * math.sin(ang)

    area = 4.0
    k = math.sqrt(area / n) * 0.92
    for step in range(280):
        t = 0.25 * (1.0 - step / 280.0) ** 1.4 + 0.004
        dx = [0.0] * n
        dy = [0.0] * n
        # Repulsion
        for i in range(n):
            for j in range(i + 1, n):
                vx = xs[i] - xs[j]
                vy = ys[i] - ys[j]
                d2 = vx * vx + vy * vy + 1e-6
                d = math.sqrt(d2)
                f = (k * k) / d
                fx, fy = (vx / d) * f, (vy / d) * f
                dx[i] += fx
                dy[i] += fy
                dx[j] -= fx
                dy[j] -= fy
        # Attraction
        for u, v in edges:
            vx = xs[u] - xs[v]
            vy = ys[u] - ys[v]
            d = math.sqrt(vx * vx + vy * vy + 1e-6)
            f = (d * d) / (k * 1.15)
            fx, fy = (vx / d) * f, (vy / d) * f
            dx[u] -= fx
            dy[u] -= fy
            dx[v] += fx
            dy[v] += fy
        # Gentle gravity toward origin
        for i in range(n):
            dx[i] -= 0.08 * xs[i]
            dy[i] -= 0.08 * ys[i]
            mag = math.sqrt(dx[i] * dx[i] + dy[i] * dy[i]) + 1e-9
            disp = min(mag, t)
            xs[i] += (dx[i] / mag) * disp
            ys[i] += (dy[i] / mag) * disp

    # Normalize to [0, 1] x [0, 1]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    rx = max(maxx - minx, 1e-6)
    ry = max(maxy - miny, 1e-6)
    return [((xs[i] - minx) / rx, (ys[i] - miny) / ry) for i in range(n)]


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    cnf_xz = col_dir / "cnf-orig" / "flat30-1.cnf.xz"
    n, edges = parse_flat30(cnf_xz)
    colors = solve_3coloring(n, edges)
    pts = force_layout(n, edges, colors)

    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    counts = [colors.count(c) for c in range(3)]

    W, H = 920, 480
    palette = [
        ("#2563eb", "#dbeafe", "Color 1 (Blue)"),
        ("#059669", "#d1fae5", "Color 2 (Emerald)"),
        ("#d97706", "#fef3c7", "Color 3 (Amber)"),
    ]

    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 12px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .vtxt { font: 700 9.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .badge { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Flat 3-Colourable Graph Coloring — Real Instance flat30-1</text>')
    out.append(f'  <text x="26" y="54" class="sub">Parsed directly from cnf-orig/flat30-1.cnf.xz ({n} vertices, {len(edges)} edges, degree {min(deg)}–{max(deg)}) with a verified proper 3-coloring</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left graph panel
    gx, gy, gw, gh = 24, 80, 520, 376
    out.append(f'  <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    pad_x, pad_y = 42, 36
    coords = [(gx + pad_x + px * (gw - 2 * pad_x), gy + pad_y + py * (gh - 2 * pad_y)) for px, py in pts]

    for u, v in edges:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#94a3b8" stroke-width="1.45" opacity="0.82"/>')
    for v, (x, y) in enumerate(coords):
        fill, _, _ = palette[colors[v]]
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="11.5" fill="{fill}" stroke="#ffffff" stroke-width="2"/>')
        out.append(f'  <text x="{x:.1f}" y="{y+3.3:.1f}" text-anchor="middle" class="vtxt">{v+1}</text>')

    # Verified badge inside graph box
    out.append('  <rect x="412" y="92" width="120" height="22" rx="11" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append('  <text x="472" y="106.5" text-anchor="middle" class="badge">0 edge conflicts ✓</text>')

    # Right explanatory panels
    rx, rw = 562, 334

    # Card 1: Flat Graph Construction
    out.append(f'  <rect x="{rx}" y="80" width="{rw}" height="126" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="104" class="h3">Culberson "Flat" Construction</text>')
    out.append(f'  <text x="{rx+16}" y="125" class="body">1. Partition V into 3 equal independent sets</text>')
    out.append(f'  <text x="{rx+28}" y="142" class="body">   (|C₁| = {counts[0]}, |C₂| = {counts[1]}, |C₃| = {counts[2]} vertices).</text>')
    out.append(f'  <text x="{rx+16}" y="162" class="body">2. Add cross-class edges while flattening</text>')
    out.append(f'  <text x="{rx+28}" y="179" class="body">   vertex degrees (deg ∈ [{min(deg)}, {max(deg)}]) to hide the</text>')
    out.append(f'  <text x="{rx+28}" y="196" class="body">   planted 3-coloring from degree heuristics.</text>')

    # Card 2: CNF Encoding
    out.append(f'  <rect x="{rx}" y="218" width="{rw}" height="134" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="242" class="h3">Direct 3-Color CNF Encoding (edge2cnf)</text>')
    out.append(f'  <text x="{rx+16}" y="264" class="body">Variables: xᵥ,c ∈ {{0,1}} for v ∈ 1..{n}, c ∈ {{1,2,3}}</text>')
    out.append(f'  <text x="{rx+16}" y="286" class="mono">ALO:  (xᵥ,₁ ∨ xᵥ,₂ ∨ xᵥ,₃)</text>')
    out.append(f'  <text x="{rx+16}" y="305" class="mono">AMO:  (¬xᵥ,a ∨ ¬xᵥ,b)   ∀a &lt; b</text>')
    out.append(f'  <text x="{rx+16}" y="324" class="mono">Edge: (¬xᵤ,c ∨ ¬xᵥ,c)   ∀{{u,v}} ∈ E, c</text>')
    out.append(f'  <text x="{rx+16}" y="343" class="body">flat30-1: 90 vars, 300 clauses → flat200: 600 vars</text>')

    # Card 3: Color Legend
    out.append(f'  <rect x="{rx}" y="364" width="{rw}" height="92" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="387" class="h3">Verified 3-Color Classes (flat30-1)</text>')
    for idx, (fill, soft, label) in enumerate(palette):
        ly = 406 + idx * 18
        out.append(f'  <circle cx="{rx+24}" cy="{ly-4}" r="5.5" fill="{fill}"/>')
        out.append(f'  <text x="{rx+38}" y="{ly}" class="body">{escape(label)} — {counts[idx]} vertices</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
