#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-select-networks.

Contrasts an independently verified 7-comparator fixed median-of-5 network (`select 5 3 7`)
against an independently verified depth-6 adaptive comparison decision tree (`select 5 3 6 --adaptive`),
illustrating the exact adaptivity gap V_3(5) = 6 < 7 = U_3^(1)(5).
"""
from __future__ import annotations

from itertools import permutations
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Verified 7-comparator fixed median-of-5 network (outputs median on wire 2)
FIXED_MED5 = [(0, 1), (2, 3), (0, 2), (1, 3), (1, 2), (2, 4), (1, 2)]


def verify_both_median5() -> None:
    # 1. Fixed network over all 5! = 120 permutations
    for perm in permutations(range(5)):
        a = list(perm)
        for i, j in FIXED_MED5:
            if a[i] > a[j]:
                a[i], a[j] = a[j], a[i]
        assert a[2] == 2, f"Fixed median-5 failed on {perm}: wire 2 = {a[2]}"

    # 2. Adaptive 6-comparison decision tree over all 5! = 120 permutations
    for perm in permutations(range(5)):
        comps = 0
        def lt(i: int, j: int) -> bool:
            nonlocal comps
            comps += 1
            return perm[i] < perm[j]

        a, b = (0, 1) if lt(0, 1) else (1, 0)
        c, d = (2, 3) if lt(2, 3) else (3, 2)
        if lt(a, c):
            # a eliminated; need 2nd smallest of {b, c, d, 4} with c < d
            u, v = (b, 4) if lt(b, 4) else (4, b)
            ans = (d if lt(d, u) else u) if lt(c, u) else (c if lt(c, v) else v)
        else:
            # c eliminated; need 2nd smallest of {a, b, d, 4} with a < b
            u, v = (d, 4) if lt(d, 4) else (4, d)
            ans = (b if lt(b, u) else u) if lt(a, u) else (a if lt(a, v) else v)
        assert comps == 6 and perm[ans] == 2, f"Adaptive med-5 failed on {perm}: comps={comps} val={perm[ans]}"


def build_svg() -> str:
    verify_both_median5()
    W, H = 960, 520
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Fixed and Adaptive Selection Network Synthesis (brewbaker-select-networks)">',
        "<defs>",
        '  <marker id="arr-t" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#0f766e"/>',
        "  </marker>",
        '  <marker id="arr-f" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#b45309"/>',
        "  </marker>",
        "</defs>",
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Fixed &amp; Adaptive Selection Network Synthesis (brewbaker-select-networks)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Data-oblivious comparator selectors vs. adaptive comparison decision trees — exact adaptivity gap V&#x2083;(5) = 6 &lt; 7 '
        '(Chad Brewbaker, sat_challenges.py select)</text>',
        '  <rect x="748" y="16" width="186" height="24" rx="12" fill="#f0fdfa" stroke="#0f766e" stroke-width="1.2"/>',
        '  <text x="841" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#0f766e">'
        '12 Instances &#x00B7; 6 SAT / 6 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Left Card: Fixed 7-Comparator Median-of-5 Network
    y1 = 78
    h1 = 278
    p.append(f'  <rect x="24" y="{y1}" width="440" height="{h1}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="24" y="{y1}" width="440" height="28" rx="10" fill="#1d4ed8"/>')
    p.append(f'  <rect x="24" y="{y1+16}" width="440" height="12" fill="#1d4ed8"/>')
    p.append(f'  <text x="38" y="{y1+19}" font-size="11.6" font-weight="700" fill="#ffffff">'
             '1A. Fixed Median-of-5 Network: K = 7 SAT (K = 6 UNSAT)</text>')
    p.append(f'  <text x="38" y="{y1+46}" font-size="9.5" fill="#475569">'
             'Oblivious sequence (select 5 3 7); boundary layers: C(5,2)+C(5,3) = 20 vectors</text>')

    wx0, wx1 = 68, 412
    wy0, dy = y1 + 74, 34
    for w in range(5):
        cy = wy0 + w * dy
        is_med = (w == 2)
        stroke = "#16a34a" if is_med else "#cbd5e1"
        sw = "2.6" if is_med else "1.7"
        p.append(f'  <line x1="{wx0}" y1="{cy}" x2="{wx1}" y2="{cy}" stroke="{stroke}" stroke-width="{sw}"/>')
        p.append(f'  <text x="{wx0-8}" y="{cy+3.5}" text-anchor="end" font-family="{MONO}" font-size="10" font-weight="700" fill="#334155">x{w}</text>')
        lbl = "med" if is_med else f"w{w}"
        lcol = "#15803d" if is_med else "#94a3b8"
        p.append(f'  <text x="{wx1+8}" y="{cy+3.5}" font-family="{MONO}" font-size="10" font-weight="700" fill="{lcol}">{lbl}</text>')

    cols = ["#2563eb", "#2563eb", "#7c3aed", "#7c3aed", "#0d9488", "#d97706", "#16a34a"]
    for idx, (a, b) in enumerate(FIXED_MED5):
        cx = wx0 + 26 + idx * 48
        ya, yb = wy0 + a * dy, wy0 + b * dy
        col = cols[idx]
        p.append(f'  <line x1="{cx}" y1="{ya}" x2="{cx}" y2="{yb}" stroke="{col}" stroke-width="2.4"/>')
        p.append(f'  <circle cx="{cx}" cy="{ya}" r="4.2" fill="{col}"/>')
        p.append(f'  <circle cx="{cx}" cy="{yb}" r="4.2" fill="{col}"/>')
        p.append(f'  <text x="{cx}" y="{wy0+4*dy+22}" text-anchor="middle" font-family="{MONO}" font-size="8.6" font-weight="700" fill="{col}">c{idx}</text>')

    p.append(f'  <rect x="38" y="{y1+240}" width="412" height="27" rx="5" fill="#eff6ff" stroke="#bfdbfe" stroke-width="0.9"/>')
    p.append(f'  <text x="244" y="{y1+257}" text-anchor="middle" font-size="9.2" fill="#1e40af">'
             'c0..c3 eliminate min(x0..x3) &amp; max(x0..x3); c4..c6 take median(w1, w2, x4) &#x2192; wire 2.</text>')

    # Right Card: Adaptive Depth-6 Decision Tree (Median-of-5)
    xr = 478
    wr = 458
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="{h1}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="{xr}" y="{y1}" width="{wr}" height="28" rx="10" fill="#0f766e"/>')
    p.append(f'  <rect x="{xr}" y="{y1+16}" width="{wr}" height="12" fill="#0f766e"/>')
    p.append(f'  <text x="{xr+14}" y="{y1+19}" font-size="11.6" font-weight="700" fill="#ffffff">'
             '1B. Adaptive Median-of-5 Decision Tree: K = 6 SAT (K = 5 UNSAT)</text>')
    p.append(f'  <text x="{xr+14}" y="{y1+46}" font-size="9.5" fill="#475569">'
             'Branching binary tree (select 5 3 6 --adaptive): 5! = 120 perms routed across 2^6 = 64 leaves</text>')

    # Clean schematic of the 6-level adaptive decision tree (showing the canonical branch in detail)
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def dnode(cx: float, cy: float, w: float, h: float, txt: str, sub: str, bg: str, bd: str, fg: str) -> None:
        p.append(f'  <rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1.1"/>')
        if sub:
            p.append(f'  <text x="{cx:.1f}" y="{cy-2:.1f}" text-anchor="middle" font-family="{MONO}" font-size="9.2" font-weight="700" fill="{fg}">{esc(txt)}</text>')
            p.append(f'  <text x="{cx:.1f}" y="{cy+10:.1f}" text-anchor="middle" font-size="7.8" fill="#475569">{esc(sub)}</text>')
        else:
            p.append(f'  <text x="{cx:.1f}" y="{cy+3.5:.1f}" text-anchor="middle" font-family="{MONO}" font-size="9.2" font-weight="700" fill="{fg}">{esc(txt)}</text>')

    # Step 1 & 2 (unconditional), Step 3 (eliminates loser), Step 4 (adaptive!), Step 5, Step 6 -> leaves
    dnode(xr + 128, y1 + 76, 126, 28, "1. cmp(x0, x1)", "a < b", "#f0fdfa", "#0f766e", "#0f766e")
    dnode(xr + 320, y1 + 76, 126, 28, "2. cmp(x2, x3)", "c < d", "#f0fdfa", "#0f766e", "#0f766e")
    p.append(f'  <line x1="{xr+191}" y1="{y1+76}" x2="{xr+252}" y2="{y1+76}" stroke="#0f766e" stroke-width="1.3" marker-end="url(#arr-t)"/>')

    dnode(xr + 228, y1 + 122, 166, 28, "3. cmp(a, c)  [root split]", "drops smaller (cannot be med)", "#eef2ff", "#4f46e5", "#3730a3")
    p.append(f'  <line x1="{xr+320}" y1="{y1+90}" x2="{xr+265}" y2="{y1+105}" stroke="#0f766e" stroke-width="1.3" marker-end="url(#arr-t)"/>')

    # Branch left (a < c) vs symmetric right (c < a)
    dnode(xr + 132, y1 + 168, 152, 28, "4. cmp(b, x4) -> u < v", "a < c: adapts to winner!", "#fffbeb", "#d97706", "#b45309")
    dnode(xr + 344, y1 + 168, 148, 28, "4'. cmp(d, x4) -> u' < v'", "c < a: symmetric branch", "#f1f5f9", "#94a3b8", "#475569")
    p.append(f'  <line x1="{xr+186}" y1="{y1+136}" x2="{xr+148}" y2="{y1+151}" stroke="#0f766e" stroke-width="1.3" marker-end="url(#arr-t)"/>')
    p.append(f'  <line x1="{xr+270}" y1="{y1+136}" x2="{xr+324}" y2="{y1+151}" stroke="#b45309" stroke-width="1.3" marker-end="url(#arr-f)"/>')
    p.append(f'  <text x="{xr+140}" y="{y1+144}" font-size="8.2" font-weight="700" fill="#0f766e">a&lt;c</text>')
    p.append(f'  <text x="{xr+316}" y="{y1+144}" font-size="8.2" font-weight="700" fill="#b45309">c&lt;a</text>')

    # Step 5 & 6
    dnode(xr + 132, y1 + 212, 134, 24, "5. cmp(c, u)", "", "#faf5ff", "#7c3aed", "#6d28d9")
    p.append(f'  <line x1="{xr+132}" y1="{y1+182}" x2="{xr+132}" y2="{y1+197}" stroke="#0f766e" stroke-width="1.3" marker-end="url(#arr-t)"/>')

    dnode(xr + 82, y1 + 252, 108, 24, "6. min(d, u)", "", "#dcfce7", "#16a34a", "#166534")
    dnode(xr + 212, y1 + 252, 108, 24, "6. min(c, v)", "", "#dcfce7", "#16a34a", "#166534")
    p.append(f'  <line x1="{xr+108}" y1="{y1+224}" x2="{xr+88}" y2="{y1+237}" stroke="#0f766e" stroke-width="1.3" marker-end="url(#arr-t)"/>')
    p.append(f'  <line x1="{xr+156}" y1="{y1+224}" x2="{xr+196}" y2="{y1+237}" stroke="#b45309" stroke-width="1.3" marker-end="url(#arr-f)"/>')
    p.append(f'  <text x="{xr+70}" y="{y1+233}" font-size="8" font-weight="700" fill="#0f766e">c&lt;u</text>')
    p.append(f'  <text x="{xr+192}" y="{y1+231}" font-size="8" font-weight="700" fill="#b45309">u&lt;c</text>')

    p.append(f'  <rect x="{xr+284}" y="{y1+200}" width="160" height="66" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'  <text x="{xr+364}" y="{y1+217}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#0f766e">Adaptivity Advantage</text>')
    p.append(f'  <text x="{xr+364}" y="{y1+232}" text-anchor="middle" font-size="8.6" fill="#334155">N=4, R=2: 4 vs 5 fixed (-1)</text>')
    p.append(f'  <text x="{xr+364}" y="{y1+246}" text-anchor="middle" font-size="8.6" fill="#334155">N=5, R=3: 6 vs 7 fixed (-1)</text>')
    p.append(f'  <text x="{xr+364}" y="{y1+260}" text-anchor="middle" font-size="8.6" fill="#334155">N=6, R=3: 8 vs 10 fixed (-2)</text>')

    # Bottom Card: 12-Instance Suite Ladder
    y2 = 370
    p.append(f'  <rect x="24" y="{y2}" width="912" height="132" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+21}" font-size="11.8" font-weight="700" fill="#0f172a">'
             '2. Twelve-Instance Fixed &amp; Adaptive Selection Benchmark Ladder (6 SAT / 6 UNSAT)</text>')

    blocks = [
        ("Fixed (4, 2)", "k=4 UNSAT / k=5 SAT", "173-216 vars | 1.3K-1.6K cls", "U2(4) = 5", "#2563eb", "#eff6ff"),
        ("Fixed (5, 3)", "k=6 UNSAT / k=7 SAT", "655-764 vars | 7.0K-8.3K cls", "Chad's fixed median-5", "#1d4ed8", "#eef2ff"),
        ("Fixed (6, 3) & (7, 4)", "k=8 UNSAT; k=10,13 SAT", "1.8K-6.7K vars | 25K-119K cls", "3rd-of-6 & median-7", "#6d28d9", "#faf5ff"),
        ("Adaptive (4, 2)", "k=3 UNSAT / k=4 SAT", "446-950 vars | 4!=24 perms", "V2(4) = 4 (< 5 fixed)", "#0f766e", "#f0fdfa"),
        ("Adaptive (5, 3)", "k=5 UNSAT / k=6 SAT", "8.3K-16.9K vars | 5!=120", "Chad's adaptive med-5", "#047857", "#ecfdf5"),
        ("Adaptive (6, 3)", "k=7 UNSAT frontier", "188K vars | 282K cls | 6!=720", "V3(6) = 8 lower bound", "#be123c", "#fff1f2"),
    ]
    bw = 140
    bgap = 8.8
    for i, (t1, t2, t3, t4, sc, bg) in enumerate(blocks):
        bx = 38 + i * (bw + bgap)
        p.append(f'  <rect x="{bx:.1f}" y="{y2+34}" width="{bw}" height="82" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.1"/>')
        p.append(f'  <text x="{bx+bw/2:.1f}" y="{y2+51}" text-anchor="middle" font-family="{MONO}" font-size="9.2" font-weight="700" fill="{sc}">{esc(t1)}</text>')
        p.append(f'  <text x="{bx+bw/2:.1f}" y="{y2+67}" text-anchor="middle" font-size="8.7" font-weight="700" fill="#0f172a">{esc(t2)}</text>')
        p.append(f'  <text x="{bx+bw/2:.1f}" y="{y2+84}" text-anchor="middle" font-size="7.9" fill="#334155">{esc(t3)}</text>')
        p.append(f'  <text x="{bx+bw/2:.1f}" y="{y2+102}" text-anchor="middle" font-size="8.0" fill="#475569">{esc(t4)}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
