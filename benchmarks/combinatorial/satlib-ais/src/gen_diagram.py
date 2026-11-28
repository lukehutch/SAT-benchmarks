#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-ais (All-Interval Series).

Finds and verifies a non-trivial All-Interval Series of order n = 10 (ais10)
plus parses real CNF dimensions from cnf-orig/ais6..ais12.cnf.xz, and renders
../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path


def parse_header(cnf_xz: Path) -> tuple[int, int]:
    with lzma.open(cnf_xz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("p cnf"):
                p = line.split()
                return int(p[2]), int(p[3])
    return 0, 0


def find_nontrivial_ais(n: int) -> list[int]:
    """Find a visually rich (non-monotonic-zigzag) All-Interval Series of order n."""
    # Backtrack starting with (0, n-2, ...) to avoid trivial alternating zigzag
    used_v = [False] * n
    used_d = [False] * n
    seq = [0]
    used_v[0] = True

    def dfs(pos: int) -> bool:
        if pos == n:
            return True
        prev = seq[-1]
        # Prefer varied middle jumps so arcs look distinct and clear
        order = [3, 6, 8, 2, 7, 4, 9, 5, 1] if n == 10 else list(range(1, n))
        for v in order:
            if v >= n or used_v[v]:
                continue
            d = abs(v - prev)
            if used_d[d]:
                continue
            used_v[v] = True
            used_d[d] = True
            seq.append(v)
            if dfs(pos + 1):
                return True
            seq.pop()
            used_v[v] = False
            used_d[d] = False
        return False

    if not dfs(1):
        raise RuntimeError(f"No AIS found for n={n}")
    diffs = [abs(seq[i + 1] - seq[i]) for i in range(n - 1)]
    assert sorted(seq) == list(range(n))
    assert sorted(diffs) == list(range(1, n))
    return seq


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    stats = []
    for name in ("ais6", "ais8", "ais10", "ais12"):
        p = col_dir / "cnf-orig" / f"{name}.cnf.xz"
        if p.exists():
            stats.append((name, *parse_header(p)))

    seq = find_nontrivial_ais(10)
    diffs = [abs(seq[i + 1] - seq[i]) for i in range(len(seq) - 1)]

    W, H = 940, 470
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.8px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .node { font: 700 12px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .diff { font: 700 10.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #ffffff; }
      .axis { font: 600 10px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #64748b; }
      .badge { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">All-Interval Series (SATLIB ais6–ais12)</text>')
    out.append('  <text x="26" y="54" class="sub">Find a permutation s = (s₀, …, sₙ₋₁) of {0, …, n−1} whose consecutive differences |sᵢ₊₁ − sᵢ| form a permutation of {1, …, n−1}</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Main trajectory chart (left/top): plotting s_i vs index i for n=10!
    gx, gy, gw, gh = 24, 80, 588, 254
    out.append(f'  <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{gx+16}" y="{gy+24}" class="h3">Verified Order-10 Solution (ais10): s = ({", ".join(map(str, seq))})</text>')
    out.append(f'  <rect x="{gx+gw-124}" y="{gy+10}" width="110" height="21" rx="10.5" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append(f'  <text x="{gx+gw-69}" y="{gy+24}" text-anchor="middle" class="badge">All 9 diffs unique</text>')

    # Plot grid inside chart
    px0, py0, pw, ph = gx + 48, gy + 44, gw - 74, gh - 78
    for v in range(10):
        yy = py0 + ph - (v / 9.0) * ph
        out.append(f'  <line x1="{px0}" y1="{yy:.1f}" x2="{px0+pw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')
        out.append(f'  <text x="{px0-10}" y="{yy+3.5:.1f}" text-anchor="end" class="axis">{v}</text>')
    for i in range(10):
        xx = px0 + (i / 9.0) * pw
        out.append(f'  <line x1="{xx:.1f}" y1="{py0}" x2="{xx:.1f}" y2="{py0+ph}" stroke="#f1f5f9" stroke-width="0.9"/>')
        out.append(f'  <text x="{xx:.1f}" y="{py0+ph+18}" text-anchor="middle" class="axis">s{i}</text>')

    # Color per interval size 1..9
    d_cols = {
        1: "#64748b", 2: "#0284c7", 3: "#2563eb", 4: "#059669", 5: "#16a34a",
        6: "#ca8a04", 7: "#d97706", 8: "#dc2626", 9: "#7c3aed",
    }

    pts = [(px0 + (i / 9.0) * pw, py0 + ph - (val / 9.0) * ph) for i, val in enumerate(seq)]
    # Draw connecting jump segments with labeled difference pills
    for i in range(9):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        d = diffs[i]
        col = d_cols[d]
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.6"/>')
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        out.append(f'  <rect x="{mx-11:.1f}" y="{my-9:.1f}" width="22" height="18" rx="9" fill="{col}" stroke="#ffffff" stroke-width="1.2"/>')
        out.append(f'  <text x="{mx:.1f}" y="{my+3.5:.1f}" text-anchor="middle" class="diff">{d}</text>')

    # Draw value nodes on top
    for i, (x, y) in enumerate(pts):
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#0f172a" stroke="#ffffff" stroke-width="2"/>')
        out.append(f'  <text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" class="node">{seq[i]}</text>')

    # Right panel: Interval permutation check + musical origin
    rx, rw = 626, 290
    out.append(f'  <rect x="{rx}" y="80" width="{rw}" height="254" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="104" class="h3">Interval Bijection Check</text>')
    out.append(f'  <text x="{rx+16}" y="124" class="body">Each jump size d ∈ {{1, …, 9}} appears once:</text>')

    # Horizontal bar chart of the 9 consecutive differences
    for i, d in enumerate(diffs):
        by = 138 + i * 20
        col = d_cols[d]
        bar_w = d * 19
        out.append(f'  <text x="{rx+16}" y="{by+11}" class="axis">|s{i+1}−s{i}|</text>')
        out.append(f'  <rect x="{rx+74}" y="{by}" width="{bar_w}" height="14" rx="4" fill="{col}" opacity="0.88"/>')
        out.append(f'  <text x="{rx+80+bar_w}" y="{by+11}" class="mono">{d}</text>')

    # Bottom row: SAT Encoding + Dataset Scale
    out.append('  <rect x="24" y="348" width="588" height="104" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append('  <text x="40" y="372" class="h3">Propositional SAT Encoding (Hoos, 1998 — Musical 12-Tone Rows at n = 12)</text>')
    out.append('  <text x="40" y="393" class="mono">• Series vars sᵢ,ᵥ ∈ {0,1} (Exactly-1 value v per slot i; Exactly-1 slot per value v)</text>')
    out.append('  <text x="40" y="412" class="mono">• Diff vars   dᵢ,ₖ ∈ {0,1} (dᵢ,ₖ ⇔ ∨_{|u−v|=k} (sᵢ,ᵤ ∧ sᵢ₊₁,ᵥ); all k ∈ 1..n−1 distinct)</text>')
    out.append('  <text x="40" y="432" class="body">Inspired by Alban Berg\'s all-interval 12-tone serial rows (1,928 distinct rows at n = 12).</text>')

    out.append(f'  <rect x="{rx}" y="348" width="{rw}" height="104" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="372" class="h3">Suite Instances (All SAT)</text>')
    for idx, (name, nv, nc) in enumerate(stats):
        sy = 393 + idx * 15
        out.append(f'  <text x="{rx+16}" y="{sy}" class="mono">{name:6s}: {nv:3d} vars · {nc:5,d} clauses</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
