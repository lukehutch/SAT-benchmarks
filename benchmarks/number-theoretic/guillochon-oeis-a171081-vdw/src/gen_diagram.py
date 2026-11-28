#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-a171081-vdw.

Renders two independently verified Frobenius 2-colorings directly from `solutions/`:
  1. `vdw_3_10_N96.model.xz` (w(2;3,10) > 96): no red 3-AP, no blue 10-AP
  2. `vdw_3_14_N185.model.xz` (w(2;3,14) > 185): no red 3-AP, no blue 14-AP
"""
from __future__ import annotations

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


def longest_mono_ap(is_red: list[bool], target: bool) -> int:
    n = len(is_red) - 1
    best = 0
    for d in range(1, n):
        for start in range(1, d + 1):
            run = 0
            for i in range(start, n + 1, d):
                run = run + 1 if is_red[i] == target else 0
                if run > best:
                    best = run
    return best


def build_svg() -> str:
    v96 = read_true_vars(ROOT / "solutions/vdw_3_10_N96.model.xz")
    c96 = [False] + [i in v96 for i in range(1, 97)]
    r96, b96 = longest_mono_ap(c96, True), longest_mono_ap(c96, False)
    assert r96 < 3 and b96 < 10, f"Invalid N=96 coloring: red={r96}, blue={b96}"
    n_red96 = sum(c96[1:])

    v185 = read_true_vars(ROOT / "solutions/vdw_3_14_N185.model.xz")
    c185 = [False] + [i in v185 for i in range(1, 186)]
    r185, b185 = longest_mono_ap(c185, True), longest_mono_ap(c185, False)
    assert r185 < 3 and b185 < 14, f"Invalid N=185 coloring: red={r185}, blue={b185}"
    n_red185 = sum(c185[1:])

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
      .mono { font: 700 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #334155; }
      .mono-sm { font: 600 9.2px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #475569; }
      .badge { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .cap { font: 400 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #334155; }
      .cap-b { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
    </style>
  </defs>""")

    add(f'  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    add('  <text x="24" y="33" class="title">OEIS A171081 (= A007783) — Van der Waerden Numbers w(2; 3, t)</text>')
    add('  <text x="24" y="52" class="subtitle">2-colorings of {1,...,N} avoiding every red 3-term arithmetic progression and every blue t-term arithmetic progression</text>')
    add('  <rect x="780" y="14" width="156" height="24" rx="12" fill="#2563eb"/>')
    add('  <text x="858" y="30" text-anchor="middle" class="badge">OPEN: w(2;3,20) = 389?</text>')

    # Panel 1: Verified N=96 Grid (4 rows x 24 cols)
    add('  <rect x="20" y="68" width="920" height="218" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius Certificate: w(2; 3, 10) &gt; 96 (solutions/vdw_3_10_N96.model.xz, 0.32 s)</text>')
    add(f'  <text x="924" y="90" text-anchor="end" class="psub">Red: {n_red96} ints (max AP = {r96} &lt; 3) | Blue: {96-n_red96} ints (max AP = {b96} &lt; 10)</text>')

    gx0, gy0 = 38, 106
    cw, ch, gx, gy = 33.8, 30, 3.2, 6.5
    for idx in range(1, 97):
        r = (idx - 1) // 24
        c = (idx - 1) % 24
        x = gx0 + c * (cw + gx)
        y = gy0 + r * (ch + gy)
        fill = "#ef4444" if c96[idx] else "#2563eb"
        add(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="4.5" fill="{fill}" fill-opacity="0.92"/>')
        add(f'  <text x="{x+cw/2:.1f}" y="{y+19:.1f}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10.2" font-weight="700" fill="#ffffff">{idx}</text>')

    # Legend inside panel 1
    add('  <rect x="38" y="261" width="13" height="13" rx="3" fill="#ef4444"/>')
    add(f'  <text x="56" y="272" class="cap"><tspan class="cap-b">Red ({n_red96} / 96 = {100*n_red96/96:.1f}%)</tspan> — sparse 3-AP-free barrier (max run {r96})</text>')
    add('  <rect x="370" y="261" width="13" height="13" rx="3" fill="#2563eb"/>')
    add(f'  <text x="388" y="272" class="cap"><tspan class="cap-b">Blue ({96-n_red96} / 96 = {100*(96-n_red96)/96:.1f}%)</tspan> — dense background (max AP {b96} &lt; 10)</text>')
    add('  <text x="924" y="272" text-anchor="end" class="cap">At N = 97: UNSAT certified via cake_lpr (0.73 s)</text>')

    # Panel 2: Verified N=185 High-Resolution Barcode Strip
    add('  <rect x="20" y="298" width="920" height="82" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="319" class="ptitle">Higher-Rung Certificate: w(2; 3, 14) &gt; 185 (vdw_3_14_N185.model.xz, 78.14 s)</text>')
    add(f'  <text x="924" y="319" text-anchor="end" class="psub">Red: {n_red185}/185 (max AP = {r185} &lt; 3) | Blue: {185-n_red185}/185 (max AP = {b185} &lt; 14)</text>')

    bx0 = 38.0
    bw_tot = 884.0
    bar_w = bw_tot / 185.0
    for idx in range(1, 186):
        x = bx0 + (idx - 1) * bar_w
        fill = "#ef4444" if c185[idx] else "#2563eb"
        add(f'  <rect x="{x:.2f}" y="330" width="{bar_w - 0.55:.2f}" height="28" fill="{fill}"/>')
    for tick in (1, 25, 50, 75, 100, 125, 150, 175, 185):
        tx = bx0 + (tick - 0.5) * bar_w
        add(f'  <text x="{tx:.1f}" y="371" text-anchor="middle" class="mono-sm">{tick}</text>')

    # Panel 3 (Bottom Left): Direct Clause Architecture
    add('  <rect x="20" y="392" width="452" height="108" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="413" class="ptitle">Direct CNF Encoding (Zero Auxiliary Variables)</text>')
    # Forbidden red 3-AP diagram
    add('  <text x="36" y="434" class="cap-b" fill="#dc2626">Red 3-AP:</text>')
    for k, lbl in enumerate(["a", "a+d", "a+2d"]):
        cx = 128 + k * 48
        if k > 0:
            add(f'  <line x1="{cx-31}" y1="430" x2="{cx-17}" y2="430" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3,2"/>')
        add(f'  <rect x="{cx-17}" y="420" width="34" height="20" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2"/>')
        add(f'  <text x="{cx}" y="433.5" text-anchor="middle" class="mono-sm" fill="#b91c1c">{lbl}</text>')
    add('  <text x="252" y="434" font-family="ui-monospace,monospace" font-size="9" font-weight="600" fill="#475569">(-x_a v -x_{a+d} v -x_{a+2d})</text>')

    # Forbidden blue t-AP diagram
    add('  <text x="36" y="463" class="cap-b" fill="#1d4ed8">Blue t-AP:</text>')
    for k, lbl in enumerate(["a", "a+d", "...", "a+(t-1)d"]):
        cx = 128 + k * 50 + (8 if k == 3 else 0)
        w_box = 48 if k == 3 else 32
        add(f'  <rect x="{cx-w_box/2:.1f}" y="449" width="{w_box}" height="20" rx="4" fill="#dbeafe" stroke="#2563eb" stroke-width="1.2"/>')
        add(f'  <text x="{cx:.1f}" y="462.5" text-anchor="middle" class="mono-sm" fill="#1e40af">{lbl}</text>')
    add('  <text x="318" y="463" font-family="ui-monospace,monospace" font-size="9" font-weight="600" fill="#475569">(+x_a v ... v +x_{a+(t-1)d})</text>')
    add('  <text x="36" y="489" class="cap">Reflection symmetry i -&gt; N+1-i left intact; pure 3-clauses + t-clauses.</text>')

    # Panel 4 (Bottom Right): OEIS A171081 Ladder & Open Frontier
    add('  <rect x="488" y="392" width="452" height="108" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="504" y="413" class="ptitle">OEIS A171081 Ladder (t = 10..20, 22 Instances)</text>')
    rungs = [
        ("t=10", "97"), ("t=11", "114"), ("t=12", "135"), ("t=13", "160"),
        ("t=14", "186"), ("t=15", "218"), ("t=16", "238"), ("t=17", "279"),
        ("t=18", "312"), ("t=19", "349"), ("t=20", "389?"),
    ]
    rx0, rw, rg = 502, 36.5, 2.5
    for i, (tl, wl) in enumerate(rungs):
        x = rx0 + i * (rw + rg)
        is_open = (i == len(rungs) - 1)
        is_cert = (i <= 2)
        bg = "#fef2f2" if is_open else ("#ecfdf5" if is_cert else "#f1f5f9")
        st = "#dc2626" if is_open else ("#059669" if is_cert else "#94a3b8")
        tc = "#b91c1c" if is_open else ("#065f46" if is_cert else "#334155")
        add(f'  <rect x="{x:.1f}" y="425" width="{rw:.1f}" height="42" rx="5" fill="{bg}" stroke="{st}" stroke-width="1.1"/>')
        add(f'  <text x="{x+rw/2:.1f}" y="440" text-anchor="middle" font-family="ui-monospace,monospace" font-size="8.5" font-weight="700" fill="{tc}">{tl}</text>')
        add(f'  <text x="{x+rw/2:.1f}" y="457" text-anchor="middle" font-family="ui-monospace,monospace" font-size="9.2" font-weight="700" fill="{tc}">{wl}</text>')
    add('  <text x="504" y="482" class="cap"><tspan fill="#059669" font-weight="700">Green:</tspan> cake_lpr UNSAT proofs in solutions/ | <tspan fill="#dc2626" font-weight="700">Red:</tspan> open vdw_3_20_N389</text>')
    add('  <text x="504" y="495" class="cap">vdw_3_20_N389.cnf: 389 vars, 41,426 clauses (UNSAT proves w(2;3,20) = 389).</text>')

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
