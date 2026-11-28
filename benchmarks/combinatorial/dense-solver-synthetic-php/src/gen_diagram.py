#!/usr/bin/env python3
"""Generate a bespoke illustrative SVG diagram (`diagram.svg`) for
`dense-solver-synthetic-php` (Multi-Encoding Pigeonhole Principle Benchmarks).

Reads actual variable/clause counts from `../cnf-orig/php9x8-*.cnf.xz` to plot
the exact footprint of all 11 PHP^{9}_{8} encodings (8 distinct PySAT/direct
At-Most-One families + functional & renamed variants), paired with a K_{5,4}
pigeonhole collision graph and scaling up to PHP^{65}_{64}.

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import lzma
import math
import xml.etree.ElementTree as ET
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent
OUT_SVG = SUITE_DIR / "diagram.svg"
FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sub(s: str) -> str:
    return f'<tspan baseline-shift="sub" font-size="72%">{esc(s)}</tspan>'


def sup(s: str) -> str:
    return f'<tspan baseline-shift="super" font-size="72%">{esc(s)}</tspan>'


def read_cnf_header(path: Path) -> tuple[int, int]:
    with lzma.open(path, "rt", encoding="latin-1", errors="replace") as f:
        for line in f:
            if line.startswith("p cnf"):
                parts = line.split()
                return int(parts[2]), int(parts[3])
    return 0, 0


def build_svg() -> str:
    W, H = 960, 512

    # Parse actual (vars, clauses) from ../cnf-orig/php9x8-*.cnf.xz
    enc_order = [
        ("php9x8-pairwise", "Pairwise", "#2563eb"),
        ("php9x8-pairwise-functional", "Pairwise+Func", "#1d4ed8"),
        ("php9x8-sequential", "Sinz Sequential", "#059669"),
        ("php9x8-sequential-renamed", "Seq. (Renamed)", "#10b981"),
        ("php9x8-bitwise", "Bitwise", "#7c3aed"),
        ("php9x8-ladder", "Ladder", "#0284c7"),
        ("php9x8-kmtotalizer", "k-ModTotalizer", "#d97706"),
        ("php9x8-mtotalizer", "ModTotalizer", "#ea580c"),
        ("php9x8-totalizer", "Totalizer", "#f59e0b"),
        ("php9x8-cardnetwrk", "CardNetwork", "#db2777"),
        ("php9x8-sortnetwrk", "SortNetwork", "#dc2626"),
    ]
    enc_stats: list[tuple[str, int, int, str]] = []
    cnf_dir = SUITE_DIR / "cnf-orig"
    for stem, label, col in enc_order:
        v, c = read_cnf_header(cnf_dir / f"{stem}.cnf.xz")
        enc_stats.append((label, v, c, col))

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Multi-Encoding Pigeonhole Principle SAT Benchmark Suite">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        # Header
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Multi-Encoding Pigeonhole Principle Suite (dense-solver-synthetic-php)</text>',
        f'    <text x="26" y="53" font-size="11.8" fill="#475569">'
        f'17 structured PHP CNFs: 11 PHP{sup("9")}{sub("8")} AMO encoding variants + '
        f'PHP{sup("8")}{sub("8")} SAT controls + scaled PHP{sup("31")}{sub("30")} &amp; PHP{sup("65")}{sub("64")}</text>',
        '    <rect x="782" y="18" width="154" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="859" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">2 SAT · 15 UNSAT</text>',
        '    <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: BIPARTITE COLLISION + SCALING TO PHP^65_64 =================
    lx, ly, lw, lh = 24, 78, 392, 412
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">1. Pigeonhole Principle (K{sub("n+1,n")} Collision)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">Global counting contradiction hidden beneath 8 AMO CNF encodings</text>')

    # Bipartite graph K_{5,4} inside a crisp white subcard
    gx, gy, gw, gh = lx + 14, ly + 48, lw - 28, 174
    p.append(f'    <rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')

    px_col, hx_col = gx + 54, gx + 178
    # All edges of K_{5,4}
    for i in range(5):
        py_i = gy + 24 + i * 31
        for j in range(4):
            hy_j = gy + 39 + j * 31
            col, sw, op = "#cbd5e1", "0.9", "0.7"
            if i < 4 and i == j:
                col, sw, op = "#2563eb", "2.2", "1.0"
            elif i == 4 and j == 3:
                col, sw, op = "#dc2626", "2.4", "1.0"
            p.append(f'    <line x1="{px_col + 12}" y1="{py_i}" x2="{hx_col - 12}" y2="{hy_j}" stroke="{col}" stroke-width="{sw}" stroke-opacity="{op}"/>')

    for i in range(5):
        py_i = gy + 24 + i * 31
        fc = "#dc2626" if i == 4 else "#2563eb"
        p.append(f'    <circle cx="{px_col}" cy="{py_i}" r="11" fill="{fc}" stroke="#ffffff" stroke-width="1.6"/>')
        p.append(f'    <text x="{px_col}" y="{py_i + 3.8}" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">p{i + 1}</text>')

    for j in range(4):
        hy_j = gy + 39 + j * 31
        fc = "#dc2626" if j == 3 else "#059669"
        p.append(f'    <rect x="{hx_col - 11}" y="{hy_j - 10.5}" width="22" height="21" rx="4.5" fill="{fc}" stroke="#ffffff" stroke-width="1.6"/>')
        p.append(f'    <text x="{hx_col}" y="{hy_j + 3.8}" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">h{j + 1}</text>')

    # Formula callout beside K_{5,4}
    fx_c = gx + 204
    p.append(f'    <rect x="{fx_c}" y="{gy + 12}" width="148" height="150" rx="7" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{fx_c + 10}" y="{gy + 31}" font-size="10.2" font-weight="700" fill="#0f172a">CNF Constraints:</text>')
    p.append(f'    <text x="{fx_c + 10}" y="{gy + 49}" font-family="{FONT_MONO}" font-size="9.5" font-weight="700" fill="#1d4ed8">ALO: ∨ⱼ xᵢ,ⱼ (∀i)</text>')
    p.append(f'    <text x="{fx_c + 10}" y="{gy + 65}" font-size="9" fill="#475569">Each pigeon ≥ 1 hole</text>')
    p.append(f'    <text x="{fx_c + 10}" y="{gy + 86}" font-family="{FONT_MONO}" font-size="9.5" font-weight="700" fill="#b91c1c">AMO: ∑ᵢ xᵢ,ⱼ ≤ 1</text>')
    p.append(f'    <text x="{fx_c + 10}" y="{gy + 102}" font-size="9" fill="#475569">Encoded 8 ways via</text>')
    p.append(f'    <text x="{fx_c + 10}" y="{gy + 115}" font-size="9" fill="#475569">aux vars / networks</text>')
    p.append(f'    <rect x="{fx_c + 10}" y="{gy + 127}" width="128" height="24" rx="5" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
    p.append(f'    <text x="{fx_c + 74}" y="{gy + 143}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#b91c1c">n+1 &gt; n ⇒ UNSAT</text>')

    # Bottom Card in Left Panel: Pairwise vs Sequential Scaling up to PHP^65_64
    sy = gy + gh + 12
    p.append(f'    <rect x="{gx}" y="{sy}" width="{gw}" height="164" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{gx + 12}" y="{sy + 19}" font-size="11.4" font-weight="700" fill="#0f172a">Scaling: Pairwise O(n³) vs Sequential O(n²)</text>')

    th = sy + 36
    p.append(f'    <rect x="{gx + 10}" y="{th - 10}" width="{gw - 20}" height="16" rx="4" fill="#e2e8f0"/>')
    for cx_h, lbl_h, anc in [
        (gx + 16, "Instance", "start"),
        (gx + 164, "Vars", "end"),
        (gx + 226, "Clauses", "end"),
        (gx + 284, "CDCL", "middle"),
        (gx + 336, "Frob.", "middle"),
    ]:
        p.append(f'    <text x="{cx_h}" y="{th + 1}" text-anchor="{anc}" font-size="8.4" font-weight="700" fill="#334155">{lbl_h}</text>')

    scale_rows = [
        ("php8x8-pairwise", "64", "232", "SAT 1.6 ms", "2.3 ms", False, True),
        ("php9x8-pairwise", "72", "297", "65–326 ms", "2.0 ms", False, False),
        ("php31x30 (s/p)", "1.8k / 930", "2.7k / 14k", ">5 s T/O", "2.4–3.4", True, False),
        ("php65x64-sequential", "8,256", "12,289", ">5 s T/O", "6.4 ms", True, False),
        ("php65x64-pairwise", "4,160", "133,185", ">5 s T/O", "18.4 ms", True, False),
    ]
    for i, (nm, vs, cs, cdcl, fr, is_to, is_sat) in enumerate(scale_rows):
        ry_r = th + 17 + i * 21
        if is_to and "65x64" in nm:
            p.append(f'    <rect x="{gx + 10}" y="{ry_r - 10.5}" width="{gw - 20}" height="18" rx="3" fill="#fef2f2"/>')
        elif is_sat:
            p.append(f'    <rect x="{gx + 10}" y="{ry_r - 10.5}" width="{gw - 20}" height="18" rx="3" fill="#ecfdf5"/>')
        p.append(f'    <text x="{gx + 16}" y="{ry_r + 1.5}" font-family="{FONT_MONO}" font-size="8.3" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{gx + 164}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.3" fill="#475569">{vs}</text>')
        p.append(f'    <text x="{gx + 226}" y="{ry_r + 1.5}" text-anchor="end" font-size="8.3" fill="#475569">{cs}</text>')
        ccol = "#b91c1c" if is_to else ("#047857" if is_sat else "#334155")
        p.append(f'    <text x="{gx + 284}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.3" font-weight="700" fill="{ccol}">{esc(cdcl)}</text>')
        p.append(f'    <text x="{gx + 336}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.3" font-weight="700" fill="#1d4ed8">{fr}</text>')

    p.append(
        f'    <text x="{gx + 12}" y="{sy + 154}" font-size="8.8" fill="#475569">'
        'All 17/17 solved in 38.2 ms (dense-solver) &amp; 95.8 ms (Frobenius 1C).</text>'
    )

    # ================= RIGHT PANEL: EXACT PHP 9x8 11-ENCODING COMPARISON CHART =================
    rx, ry, rw, rh = 432, 78, 504, 412
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 16}" y="{ry + 22}" font-size="13" font-weight="700" fill="#0f172a">2. Exact CNF Footprint Across All 11 PHP{sup("9")}{sub("8")} Encodings</text>')
    p.append(f'    <text x="{rx + 16}" y="{ry + 38}" font-size="10.4" fill="#475569">Parsed from cnf-orig/php9x8-*.cnf.xz — log-scaled variables (solid) &amp; clauses (tinted)</text>')

    # Legend
    p.append(f'    <rect x="{rx + 16}" y="{ry + 48}" width="12" height="9" rx="2" fill="#2563eb"/>')
    p.append(f'    <text x="{rx + 33}" y="{ry + 56}" font-size="9.4" font-weight="600" fill="#334155">Variables n (aux encoding overhead)</text>')
    p.append(f'    <rect x="{rx + 230}" y="{ry + 48}" width="12" height="9" rx="2" fill="#2563eb" fill-opacity="0.32" stroke="#2563eb" stroke-width="1"/>')
    p.append(f'    <text x="{rx + 247}" y="{ry + 56}" font-size="9.4" font-weight="600" fill="#334155">Clauses m (log₁₀ scale)</text>')

    # Chart card
    cx0, cy0, cw0, ch0 = rx + 14, ry + 66, rw - 28, 294
    p.append(f'    <rect x="{cx0}" y="{cy0}" width="{cw0}" height="{ch0}" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')

    bar_x0 = cx0 + 114
    bar_w_max = 266
    log_min, log_max = math.log10(50), math.log10(2000)

    def x_for(val: int) -> float:
        lv = max(log_min, min(log_max, math.log10(max(val, 1))))
        return bar_x0 + (lv - log_min) / (log_max - log_min) * bar_w_max

    # Vertical log grid lines (100, 250, 500, 1000, 1500)
    for gv in (100, 250, 500, 1000, 1500):
        gx_l = x_for(gv)
        p.append(f'    <line x1="{gx_l:.1f}" y1="{cy0 + 10}" x2="{gx_l:.1f}" y2="{cy0 + ch0 - 22}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,2"/>')
        p.append(f'    <text x="{gx_l:.1f}" y="{cy0 + ch0 - 8}" text-anchor="middle" font-size="8.6" fill="#64748b">{gv:,}</text>')

    row_step = 23.8
    for idx, (lbl, nv, nc, col) in enumerate(enc_stats):
        yy = cy0 + 18 + idx * row_step
        p.append(f'    <text x="{bar_x0 - 8}" y="{yy + 11}" text-anchor="end" font-size="9.6" font-weight="700" fill="#1e293b">{esc(lbl)}</text>')
        wv = max(4.0, x_for(nv) - bar_x0)
        wc = max(4.0, x_for(nc) - bar_x0)
        # Upper bar: variables
        p.append(f'    <rect x="{bar_x0}" y="{yy}" width="{wv:.1f}" height="8.5" rx="2.5" fill="{col}"/>')
        # Lower bar: clauses
        p.append(f'    <rect x="{bar_x0}" y="{yy + 9.5}" width="{wc:.1f}" height="8.5" rx="2.5" fill="{col}" fill-opacity="0.30" stroke="{col}" stroke-width="0.8"/>')
        # Numeric readout on right
        p.append(f'    <text x="{cx0 + cw0 - 8}" y="{yy + 11}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.6" font-weight="600" fill="#334155">{nv:,}v / {nc:,}c</text>')

    # Bottom takeaway strip in Right Panel
    p.append(f'    <rect x="{rx + 14}" y="{cy0 + ch0 + 10}" width="{rw - 28}" height="32" rx="7" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>')
    p.append(
        f'    <text x="{rx + rw / 2:.1f}" y="{cy0 + ch0 + 29.5}" text-anchor="middle" font-size="9.8" font-weight="600" fill="#1e3a8a">'
        f'Auxiliary AMO variables shift ρ{sub("crit")} from 0.55× (k-ModTotalizer) to 32.0× (Pairwise 65×64) — 0 native XORs</text>'
    )

    p.append("  </g>")
    p.append("</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT_SVG.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
