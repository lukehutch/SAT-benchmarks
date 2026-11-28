#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-a067782-sortnet.

Renders the independently verified 12-input depth-8 sorting network (46 comparators)
decoded directly from `solutions/sortnet_n12_d8.model.xz` and verified bit-parallel
across all 2^12 = 4,096 binary inputs via the 0/1 principle.
"""
from __future__ import annotations

import json
import lzma
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_true_vars(path: Path) -> set[int]:
    opener = lzma.open if path.suffix == ".xz" else open
    true_vars: set[int] = set()
    with opener(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ("c", "s"):
                continue
            toks = s.split()
            if toks[0] == "v":
                toks = toks[1:]
            for tok in toks:
                lit = int(tok)
                if lit > 0:
                    true_vars.add(lit)
    return true_vars


def sorts_01(n: int, layers: list[list[tuple[int, int]]]) -> bool:
    """Bit-parallel 0/1-principle verification across all 2^n binary inputs."""
    N = 1 << n
    full = (1 << N) - 1
    ch = []
    for c in range(n):
        b = n - 1 - c
        block = ((1 << (1 << b)) - 1) << (1 << b)
        period = 1 << (b + 1)
        pat, width = block, period
        while width < N:
            pat |= pat << width
            width *= 2
        ch.append(pat & full)
    for layer in layers:
        for i, j in layer:
            ch[i], ch[j] = ch[i] & ch[j], ch[i] | ch[j]
    for c in range(n - 1):
        if ch[c] & ~ch[c + 1] & full:
            return False
    return True


def assign_lanes(layer: list[tuple[int, int]]) -> tuple[list[int], int]:
    """Greedy interval-coloring so no two overlapping comparators share an x-lane."""
    intervals = sorted(enumerate(layer), key=lambda kv: (kv[1][0], kv[1][1]))
    lane_ends: list[int] = []
    lanes = [0] * len(layer)
    for orig_idx, (a, b) in intervals:
        placed = False
        for li, end_wire in enumerate(lane_ends):
            if a > end_wire:
                lane_ends[li] = b
                lanes[orig_idx] = li
                placed = True
                break
        if not placed:
            lanes[orig_idx] = len(lane_ends)
            lane_ends.append(b)
    return lanes, max(1, len(lane_ends))


def build_svg() -> str:
    meta = json.loads(
        (ROOT / "src/upstream/sequences/A067782/cnf/sortnet_n12_d8.cnf.map.json").read_text(encoding="utf-8")
    )
    true_vars = read_true_vars(ROOT / "solutions/sortnet_n12_d8.model.xz")
    n = meta["n"]
    layers: list[list[tuple[int, int]]] = [[tuple(p) for p in layer] for layer in meta["prefix"]]
    for layer in meta["free_layers"]:
        layers.append([(i, j) for i, j, v in layer if v in true_vars])

    assert n == 12 and len(layers) == 8, f"Unexpected network dimensions: n={n}, d={len(layers)}"
    assert sorts_01(n, layers), "Decoded 12-input network failed 0/1-principle verification!"
    n_comps = sum(len(l) for l in layers)

    W, H = 960, 520
    els: list[str] = []
    add = els.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    add("""  <defs>
    <style>
      .title { font: 700 17.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .subtitle { font: 400 11.8px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .ptitle { font: 700 13px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .psub { font: 400 11px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .mono { font: 600 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #334155; }
      .mono-sm { font: 600 9.2px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #475569; }
      .badge { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .cap { font: 400 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #334155; }
      .cap-b { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
    </style>
  </defs>""")

    # Explicit white card background
    add(f'  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')

    # Header
    add('  <text x="24" y="33" class="title">OEIS A067782 — Optimal-Depth Sorting Networks (n = 11–18)</text>')
    add('  <text x="24" y="52" class="subtitle">Verified Frobenius SAT certificate for sortnet_n12_d8 (n = 12, depth 8, 46 comparators; bit-parallel verified on all 4,096 0/1 inputs)</text>')
    add('  <rect x="786" y="14" width="150" height="24" rx="12" fill="#dc2626"/>')
    add('  <text x="861" y="30" text-anchor="middle" class="badge">OPEN: a(18) in {10, 11}</text>')

    # Main Sorting Network Card
    add('  <rect x="20" y="68" width="920" height="314" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Decoded 12-Input Depth-8 Sorting Network (solutions/sortnet_n12_d8.model.xz)</text>')
    add(f'  <text x="924" y="90" text-anchor="end" class="psub">{n_comps} comparators across 8 parallel layers | 0/1-principle check: PASS</text>')

    wx0, wx1 = 68, 892
    wy0, wdy = 114, 19.5
    for w in range(n):
        cy = wy0 + w * wdy
        add(f'  <line x1="{wx0}" y1="{cy:.1f}" x2="{wx1}" y2="{cy:.1f}" stroke="#cbd5e1" stroke-width="1.5"/>')
        add(f'  <text x="{wx0-10}" y="{cy+3.5:.1f}" text-anchor="end" class="mono">x{w}</text>')
        add(f'  <text x="{wx1+8}" y="{cy+3.5:.1f}" class="mono">y{w}</text>')

    layer_colors = ["#2563eb", "#0d9488", "#7c3aed", "#d97706", "#db2777", "#0284c7", "#4f46e5", "#059669"]
    layer_notes = ["fixed", "free", "free", "free", "free", "free", "free", "adj."]

    band_x0 = 84
    band_w = 90
    band_gap = 12
    for li, layer in enumerate(layers):
        col = layer_colors[li]
        bx = band_x0 + li * (band_w + band_gap)
        add(f'  <rect x="{bx}" y="{wy0-11:.1f}" width="{band_w}" height="{(n-1)*wdy+22:.1f}" rx="6" fill="{col}" fill-opacity="0.065" stroke="{col}" stroke-opacity="0.22" stroke-width="1"/>')

        lanes, n_lanes = assign_lanes(layer)
        inner_pad = 12
        usable = band_w - 2 * inner_pad
        for (a, b), lane in zip(layer, lanes):
            if n_lanes == 1:
                cx = bx + band_w / 2.0
            else:
                cx = bx + inner_pad + lane * (usable / (n_lanes - 1))
            ya = wy0 + a * wdy
            yb = wy0 + b * wdy
            add(f'  <line x1="{cx:.1f}" y1="{ya:.1f}" x2="{cx:.1f}" y2="{yb:.1f}" stroke="{col}" stroke-width="2.1"/>')
            add(f'  <circle cx="{cx:.1f}" cy="{ya:.1f}" r="3.4" fill="{col}"/>')
            add(f'  <circle cx="{cx:.1f}" cy="{yb:.1f}" r="3.4" fill="{col}"/>')

        lx_mid = bx + band_w / 2.0
        ly_lbl = wy0 + (n - 1) * wdy + 26
        add(f'  <text x="{lx_mid:.1f}" y="{ly_lbl:.1f}" text-anchor="middle" class="mono" fill="{col}">L{li+1} ({len(layer)})</text>')
        add(f'  <text x="{lx_mid:.1f}" y="{ly_lbl+13:.1f}" text-anchor="middle" class="mono-sm">{layer_notes[li]}</text>')

    # Bottom-Left Card: Encoding & Comparator Semantics
    add('  <rect x="20" y="394" width="452" height="106" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="415" class="ptitle">Bundala-Zavodny One-Sided 0/1 Encoding</text>')
    # Mini comparator icon
    add('  <line x1="36" y1="438" x2="108" y2="438" stroke="#94a3b8" stroke-width="1.5"/>')
    add('  <line x1="36" y1="464" x2="108" y2="464" stroke="#94a3b8" stroke-width="1.5"/>')
    add('  <line x1="72" y1="438" x2="72" y2="464" stroke="#2563eb" stroke-width="2.2"/>')
    add('  <circle cx="72" cy="438" r="3.6" fill="#2563eb"/>')
    add('  <circle cx="72" cy="464" r="3.6" fill="#2563eb"/>')
    add('  <text x="36" y="432" class="mono-sm">a</text>')
    add('  <text x="36" y="477" class="mono-sm">b</text>')
    add('  <text x="112" y="441" class="mono-sm">min(a,b)</text>')
    add('  <text x="112" y="467" class="mono-sm">max(a,b)</text>')
    add('  <text x="180" y="436" class="cap">- <tspan class="cap-b">L1 fixed</tspan> to (0,1),(2,3),... (Parberry 1991).</text>')
    add('  <text x="180" y="454" class="cap">- <tspan class="cap-b">Last layer adjacent-only</tspan> (i, i+1) (Codish et al. 2015).</text>')
    add('  <text x="180" y="472" class="cap">- Encodes only unsorted L1 0/1 outputs (19,664 at n=18).</text>')
    add('  <text x="180" y="490" class="cap">- No reflection symmetry breaking; SAT model self-checks.</text>')

    # Bottom-Right Card: OEIS A067782 Depth Ladder
    add('  <rect x="488" y="394" width="452" height="106" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="504" y="415" class="ptitle">OEIS A067782 Calibration Ladder &amp; Open Frontier (10 CNFs)</text>')
    ladder = [
        ("n=11", "d=8", "d=7 UNSAT", "#0f766e", "#f0fdfa"),
        ("n=12", "d=8", "d=7/8", "#0f766e", "#f0fdfa"),
        ("n=14", "d=9", "d=8 UNSAT", "#0284c7", "#f0f9ff"),
        ("n=16", "d=9", "d=8/9", "#0284c7", "#f0f9ff"),
        ("n=17", "d=10", "d=9/10", "#4f46e5", "#eef2ff"),
        ("n=18", "10 or 11", "OPEN d=10", "#dc2626", "#fef2f2"),
    ]
    bx0 = 504
    bw = 66
    bg = 5
    for idx, (ntxt, dtxt, subtxt, scol, fcol) in enumerate(ladder):
        x = bx0 + idx * (bw + bg)
        add(f'  <rect x="{x}" y="426" width="{bw}" height="52" rx="6" fill="{fcol}" stroke="{scol}" stroke-width="1.2"/>')
        add(f'  <text x="{x+bw/2:.1f}" y="441" text-anchor="middle" class="mono" fill="{scol}">{ntxt}</text>')
        add(f'  <text x="{x+bw/2:.1f}" y="456" text-anchor="middle" class="cap-b" fill="{scol}">{dtxt}</text>')
        add(f'  <text x="{x+bw/2:.1f}" y="471" text-anchor="middle" font-family="ui-monospace,monospace" font-size="8.2" fill="#475569">{subtxt}</text>')
    add('  <text x="504" y="492" class="cap">Open sortnet_n18_d10.cnf: 2,598,203 vars, 63,274,184 clauses (75.8 MB .xz).</text>')

    add("</svg>")
    return "\n".join(els) + "\n"


def main() -> None:
    svg = build_svg()
    out = ROOT / "diagram.svg"
    out.write_text(svg, encoding="utf-8")
    ET.parse(out)
    print(f"Wrote and XML-validated {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
