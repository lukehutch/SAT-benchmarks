#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-sw-gcp.

Directly parses three real morphed small-world 5-coloring instances from cnf-orig/:
  - sw100-8-p0-c5_sw100-1.cnf.xz  (pure ring lattice, p = 0)
  - sw100-8-lp4-c5_sw100-1.cnf.xz (intermediate Watts-Strogatz morphing)
  - sw100-8-lp0-c5_sw100-1.cnf.xz (strong random rewiring)
and renders their actual 100-vertex chord-ring edge topologies side-by-side.
"""
from __future__ import annotations

import lzma
import math
from pathlib import Path
from xml.sax.saxutils import escape


def parse_sw100(cnf_xz: Path) -> tuple[int, list[tuple[int, int]]]:
    """Extract undirected edges from 5-coloring edge2cnf DIMACS file."""
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
                u, cu = divmod(a, 5)
                v, cv = divmod(b, 5)
                if u != v and cu == cv:
                    edges_set.add((min(u, v), max(u, v)))
    return n_vars // 5, sorted(edges_set)


def ring_dist(u: int, v: int, n: int) -> int:
    d = abs(u - v)
    return min(d, n - d)


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    specs = [
        ("sw100-8-p0-c5_sw100-1.cnf.xz", "Pure Ring Lattice (p0)", "p = 0 · regular local structure", "#2563eb"),
        ("sw100-8-lp4-c5_sw100-1.cnf.xz", "Small-World Morphed (lp4)", "intermediate random rewiring", "#7c3aed"),
        ("sw100-8-lp0-c5_sw100-1.cnf.xz", "Heavily Rewired (lp0)", "dense long-range shortcut chords", "#d97706"),
    ]

    W, H = 940, 480
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .ptitle { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .psub { font: 400 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .stat { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #334155; }
      .foot { font: 400 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .foot-b { font: 700 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Morphed Small-World 5-Colouring Graphs (SATLIB sw100-8)</text>')
    out.append('  <text x="26" y="54" class="sub">Real 100-vertex edge topologies parsed from cnf-orig/: Watts–Strogatz rewiring interpolates ring lattice → random graph</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # 5-color ring palette for vertex dots (canonical cyclic 5-coloring of ring lattice)
    c5 = ["#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed"]

    for idx, (fname, title, sub, accent) in enumerate(specs):
        n, edges = parse_sw100(col_dir / "cnf-orig" / fname)
        # Classify local (ring distance <= 4) vs long-range shortcut chords (> 4)
        local_e = [(u, v) for u, v in edges if ring_dist(u, v, n) <= 4]
        short_e = [(u, v) for u, v in edges if ring_dist(u, v, n) > 4]

        px = 24 + idx * 302
        py, pw, ph = 78, 288, 326
        out.append(f'  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
        out.append(f'  <text x="{px+14}" y="{py+24}" class="ptitle">{escape(title)}</text>')
        out.append(f'  <text x="{px+14}" y="{py+41}" class="psub">{escape(sub)}</text>')

        cx, cy, rad = px + pw / 2.0, py + 178.0, 108.0
        vpos = [
            (cx + rad * math.cos(-math.pi / 2 + 2 * math.pi * i / n),
             cy + rad * math.sin(-math.pi / 2 + 2 * math.pi * i / n))
            for i in range(n)
        ]

        # Batch local edges into one compact <path>
        if local_e:
            d_loc = " ".join(f"M{vpos[u][0]:.1f},{vpos[u][1]:.1f}L{vpos[v][0]:.1f},{vpos[v][1]:.1f}" for u, v in local_e)
            out.append(f'  <path d="{d_loc}" fill="none" stroke="#475569" stroke-width="1.35" opacity="0.72"/>')

        # Batch rewired long-range chords into one compact <path>
        if short_e:
            parts_s = []
            for u, v in short_e:
                x1, y1 = vpos[u]
                x2, y2 = vpos[v]
                mx = (x1 + x2) * 0.5 * 0.65 + cx * 0.35
                my = (y1 + y2) * 0.5 * 0.65 + cy * 0.35
                parts_s.append(f"M{x1:.1f},{y1:.1f}Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}")
            op = "0.52" if len(short_e) < 120 else "0.26"
            sw = "1.15" if len(short_e) < 120 else "0.85"
            out.append(f'  <path d="{" ".join(parts_s)}" fill="none" stroke="{accent}" stroke-width="{sw}" opacity="{op}"/>')

        # Draw 100 ring vertices (colored cyclically mod 5 to highlight k=5)
        for i, (x, y) in enumerate(vpos):
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{c5[i % 5]}" stroke="#ffffff" stroke-width="0.5"/>')

        pct = 100.0 * len(short_e) / max(len(edges), 1)
        out.append(f'  <text x="{px+14}" y="{py+312}" class="stat">|E|={len(edges)} · local={len(local_e)} · chords={len(short_e)} ({pct:.0f}%)</text>')

    # Arrows between panels
    for ax in (313, 615):
        out.append(f'  <polygon points="{ax},235 {ax+11},241 {ax},247" fill="#64748b"/>')

    # Footer bar
    out.append('  <rect x="24" y="416" width="892" height="48" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    out.append('  <text x="38" y="436" class="foot"><tspan class="foot-b">Benchmark Origin (Gent, Hoos, Prosser &amp; Walsh):</tspan> 100 vertices (5 colors → 500 vars, 3,100 clauses); rewiring probability interpolates easy lattice → hard small-world.</text>')
    out.append('  <text x="38" y="454" class="foot"><tspan class="foot-b">Visual Key:</tspan> Slate perimeter arcs = local ring-lattice edges (d ≤ 4); colored interior chords = rewired small-world shortcuts (d &gt; 4); all 5 instances SAT.</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
