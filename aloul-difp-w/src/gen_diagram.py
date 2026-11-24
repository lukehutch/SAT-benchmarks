#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`aloul-difp-w` (Aloul Wallace-Multiplier Integer Factoring Benchmarks).

Zero external dependencies (Python 3 stdlib only). Writes `../diagram.svg`
deterministically from any working directory and validates XML well-formedness.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sub(text: str) -> str:
    return f'<tspan baseline-shift="sub" font-size="72%">{esc(text)}</tspan>'


def sup(text: str) -> str:
    return f'<tspan baseline-shift="super" font-size="72%">{esc(text)}</tspan>'


def build_svg() -> str:
    W, H = 920, 480
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Aloul Wallace-Tree Multiplier Integer Factoring SAT Architecture">',
        "  <defs>",
        '    <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        '    <marker id="arr-purp" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>',
        "    </marker>",
        '    <marker id="arr-amb" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Aloul Wallace-Tree Multiplier Integer Factoring (aloul-difp-w)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Parallel 3:2 Carry-Save Adder (CSA) tree reduction in O(log₃/₂ n) depth · '
        '15 SAT semiprimes (n ∈ {19, 20, 21}-bit primes, randomly reordered)</text>',
        '    <rect x="772" y="18" width="122" height="24" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>',
        '    <text x="833" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#6d28d9">15 SAT · Wallace</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: WALLACE 3:2 CSA REDUCTION DOT DIAGRAM =================
    lx, ly, lw, lh = 24, 78, 540, 380
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Wallace 3:2 Carry-Save Reduction Tree (6×6 Bit-Column Schematic of n×n)</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Groups of 3 bits per column compress in parallel (FA: 3→2, HA: 2→2) until height ≤ 2 for final CPA</text>'
    )

    # 12 bit columns (bit 11 on left .. bit 0 on right)
    # Column centers
    n_cols = 12
    c_start = lx + 126  # bit 11 x
    c_step = 35
    col_x = [c_start + (n_cols - 1 - b) * c_step for b in range(n_cols)]  # col_x[0] is rightmost (2^0)

    # Column weight header
    for b in range(n_cols):
        p.append(
            f'    <text x="{col_x[b]}" y="{ly + 56}" text-anchor="middle" '
            f'font-family="{mono}" font-size="8.6" font-weight="600" fill="#64748b">2{sup(str(b))}</text>'
        )

    def wallace_step(counts: list[int]) -> tuple[list[int], list[tuple[int, int, int]]]:
        nxt = [0] * n_cols
        ops: list[tuple[int, int, int]] = []
        for b in range(n_cols):
            c = counts[b]
            n_fa = c // 3
            rem = c % 3
            n_ha = 1 if (rem == 2 and c > 2) else 0
            pass_cnt = rem if n_ha == 0 else 0
            nxt[b] += n_fa + n_ha + pass_cnt
            if b + 1 < n_cols:
                nxt[b + 1] += n_fa + n_ha
            ops.append((b, n_fa, n_ha))
        return nxt, ops

    s0 = [min(b + 1, 11 - b) if b <= 10 else 0 for b in range(n_cols)]
    s1, ops0 = wallace_step(s0)
    s2, ops1 = wallace_step(s1)
    s3, ops2 = wallace_step(s2)

    stages = [
        ("Stage 0", "Partial Prod", f'h{sub("max")} = 6', s0, ops0, ly + 62, 84, 10.6, "#2563eb"),
        ("Stage 1", "3:2 CSA L1", f'h{sub("max")} = 4', s1, ops1, ly + 153, 56, 10.8, "#7c3aed"),
        ("Stage 2", "3:2 CSA L2", f'h{sub("max")} = 3', s2, ops2, ly + 216, 44, 10.8, "#7c3aed"),
        ("Stage 3", "2-Row Sum", f'h{sub("max")} = 2', s3, None, ly + 267, 36, 11.2, "#059669"),
    ]

    for s_name, s_sub, s_h, counts, ops, sy, sh, dot_dy, col in stages:
        p.append(f'    <rect x="{lx + 14}" y="{sy}" width="{lw - 28}" height="{sh}" rx="6" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
        p.append(f'    <text x="{lx + 22}" y="{sy + 16}" font-size="10.2" font-weight="700" fill="{col}">{s_name}</text>')
        p.append(f'    <text x="{lx + 22}" y="{sy + 29}" font-size="9" fill="#475569">{s_sub}</text>')
        if sh >= 42:
            p.append(f'    <text x="{lx + 22}" y="{sy + 40}" font-family="{mono}" font-size="8.6" font-weight="600" fill="#64748b">{s_h}</text>')

        for b in range(n_cols):
            cnt = counts[b]
            if cnt == 0:
                continue
            bx = col_x[b]
            total_h = (cnt - 1) * dot_dy
            y_top = sy + sh / 2 - total_h / 2

            if ops is not None:
                _, n_fa, n_ha = ops[b]
                idx_d = 0
                for _ in range(n_fa):
                    gy0 = y_top + idx_d * dot_dy - 4.8
                    gh = 2 * dot_dy + 9.6
                    p.append(f'    <rect x="{bx - 7.5:.1f}" y="{gy0:.1f}" width="15" height="{gh:.1f}" rx="4" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1"/>')
                    idx_d += 3
                for _ in range(n_ha):
                    gy0 = y_top + idx_d * dot_dy - 4.8
                    gh = 1 * dot_dy + 9.6
                    p.append(f'    <rect x="{bx - 7.5:.1f}" y="{gy0:.1f}" width="15" height="{gh:.1f}" rx="4" fill="#fffbeb" stroke="#d97706" stroke-width="1"/>')
                    idx_d += 2

            for k in range(cnt):
                dy = y_top + k * dot_dy
                p.append(f'    <circle cx="{bx}" cy="{dy:.1f}" r="3.2" fill="{col}"/>')

        if ops is not None:
            p.append(f'    <line x1="{lx + 96}" y1="{sy + sh - 1}" x2="{lx + 96}" y2="{sy + sh + 6}" stroke="#475569" stroke-width="1.3" marker-end="url(#arr-slate)"/>')

    # Final CPA bar + Clamped Target N bits
    cpa_y = ly + 313
    p.append(f'    <rect x="{lx + 14}" y="{cpa_y}" width="{lw - 28}" height="24" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + lw / 2:.1f}" y="{cpa_y + 15.5}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#047857">Final Carry-Propagate Adder (CPA: 2 rows → 2n-bit product P = p × q)</text>')

    out_y = ly + 347
    p.append(f'    <rect x="{lx + 14}" y="{out_y}" width="{lw - 28}" height="22" rx="6" fill="#059669"/>')
    p.append(f'    <text x="{lx + 24}" y="{out_y + 14.5}" font-size="9.5" font-weight="700" fill="#ffffff">Clamped N:</text>')
    for b in range(n_cols):
        p.append(f'    <text x="{col_x[b]}" y="{out_y + 14.5}" text-anchor="middle" font-family="{mono}" font-size="9.2" font-weight="700" fill="#ffffff">N{b}</text>')

    # ================= RIGHT PANEL: CSA CELL, ARRAY VS WALLACE & CORPUS =================
    rx, ry, rw = 580, 78, 316

    # Card 1: 3:2 CSA Compressor Cell Schematic
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="112" rx="9" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 20}" font-size="12" font-weight="700" fill="#6d28d9">3:2 Carry-Save Adder (CSA) Cell</text>')

    bx_csa, by_csa = rx + 82, ry + 32
    p.append(f'    <rect x="{bx_csa}" y="{by_csa}" width="102" height="50" rx="7" fill="#ffffff" stroke="#7c3aed" stroke-width="1.4"/>')
    p.append(f'    <text x="{bx_csa + 51}" y="{by_csa + 22}" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">Full Adder</text>')
    p.append(f'    <text x="{bx_csa + 51}" y="{by_csa + 38}" text-anchor="middle" font-size="9" fill="#6d28d9">3 bits → 2 bits</text>')
    for i, lbl in enumerate([f'a{sub("k")}', f'b{sub("k")}', f'c{sub("k")}']):
        iy = by_csa + 10 + i * 15
        p.append(f'    <line x1="{bx_csa - 34}" y1="{iy}" x2="{bx_csa - 2}" y2="{iy}" stroke="#475569" stroke-width="1.4" marker-end="url(#arr-slate)"/>')
        p.append(f'    <text x="{bx_csa - 40}" y="{iy + 3.5}" text-anchor="end" font-family="{mono}" font-size="9.5" font-weight="700" fill="#0f172a">{lbl}</text>')
    p.append(f'    <line x1="{bx_csa + 102}" y1="{by_csa + 16}" x2="{bx_csa + 132}" y2="{by_csa + 16}" stroke="#7c3aed" stroke-width="1.6" marker-end="url(#arr-purp)"/>')
    p.append(f'    <text x="{bx_csa + 138}" y="{by_csa + 19.5}" font-size="9.4" font-weight="700" fill="#6d28d9">s{sub("k")} = a⊕b⊕c</text>')
    p.append(f'    <line x1="{bx_csa + 102}" y1="{by_csa + 36}" x2="{bx_csa + 132}" y2="{by_csa + 36}" stroke="#d97706" stroke-width="1.6" marker-end="url(#arr-amb)"/>')
    p.append(f'    <text x="{bx_csa + 138}" y="{by_csa + 39.5}" font-size="9.4" font-weight="700" fill="#b45309">c{sub("k+1")} = Maj₃</text>')

    p.append(f'    <text x="{rx + 14}" y="{ry + 101}" font-size="9.4" fill="#475569">Depth recurrence: h{sub("t+1")} ≤ ⌈2·h{sub("t")} / 3⌉ ⇒ O(log₃/₂ n) layers</text>')

    # Card 2: Direct Comparison vs Array
    cy2 = ry + 122
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="124" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">Wallace vs Array (Same Semiprime)</text>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 34}" font-family="{mono}" font-size="9.1" fill="#047857">0x1451990C0F = 283,097 × 308,263 (19b)</text>')

    cmp_rows = [
        ("CNF Vars", "1,755", "1,201", "+46%"),
        ("CNF Clauses", "10,446", "6,563", "+59%"),
        ("Native XORs", "567", "380", "+49%"),
        ("Deg CV (skew)", "4.23", "0.45", "9.4× hub!"),
        ("Logic Depth", "O(log n)", "O(n)", "Shallow"),
    ]
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 50}" font-size="9.2" font-weight="700" fill="#64748b">Metric</text>')
    p.append(f'    <text x="{rx + 146}" y="{cy2 + 50}" text-anchor="end" font-size="9.2" font-weight="700" fill="#6d28d9">Wallace</text>')
    p.append(f'    <text x="{rx + 212}" y="{cy2 + 50}" text-anchor="end" font-size="9.2" font-weight="700" fill="#2563eb">Array</text>')
    p.append(f'    <text x="{rx + rw - 14}" y="{cy2 + 50}" text-anchor="end" font-size="9.2" font-weight="700" fill="#475569">Delta</text>')
    p.append(f'    <line x1="{rx + 12}" y1="{cy2 + 54}" x2="{rx + rw - 12}" y2="{cy2 + 54}" stroke="#e2e8f0" stroke-width="1"/>')
    for i, (m, wv, av, dlt) in enumerate(cmp_rows):
        yy = cy2 + 66 + i * 13.5
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.3" fill="#334155">{m}</text>')
        p.append(f'    <text x="{rx + 146}" y="{yy:.1f}" text-anchor="end" font-family="{mono}" font-size="9.2" font-weight="700" fill="#6d28d9">{wv}</text>')
        p.append(f'    <text x="{rx + 212}" y="{yy:.1f}" text-anchor="end" font-family="{mono}" font-size="9.2" fill="#2563eb">{av}</text>')
        p.append(f'    <text x="{rx + rw - 14}" y="{yy:.1f}" text-anchor="end" font-size="9.1" font-weight="600" fill="#0f172a">{dlt}</text>')

    # Card 3: Corpus Summary (extra vertical spacing!)
    cy3 = cy2 + 134
    p.append(f'    <rect x="{rx}" y="{cy3}" width="{rw}" height="124" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy3 + 20}" font-size="12" font-weight="700" fill="#0f172a">Corpus Dimensions (15 SAT Instances)</text>')
    groups = [
        ("difp_19 / 20 (wal)", "10 files", "1,755 v · 10,446 c · 567 XOR", 0.82, "#7c3aed"),
        ("difp_21 (wal)", "5 files", "2,125 v · 12,677 c · 683 XOR", 1.00, "#2563eb"),
    ]
    for i, (g, cnt, stat, frac, col) in enumerate(groups):
        yy = cy3 + 40 + i * 37
        p.append(f'    <text x="{rx + 14}" y="{yy}" font-family="{mono}" font-size="9.5" font-weight="700" fill="#0f172a">{g}</text>')
        p.append(f'    <text x="{rx + rw - 14}" y="{yy}" text-anchor="end" font-size="9.4" font-weight="600" fill="{col}">{cnt}</text>')
        p.append(f'    <rect x="{rx + 14}" y="{yy + 4}" width="{rw - 28}" height="7.5" rx="3" fill="#e2e8f0"/>')
        p.append(f'    <rect x="{rx + 14}" y="{yy + 4}" width="{(rw - 28) * frac:.1f}" height="7.5" rx="3" fill="{col}" fill-opacity="0.85"/>')
        p.append(f'    <text x="{rx + 14}" y="{yy + 22}" font-size="9" fill="#475569">{stat}</text>')

    p.append(
        f'    <text x="{rx + 14}" y="{cy3 + 116}" font-size="9.3" fill="#475569">'
        f'Total native XORs: 9,085 · ρ{sub("crit")} = 1.36× · κ = 0.97 · 8% Bin</text>'
    )

    p.append("  </g>")
    p.append("</svg>\n")
    return "\n".join(p)


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "diagram.svg"
    out.write_text(build_svg(), encoding="utf-8")
    ET.parse(out)
    print(f"Wrote and validated {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
