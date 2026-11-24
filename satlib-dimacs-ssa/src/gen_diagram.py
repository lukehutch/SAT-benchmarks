#!/usr/bin/env python3
"""Generate a standalone illustrative SVG diagram (`diagram.svg`) for
`satlib-dimacs-ssa` (SATLIB Single-Stuck-At Circuit Faults — Van Gelder & Tsuji).

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
    W, H = 920, 488
    font = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Single-Stuck-At Circuit Fault ATPG and D-Calculus Propagation Miter">',
        "  <defs>",
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
        'SATLIB Single-Stuck-At Circuit Fault ATPG (satlib-dimacs-ssa)</text>',
        '    <text x="28" y="53" font-size="11.8" fill="#475569">'
        'Larrabee / Nemesis D-calculus fault-activation &amp; propagation miters on ISCAS\'85 '
        '(c432, c2670, c6288, c7552)</text>',
        '    <rect x="752" y="18" width="142" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="823" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">4 SAT · 4 UNSAT</text>',
        '    <line x1="24" y1="65" x2="896" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: SINGLE-STUCK-AT D-PROPAGATION CIRCUIT =================
    lx, ly, lw, lh = 24, 78, 562, 388
    p.append(
        f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 22}" font-size="13" font-weight="700" fill="#0f172a">'
        'ATPG Fault Activation &amp; D-Calculus Propagation (Wire w Stuck-At-0)</text>'
    )
    p.append(
        f'    <text x="{lx + 16}" y="{ly + 38}" font-size="10.4" fill="#475569">'
        'Composite Roth signal D = (good=1 / faulty=0), D̄ = (0/1) propagates via non-controlling side inputs</text>'
    )

    # Gate-level canvas inside Left Panel
    gy0 = ly + 50
    p.append(f'    <rect x="{lx + 14}" y="{gy0}" width="{lw - 28}" height="214" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.2"/>')

    # Stage phase headers across top of gate canvas
    p.append(f'    <rect x="{lx + 24}" y="{gy0 + 8}" width="154" height="20" rx="4" fill="#eff6ff"/>')
    p.append(f'    <text x="{lx + 101}" y="{gy0 + 21.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1d4ed8">1. Fault Activation (Justify)</text>')
    p.append(f'    <rect x="{lx + 190}" y="{gy0 + 8}" width="214" height="20" rx="4" fill="#fef2f2"/>')
    p.append(f'    <text x="{lx + 297}" y="{gy0 + 21.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#b91c1c">2. Path Sensitization (D-Chain)</text>')
    p.append(f'    <rect x="{lx + 416}" y="{gy0 + 8}" width="118" height="20" rx="4" fill="#ecfdf5"/>')
    p.append(f'    <text x="{lx + 475}" y="{gy0 + 21.5}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#047857">3. Observe (Miter)</text>')

    # Primary Inputs on far left: x1=1, x2=1, x3=1 (non-ctrl for NAND), x4=0 (non-ctrl for OR)
    px_in = lx + 46
    in_specs = [
        (gy0 + 62, "x₁ = 1", "#1d4ed8", "#eff6ff", "#2563eb"),
        (gy0 + 98, "x₂ = 1", "#1d4ed8", "#eff6ff", "#2563eb"),
        (gy0 + 144, "x₃ = 1", "#047857", "#ecfdf5", "#059669"),
        (gy0 + 186, "x₄ = 0", "#047857", "#ecfdf5", "#059669"),
    ]
    for iy, ilbl, tc, bg, st in in_specs:
        p.append(f'    <rect x="{px_in - 24}" y="{iy - 11}" width="48" height="22" rx="5" fill="{bg}" stroke="{st}" stroke-width="1.2"/>')
        p.append(f'    <text x="{px_in}" y="{iy + 3.5}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="{tc}">{ilbl}</text>')

    # Gate 1: AND(x1, x2) -> wire w (good=1)
    g1x, g1y = lx + 128, gy0 + 80
    p.append(f'    <line x1="{px_in + 24}" y1="{in_specs[0][0]}" x2="{g1x - 28}" y2="{g1y - 8}" stroke="#2563eb" stroke-width="1.8" marker-end="url(#arr-slate)"/>')
    p.append(f'    <line x1="{px_in + 24}" y1="{in_specs[1][0]}" x2="{g1x - 28}" y2="{g1y + 8}" stroke="#2563eb" stroke-width="1.8" marker-end="url(#arr-slate)"/>')
    p.append(f'    <rect x="{g1x - 26}" y="{g1y - 20}" width="52" height="40" rx="7" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>')
    p.append(f'    <text x="{g1x}" y="{g1y + 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1d4ed8">AND</text>')

    # Wire w exits Gate 1 -> Fault Injection Site (s-a-0) -> D = 1/0 -> Gate 2 (NAND)
    fx_s, fy_s = lx + 214, g1y
    g2x, g2y = lx + 296, gy0 + 104
    p.append(f'    <line x1="{g1x + 26}" y1="{g1y}" x2="{fx_s - 22}" y2="{fy_s}" stroke="#2563eb" stroke-width="2"/>')
    p.append(f'    <text x="{(g1x + 26 + fx_s - 22)/2:.1f}" y="{g1y - 7}" text-anchor="middle" font-family="{mono}" font-size="8.6" font-weight="700" fill="#1d4ed8">w=1</text>')

    # Fault Injection Badge: s-a-0
    p.append(f'    <rect x="{fx_s - 22}" y="{fy_s - 15}" width="44" height="30" rx="6" fill="#dc2626" stroke="#991b1b" stroke-width="1.4"/>')
    p.append(f'    <text x="{fx_s}" y="{fy_s - 1}" text-anchor="middle" font-size="8.5" font-weight="800" fill="#ffffff">s-a-0</text>')
    p.append(f'    <text x="{fx_s}" y="{fy_s + 10}" text-anchor="middle" font-family="{mono}" font-size="8.4" font-weight="700" fill="#fef2f2">D=1/0</text>')

    # Active Fault Path (glowing thick red line) from s-a-0 -> NAND -> OR -> Miter Output
    p.append(f'    <path d="M {fx_s + 22} {fy_s} C {fx_s + 42} {fy_s}, {g2x - 42} {g2y - 9}, {g2x - 30} {g2y - 9}" fill="none" stroke="#dc2626" stroke-width="2.6" marker-end="url(#arr-red)"/>')

    # Side input x3=1 (non-controlling for NAND) -> Gate 2
    p.append(f'    <path d="M {px_in + 24} {in_specs[2][0]} L {g2x - 54} {in_specs[2][0]} L {g2x - 30} {g2y + 10}" fill="none" stroke="#059669" stroke-width="1.8" stroke-dasharray="4,2" marker-end="url(#arr-grn)"/>')
    p.append(f'    <text x="{lx + 178}" y="{in_specs[2][0] - 6}" text-anchor="middle" font-size="8.6" font-weight="600" fill="#047857">non-ctrl side input (1)</text>')

    # Gate 2: NAND(D, 1) -> D̄ = 0/1
    p.append(f'    <rect x="{g2x - 28}" y="{g2y - 20}" width="56" height="40" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>')
    p.append(f'    <text x="{g2x}" y="{g2y + 4}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#b91c1c">NAND</text>')
    p.append(f'    <circle cx="{g2x + 32}" cy="{g2y}" r="4" fill="#ffffff" stroke="#dc2626" stroke-width="1.5"/>')

    # Gate 3: OR(D̄, 0) -> D̄ = 0/1
    g3x, g3y = lx + 394, gy0 + 132
    p.append(f'    <path d="M {g2x + 36} {g2y} C {g2x + 52} {g2y}, {g3x - 44} {g3y - 9}, {g3x - 28} {g3y - 9}" fill="none" stroke="#dc2626" stroke-width="2.6" marker-end="url(#arr-red)"/>')
    p.append(f'    <rect x="{(g2x + g3x)/2 - 18:.1f}" y="{g2y - 21}" width="44" height="16" rx="4" fill="#fffbeb" stroke="#d97706" stroke-width="1"/>')
    p.append(f'    <text x="{(g2x + g3x)/2 + 4:.1f}" y="{g2y - 10}" text-anchor="middle" font-family="{mono}" font-size="8.8" font-weight="700" fill="#b45309">D̄=0/1</text>')

    # Side input x4=0 (non-controlling for OR) -> Gate 3
    p.append(f'    <path d="M {px_in + 24} {in_specs[3][0]} L {g3x - 58} {in_specs[3][0]} L {g3x - 28} {g3y + 10}" fill="none" stroke="#059669" stroke-width="1.8" stroke-dasharray="4,2" marker-end="url(#arr-grn)"/>')
    p.append(f'    <text x="{lx + 226}" y="{in_specs[3][0] - 6}" text-anchor="middle" font-size="8.6" font-weight="600" fill="#047857">non-ctrl side input (0)</text>')

    p.append(f'    <rect x="{g3x - 26}" y="{g3y - 20}" width="52" height="40" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>')
    p.append(f'    <text x="{g3x}" y="{g3y + 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#b91c1c">OR</text>')

    # Output Observation Miter Box
    ox, oy = lx + 482, g3y
    p.append(f'    <line x1="{g3x + 26}" y1="{g3y}" x2="{ox - 42}" y2="{oy}" stroke="#dc2626" stroke-width="2.6" marker-end="url(#arr-red)"/>')
    p.append(f'    <rect x="{ox - 40}" y="{oy - 28}" width="82" height="56" rx="8" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>')
    p.append(f'    <text x="{ox + 1}" y="{oy - 8}" text-anchor="middle" font-family="{mono}" font-size="9.5" font-weight="700" fill="#047857">y ⊕ y{sup("f")} = 1</text>')
    p.append(f'    <text x="{ox + 1}" y="{oy + 7}" text-anchor="middle" font-size="9" font-weight="700" fill="#b91c1c">Output D̄!</text>')
    p.append(f'    <text x="{ox + 1}" y="{oy + 21}" text-anchor="middle" font-size="8.4" fill="#334155">Detected</text>')

    # Bottom dual SAT vs UNSAT ATPG Interpretation Cards inside Left Panel
    vy = ly + 276
    p.append(f'    <rect x="{lx + 14}" y="{vy}" width="260" height="96" rx="8" fill="#ecfdf5" stroke="#059669" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 26}" y="{vy + 19}" font-size="11.2" font-weight="700" fill="#047857">SAT ⇒ Detectable Fault (Test Pattern)</text>')
    p.append(f'    <text x="{lx + 26}" y="{vy + 37}" font-size="9.6" fill="#334155">• Satisfying model x* activates s-a-0/1</text>')
    p.append(f'    <text x="{lx + 26}" y="{vy + 53}" font-size="9.6" fill="#334155">  and propagates D/D̄ to a primary output</text>')
    p.append(f'    <text x="{lx + 26}" y="{vy + 69}" font-size="9.6" fill="#334155">• Used in chip silicon manufacturing test</text>')
    p.append(f'    <text x="{lx + 26}" y="{vy + 86}" font-size="9.4" font-weight="700" fill="#047857">4 SAT instances: ssa7552-{ "{038,158,159,160}" }</text>')

    p.append(f'    <rect x="{lx + 286}" y="{vy}" width="262" height="96" rx="8" fill="#fef2f2" stroke="#dc2626" stroke-width="1.3"/>')
    p.append(f'    <text x="{lx + 298}" y="{vy + 19}" font-size="11.2" font-weight="700" fill="#b91c1c">UNSAT ⇒ Redundant / Untestable Fault</text>')
    p.append(f'    <text x="{lx + 298}" y="{vy + 37}" font-size="9.6" fill="#334155">• No vector x can simultaneously justify</text>')
    p.append(f'    <text x="{lx + 298}" y="{vy + 53}" font-size="9.6" fill="#334155">  and sensitize wire w to any output y{sub("j")}</text>')
    p.append(f'    <text x="{lx + 298}" y="{vy + 69}" font-size="9.6" fill="#334155">• Enables redundancy removal in synthesis</text>')
    p.append(f'    <text x="{lx + 298}" y="{vy + 86}" font-size="9.4" font-weight="700" fill="#b91c1c">4 UNSAT: c432, c2670 (×2), c6288 (16×16)</text>')

    # ================= RIGHT PANEL: ALL 8 INSTANCES & D-CALCULUS ENCODING =================
    rx, ry, rw = 602, 78, 294

    # Card 1: All 8 Nemesis ISCAS'85 SSA Instances
    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="258" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12" font-weight="700" fill="#0f172a">All 8 ISCAS\'85 SSA Benchmarks</text>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 35}" font-size="9.4" fill="#64748b">Vars: 435–10,410 · Clauses: 1,027–34,238 · 92 XORs</text>')

    ssa_rows = [
        ("ssa0432-003", "c432", "435 v · 1,027 c", "UNSAT", "#dc2626", "#fef2f2"),
        ("ssa2670-130", "c2670", "1,359 v · 3,321 c", "UNSAT", "#dc2626", "#fef2f2"),
        ("ssa2670-141", "c2670", "986 v · 2,315 c", "UNSAT", "#dc2626", "#fef2f2"),
        ("ssa6288-047", "c6288", "10,410 v · 34.2k c", "UNSAT", "#dc2626", "#fef2f2"),
        ("ssa7552-038", "c7552", "1,501 v · 3,575 c", "SAT", "#059669", "#ecfdf5"),
        ("ssa7552-158", "c7552", "1,363 v · 3,034 c", "SAT", "#059669", "#ecfdf5"),
        ("ssa7552-159", "c7552", "1,363 v · 3,032 c", "SAT", "#059669", "#ecfdf5"),
        ("ssa7552-160", "c7552", "1,391 v · 3,126 c", "SAT", "#059669", "#ecfdf5"),
    ]
    for i, (nm, ckt, dim, verd, col, bg) in enumerate(ssa_rows):
        yy = ry + 48 + i * 25.5
        p.append(f'    <rect x="{rx + 10}" y="{yy:.1f}" width="{rw - 20}" height="21.5" rx="4.5" fill="#f8fafc" stroke="#e2e8f0" stroke-width="0.8"/>')
        p.append(f'    <text x="{rx + 17}" y="{yy + 14:.1f}" font-family="{mono}" font-size="8.9" font-weight="700" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{rx + 100}" y="{yy + 14:.1f}" font-size="8.5" fill="#475569">{dim}</text>')
        p.append(f'    <rect x="{rx + rw - 54}" y="{yy + 3.5:.1f}" width="38" height="14.5" rx="7" fill="{bg}" stroke="{col}" stroke-width="0.9"/>')
        p.append(f'    <text x="{rx + rw - 35}" y="{yy + 13.5:.1f}" text-anchor="middle" font-size="8.1" font-weight="700" fill="{col}">{verd}</text>')

    # Card 2: Nemesis / Larrabee CNF Encoding Anatomy
    cy2 = ry + 270
    p.append(f'    <rect x="{rx}" y="{cy2}" width="{rw}" height="118" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{cy2 + 20}" font-size="12" font-weight="700" fill="#0f172a">Larrabee / Nemesis CNF Encoding</text>')
    s_lines = [
        ("Fault Cone:", "Duplicates only gates reachable from wire w"),
        ("Active Flag:", f'a{sub("g")} ⇒ (g ≠ g{sup("f")}) ∧ ⋁{sub("h∈out(g)")} a{sub("h")}'),
        ("Clause Mix:", "52–80% binary · 72–80% Horn · k̄ ≈ 2.3"),
        ("Regime:", f'Over (ρ{sub("crit")} = 1.84×–2.04×, κ = 0.84)'),
        ("Benchmarks:", "c6288 is a 16×16 array multiplier (34k cls)"),
    ]
    for i, (k, v) in enumerate(s_lines):
        yy = cy2 + 39 + i * 15.8
        p.append(f'    <text x="{rx + 14}" y="{yy:.1f}" font-size="9.4" font-weight="700" fill="#1d4ed8">{esc(k)}</text>')
        p.append(f'    <text x="{rx + 84}" y="{yy:.1f}" font-size="9.2" fill="#334155">{v}</text>')

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
