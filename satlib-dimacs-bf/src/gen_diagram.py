#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`satlib-dimacs-bf` (SATLIB Circuit Bridge-Fault Analysis — Van Gelder & Tsuji).

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
    W, H = 920, 478
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Combinational Circuit Bridging Short-Circuit Fault ATPG Miter">',
        "  <defs>",
        '    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>',
        "    </marker>",
        '    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>',
        "    </marker>",
        '    <marker id="arr-grn" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>',
        "    </marker>",
        '    <marker id="arr-amb" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706"/>',
        "    </marker>",
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{font}">',
        # Header
        '    <text x="28" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'SATLIB Circuit Bridging-Fault ATPG (satlib-dimacs-bf)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Wired-AND / Wired-OR internal short-circuit fault miters on ISCAS\'85 (c432, c1355, c2670) · '
        'Van Gelder &amp; Tsuji (Nemesis)</text>',
        '    <rect x="742" y="18" width="152" height="24" rx="12" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>',
        '    <text x="818" y="34" text-anchor="middle" font-size="10.8" font-weight="700" fill="#b91c1c">4 UNSAT · Redundant</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: BRIDGING SHORT-CIRCUIT FAULT MITER =================
    lx, ly, lw, lh = 24, 78, 566, 378
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        f'Bridging Short-Circuit Fault ATPG Miter (Good C vs Bridged C{sub("BF")})</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Seeks an input vector x exciting u(x) ≠ v(x) and propagating the wired-short error to ≥ 1 output</text>'
    )

    # Shared Primary Input Vector x
    ix, iy, iw, ih = lx + 16, ly + 132, 68, 106
    p.append(f'    <rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="8" fill="#ffffff" stroke="#334155" stroke-width="1.5"/>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 26}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0f172a">Test</text>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 40}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0f172a">Vector</text>')
    p.append(f'    <rect x="{ix + 8}" y="{iy + 52}" width="52" height="36" rx="5" fill="#eff6ff" stroke="#2563eb" stroke-width="1.1"/>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 68}" text-anchor="middle" font-family="{mono}" font-size="10" font-weight="700" fill="#1d4ed8">x₁…x{sub("m")}</text>')
    p.append(f'    <text x="{ix + iw/2:.1f}" y="{iy + 81}" text-anchor="middle" font-size="8.4" fill="#475569">(shared)</text>')

    # Branch to Good Circuit C (top) and Bridged Circuit C_BF (bottom)
    cx = lx + 114
    cw = 286
    cy_g, ch_g = ly + 52, 114
    cy_f, ch_f = ly + 186, 132

    p.append(f'    <path d="M {ix + iw} {iy + 30} L {ix + iw + 14} {iy + 30} L {ix + iw + 14} {cy_g + ch_g/2:.1f} L {cx - 2} {cy_g + ch_g/2:.1f}" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arr-grn)"/>')
    p.append(f'    <path d="M {ix + iw} {iy + 76} L {ix + iw + 14} {iy + 76} L {ix + iw + 14} {cy_f + ch_f/2:.1f} L {cx - 2} {cy_f + ch_f/2:.1f}" fill="none" stroke="#dc2626" stroke-width="2" marker-end="url(#arr-red)"/>')

    # --- TOP BOX: Fault-Free Circuit C(x) ---
    p.append(f'    <rect x="{cx}" y="{cy_g}" width="{cw}" height="{ch_g}" rx="9" fill="#ecfdf5" stroke="#059669" stroke-width="1.4"/>')
    p.append(f'    <text x="{cx + 12}" y="{cy_g + 19}" font-size="11.2" font-weight="700" fill="#047857">Fault-Free Circuit C(x) — Independent Nets u, v</text>')

    # Upstream & downstream logic cones in Good circuit
    p.append(f'    <rect x="{cx + 14}" y="{cy_g + 32}" width="66" height="68" rx="6" fill="#ffffff" stroke="#059669" stroke-width="1.2"/>')
    p.append(f'    <text x="{cx + 47}" y="{cy_g + 62}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Input</text>')
    p.append(f'    <text x="{cx + 47}" y="{cy_g + 75}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Cone</text>')

    p.append(f'    <rect x="{cx + 202}" y="{cy_g + 32}" width="70" height="68" rx="6" fill="#ffffff" stroke="#059669" stroke-width="1.2"/>')
    p.append(f'    <text x="{cx + 237}" y="{cy_g + 62}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Output</text>')
    p.append(f'    <text x="{cx + 237}" y="{cy_g + 75}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Logic</text>')

    # Two parallel independent wires u and v
    u_yg, v_yg = cy_g + 48, cy_g + 84
    p.append(f'    <line x1="{cx + 80}" y1="{u_yg}" x2="{cx + 200}" y2="{u_yg}" stroke="#059669" stroke-width="2.2" marker-end="url(#arr-grn)"/>')
    p.append(f'    <line x1="{cx + 80}" y1="{v_yg}" x2="{cx + 200}" y2="{v_yg}" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arr-blue)"/>')
    p.append(f'    <rect x="{cx + 114}" y="{u_yg - 11}" width="54" height="16" rx="4" fill="#ffffff" stroke="#a7f3d0" stroke-width="1"/>')
    p.append(f'    <text x="{cx + 141}" y="{u_yg + 0.5}" text-anchor="middle" font-family="{mono}" font-size="9" font-weight="700" fill="#047857">net u = 1</text>')
    p.append(f'    <rect x="{cx + 114}" y="{v_yg - 11}" width="54" height="16" rx="4" fill="#ffffff" stroke="#bfdbfe" stroke-width="1"/>')
    p.append(f'    <text x="{cx + 141}" y="{v_yg + 0.5}" text-anchor="middle" font-family="{mono}" font-size="9" font-weight="700" fill="#1d4ed8">net v = 0</text>')

    # --- BOTTOM BOX: Bridged-Fault Circuit C_BF(x) ---
    p.append(f'    <rect x="{cx}" y="{cy_f}" width="{cw}" height="{ch_f}" rx="9" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>')
    p.append(f'    <text x="{cx + 12}" y="{cy_f + 19}" font-size="11.2" font-weight="700" fill="#b91c1c">Faulty Circuit C{sub("BF")}(x) — Short-Circuit Bridge (u, v)</text>')

    p.append(f'    <rect x="{cx + 14}" y="{cy_f + 32}" width="66" height="72" rx="6" fill="#ffffff" stroke="#dc2626" stroke-width="1.2"/>')
    p.append(f'    <text x="{cx + 47}" y="{cy_f + 64}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Input</text>')
    p.append(f'    <text x="{cx + 47}" y="{cy_f + 77}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Cone</text>')

    p.append(f'    <rect x="{cx + 202}" y="{cy_f + 32}" width="70" height="72" rx="6" fill="#ffffff" stroke="#dc2626" stroke-width="1.2"/>')
    p.append(f'    <text x="{cx + 237}" y="{cy_f + 64}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Output</text>')
    p.append(f'    <text x="{cx + 237}" y="{cy_f + 77}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#0f172a">Logic</text>')

    # Wires entering wired-AND/OR short-circuit bridge node!
    u_yf, v_yf = cy_f + 48, cy_f + 88
    bx_m, by_m = cx + 141, cy_f + 68
    p.append(f'    <line x1="{cx + 80}" y1="{u_yf}" x2="{bx_m - 26}" y2="{u_yf}" stroke="#475569" stroke-width="2"/>')
    p.append(f'    <line x1="{cx + 80}" y1="{v_yf}" x2="{bx_m - 26}" y2="{v_yf}" stroke="#475569" stroke-width="2"/>')
    # Short-circuit bridge vertical red lightning/short box
    p.append(f'    <rect x="{bx_m - 30}" y="{u_yf - 9}" width="60" height="{v_yf - u_yf + 18}" rx="7" fill="#dc2626" stroke="#991b1b" stroke-width="1.4"/>')
    p.append(f'    <text x="{bx_m}" y="{by_m - 6}" text-anchor="middle" font-size="9.2" font-weight="800" fill="#ffffff">SHORT</text>')
    p.append(f'    <text x="{bx_m}" y="{by_m + 7}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="#fef2f2">u′=v′=</text>')
    p.append(f'    <text x="{bx_m}" y="{by_m + 18}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="#fef2f2">u∧v / u∨v</text>')

    # Faulty propagated outputs u', v'
    p.append(f'    <line x1="{bx_m + 30}" y1="{u_yf}" x2="{cx + 200}" y2="{u_yf}" stroke="#dc2626" stroke-width="2.2" marker-end="url(#arr-red)"/>')
    p.append(f'    <line x1="{bx_m + 30}" y1="{v_yf}" x2="{cx + 200}" y2="{v_yf}" stroke="#dc2626" stroke-width="2.2" marker-end="url(#arr-red)"/>')
    p.append(f'    <text x="{cx + 186}" y="{u_yf - 6}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="#b91c1c">u′!</text>')
    p.append(f'    <text x="{cx + 186}" y="{v_yf + 12}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="#b91c1c">v′!</text>')

    # Excitation callout pill at bottom of C_BF (comfortable padding inside red box!)
    p.append(f'    <text x="{cx + cw/2:.1f}" y="{cy_f + 122}" text-anchor="middle" font-size="8.7" font-weight="700" fill="#b91c1c">Excitation: u(x) ⊕ v(x) = 1 (opposite drive strengths collide)</text>')

    # --- RIGHT SIDE OF LEFT PANEL: OUTPUT MITER XOR + OR ---
    mx_x = lx + 448
    xor_ys = [ly + 114, ly + 168, ly + 228]
    for idx_m, xy in enumerate(xor_ys):
        yg_o = cy_g + 46 + idx_m * 22
        yf_o = cy_f + 46 + idx_m * 24
        p.append(f'    <path d="M {cx + cw} {yg_o} C {mx_x - 24} {yg_o}, {mx_x - 24} {xy - 4}, {mx_x - 14} {xy - 4}" fill="none" stroke="#059669" stroke-width="1.4"/>')
        p.append(f'    <path d="M {cx + cw} {yf_o} C {mx_x - 24} {yf_o}, {mx_x - 24} {xy + 4}, {mx_x - 14} {xy + 4}" fill="none" stroke="#dc2626" stroke-width="1.4"/>')
        p.append(f'    <circle cx="{mx_x}" cy="{xy}" r="12.5" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>')
        p.append(f'    <text x="{mx_x}" y="{xy + 4.5}" text-anchor="middle" font-size="13" font-weight="700" fill="#b45309">⊕</text>')

    # Big OR output badge
    or_x, or_y = lx + 516, ly + 170
    for xy in xor_ys:
        p.append(f'    <path d="M {mx_x + 12.5} {xy} C {mx_x + 34} {xy}, {or_x - 32} {or_y}, {or_x - 22} {or_y}" fill="none" stroke="#d97706" stroke-width="1.5"/>')
    p.append(f'    <rect x="{or_x - 22}" y="{or_y - 24}" width="48" height="48" rx="9" fill="#fef2f2" stroke="#dc2626" stroke-width="1.6"/>')
    p.append(f'    <text x="{or_x + 2}" y="{or_y - 3}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#b91c1c">⋁ OR</text>')
    p.append(f'    <text x="{or_x + 2}" y="{or_y + 13}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#dc2626">= 1</text>')

    # Bottom Verdict Banner inside Left Panel
    vb_y = ly + 332
    p.append(f'    <rect x="{lx + 16}" y="{vb_y}" width="{lw - 32}" height="34" rx="7" fill="#ffffff" stroke="#dc2626" stroke-width="1.2"/>')
    p.append(
        f'    <text x="{lx + lw/2:.1f}" y="{vb_y + 21}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#0f172a">'
        'All 4 SATLIB BF Benchmarks Are <tspan fill="#dc2626">UNSAT</tspan>: Reconvergent Fan-Out Masks the Short (Undetectable Fault)'
        '</text>'
    )

    # ================= RIGHT PANEL: ALL 4 INSTANCES & ENCODING PROFILE =================
    rx, ry, rw = 604, 78, 292

    # Card 1: All 4 Instances (ISCAS'85 Circuits)
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="218" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#0f172a">All 4 Nemesis BF Instances (UNSAT)</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 36}" font-size="9.4" fill="#64748b">ISCAS\'85 combinational benchmarks · 2nd DIMACS Challenge</text>')

    bf_insts = [
        ("bf0432-007", "c432 (27-ch interrupt ctrl)", "1,040 v · 3,668 c · 6 XOR", 0.54, "#2563eb"),
        ("bf1355-075", "c1355 (32-bit SEC circuit)", "2,180 v · 6,778 c · 0 XOR", 1.00, "#dc2626"),
        ("bf1355-638", "c1355 (32-bit SEC circuit)", "2,177 v · 6,768 c · 0 XOR", 1.00, "#dc2626"),
        ("bf2670-001", "c2670 (12-bit ALU &amp; ctrl)", "1,393 v · 3,434 c · 22 XOR", 0.51, "#7c3aed"),
    ]
    for i, (nm, desc, stat, frac, col) in enumerate(bf_insts):
        yy = ry + 50 + i * 40
        p.append(f'    <rect x="{rx + 10}" y="{yy}" width="{rw - 20}" height="35" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + 18}" y="{yy + 14}" font-family="{mono}" font-size="9.6" font-weight="700" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{rx + rw - 18}" y="{yy + 14}" text-anchor="end" font-size="8.6" font-weight="700" fill="#b91c1c">UNSAT</text>')
        p.append(f'    <text x="{rx + 18}" y="{yy + 27}" font-size="8.6" fill="#475569">{desc} · {stat}</text>')

    # Card 2: Nemesis 6-CNF Structural Profile
    cy2 = ry + 230
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="148" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 21}" font-size="12" font-weight="700" fill="#0f172a">Nemesis 6-CNF Encoding Profile</text>')
    s_lines = [
        ("Clause Width:", f'k̄ = 2.33–2.61 (k{sub("max")} = 5–6)'),
        ("Binary / Horn:", "49–73% binary · 72–75% Horn"),
        ("Phase Regime:", f'Over (ρ{sub("crit")} = 1.94×–2.11×, κ = 0.96)'),
        ("Degree Skew:", "Deg CV = 0.47–0.77 (moderate fan-out)"),
        ("Native XORs:", "28 extracted total (c432 + c2670)"),
        ("CDCL Speed:", "All 4 closed in 5–29 ms on 1 core"),
    ]
    for i, (k, v) in enumerate(s_lines):
        yy = cy2 + 41 + i * 17.5
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.5" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 92}" y="{yy:.1f}" font-size="9.4" fill="#334155">{v}</text>')

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
