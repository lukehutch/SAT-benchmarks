#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`satlib-bmc` (SATLIB Bounded Model Checking — Ofer Shtrichman IBM/Galileo Suite).

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


def build_svg() -> str:
    W, H = 920, 485
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Hardware Bounded Model Checking k-Step Unrolled Transition Relation">',
        "  <defs>",
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>',
        "    </marker>",
        '    <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>',
        "    </marker>",
        '    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>',
        "    </marker>",
        '    <marker id="arr-grn" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'SATLIB Hardware Bounded Model Checking — Shtrichman (satlib-bmc)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Unrolling sequential hardware FSMs across k clock cycles to find safety-property counterexamples · '
        '13 IBM/Galileo SAT benchmarks</text>',
        '    <rect x="756" y="18" width="138" height="24" rx="12" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>',
        '    <text x="825" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">13 SAT · Bug Trace</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: FSM -> k-STEP UNROLLED BMC TIMEFRAMES =================
    lx, ly, lw, lh = 24, 78, 562, 385
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'Sequential Circuit Unrolling into a k-Step Combinational SAT Formula</text>'
    )

    # Top Sub-band: Compact Sequential FSM with feedback latch
    fy = ly + 34
    p.append(f'    <rect x="{lx + 16}" y="{fy}" width="{lw - 32}" height="74" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.1"/>')
    p.append(f'    <text x="{lx + 28}" y="{fy + 17}" font-size="10.2" font-weight="700" fill="#475569">Sequential Hardware Design (FSM):</text>')
    # Input arrow -> Combinational Logic T -> State Register FF -> Feedback loop
    p.append(f'    <text x="{lx + 36}" y="{fy + 47}" font-size="9.6" font-weight="700" fill="#1d4ed8">Inputs i</text>')
    p.append(f'    <line x1="{lx + 76}" y1="{fy + 43}" x2="{lx + 108}" y2="{fy + 43}" stroke="#2563eb" stroke-width="1.7" marker-end="url(#arr-blue)"/>')
    p.append(f'    <rect x="{lx + 110}" y="{fy + 25}" width="144" height="36" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 182}" y="{fy + 41}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#1d4ed8">Next-State Logic T(s,i,s\')</text>')
    p.append(f'    <text x="{lx + 182}" y="{fy + 54}" text-anchor="middle" font-size="8.8" fill="#475569">combinational gates + XORs</text>')
    p.append(f'    <line x1="{lx + 254}" y1="{fy + 43}" x2="{lx + 286}" y2="{fy + 43}" stroke="#475569" stroke-width="1.7" marker-end="url(#arr-slate)"/>')
    p.append(f'    <rect x="{lx + 288}" y="{fy + 25}" width="84" height="36" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 330}" y="{fy + 41}" text-anchor="middle" font-size="10" font-weight="700" fill="#b45309">Latches (FF)</text>')
    p.append(f'    <text x="{lx + 330}" y="{fy + 54}" text-anchor="middle" font-size="8.8" fill="#475569">state s → s\'</text>')
    # Feedback loop under FF back to T
    p.append(f'    <path d="M {lx + 330} {fy + 61} L {lx + 330} {fy + 69} L {lx + 182} {fy + 69} L {lx + 182} {fy + 63}" fill="none" stroke="#d97706" stroke-width="1.4" marker-end="url(#arr-slate)"/>')
    # Property Monitor P(s) on right
    p.append(f'    <line x1="{lx + 372}" y1="{fy + 43}" x2="{lx + 404}" y2="{fy + 43}" stroke="#dc2626" stroke-width="1.7" marker-end="url(#arr-red)"/>')
    p.append(f'    <rect x="{lx + 406}" y="{fy + 25}" width="124" height="36" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 468}" y="{fy + 41}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#b91c1c">Safety Check P(s)</text>')
    p.append(f'    <text x="{lx + 468}" y="{fy + 54}" text-anchor="middle" font-size="8.8" fill="#475569">assert ¬P(s) for bug</text>')

    # Downward "Unroll k clock steps" connector
    p.append(f'    <text x="{lx + lw/2:.1f}" y="{fy + 91}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#2563eb">↓  Unroll transition relation T across k discrete timeframes (t = 0, 1, …, k)  ↓</text>')

    # Main Unrolled Timeframe Diagram
    uy = ly + 136
    # Initial State I(s0)
    ix = lx + 18
    p.append(f'    <rect x="{ix}" y="{uy + 26}" width="54" height="58" rx="7" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>')
    p.append(f'    <text x="{ix + 27}" y="{uy + 50}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1d4ed8">I(s₀)</text>')
    p.append(f'    <text x="{ix + 27}" y="{uy + 66}" text-anchor="middle" font-size="8.6" fill="#334155">Init state</text>')

    # 3 visible Transition Relation copies: T_0, T_1, ..., T_{k-1}
    txs = [lx + 102, lx + 220, lx + 382]
    tw = 94
    t_lbls = [
        ("T(s₀, i₀, s₁)", "Step t = 0", "i₀"),
        ("T(s₁, i₁, s₂)", "Step t = 1", "i₁"),
        (f'T(s{sub("k−1")}, i{sub("k−1")}, s{sub("k")})', "Step t = k − 1", f'i{sub("k−1")}'),
    ]

    # Wire I(s0) -> T0
    p.append(f'    <line x1="{ix + 54}" y1="{uy + 55}" x2="{txs[0] - 2}" y2="{uy + 55}" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    p.append(f'    <text x="{(ix + 54 + txs[0]) / 2:.1f}" y="{uy + 48}" text-anchor="middle" font-family="{mono}" font-size="9" font-weight="700" fill="#1d4ed8">s₀</text>')

    # Wire T0 -> T1
    p.append(f'    <line x1="{txs[0] + tw}" y1="{uy + 55}" x2="{txs[1] - 2}" y2="{uy + 55}" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    p.append(f'    <text x="{(txs[0] + tw + txs[1]) / 2:.1f}" y="{uy + 48}" text-anchor="middle" font-family="{mono}" font-size="9" font-weight="700" fill="#1d4ed8">s₁</text>')

    # Ellipsis between T1 and T_{k-1} (extra room so s_{k-1} sits cleanly!)
    p.append(f'    <line x1="{txs[1] + tw}" y1="{uy + 55}" x2="{txs[1] + tw + 16}" y2="{uy + 55}" stroke="#2563eb" stroke-width="2"/>')
    p.append(f'    <text x="{txs[1] + tw + 27}" y="{uy + 59}" text-anchor="middle" font-size="15" font-weight="700" fill="#64748b">⋯</text>')
    p.append(f'    <line x1="{txs[2] - 32}" y1="{uy + 55}" x2="{txs[2] - 2}" y2="{uy + 55}" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')
    p.append(f'    <text x="{txs[2] - 18}" y="{uy + 46}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="#1d4ed8">s{sub("k−1")}</text>')

    # Draw T blocks + primary input arrows from above
    for idx_t, tx in enumerate(txs):
        tlbl, tsub, ilbl = t_lbls[idx_t]
        p.append(f'    <text x="{tx + tw/2:.1f}" y="{uy + 8}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#475569">{ilbl}</text>')
        p.append(f'    <line x1="{tx + tw/2:.1f}" y1="{uy + 12}" x2="{tx + tw/2:.1f}" y2="{uy + 24}" stroke="#475569" stroke-width="1.5" marker-end="url(#arr-slate)"/>')
        p.append(f'    <rect x="{tx}" y="{uy + 26}" width="{tw}" height="58" rx="7" fill="#ffffff" stroke="#2563eb" stroke-width="1.5"/>')
        p.append(f'    <text x="{tx + tw/2:.1f}" y="{uy + 49}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">{tlbl}</text>')
        p.append(f'    <text x="{tx + tw/2:.1f}" y="{uy + 67}" text-anchor="middle" font-size="8.8" fill="#475569">{tsub}</text>')

    # Final state s_k output tap on right (cleanly inside left panel!)
    sk_x = lx + 506
    p.append(f'    <line x1="{txs[2] + tw}" y1="{uy + 55}" x2="{sk_x - 2}" y2="{uy + 55}" stroke="#dc2626" stroke-width="2.2" marker-end="url(#arr-red)"/>')
    p.append(f'    <rect x="{sk_x}" y="{uy + 34}" width="36" height="42" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.6"/>')
    p.append(f'    <text x="{sk_x + 18}" y="{uy + 59}" text-anchor="middle" font-family="{mono}" font-size="10.2" font-weight="700" fill="#b91c1c">s{sub("k")}</text>')

    # Property Violation Taps ¬P(s_t) dropping down to Disjunction Bar
    or_y = uy + 130
    tap_xs = [ix + 68, txs[0] + tw + 13, txs[1] + tw + 10, sk_x + 18]
    tap_lbls = ["¬P(s₀)", "¬P(s₁)", "¬P(s₂)", f'¬P(s{sub("k")})=1!']
    for idx_p, tpx in enumerate(tap_xs):
        is_hit = idx_p == 3
        col_p = "#dc2626" if is_hit else "#94a3b8"
        dash_p = "" if is_hit else ' stroke-dasharray="3,2"'
        y_src = uy + 76 if is_hit else uy + 55
        p.append(f'    <line x1="{tpx}" y1="{y_src}" x2="{tpx}" y2="{or_y - 2}" stroke="{col_p}" stroke-width="{"2.2" if is_hit else "1.4"}"{dash_p} marker-end="url(#{"arr-red" if is_hit else "arr-slate"})"/>')
        pw_b = 64 if is_hit else 50
        bx_b = min(tpx - pw_b / 2, lx + lw - 16 - pw_b)
        p.append(f'    <rect x="{bx_b:.1f}" y="{uy + 96}" width="{pw_b}" height="20" rx="4" fill="{"#fef2f2" if is_hit else "#ffffff"}" stroke="{col_p}" stroke-width="1.1"/>')
        p.append(f'    <text x="{bx_b + pw_b / 2:.1f}" y="{uy + 109.5}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="{"#b91c1c" if is_hit else "#475569"}">{tap_lbls[idx_p]}</text>')

    # Big Disjunction OR Bar at bottom of unrolled chain
    p.append(f'    <rect x="{lx + 18}" y="{or_y}" width="{lw - 36}" height="32" rx="7" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>')
    p.append(
        f'    <text x="{lx + lw/2:.1f}" y="{or_y + 20}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#047857">'
        f'⋁{sub("t=0..k")} ¬P(s{sub("t")}) = 1  ⇒  SAT Model Yields Counterexample Trace (i₀, i₁, …, i{sub("k−1")})'
        '</text>'
    )

    # Full BMC Formula Box at bottom of Left Panel
    fb_y = ly + 314
    p.append(f'    <rect x="{lx + 16}" y="{fb_y}" width="{lw - 32}" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.1"/>')
    p.append(f'    <text x="{lx + 28}" y="{fb_y + 19}" font-size="10.8" font-weight="700" fill="#0f172a">Bounded Model Checking Formula Φ{sub("k")} (Biere et al. 1999; Shtrichman CAV 2000):</text>')
    p.append(f'    <text x="{lx + 28}" y="{fb_y + 38}" font-family="{mono}" font-size="10.2" font-weight="700" fill="#1d4ed8">Φ{sub("k")} = I(s₀) ∧ ⋀{sub("t=0..k−1")} T(s{sub("t")}, i{sub("t")}, s{sub("t+1")}) ∧ ⋁{sub("t=0..k")} ¬P(s{sub("t")})</text>')
    p.append(f'    <text x="{lx + 28}" y="{fb_y + 52}" font-size="9.2" fill="#475569">Temporal repetition of T creates strong clause-replication &amp; fan-out hub structure (Deg CV up to 5.28)</text>')

    # ================= RIGHT PANEL: CORPUS SCALE & STRUCTURAL SIGNATURES =================
    rx, ry, rw = 602, 78, 294

    # Card 1: Real IBM & Galileo Corpus Scale (all 13 SAT instances grouped/shown)
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="266" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#0f172a">IBM &amp; Galileo Corpus (13 SAT Files)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 35}" font-size="9.4" fill="#64748b">Vars: 2.8k–63.6k · Clauses: 11.7k–368.4k · 17,125 XORs</text>')

    # Real data from satlib-bmc/README.md sorted by clauses (top 10 + compact tail note or all 13 compact!)
    # All 13 fit cleanly with 15.8px row spacing!
    bmc_rows = [
        ("bmc-ibm-6", 368352, "1,385 XOR", "#2563eb"),
        ("bmc-galileo-9", 326999, "1,162 XOR", "#7c3aed"),
        ("bmc-ibm-10", 323700, "269 XOR", "#2563eb"),
        ("bmc-galileo-8", 294821, "1,066 XOR", "#7c3aed"),
        ("bmc-ibm-12", 194778, "4,724 XOR", "#059669"),
        ("bmc-ibm-11", 150027, "4,465 XOR", "#059669"),
        ("bmc-ibm-4", 139716, "836 XOR", "#2563eb"),
        ("bmc-ibm-3", 72106, "1,344 XOR", "#2563eb"),
        ("bmc-ibm-13", 65728, "1,722 XOR", "#2563eb"),
        ("bmc-ibm-1", 55870, "0 XOR", "#64748b"),
        ("bmc-ibm-5", 41207, "120 XOR", "#2563eb"),
        ("bmc-ibm-7", 39774, "32 XOR", "#2563eb"),
        ("bmc-ibm-2", 11683, "0 XOR", "#64748b"),
    ]
    max_c = 368352
    for i, (nm, cls_n, xstr, col) in enumerate(bmc_rows):
        yy = ry + 52 + i * 16.2
        p.append(f'    <text x="{rx + 12}" y="{yy:.1f}" font-family="{mono}" font-size="8.6" font-weight="600" fill="#0f172a">{nm}</text>')
        bx, bw = rx + 98, 92
        p.append(f'    <rect x="{bx}" y="{yy - 7.5:.1f}" width="{bw}" height="8.5" rx="2" fill="#f1f5f9"/>')
        p.append(f'    <rect x="{bx}" y="{yy - 7.5:.1f}" width="{max(3.0, bw * cls_n / max_c):.1f}" height="8.5" rx="2" fill="{col}" fill-opacity="0.85"/>')
        p.append(f'    <text x="{rx + rw - 54}" y="{yy:.1f}" text-anchor="end" font-size="8.3" fill="#334155">{round(cls_n / 1000)}k c</text>')
        p.append(f'    <text x="{rx + rw - 10}" y="{yy:.1f}" text-anchor="end" font-size="8.1" font-weight="600" fill="{col}">{xstr.replace(" XOR", "x")}</text>')

    # Card 2: Structural Profile
    cy2 = ry + 278
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="107" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">Industrial CNF Structural Profile</text>')
    s_lines = [
        ("Clause Mix:", "72–87% binary · 76–90% Horn · k̄ ≈ 2.6"),
        ("Hub Skew:", "Deg CV = 1.17–5.28 (clock/reset fan-out)"),
        ("XOR Logic:", "17,125 parity gates (ibm-11/12 &gt; 4.4k)"),
        ("Regime:", f'Over (ρ{sub("crit")} = 3.47×–6.33×, κ = 1.74)'),
        ("4 Formats:", "CNF, AIGER (≤838k ANDs), XCNF, ANF"),
    ]
    for i, (k, v) in enumerate(s_lines):
        yy = cy2 + 38 + i * 15.2
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.4" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 84}" y="{yy:.1f}" font-size="9.3" fill="#334155">{v}</text>')

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
