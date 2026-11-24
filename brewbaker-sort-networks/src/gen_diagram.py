#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-sort-networks.

Visualizes independently verified size-optimal sorting networks for N=4 (5 comparators)
and N=5 (9 comparators), verified across all 2^N binary inputs via the 0/1 principle,
alongside the sequential-slot encoding and OEIS A003075 size-optimality ladder (N=4..7).
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Classic size-optimal networks: S(4) = 5, S(5) = 9 (Floyd-Knuth / OEIS A003075)
NET_4 = [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2)]
NET_5 = [(0, 1), (3, 4), (2, 4), (2, 3), (0, 3), (0, 2), (1, 4), (1, 3), (1, 2)]


def verify_sort_01(n: int, net: list[tuple[int, int]]) -> None:
    for mask in range(1 << n):
        a = [(mask >> i) & 1 for i in range(n)]
        for i, j in net:
            if a[i] > a[j]:
                a[i], a[j] = a[j], a[i]
        assert a == sorted(a), f"Network failed on {mask:0{n}b}: got {a}"


def draw_net(
    p: list[str],
    x0: float,
    y0: float,
    w: float,
    h: float,
    n: int,
    net: list[tuple[int, int]],
    title: str,
    subtitle: str,
    accent: str,
) -> None:
    p.append(f'  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="{x0}" y="{y0}" width="{w}" height="28" rx="10" fill="{accent}"/>')
    p.append(f'  <rect x="{x0}" y="{y0+16}" width="{w}" height="12" fill="{accent}"/>')
    p.append(f'  <text x="{x0+14}" y="{y0+19}" font-size="11.5" font-weight="700" fill="#ffffff">{title}</text>')
    p.append(f'  <text x="{x0+14}" y="{y0+46}" font-size="9.6" fill="#475569">{subtitle}</text>')

    wx0, wx1 = x0 + 42, x0 + w - 42
    wy0 = y0 + 68
    dy = (h - 102) / max(1, n - 1)
    for i in range(n):
        cy = wy0 + i * dy
        p.append(f'  <line x1="{wx0:.1f}" y1="{cy:.1f}" x2="{wx1:.1f}" y2="{cy:.1f}" stroke="#cbd5e1" stroke-width="1.8"/>')
        p.append(f'  <text x="{wx0-8:.1f}" y="{cy+3.5:.1f}" text-anchor="end" font-family="{MONO}" font-size="10" font-weight="700" fill="#334155">x{i}</text>')
        p.append(f'  <text x="{wx1+8:.1f}" y="{cy+3.5:.1f}" font-family="{MONO}" font-size="10" font-weight="700" fill="#0f766e">y{i}</text>')

    step = (wx1 - wx0 - 36) / max(1, len(net) - 1) if len(net) > 1 else 0
    palette = ["#2563eb", "#0d9488", "#7c3aed", "#d97706", "#db2777", "#0284c7", "#4f46e5", "#059669", "#dc2626"]
    for idx, (a, b) in enumerate(net):
        cx = wx0 + 18 + idx * step
        ya = wy0 + a * dy
        yb = wy0 + b * dy
        col = palette[idx % len(palette)]
        p.append(f'  <line x1="{cx:.1f}" y1="{ya:.1f}" x2="{cx:.1f}" y2="{yb:.1f}" stroke="{col}" stroke-width="2.4"/>')
        p.append(f'  <circle cx="{cx:.1f}" cy="{ya:.1f}" r="4.0" fill="{col}"/>')
        p.append(f'  <circle cx="{cx:.1f}" cy="{yb:.1f}" r="4.0" fill="{col}"/>')
        p.append(f'  <text x="{cx:.1f}" y="{y0+h-10:.1f}" text-anchor="middle" font-family="{MONO}" font-size="8.6" font-weight="600" fill="{col}">c{idx}</text>')


def build_svg() -> str:
    verify_sort_01(4, NET_4)
    verify_sort_01(5, NET_5)

    W, H = 960, 496
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Minimum-Comparator Sorting Network Synthesis (brewbaker-sort-networks)">',
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Minimum-Comparator Sorting Network Synthesis (brewbaker-sort-networks)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Size-optimal sequential compare-exchange networks S(N) (OEIS A003075) via the 0/1 principle '
        '(Chad Brewbaker, sat_challenges.py sort)</text>',
        '  <rect x="752" y="16" width="182" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '  <text x="843" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#1d4ed8">'
        '8 Instances &#x00B7; 4 SAT / 4 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Top row: N=4 (5 comparators) and N=5 (9 comparators) verified networks
    draw_net(p, 24, 78, 376, 224, 4, NET_4,
             "1A. Optimal 4-Wire Network: S(4) = 5 (Chad's Pair)",
             "K=4 UNSAT / K=5 SAT | 0/1-principle verified on all 2^4 = 16 inputs", "#1d4ed8")
    draw_net(p, 414, 78, 522, 224, 5, NET_5,
             "1B. Optimal 5-Wire Network: S(5) = 9 Comparators",
             "K=8 UNSAT / K=9 SAT | 0/1-principle verified on all 2^5 = 32 inputs", "#0f766e")

    # Bottom-left: Sequential slot SAT encoding
    y2 = 316
    p.append(f'  <rect x="24" y="{y2}" width="440" height="164" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+22}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '2. Sequential Comparator-Slot Encoding (sat_challenges.py)</text>')
    # Mini comparator schematic
    p.append(f'  <line x1="42" y1="{y2+50}" x2="124" y2="{y2+50}" stroke="#94a3b8" stroke-width="1.8"/>')
    p.append(f'  <line x1="42" y1="{y2+82}" x2="124" y2="{y2+82}" stroke="#94a3b8" stroke-width="1.8"/>')
    p.append(f'  <line x1="83" y1="{y2+50}" x2="83" y2="{y2+82}" stroke="#2563eb" stroke-width="2.4"/>')
    p.append(f'  <circle cx="83" cy="{y2+50}" r="4" fill="#2563eb"/>')
    p.append(f'  <circle cx="83" cy="{y2+82}" r="4" fill="#2563eb"/>')
    p.append(f'  <text x="42" y="{y2+44}" font-family="{MONO}" font-size="9.5" fill="#334155">a</text>')
    p.append(f'  <text x="42" y="{y2+95}" font-family="{MONO}" font-size="9.5" fill="#334155">b</text>')
    p.append(f'  <text x="128" y="{y2+53}" font-family="{MONO}" font-size="9.2" fill="#1d4ed8">lo = a &amp; b</text>')
    p.append(f'  <text x="128" y="{y2+85}" font-family="{MONO}" font-size="9.2" fill="#1d4ed8">hi = a | b</text>')

    notes = [
        "Each slot t in 0..K-1 selects at most one pair (i,j), i &lt; j.",
        "AMO(C(N,2)) allows idle slots (upper-bound budget K).",
        "Propagates all 2^N - (N+1) unsorted 0/1 input vectors.",
        "Untouched wires preserve state via frame clauses.",
        "Pure size optimization (contrast parallel depth A067782).",
    ]
    for i, ln in enumerate(notes):
        p.append(f'  <text x="202" y="{y2+44+i*22}" font-size="9.4" fill="#334155">&#x2022; {ln}</text>')

    # Bottom-right: OEIS A003075 Ladder
    xr = 478
    p.append(f'  <rect x="{xr}" y="{y2}" width="458" height="164" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="{xr+14}" y="{y2+22}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '3. OEIS A003075 Size-Optimality Ladder (8 Instances)</text>')
    rungs = [
        ("N = 4", "S(4) = 5", "k=4 / k=5", "221-276 vars", "1.8K-2.3K cls", "#0f766e", "#f0fdfa"),
        ("N = 5", "S(5) = 9", "k=8 / k=9", "1.2K-1.3K vars", "13.8K-15.7K cls", "#2563eb", "#eff6ff"),
        ("N = 6", "S(6) = 12", "k=11 / k=12", "4.1K-4.5K vars", "61.4K-67.3K cls", "#7c3aed", "#faf5ff"),
        ("N = 7", "S(7) = 16", "k=15 / k=16", "13.2K-14.1K vars", "244K-261K cls", "#be123c", "#fff1f2"),
    ]
    rw = 104
    rg = 6
    for i, (t1, t2, t3, t4, t5, sc, bg) in enumerate(rungs):
        rx = xr + 12 + i * (rw + rg)
        p.append(f'  <rect x="{rx}" y="{y2+34}" width="{rw}" height="114" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.2"/>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+52}" text-anchor="middle" font-family="{MONO}" font-size="10.2" font-weight="700" fill="{sc}">{t1}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+70}" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">{t2}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+87}" text-anchor="middle" font-family="{MONO}" font-size="8.6" font-weight="600" fill="#334155">{t3} (U/S)</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+106}" text-anchor="middle" font-size="8.2" fill="#475569">{t4}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y2+122}" text-anchor="middle" font-size="8.2" fill="#64748b">{t5}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
