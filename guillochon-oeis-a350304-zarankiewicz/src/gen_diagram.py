#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-a350304-zarankiewicz.

Renders the independently verified 17x17 K_{3,3}-free binary matrix with 135 ones
(`src/upstream/sequences/A350304/certificates/zaran3_n17_135.model`), verifying via
bitwise AND over all C(17,3) = 680 row triples that no 3x3 all-ones submatrix exists.
"""
from __future__ import annotations

import lzma
import xml.etree.ElementTree as ET
from itertools import combinations
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


def build_svg() -> str:
    n = 17
    z_true = read_true_vars(ROOT / "src/upstream/sequences/A350304/certificates/zaran3_n17_135.model")
    mat = [[(r * n + c + 1) in z_true for c in range(n)] for r in range(n)]
    row_masks = [sum((1 << c) for c in range(n) if mat[r][c]) for r in range(n)]
    ones = sum(sum(row) for row in mat)
    worst = max((a & b & c).bit_count() for a, b, c in combinations(row_masks, 3))
    assert ones == 135 and worst < 3, f"Invalid Zarankiewicz matrix: ones={ones}, max_common={worst}"

    row_sums = [sum(mat[r]) for r in range(n)]
    col_sums = [sum(mat[r][c] for r in range(n)) for c in range(n)]

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
      .mono { font: 700 9.6px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #334155; }
      .mono-sm { font: 600 8.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #64748b; }
      .badge { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .cap { font: 400 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #334155; }
      .cap-b { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
    </style>
  </defs>""")

    add(f'  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    add('  <text x="24" y="33" class="title">OEIS A350304 — Zarankiewicz Numbers z(n; 3) (K3,3-Free Binary Matrices)</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum ones in an n x n binary matrix avoiding every 3 x 3 all-ones submatrix (also settles A001198, A347473, A350237)</text>')
    add('  <rect x="760" y="14" width="176" height="24" rx="12" fill="#0d9488"/>')
    add('  <text x="848" y="30" text-anchor="middle" class="badge">OPEN: 135 &lt;= z(17;3) &lt;= 150</text>')

    # Left Card: Verified 17x17 Matrix + Row/Col Marginals
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified 17x17 K3,3-Free Certificate (135 Ones, z(17; 3) &gt;= 135)</text>')
    add(f'  <text x="36" y="106" class="psub">zaran3_n17_135.model | density {100*ones/289:.1f}% | max common cols across all 680 row triples = {worst} (&lt; 3)</text>')

    cell = 19.2
    mx0, my0 = 48.0, 122.0
    mw = n * cell
    add(f'  <rect x="{mx0-1.5:.1f}" y="{my0-1.5:.1f}" width="{mw+3:.1f}" height="{mw+3:.1f}" fill="#ffffff" stroke="#475569" stroke-width="1.4"/>')
    for r in range(n):
        for c in range(n):
            x = mx0 + c * cell
            y = my0 + r * cell
            fill = "#0f766e" if mat[r][c] else "#f1f5f9"
            add(f'  <rect x="{x+1:.1f}" y="{y+1:.1f}" width="{cell-2:.1f}" height="{cell-2:.1f}" rx="2.2" fill="{fill}"/>')

    # Row-sum histogram on the right of matrix
    hx0 = mx0 + mw + 14
    add(f'  <text x="{hx0:.1f}" y="{my0-5:.1f}" class="mono-sm">row 1s</text>')
    max_rs = max(row_sums)
    for r, rs in enumerate(row_sums):
        y = my0 + r * cell + 3.5
        bw = (rs / max_rs) * 68.0
        add(f'  <rect x="{hx0:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{cell-7:.1f}" rx="2.5" fill="#14b8a6" fill-opacity="0.78"/>')
        add(f'  <text x="{hx0+bw+5:.1f}" y="{y+9.5:.1f}" class="mono-sm">{rs}</text>')

    # Col-sum numbers below matrix
    for c, cs in enumerate(col_sums):
        cx = mx0 + c * cell + cell / 2.0
        add(f'  <text x="{cx:.1f}" y="{my0+mw+14:.1f}" text-anchor="middle" class="mono-sm">{cs}</text>')
    add(f'  <text x="{mx0-4:.1f}" y="{my0+mw+14:.1f}" text-anchor="end" class="mono-sm">col:</text>')

    # Legend
    add('  <rect x="48" y="476" width="12" height="12" rx="2.5" fill="#0f766e"/>')
    add(f'  <text x="65" y="486" class="cap"><tspan class="cap-b">1-entry ({ones} cells)</tspan>, row weights {min(row_sums)}-{max(row_sums)}, col weights {min(col_sums)}-{max(col_sums)}</text>')
    add('  <rect x="358" y="476" width="12" height="12" rx="2.5" fill="#f1f5f9" stroke="#cbd5e1"/>')
    add(f'  <text x="375" y="486" class="cap"><tspan class="cap-b">0-entry ({289-ones})</tspan></text>')

    # Right Top Card: Forbidden K_{3,3} Submatrix & Double-Lex Encoding
    add('  <rect x="532" y="68" width="408" height="210" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Forbidden K3,3 Submatrix &amp; Double-Lex Symmetry</text>')
    add('  <text x="548" y="106" class="psub">C(n,3)^2 9-clauses forbid all-1s 3x3 blocks (462,400 at n = 17)</text>')

    # Mini bipartite K_{3,3} diagram (left side of card)
    lx, rx = 568, 650
    ys = [138, 178, 218]
    for y1 in ys:
        for y2 in ys:
            add(f'  <line x1="{lx}" y1="{y1}" x2="{rx}" y2="{y2}" stroke="#ef4444" stroke-width="1.4" stroke-opacity="0.72"/>')
    for i, y in enumerate(ys):
        add(f'  <circle cx="{lx}" cy="{y}" r="8.5" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>')
        add(f'  <text x="{lx}" y="{y+3.3}" text-anchor="middle" class="mono-sm" fill="#b91c1c">r{i+1}</text>')
        add(f'  <circle cx="{rx}" cy="{y}" r="8.5" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>')
        add(f'  <text x="{rx}" y="{y+3.3}" text-anchor="middle" class="mono-sm" fill="#b91c1c">c{i+1}</text>')
    add('  <text x="609" y="246" text-anchor="middle" class="cap-b" fill="#dc2626">Forbidden K3,3</text>')
    add('  <text x="609" y="261" text-anchor="middle" class="mono-sm">9 all-ones entries</text>')

    # Encoding notes (right side of card)
    tx = 682
    add(f'  <text x="{tx}" y="136" class="cap-b">Encoding Highlights:</text>')
    add(f'  <text x="{tx}" y="155" class="cap">- n^2 vars: x(r,c) = 1 iff M[r,c]=1.</text>')
    add(f'  <text x="{tx}" y="173" class="cap">- Forbidden 3x3: (~x_r1,c1 v ... v ~x_r3,c3).</text>')
    add(f'  <text x="{tx}" y="191" class="cap">- Sinz counter enforces sum(x) &gt;= m.</text>')
    add(f'  <text x="{tx}" y="209" class="cap">- <tspan class="cap-b">Double-lex symmetry breaking</tspan></text>')
    add(f'  <text x="{tx}" y="225" class="cap">  (Flener et al. 2002): rows &amp; cols</text>')
    add(f'  <text x="{tx}" y="241" class="cap">  lex-nonincreasing (sound).</text>')
    add(f'  <text x="{tx}" y="261" class="cap">- Frobenius UNSAT proof at n=10, m=61.</text>')

    # Right Bottom Card: Open Bracket at n = 17 & Known Ladder
    add('  <rect x="532" y="290" width="408" height="210" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="312" class="ptitle">Open n = 17 Bracket &amp; Known OEIS A350304 Terms</text>')
    add('  <text x="548" y="328" class="psub">Tan (2022) z(16,17;3) &lt;= 142 =&gt; z(17;3) &lt;= floor(17*142/16) = 150</text>')

    # Bracket axis 135..151
    ax0, ax1, ay = 556.0, 916.0, 368.0
    add(f'  <line x1="{ax0}" y1="{ay}" x2="{ax1}" y2="{ay}" stroke="#94a3b8" stroke-width="2.5"/>')
    # Open span highlight 136..150
    def mx_pos(val: int) -> float:
        return ax0 + (val - 135) * (ax1 - ax0) / 16.0
    add(f'  <rect x="{mx_pos(136):.1f}" y="{ay-7:.1f}" width="{mx_pos(150)-mx_pos(136):.1f}" height="14" rx="7" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>')
    markers = [
        (135, "135", "SAT", "#059669"),
        (136, "136", "OPEN", "#d97706"),
        (140, "140", "OPEN", "#d97706"),
        (144, "144", "OPEN", "#d97706"),
        (148, "148", "OPEN", "#d97706"),
        (151, "151", "UNSAT", "#dc2626"),
    ]
    for val, lbl, tag, col in markers:
        px = mx_pos(val)
        add(f'  <circle cx="{px:.1f}" cy="{ay}" r="6" fill="{col}" stroke="#ffffff" stroke-width="1.5"/>')
        add(f'  <text x="{px:.1f}" y="{ay-13}" text-anchor="middle" class="mono" fill="{col}">{lbl}</text>')
        add(f'  <text x="{px:.1f}" y="{ay+20}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="8.2" font-weight="700" fill="{col}">{tag}</text>')

    # Known calibration terms n=10..16
    known = [(10, 60), (11, 69), (12, 80), (13, 92), (14, 105), (15, 120), (16, 128)]
    kx0, kw, kg = 548, 51, 3.5
    add('  <text x="548" y="416" class="cap-b">Known Optimal Calibration Ladder (SAT at z, UNSAT at z+1):</text>')
    for i, (nn, zz) in enumerate(known):
        x = kx0 + i * (kw + kg)
        cert = nn in (10, 11)
        bg = "#ecfdf5" if cert else "#f1f5f9"
        st = "#059669" if cert else "#94a3b8"
        tc = "#065f46" if cert else "#334155"
        add(f'  <rect x="{x:.1f}" y="425" width="{kw}" height="38" rx="5" fill="{bg}" stroke="{st}" stroke-width="1.1"/>')
        add(f'  <text x="{x+kw/2:.1f}" y="440" text-anchor="middle" class="mono-sm" fill="{tc}">n={nn}</text>')
        add(f'  <text x="{x+kw/2:.1f}" y="456" text-anchor="middle" class="mono" fill="{tc}">{zz}</text>')

    add('  <text x="548" y="484" class="cap">20 instances total: 8 SAT / 8 UNSAT / 4 OPEN (zaran3_n17_m{136,140,144,148}).</text>')

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
