#!/usr/bin/env python3
"""Generate illustrative SVG diagram for hamd-hamiltonian-cycle.

Showcases three real graph families from the suite:
  1. Generalized Petersen GP(15, 2) (SAT, 30 vertices, with verified Hamiltonian cycle)
  2. Generalized Petersen GP(11, 2) (UNSAT, 22 vertices, hypohamiltonian)
  3. Isaacs Flower Snark J_5 (UNSAT, 20 vertices, cyclically 6-edge-connected)

Writes ../diagram.svg deterministically using stdlib only.
"""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape


def gp_graph(n: int, k: int = 2) -> tuple[list[tuple[int, int]], dict[int, list[int]]]:
    edges = []
    adj: dict[int, list[int]] = {i: [] for i in range(2 * n)}
    def add(u: int, v: int) -> None:
        edges.append((u, v))
        adj[u].append(v)
        adj[v].append(u)
    for i in range(n):
        add(i, (i + 1) % n)              # outer ring 0..n-1
        add(n + i, n + (i + k) % n)      # inner star n..2n-1
        add(i, n + i)                    # spoke
    return edges, adj


def find_hamiltonian_cycle(n_verts: int, adj: dict[int, list[int]]) -> list[int]:
    """Deterministic Warnsdorff-guided backtracking for small 3-regular graphs."""
    path = [0]
    used = [False] * n_verts
    used[0] = True
    start_neighbors = set(adj[0])

    def dfs(u: int, depth: int) -> bool:
        if depth == n_verts:
            return u in start_neighbors
        cands = [v for v in adj[u] if not used[v]]
        # Prefer vertices with fewer remaining exits (tight constraints first)
        cands.sort(key=lambda v: (sum(1 for w in adj[v] if not used[w]), v))
        for v in cands:
            used[v] = True
            path.append(v)
            if dfs(v, depth + 1):
                return True
            path.pop()
            used[v] = False
        return False

    if not dfs(0, 1):
        raise RuntimeError("No Hamiltonian cycle found")
    # Verify cycle
    assert len(path) == n_verts and len(set(path)) == n_verts
    for i in range(n_verts):
        assert path[(i + 1) % n_verts] in adj[path[i]]
    return path


def flower_snark_j5() -> tuple[list[tuple[float, float]], list[tuple[int, int]], list[tuple[int, int]]]:
    """Return coordinates (unit circle normalized), regular edges, and twist edges for J_5."""
    k = 5
    # Vertices per petal i in 0..4:
    # a_i = 4*i (outer), b_i = 4*i+1 (center of claw), c_i = 4*i+2 (mid-left), d_i = 4*i+3 (mid-right)
    # Edges: claw (b_i, a_i), (b_i, c_i), (b_i, d_i);
    # cycle a_i - a_{i+1};
    # c_i - c_{i+1} and d_i - d_{i+1} for i=0..k-2, and twisted c_{k-1} - d_0, d_{k-1} - c_0!
    pos: list[tuple[float, float]] = [(0.0, 0.0)] * (4 * k)
    for i in range(k):
        ang = -math.pi / 2 + 2 * math.pi * i / k
        ang_l = ang - 0.24
        ang_r = ang + 0.24
        pos[4 * i] = (0.98 * math.cos(ang), 0.98 * math.sin(ang))       # a_i (outermost)
        pos[4 * i + 1] = (0.64 * math.cos(ang), 0.64 * math.sin(ang))   # b_i (claw hub)
        pos[4 * i + 2] = (0.37 * math.cos(ang_l), 0.37 * math.sin(ang_l))  # c_i
        pos[4 * i + 3] = (0.37 * math.cos(ang_r), 0.37 * math.sin(ang_r))  # d_i
    reg_edges = []
    twist_edges = []
    for i in range(k):
        a, b, c, d = 4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3
        an = 4 * ((i + 1) % k)
        cn = 4 * ((i + 1) % k) + 2
        dn = 4 * ((i + 1) % k) + 3
        reg_edges.extend([(b, a), (b, c), (b, d), (a, an)])
        if i < k - 1:
            reg_edges.extend([(c, cn), (d, dn)])
        else:
            twist_edges.extend([(c, dn), (d, cn)])
    return pos, reg_edges, twist_edges


def build_svg() -> str:
    W, H = 940, 485
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .panel-title { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .panel-sub { font: 400 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .badge-sat { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
      .badge-unsat { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #b91c1c; }
      .foot { font: 400 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .foot-b { font: 700 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .mini { font: 600 10px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #64748b; }
    </style>
  </defs>""")

    # Card background (safe in GitHub Light & Dark mode)
    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')

    # Header
    out.append('  <text x="26" y="34" class="title">Provably SAT / UNSAT Hamiltonian Cycle Graphs (HAMD / HCP)</text>')
    out.append('  <text x="26" y="54" class="sub">Locally indistinguishable 3-regular, 3-connected graph instances encoded via O(|E| log N) binary-order MTZ CNF</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Three panels
    panels = [
        (24, 78, 288, 326, "GP(15, 2) — Generalized Petersen", "N = 30, |E| = 45 · n ≡ 3 (mod 6)", "SAT · 3 cycles", True),
        (326, 78, 288, 326, "GP(11, 2) — Generalized Petersen", "N = 22, |E| = 33 · n ≡ 5 (mod 6)", "UNSAT · 0 cycles", False),
        (628, 78, 288, 326, "Isaacs Flower Snark J₅", "N = 20, |E| = 30 · Möbius parity twist", "UNSAT · 0 cycles", False),
    ]
    for px, py, pw, ph, title, sub, badge, is_sat in panels:
        out.append(f'  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
        out.append(f'  <text x="{px+14}" y="{py+24}" class="panel-title">{escape(title)}</text>')
        out.append(f'  <text x="{px+14}" y="{py+41}" class="panel-sub">{escape(sub)}</text>')
        bfill, bstroke, bcls = ("#ecfdf5", "#6ee7b7", "badge-sat") if is_sat else ("#fef2f2", "#fca5a5", "badge-unsat")
        bw = 110 if is_sat else 118
        out.append(f'  <rect x="{px+pw-bw-12}" y="{py+ph-30}" width="{bw}" height="21" rx="10.5" fill="{bfill}" stroke="{bstroke}" stroke-width="1"/>')
        out.append(f'  <text x="{px+pw-bw/2-12:.1f}" y="{py+ph-16}" text-anchor="middle" class="{bcls}">{escape(badge)}</text>')

    # Panel 1: GP(15, 2) + verified Hamiltonian cycle
    cx1, cy1, r_out1, r_in1 = 168.0, 240.0, 106.0, 58.0
    n1 = 15
    edges1, adj1 = gp_graph(n1, 2)
    cyc1 = find_hamiltonian_cycle(2 * n1, adj1)
    cyc_edges1 = {tuple(sorted((cyc1[i], cyc1[(i + 1) % len(cyc1)]))) for i in range(len(cyc1))}

    pos1 = {}
    for i in range(n1):
        a = -math.pi / 2 + 2 * math.pi * i / n1
        pos1[i] = (cx1 + r_out1 * math.cos(a), cy1 + r_out1 * math.sin(a))
        pos1[n1 + i] = (cx1 + r_in1 * math.cos(a), cy1 + r_in1 * math.sin(a))

    # Non-cycle edges first (muted), then Hamiltonian cycle edges (emerald/blue bold)
    for u, v in edges1:
        if tuple(sorted((u, v))) not in cyc_edges1:
            x1, y1 = pos1[u]
            x2, y2 = pos1[v]
            out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#cbd5e1" stroke-width="1.4" stroke-dasharray="3,2"/>')
    for i in range(len(cyc1)):
        u, v = cyc1[i], cyc1[(i + 1) % len(cyc1)]
        x1, y1 = pos1[u]
        x2, y2 = pos1[v]
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#059669" stroke-width="2.9" stroke-linecap="round"/>')
    for v in range(2 * n1):
        x, y = pos1[v]
        fill = "#2563eb" if v < n1 else "#059669"
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{fill}" stroke="#ffffff" stroke-width="1.3"/>')
    out.append('  <text x="38" y="388" class="mini">Green = verified 30-vertex cycle</text>')

    # Panel 2: GP(11, 2) UNSAT
    cx2, cy2, r_out2, r_in2 = 470.0, 240.0, 106.0, 58.0
    n2 = 11
    edges2, _ = gp_graph(n2, 2)
    pos2 = {}
    for i in range(n2):
        a = -math.pi / 2 + 2 * math.pi * i / n2
        pos2[i] = (cx2 + r_out2 * math.cos(a), cy2 + r_out2 * math.sin(a))
        pos2[n2 + i] = (cx2 + r_in2 * math.cos(a), cy2 + r_in2 * math.sin(a))
    for u, v in edges2:
        x1, y1 = pos2[u]
        x2, y2 = pos2[v]
        col = "#94a3b8" if (u < n2 and v < n2) else ("#f87171" if (u >= n2 and v >= n2) else "#64748b")
        w = "1.8" if (u >= n2 and v >= n2) else "1.6"
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"/>')
    for v in range(2 * n2):
        x, y = pos2[v]
        fill = "#dc2626" if v >= n2 else "#475569"
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{fill}" stroke="#ffffff" stroke-width="1.3"/>')
    out.append('  <text x="340" y="388" class="mini">Hypohamiltonian: G−v SAT ∀v</text>')

    # Panel 3: Flower Snark J_5 UNSAT
    cx3, cy3, rad3 = 772.0, 242.0, 108.0
    spos, reg_e, twist_e = flower_snark_j5()
    def sc(pt: tuple[float, float]) -> tuple[float, float]:
        return (cx3 + rad3 * pt[0], cy3 + rad3 * pt[1])
    for u, v in reg_e:
        x1, y1 = sc(spos[u])
        x2, y2 = sc(spos[v])
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#64748b" stroke-width="1.65"/>')
    for u, v in twist_e:
        x1, y1 = sc(spos[u])
        x2, y2 = sc(spos[v])
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#dc2626" stroke-width="2.6" stroke-dasharray="5,3"/>')
    for idx, pt in enumerate(spos):
        x, y = sc(pt)
        role = idx % 4
        fill = "#2563eb" if role == 0 else ("#7c3aed" if role == 1 else "#d97706")
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{fill}" stroke="#ffffff" stroke-width="1.3"/>')
    out.append('  <text x="642" y="388" class="mini">Red dashed = Möbius twist</text>')

    # Bottom summary strip
    out.append('  <rect x="24" y="416" width="892" height="52" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    out.append('  <text x="38" y="437" class="foot"><tspan class="foot-b">Suite Coverage (22 instances · 12 SAT / 10 UNSAT):</tspan> Gen. Petersen GP(n,2), Flower Snarks J₅/J₇, Meredith G₃/G₄, Chvátal t&lt;1, Broken Crowns Bₙ,ₖ, Planted Random.</text>')
    out.append('  <text x="38" y="456" class="foot"><tspan class="foot-b">CNF Encoding:</tspan> Directed 1-factor (∑out=1, ∑in=1) + no 2-cycles + binary-order MTZ rank (aᵤ→ᵥ ⇒ rᵤ &lt; rᵥ); vertices randomly permuted to hide structure.</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
