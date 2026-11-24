#!/usr/bin/env python3
"""Generate a bespoke illustrative SVG diagram (`diagram.svg`) for
`dense-solver-synthetic-chessboard` (Mutilated Chessboard Domino Tiling UNSAT).

Illustrates the 8x8 opposite-corner mutilated chessboard with a concrete
30-domino partial tiling leaving exactly 2 dark squares stranded, the
bipartite Hall parity obstruction (|D| = N^2/2 != N^2/2 - 2 = |L|),
the edge-variable CNF encoding from `src/chessboard.py`, and scaling
across chessboard12, chessboard16, and chessboard32.

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"
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


def build_svg() -> str:
    W, H = 940, 486
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Mutilated Chessboard Domino Tiling Parity Obstruction and CNF Encoding">',
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        # Header
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Mutilated Chessboard Domino Tiling (dense-solver-synthetic-chessboard)</text>',
        '    <text x="26" y="53" font-size="11.8" fill="#475569">'
        'Opposite-corner N×N domino tiling UNSAT formulas (chessboard12, 16, 32) · '
        'Bipartite color-parity obstruction (|D| − |L| = 2)</text>',
        '    <rect x="782" y="18" width="132" height="24" rx="12" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#b91c1c">3 UNSAT · N=12..32</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: 8x8 MUTILATED CHESSBOARD WITH 30 DOMINOES =================
    lx, ly, lw, lh = 24, 78, 434, 386
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Maximal 30-Domino Tiling on 8×8 Mutilated Board</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Light corners (0,0) &amp; (7,7) excised → 30 Light, 32 Dark squares remain</text>'
    )

    N = 8
    cell = 33
    bx, by = lx + 85, ly + 62
    p.append(
        f'    <rect x="{bx - 3}" y="{by - 3}" width="{N * cell + 6}" height="{N * cell + 6}" '
        'rx="5" fill="#1e293b"/>'
    )

    # Color convention: (r + c) % 2 == 0 is Light (corners (0,0) and (7,7) are Light!),
    # (r + c) % 2 == 1 is Dark.
    for r in range(N):
        for c in range(N):
            x, y = bx + c * cell, by + r * cell
            if (r, c) in ((0, 0), (N - 1, N - 1)):
                p.append(f'    <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>')
                p.append(f'    <line x1="{x + 8}" y1="{y + 8}" x2="{x + cell - 8}" y2="{y + cell - 8}" stroke="#dc2626" stroke-width="2.4" stroke-linecap="round"/>')
                p.append(f'    <line x1="{x + cell - 8}" y1="{y + 8}" x2="{x + 8}" y2="{y + cell - 8}" stroke="#dc2626" stroke-width="2.4" stroke-linecap="round"/>')
            else:
                fill = "#cbd5e1" if (r + c) % 2 == 1 else "#ffffff"
                p.append(f'    <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#94a3b8" stroke-width="0.6"/>')

    # Construct a true valid maximal packing of 30 disjoint 1x2 dominoes covering ALL 30 light squares
    # and 30 dark squares, leaving ONLY the two dark squares (7, 0) and (6, 7) uncovered!
    # Row 0: (0,1)-(0,2), (0,3)-(0,4), (0,5)-(0,6) -> (0,7) dark left for vertical? Wait:
    # Let's tile rows 0..7 systematically so every single square except (0,0), (7,7), (0,7)[dark], (7,0)[dark] is covered!
    # Check:
    #   Row 0: (0,1)-(0,2), (0,3)-(0,4), (0,5)-(0,6)  [leaves (0,7) dark uncovered!]
    #   Rows 1..6 (all 8 cols, 4 horizontal dominoes each): 6 * 4 = 24 dominoes!
    #   Row 7: (7,1)-(7,2), (7,3)-(7,4), (7,5)-(7,6)  [leaves (7,0) dark uncovered!]
    # Mix horizontal and vertical dominoes in rows 1..6 for a realistic tiling!
    dominoes: list[tuple[tuple[int, int], tuple[int, int]]] = [
        # Row 0 (leaves (0,7) dark stranded!)
        ((0, 1), (0, 2)), ((0, 3), (0, 4)), ((0, 5), (0, 6)),
        # Rows 1-2: mix of vertical and horizontal covering all 16 cells
        ((1, 0), (2, 0)), ((1, 1), (1, 2)), ((2, 1), (2, 2)),
        ((1, 3), (2, 3)), ((1, 4), (2, 4)), ((1, 5), (1, 6)),
        ((2, 5), (2, 6)), ((1, 7), (2, 7)),
        # Rows 3-4: mix of horizontal and vertical covering all 16 cells
        ((3, 0), (3, 1)), ((4, 0), (4, 1)), ((3, 2), (4, 2)),
        ((3, 3), (3, 4)), ((4, 3), (4, 4)), ((3, 5), (4, 5)),
        ((3, 6), (3, 7)), ((4, 6), (4, 7)),
        # Rows 5-6: mix covering all 16 cells
        ((5, 0), (6, 0)), ((5, 1), (6, 1)), ((5, 2), (5, 3)),
        ((6, 2), (6, 3)), ((5, 4), (6, 4)), ((5, 5), (5, 6)),
        ((6, 5), (6, 6)), ((5, 7), (6, 7)),
        # Row 7 (leaves (7,0) dark stranded!)
        ((7, 1), (7, 2)), ((7, 3), (7, 4)), ((7, 5), (7, 6)),
    ]
    # Assert mathematically that these 30 dominoes are valid, disjoint, and cover every square except (0,0),(7,7),(0,7),(7,0)
    covered: set[tuple[int, int]] = set()
    for (r1, c1), (r2, c2) in dominoes:
        assert abs(r1 - r2) + abs(c1 - c2) == 1
        assert (r1, c1) not in covered and (r2, c2) not in covered
        covered.add((r1, c1))
        covered.add((r2, c2))
    assert len(dominoes) == 30
    uncovered = {(r, c) for r in range(N) for c in range(N)} - covered - {(0, 0), (7, 7)}
    assert uncovered == {(0, 7), (7, 0)}

    for (r1, c1), (r2, c2) in dominoes:
        is_horiz = r1 == r2
        col = "#2563eb" if is_horiz else "#059669"
        x1 = bx + min(c1, c2) * cell + 3
        y1 = by + min(r1, r2) * cell + 3
        w = (abs(c2 - c1) + 1) * cell - 6
        h = (abs(r2 - r1) + 1) * cell - 6
        p.append(
            f'    <rect x="{x1}" y="{y1}" width="{w}" height="{h}" rx="5" '
            f'fill="{col}" fill-opacity="0.20" stroke="{col}" stroke-width="1.8"/>'
        )
        # Subtle domino midpoint divider pip
        mx = x1 + w / 2
        my = y1 + h / 2
        if is_horiz:
            p.append(f'    <line x1="{mx:.1f}" y1="{y1 + 5}" x2="{mx:.1f}" y2="{y1 + h - 5}" stroke="{col}" stroke-opacity="0.45" stroke-width="1"/>')
        else:
            p.append(f'    <line x1="{x1 + 5}" y1="{my:.1f}" x2="{x1 + w - 5}" y2="{my:.1f}" stroke="{col}" stroke-opacity="0.45" stroke-width="1"/>')

    # Highlight the 2 stranded Dark squares (0, 7) and (7, 0)
    for rr, cc in ((0, 7), (7, 0)):
        x, y = bx + cc * cell, by + rr * cell
        p.append(
            f'    <rect x="{x + 2.5:.1f}" y="{y + 2.5:.1f}" width="{cell - 5}" height="{cell - 5}" rx="5" '
            'fill="#dc2626" fill-opacity="0.28" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="4,2"/>'
        )
        p.append(
            f'    <text x="{x + cell / 2:.1f}" y="{y + cell / 2 + 4.5:.1f}" text-anchor="middle" '
            'font-size="13" font-weight="800" fill="#991b1b">!</text>'
        )

    # Row/col coordinate annotations on left & top
    for i in range(N):
        p.append(f'    <text x="{bx - 11}" y="{by + i * cell + cell / 2 + 3.5:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="9" fill="#64748b">{i}</text>')
        p.append(f'    <text x="{bx + i * cell + cell / 2:.1f}" y="{by - 8}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" fill="#64748b">{i}</text>')

    # Legend strip at bottom of left panel
    leg_y = ly + lh - 40
    p.append(f'    <rect x="{lx + 14}" y="{leg_y}" width="{lw - 28}" height="28" rx="6" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    p.append(f'    <rect x="{lx + 24}" y="{leg_y + 8}" width="16" height="12" rx="3" fill="#2563eb" fill-opacity="0.24" stroke="#2563eb" stroke-width="1.5"/>')
    p.append(f'    <text x="{lx + 46}" y="{leg_y + 18}" font-size="9.5" font-weight="600" fill="#334155">Horiz. domino</text>')
    p.append(f'    <rect x="{lx + 132}" y="{leg_y + 8}" width="12" height="12" rx="3" fill="#059669" fill-opacity="0.24" stroke="#059669" stroke-width="1.5"/>')
    p.append(f'    <text x="{lx + 150}" y="{leg_y + 18}" font-size="9.5" font-weight="600" fill="#334155">Vert. domino</text>')
    p.append(f'    <rect x="{lx + 228}" y="{leg_y + 8}" width="12" height="12" rx="3" fill="#dc2626" fill-opacity="0.28" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,1.5"/>')
    p.append(f'    <text x="{lx + 246}" y="{leg_y + 18}" font-size="9.5" font-weight="700" fill="#b91c1c">2 Dark stranded</text>')
    p.append(f'    <rect x="{lx + 344}" y="{leg_y + 8}" width="12" height="12" rx="2" fill="#fef2f2" stroke="#fca5a5" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 350}" y="{leg_y + 17.5}" text-anchor="middle" font-size="9.5" font-weight="800" fill="#dc2626">×</text>')
    p.append(f'    <text x="{lx + 362}" y="{leg_y + 18}" font-size="9.5" font-weight="600" fill="#475569">Excised</text>')

    # ================= RIGHT PANEL: PARITY OBSTRUCTION, CNF ENCODING & SCALING =================
    rx, ry, rw = 474, 78, 442

    # Card 1: Bipartite Parity & Hall Deficiency Proof
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="124" rx="9" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#991b1b">1. Bipartite Matching &amp; Hall Deficiency Obstruction</text>')

    # Mini bipartite diagram (Dark vs Light sets) on left of Card 1
    p.append(f'    <rect x="{rx + 16}" y="{ry + 32}" width="92" height="78" rx="7" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1"/>')
    p.append(f'    <text x="{rx + 62}" y="{ry + 49}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1e293b">Dark set D</text>')
    p.append(f'    <text x="{rx + 62}" y="{ry + 68}" text-anchor="middle" font-family="{FONT_MONO}" font-size="11.5" font-weight="700" fill="#0f172a">|D| = N²/2</text>')
    p.append(f'    <text x="{rx + 62}" y="{ry + 85}" text-anchor="middle" font-size="9.2" fill="#475569">N=8 → 32</text>')
    p.append(f'    <text x="{rx + 62}" y="{ry + 99}" text-anchor="middle" font-size="9.2" fill="#475569">N=32 → 512</text>')

    p.append(f'    <line x1="{rx + 108}" y1="{ry + 56}" x2="{rx + 150}" y2="{ry + 56}" stroke="#2563eb" stroke-width="2"/>')
    p.append(f'    <line x1="{rx + 108}" y1="{ry + 71}" x2="{rx + 150}" y2="{ry + 71}" stroke="#059669" stroke-width="2"/>')
    p.append(f'    <line x1="{rx + 108}" y1="{ry + 86}" x2="{rx + 150}" y2="{ry + 86}" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="3,2"/>')
    p.append(f'    <text x="{rx + 129}" y="{ry + 48}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#1d4ed8">1×2</text>')
    p.append(f'    <text x="{rx + 129}" y="{ry + 102}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#b91c1c">−2</text>')

    p.append(f'    <rect x="{rx + 150}" y="{ry + 32}" width="92" height="78" rx="7" fill="#ffffff" stroke="#94a3b8" stroke-width="1.1"/>')
    p.append(f'    <text x="{rx + 196}" y="{ry + 49}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1e293b">Light set L</text>')
    p.append(f'    <text x="{rx + 196}" y="{ry + 68}" text-anchor="middle" font-family="{FONT_MONO}" font-size="10.6" font-weight="700" fill="#b91c1c">|L| = N²/2−2</text>')
    p.append(f'    <text x="{rx + 196}" y="{ry + 85}" text-anchor="middle" font-size="9.2" fill="#475569">N=8 → 30</text>')
    p.append(f'    <text x="{rx + 196}" y="{ry + 99}" text-anchor="middle" font-size="9.2" fill="#475569">N=32 → 510</text>')

    # Proof text on right of Card 1
    p.append(f'    <text x="{rx + 256}" y="{ry + 47}" font-size="10" font-weight="700" fill="#0f172a">Every domino covers</text>')
    p.append(f'    <text x="{rx + 256}" y="{ry + 62}" font-size="10" font-weight="700" fill="#0f172a">1 Dark + 1 Light square.</text>')
    p.append(f'    <text x="{rx + 256}" y="{ry + 82}" font-size="9.8" fill="#334155">Hall deficiency: |D| &gt; |N(D)|</text>')
    p.append(f'    <text x="{rx + 256}" y="{ry + 98}" font-size="9.8" fill="#334155">Pure Resolution requires</text>')
    p.append(f'    <text x="{rx + 256}" y="{ry + 112}" font-size="9.8" font-weight="700" fill="#b91c1c">2{sup("Ω(N)")} refutation size.</text>')

    # Card 2: Exact CNF Encoding (src/chessboard.py)
    cy2 = ry + 136
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="106" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">2. Direct Edge-Variable CNF Encoding (src/chessboard.py)</text>')
    enc_rows = [
        ("Variables:", f'e{sub("u,v")} ∈ {{0,1}} for each grid edge (u,v):  n = 2N(N−1) − 4'),
        ("ALO Cover:", f'∀ square u ∈ D∪L:  ⋁{sub("v~u")} e{sub("u,v")}   (clause len 2–4, positive)'),
        ("AMO Pair:", f'∀ square u, ∀ v≠w ~ u:  ¬e{sub("u,v")} ∨ ¬e{sub("u,w")}   (84–85% binary Horn)'),
        ("Profile:", f'ρ{sub("crit")} = 2.84×–2.97× (Over) · k̄ = 2.28 (k{sub("max")}=4) · 0 native XORs'),
    ]
    for i, (k, v) in enumerate(enc_rows):
        yy = cy2 + 40 + i * 17
        p.append(f'    <text x="{rx + 14}" y="{yy}" font-size="9.8" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 84}" y="{yy}" font-size="9.7" fill="#334155">{v}</text>')

    # Card 3: Suite Scaling & 1-Core Benchmark Table
    cy3 = cy2 + 118
    p.append(f'    <rect x="{rx}" y="{cy3}" width="{rw}" height="132" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy3 + 20}" font-size="12" font-weight="700" fill="#0f172a">3. Corpus Scaling &amp; 1-Core Solve Time (T{sub("max")} = 5 s)</text>')

    # Header bar
    th = cy3 + 38
    p.append(f'    <rect x="{rx + 12}" y="{th - 11}" width="{rw - 24}" height="17" rx="4" fill="#e2e8f0"/>')
    for hx_c, hlbl, anc in [
        (rx + 18, "Instance", "start"),
        (rx + 122, "Vars", "end"),
        (rx + 178, "Clauses", "end"),
        (rx + 252, "CDCL", "middle"),
        (rx + 332, "dense-solver", "middle"),
        (rx + 402, "Frob. 1C", "middle"),
    ]:
        p.append(f'    <text x="{hx_c}" y="{th + 1}" text-anchor="{anc}" font-size="8.8" font-weight="700" fill="#334155">{hlbl}</text>')

    rows = [
        ("chessboard12", "260", "856", "399–495 ms", "1.66 ms", "1.71 ms", False),
        ("chessboard16", "476", "1,592", ">5 s (T/O)", "2.09 ms", "2.53 ms", True),
        ("chessboard32", "1,980", "6,776", ">5 s (T/O)", "3.62 ms", "3.80 ms", True),
    ]
    for i, (nm, vs, cs, cdcl, ds, fr, to) in enumerate(rows):
        ry_r = th + 19 + i * 22
        if to:
            p.append(f'    <rect x="{rx + 12}" y="{ry_r - 12}" width="{rw - 24}" height="20" rx="3" fill="#fef2f2"/>')
        p.append(f'    <text x="{rx + 18}" y="{ry_r + 1}" font-family="{FONT_MONO}" font-size="9.2" font-weight="700" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{rx + 122}" y="{ry_r + 1}" text-anchor="end" font-size="9.2" fill="#475569">{vs}</text>')
        p.append(f'    <text x="{rx + 178}" y="{ry_r + 1}" text-anchor="end" font-size="9.2" fill="#475569">{cs}</text>')
        p.append(f'    <text x="{rx + 252}" y="{ry_r + 1}" text-anchor="middle" font-size="9.1" font-weight="700" fill="{"#b91c1c" if to else "#334155"}">{esc(cdcl)}</text>')
        p.append(f'    <text x="{rx + 332}" y="{ry_r + 1}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#047857">{ds}</text>')
        p.append(f'    <text x="{rx + 402}" y="{ry_r + 1}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#1d4ed8">{fr}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy3 + 122}" font-size="9.2" fill="#475569">'
        '4 Formats: 3 CNF (16.3 KB) · 3 AIG (18.0 KB) · 3 XCNF (16.7 KB) · 3 ANF (38.8 KB, deg ≤ 3)</text>'
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
