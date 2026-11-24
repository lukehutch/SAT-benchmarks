#!/usr/bin/env python3
"""Generate bespoke illustrative SVG (`diagram.svg`) for `picat-mapf`
(Multi-Agent Path Finding — Makespan via Picat-SAT `mapf_makespan.pi`).

Standalone Python 3 stdlib only. Writes `../diagram.svg` and validates XML.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"
FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_svg() -> str:
    W, H = 940, 504
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'role="img" aria-label="Picat-SAT Multi-Agent Path Finding Makespan Bottleneck Grid and Chen-AMO Encoding">',
        "  <defs>",
        '    <marker id="arr-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>',
        '    <marker id="arr-r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/></marker>',
        '    <marker id="arr-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/></marker>',
        "  </defs>",
        f'  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'  <g font-family="{FONT_SANS}">',
        '    <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'Multi-Agent Path Finding — Makespan (picat-mapf)</text>',
        '    <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Picat 3.9#12 SAT compilation of Barták &amp; Zhou (ICTAI′17) mapf_makespan.pi (MPL-2.0) · '
        'Spacetime reachability pruning + Chen 2-product AMO</text>',
        '    <rect x="780" y="18" width="136" height="24" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>',
        '    <text x="848" y="34" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">6 SAT · 2 UNSAT</text>',
        '    <line x1="24" y1="65" x2="916" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # ================= LEFT PANEL: 9x9 TWO-ROOM DOORWAY BOTTLENECK =================
    lx, ly, lw, lh = 24, 78, 444, 404
    p.append(f'    <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 23}" font-size="13" font-weight="700" fill="#0f172a">1. Bottleneck Grid (mapf_bn9x9_k12: LB=16, M*=19)</text>')
    p.append(f'    <text x="{lx + 16}" y="{ly + 39}" font-size="10.2" fill="#475569">12 agents swap rooms through single gate (4,4) ⇒ M=18 UNSAT, M=19 SAT</text>')

    # 9x9 grid
    gx0, gy0, cell = lx + 30, ly + 56, 28
    for r in range(9):
        for c in range(9):
            cx = gx0 + c * cell
            cy = gy0 + r * cell
            is_wall = (c == 4 and r != 4)
            is_gate = (c == 4 and r == 4)
            if is_wall:
                fill, st = "#334155", "#1e293b"
            elif is_gate:
                fill, st = "#fef3c7", "#d97706"
            else:
                fill, st = "#ffffff", "#cbd5e1"
            p.append(f'    <rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" fill="{fill}" stroke="{st}" stroke-width="1.1"/>')

    def ctr(r: int, c: int) -> tuple[float, float]:
        return gx0 + c * cell + cell / 2.0, gy0 + r * cell + cell / 2.0

    # Sample trajectories through the single-cell gate
    traj_specs = [
        ([(0, 0), (0, 2), (4, 2), (4, 4), (4, 6), (0, 6), (0, 8)], "#2563eb", "arr-b", 0, -4),
        ([(8, 8), (8, 6), (4, 6), (4, 4), (4, 2), (8, 2), (8, 0)], "#dc2626", "arr-r", 0, 4),
        ([(2, 1), (4, 1), (4, 4), (4, 7), (2, 7)], "#059669", "arr-g", 0, 0),
    ]
    for pts_rc, col, mk, ox, oy in traj_specs:
        d_cmds = []
        for idx, (r, c) in enumerate(pts_rc):
            x, y = ctr(r, c)
            d_cmds.append(("M" if idx == 0 else "L") + f" {x + ox:.1f} {y + oy:.1f}")
        p.append(f'    <path d="{" ".join(d_cmds)}" fill="none" stroke="{col}" stroke-width="2.1" opacity="0.82" marker-end="url(#{mk})"/>')

    # Crisp GATE pill badge positioned cleanly on the wall cell directly above (4,4) so paths never obscure it
    gxc, gyc = ctr(3, 4)
    p.append(f'    <rect x="{gxc - 18:.1f}" y="{gyc - 8:.1f}" width="36" height="16" rx="4" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>')
    p.append(f'    <text x="{gxc:.1f}" y="{gyc + 3.2:.1f}" text-anchor="middle" font-size="8.2" font-weight="700" fill="#b45309">GATE</text>')

    # Agent start badges (6 left-to-right blue, 6 right-to-left red)
    left_starts = [(0, 0, "A1"), (2, 1, "A3"), (4, 1, "A5"), (4, 2, "A11"), (6, 1, "A7"), (8, 0, "A9")]
    right_starts = [(0, 8, "A2"), (2, 7, "A4"), (4, 7, "A6"), (4, 6, "A12"), (6, 7, "A8"), (8, 8, "A10")]
    for r, c, lbl in left_starts:
        x, y = ctr(r, c)
        p.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="9.5" fill="#2563eb" stroke="#ffffff" stroke-width="1.3"/>')
        p.append(f'    <text x="{x:.1f}" y="{y + 3:.1f}" text-anchor="middle" font-size="7.4" font-weight="700" fill="#ffffff">{lbl}</text>')
    for r, c, lbl in right_starts:
        x, y = ctr(r, c)
        p.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="9.5" fill="#dc2626" stroke="#ffffff" stroke-width="1.3"/>')
        p.append(f'    <text x="{x:.1f}" y="{y + 3:.1f}" text-anchor="middle" font-size="7.4" font-weight="700" fill="#ffffff">{lbl}</text>')

    # Side callout next to 9x9 grid
    sx0 = gx0 + 9 * cell + 14
    p.append(f'    <rect x="{sx0}" y="{gy0}" width="{lx + lw - sx0 - 14}" height="{9 * cell}" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{sx0 + 10}" y="{gy0 + 19}" font-size="9.8" font-weight="700" fill="#0f172a">Collision Queuing</text>')
    qnotes = [
        ("Individual LB:", "#475569", False),
        ("  max dist = 16", "#1e3a8a", True),
        ("Gate capacity:", "#475569", False),
        ("  ≤ 1 agent / step", "#b45309", True),
        ("12 crossings force", "#475569", False),
        ("queuing delay +3:", "#475569", False),
        ("  M = 18: UNSAT", "#b91c1c", True),
        ("  M*= 19: SAT", "#047857", True),
        ("", "#475569", False),
        ("All agents can", "#475569", False),
        ("reach goal alone", "#475569", False),
        ("at M=18; only", "#475569", False),
        ("vertex AMO makes", "#475569", False),
        ("M=18 infeasible.", "#475569", False),
    ]
    for i, (txt, col, mono) in enumerate(qnotes):
        p.append(
            f'    <text x="{sx0 + 10}" y="{gy0 + 38 + i * 15}" '
            f'{"font-family=\"" + FONT_MONO + "\" " if mono else ""}'
            f'font-size="8.6" font-weight="{"700" if mono else "400"}" fill="{col}">{esc(txt)}</text>'
        )

    # Bottom spacetime reachability box in left panel
    by = ly + 322
    p.append(f'    <rect x="{lx + 14}" y="{by}" width="{lw - 28}" height="68" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    p.append(f'    <text x="{lx + 24}" y="{by + 18}" font-size="10" font-weight="700" fill="#0f172a">Spacetime Reachability Pruning (B[t, a, v] ∈ {{0, 1}},  t ∈ 1..M+1):</text>')
    p.append(f'    <text x="{lx + 24}" y="{by + 36}" font-family="{FONT_MONO}" font-size="8.8" fill="#1e3a8a">'
             'dist(start_a, v) &gt; t−1  ∨  dist(v, goal_a) &gt; M+1−t  ⇒  B[t,a,v] = 0</text>')
    p.append(f'    <text x="{lx + 24}" y="{by + 54}" font-size="9" fill="#475569">'
             'Eliminates unreachable spacetime vertices before Picat compiles EO/AMO/transition clauses.</text>')

    # ================= RIGHT PANEL: ENCODING + 8-INSTANCE TABLE =================
    rx, ry, rw = 484, 78, 432

    p.append(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="148" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ry + 21}" font-size="12.2" font-weight="700" fill="#0f172a">2. Barták–Zhou ICTAI′17 Boolean Model</text>')
    clauses = [
        ("Exactly-One location per agent &amp; step", "Σ_v B[t,a,v] = 1  (ALO + Chen 2-product AMO)", "#eff6ff", "#93c5fd", "#1e3a8a"),
        ("No vertex collision (at most 1 agent/cell)", "Σ_a B[t,a,v] ≤ 1  (sparse Chen 2-product AMO)", "#fef2f2", "#fca5a5", "#991b1b"),
        ("Valid 4-neighbor / wait transition", "B[t,a,v] ⇒ ⋁_{u ∈ N(v)∪{v}} B[t+1,a,u]  (length ≤ 6)", "#ecfdf5", "#6ee7b7", "#065f46"),
    ]
    for idx, (t1, t2, bg, bd, fg) in enumerate(clauses):
        yy = ry + 32 + idx * 36
        p.append(f'    <rect x="{rx + 14}" y="{yy}" width="{rw - 28}" height="30" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 12.5}" font-size="9.2" font-weight="700" fill="{fg}">{t1}</text>')
        p.append(f'    <text x="{rx + 22}" y="{yy + 24.5}" font-family="{FONT_MONO}" font-size="8.2" fill="#475569">{esc(t2)}</text>')

    ty = ry + 160
    th = 244
    p.append(f'    <rect x="{rx}" y="{ty}" width="{rw}" height="{th}" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'    <text x="{rx + 14}" y="{ty + 21}" font-size="12.2" font-weight="700" fill="#0f172a">3. Curated 8-Instance MAPF Suite (9×9 .. 32×32)</text>')

    hdrs = ["Instance", "Grid / K", "M (LB)", "Verdict", "Vars / Cls"]
    xs = [rx + 14, rx + 188, rx + 258, rx + 314, rx + 418]
    p.append(f'    <rect x="{rx + 10}" y="{ty + 30}" width="{rw - 20}" height="20" rx="4" fill="#f1f5f9"/>')
    for idx, (h, x) in enumerate(zip(hdrs, xs)):
        anc = "end" if idx == 4 else ("middle" if idx in (1, 2, 3) else "start")
        p.append(f'    <text x="{x}" y="{ty + 43.5}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{h}</text>')

    rows = [
        ("mapf_bn9x9_k12_m18", "9×9 / 12", "18 (16)", "UNSAT", "6.0k / 28.6k"),
        ("mapf_bn9x9_k12_m19", "9×9 / 12", "19 (16)", "SAT", "7.0k / 34.3k"),
        ("mapf_bn11x11_k18_m24", "11×11 / 18", "24 (20)", "UNSAT", "19.3k / 100k"),
        ("mapf_bn11x11_k18_m25", "11×11 / 18", "25 (20)", "SAT", "21.9k / 113k"),
        ("mapf_g16_p10_a10_m19", "16×16 / 10", "19 (19)", "SAT", "6.6k / 23.5k"),
        ("mapf_g16_p20_a20_m23", "16×16 / 20", "23 (23)", "SAT", "17.7k / 83.9k"),
        ("mapf_g16_p20_a40_m22", "16×16 / 40", "22 (22)", "SAT", "40.5k / 206k"),
        ("mapf_32x32_k30_m43", "32×32 / 30", "43 (43)", "SAT", "188k / 968k"),
    ]
    for r_i, (nm, gk, mlb, verd, vc) in enumerate(rows):
        yy = ty + 68 + r_i * 21.5
        if r_i % 2 == 1:
            p.append(f'    <rect x="{rx + 10}" y="{yy - 14}" width="{rw - 20}" height="20.5" fill="#f8fafc"/>')
        vcol = "#047857" if verd == "SAT" else "#b91c1c"
        p.append(f'    <text x="{xs[0]}" y="{yy}" font-family="{FONT_MONO}" font-size="8.5" font-weight="600" fill="#0f172a">{nm}</text>')
        p.append(f'    <text x="{xs[1]}" y="{yy}" text-anchor="middle" font-size="8.5" fill="#334155">{gk}</text>')
        p.append(f'    <text x="{xs[2]}" y="{yy}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.4" fill="#475569">{mlb}</text>')
        p.append(f'    <text x="{xs[3]}" y="{yy}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{vcol}">{verd}</text>')
        p.append(f'    <text x="{xs[4]}" y="{yy}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.4" fill="#475569">{vc}</text>')

    p.append("  </g>")
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
