#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-beijing."""
from __future__ import annotations

import lzma
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_beijing() -> dict[str, list[tuple[str, int, int, str]]]:
    verdicts: dict[str, str] = {}
    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            fn, v = line.split("\t")[:2]
            verdicts[fn.strip()] = v.strip()

    fams: dict[str, list[tuple[str, int, int, str]]] = {"circuit": [], "blocks": [], "sched": []}
    cnf_dir = COL / "cnf-orig"
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*.cnf.xz")):
            stem = p.name.replace(".cnf.xz", "")
            nv = nc = 0
            with lzma.open(p, "rt", errors="replace") as f:
                for line in f:
                    if line.startswith("p cnf"):
                        parts = line.split()
                        nv, nc = int(parts[2]), int(parts[3])
                        break
            v = verdicts.get(stem + ".cnf", "SAT")
            if stem.startswith(("2bit", "3bit")):
                fams["circuit"].append((stem, nv, nc, v))
            elif "blocks" in stem:
                fams["blocks"].append((stem, nv, nc, v))
            else:
                fams["sched"].append((stem, nv, nc, v))
    return fams


def main() -> None:
    fams = parse_beijing()
    all_rows = fams["circuit"] + fams["blocks"] + fams["sched"]
    n_sat = sum(1 for r in all_rows if r[3] == "SAT")
    n_unsat = sum(1 for r in all_rows if r[3] == "UNSAT")

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB 1996 Beijing SAT Competition multi-family showcase">')
    a('<defs>')
    a('  <marker id="arr-s" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>')
    a('  <marker id="arr-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>')
    a('</defs>')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB 1996 Beijing SAT Competition Showcase (satlib-beijing)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">Three classic problem domains: Boolean circuit synthesis ({len(fams["circuit"])}), Blocks World planning ({len(fams["blocks"])}), and 10×5 scheduling ({len(fams["sched"])}) · {n_sat} SAT / {n_unsat} UNSAT</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # 3 Equal-Height Domain Cards (y=78..384)
    card_y, card_h = 78, 304

    # --- Card 1: Arithmetic Circuit Synthesis (x=24..312, w=288) ---
    c1x, c1w = 24, 288
    a(f'<rect x="{c1x}" y="{card_y}" width="{c1w}" height="{card_h}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<rect x="{c1x}" y="{card_y}" width="{c1w}" height="30" rx="10" fill="#2563eb"/>')
    a(f'<rect x="{c1x}" y="{card_y+18}" width="{c1w}" height="12" fill="#2563eb"/>')
    a(f'<text x="{c1x+c1w/2:.1f}" y="{card_y+20}" text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff">1. Minimum-Gate Circuit Synthesis (7)</text>')

    # Mini 2-bit adder synthesis schematic
    sx, sy = c1x + 14, card_y + 44
    a(f'<rect x="{sx}" y="{sy}" width="{c1w-28}" height="132" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{sx+10}" y="{sy+17}" font-size="10.2" font-weight="700" fill="#1e3a8a">2-Bit Adder / Comparator Gate Bound k</text>')

    # Inputs A1,A0,B1,B0 on left
    in_lbls = ["A₁", "A₀", "B₁", "B₀"]
    for i, lbl in enumerate(in_lbls):
        iy = sy + 36 + i * 22
        a(f'<rect x="{sx+10}" y="{iy-8}" width="26" height="16" rx="3" fill="#eff6ff" stroke="#93c5fd" stroke-width="0.9"/>')
        a(f'<text x="{sx+23}" y="{iy+3.5}" text-anchor="middle" font-family="{MONO}" font-size="9" font-weight="700" fill="#1d4ed8">{lbl}</text>')
        a(f'<line x1="{sx+36}" y1="{iy}" x2="{sx+68}" y2="{iy}" stroke="#64748b" stroke-width="1.2"/>')

    # Synthesized k-gate box in middle
    a(f'<rect x="{sx+68}" y="{sy+28}" width="112" height="84" rx="7" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.3" stroke-dasharray="4,2"/>')
    a(f'<text x="{sx+124}" y="{sy+46}" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">k Binary Gates</text>')
    # Mini gate nodes inside
    for gx, gy_g, gl in [(sx+94, sy+66, "⊕"), (sx+150, sy+66, "∧"), (sx+94, sy+94, "∨"), (sx+150, sy+94, "⊕")]:
        a(f'<circle cx="{gx}" cy="{gy_g}" r="11" fill="#ffffff" stroke="#7c3aed" stroke-width="1.1"/>')
        a(f'<text x="{gx}" y="{gy_g+4}" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">{gl}</text>')
    a(f'<line x1="{sx+105}" y1="{sy+66}" x2="{sx+139}" y2="{sy+66}" stroke="#a78bfa" stroke-width="1.1"/>')
    a(f'<line x1="{sx+105}" y1="{sy+94}" x2="{sx+139}" y2="{sy+94}" stroke="#a78bfa" stroke-width="1.1"/>')

    # Outputs S2,S1,S0 on right
    out_lbls = ["S₂", "S₁", "S₀"]
    for i, lbl in enumerate(out_lbls):
        oy = sy + 44 + i * 26
        a(f'<line x1="{sx+180}" y1="{oy}" x2="{sx+214}" y2="{oy}" stroke="#64748b" stroke-width="1.2"/>')
        a(f'<rect x="{sx+214}" y="{oy-9}" width="32" height="18" rx="3" fill="#ecfdf5" stroke="#059669" stroke-width="0.9"/>')
        a(f'<text x="{sx+230}" y="{oy+3.5}" text-anchor="middle" font-family="{MONO}" font-size="9" font-weight="700" fill="#047857">{lbl}</text>')

    # Instance table inside Card 1
    ly1 = card_y + 190
    a(f'<text x="{c1x+14}" y="{ly1}" font-size="10" font-weight="700" fill="#334155">Exact Gate-Bound Thresholds:</text>')
    c1_items = [
        ("2bitadd_10", "k=10 gates", "UNSAT", "#dc2626", "#fef2f2"),
        ("2bitadd_11, 12", "k=11, 12 gates", "SAT", "#059669", "#ecfdf5"),
        ("2bitcomp_5 / max_6", "4→1 / 4→2 bit", "SAT", "#059669", "#ecfdf5"),
        ("3bitadd_31, 32", "k=31, 32 (32k cls)", "SAT", "#059669", "#ecfdf5"),
    ]
    for i, (nm, desc, verd, col, bg) in enumerate(c1_items):
        yy = ly1 + 19 + i * 22
        a(f'<text x="{c1x+14}" y="{yy}" font-family="{MONO}" font-size="9.4" font-weight="700" fill="#0f172a">{nm}</text>')
        a(f'<text x="{c1x+138}" y="{yy}" font-size="9" fill="#64748b">{desc}</text>')
        a(f'<rect x="{c1x+c1w-58}" y="{yy-10}" width="44" height="14" rx="3" fill="{bg}" stroke="{col}" stroke-width="0.7"/>')
        a(f'<text x="{c1x+c1w-36}" y="{yy}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{col}">{verd}</text>')

    # --- Card 2: Blocks World Planning (x=326..584, w=258) ---
    c2x, c2w = 326, 258
    a(f'<rect x="{c2x}" y="{card_y}" width="{c2w}" height="{card_h}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<rect x="{c2x}" y="{card_y}" width="{c2w}" height="30" rx="10" fill="#7c3aed"/>')
    a(f'<rect x="{c2x}" y="{card_y+18}" width="{c2w}" height="12" fill="#7c3aed"/>')
    a(f'<text x="{c2x+c2w/2:.1f}" y="{card_y+20}" text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff">2. Blocks World Planning (3)</text>')

    # Visual state transition t=0 -> t=T
    bx, by = c2x + 12, card_y + 44
    a(f'<rect x="{bx}" y="{by}" width="{c2w-24}" height="132" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{bx+10}" y="{by+17}" font-size="10.2" font-weight="700" fill="#5b21b6">STRIPS Action Horizon t = 0 → T</text>')

    # Table line for initial state (left) and goal state (right)
    ty_tbl = by + 112
    a(f'<line x1="{bx+14}" y1="{ty_tbl}" x2="{bx+94}" y2="{ty_tbl}" stroke="#334155" stroke-width="2"/>')
    a(f'<line x1="{bx+140}" y1="{ty_tbl}" x2="{bx+220}" y2="{ty_tbl}" stroke="#334155" stroke-width="2"/>')
    a(f'<text x="{bx+54}" y="{ty_tbl+13}" text-anchor="middle" font-size="9" font-weight="600" fill="#64748b">Init (t = 0)</text>')
    a(f'<text x="{bx+180}" y="{ty_tbl+13}" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">Goal (t = T)</text>')

    # Initial stacks: [B on A] + [D on C]
    blk_cols = {"A": ("#eff6ff", "#2563eb"), "B": ("#fffbeb", "#d97706"), "C": ("#ecfdf5", "#059669"), "D": ("#f5f3ff", "#7c3aed")}
    init_pos = [("A", bx+22, ty_tbl-22), ("B", bx+22, ty_tbl-44), ("C", bx+58, ty_tbl-22), ("D", bx+58, ty_tbl-44)]
    for ch_b, x_b, y_b in init_pos:
        bg, col = blk_cols[ch_b]
        a(f'<rect x="{x_b}" y="{y_b}" width="26" height="20" rx="3" fill="{bg}" stroke="{col}" stroke-width="1.3"/>')
        a(f'<text x="{x_b+13}" y="{y_b+13.5}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{col}">{ch_b}</text>')

    # Transition arrow
    a(f'<line x1="{bx+98}" y1="{by+72}" x2="{bx+136}" y2="{by+72}" stroke="#475569" stroke-width="1.8" marker-end="url(#arr-s)"/>')
    a(f'<text x="{bx+117}" y="{by+64}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#475569">move</text>')

    # Goal tower: D on C on B on A
    goal_pos = [("A", bx+167, ty_tbl-22), ("B", bx+167, ty_tbl-43), ("C", bx+167, ty_tbl-64), ("D", bx+167, ty_tbl-85)]
    for ch_b, x_b, y_b in goal_pos:
        bg, col = blk_cols[ch_b]
        a(f'<rect x="{x_b}" y="{y_b}" width="26" height="19" rx="3" fill="{bg}" stroke="{col}" stroke-width="1.3"/>')
        a(f'<text x="{x_b+13}" y="{y_b+13}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="{col}">{ch_b}</text>')

    # Parsed Blocks instances list
    ly2 = card_y + 190
    a(f'<text x="{c2x+14}" y="{ly2}" font-size="10" font-weight="700" fill="#334155">Parsed Instances (100% Horn):</text>')
    for i, (stem, nv, nc, v) in enumerate(fams["blocks"]):
        yy = ly2 + 21 + i * 24
        a(f'<text x="{c2x+14}" y="{yy}" font-family="{MONO}" font-size="10" font-weight="700" fill="#0f172a">{stem}</text>')
        a(f'<text x="{c2x+92}" y="{yy}" font-family="{MONO}" font-size="9.2" fill="#475569">{nv}v / {nc:,}c</text>')
        a(f'<rect x="{c2x+c2w-48}" y="{yy-10}" width="36" height="14" rx="3" fill="#ecfdf5" stroke="#059669" stroke-width="0.7"/>')
        a(f'<text x="{c2x+c2w-30}" y="{yy}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#047857">{v}</text>')

    a(f'<text x="{c2x+14}" y="{card_y+290}" font-size="9.2" fill="#64748b">High clause density α = 34–63 (ρ_crit ≤ 24.8×)</text>')

    # --- Card 3: 10x5 Job-Shop Scheduling (x=598..896, w=298) ---
    c3x, c3w = 598, 298
    a(f'<rect x="{c3x}" y="{card_y}" width="{c3w}" height="{card_h}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<rect x="{c3x}" y="{card_y}" width="{c3w}" height="30" rx="10" fill="#059669"/>')
    a(f'<rect x="{c3x}" y="{card_y+18}" width="{c3w}" height="12" fill="#059669"/>')
    a(f'<text x="{c3x+c3w/2:.1f}" y="{card_y+20}" text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff">3. 10×5 Job-Shop Scheduling (6)</text>')

    # Gantt Timeline Chart (5 Machines M1..M5)
    gx, gy = c3x + 12, card_y + 44
    a(f'<rect x="{gx}" y="{gy}" width="{c3w-24}" height="132" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{gx+10}" y="{gy+17}" font-size="10.2" font-weight="700" fill="#065f46">5-Machine Gantt Schedule &amp; Deadlines</text>')

    # Machine rows M1..M5
    tx0, tx1 = gx + 36, gx + c3w - 38
    tw = tx1 - tx0
    # Deadline dashed vertical line
    dl_x = tx0 + tw * 0.86
    a(f'<line x1="{dl_x:.1f}" y1="{gy+24}" x2="{dl_x:.1f}" y2="{gy+118}" stroke="#dc2626" stroke-width="1.3" stroke-dasharray="4,2"/>')
    a(f'<text x="{dl_x:.1f}" y="{gy+127}" text-anchor="middle" font-size="8.2" font-weight="700" fill="#dc2626">Deadline D</text>')

    sched_bars = [
        ("M₁", [(0.02, 0.24, "J1", "#2563eb"), (0.28, 0.26, "J4", "#7c3aed"), (0.58, 0.24, "J7", "#059669")]),
        ("M₂", [(0.08, 0.28, "J2", "#d97706"), (0.40, 0.22, "J1", "#2563eb"), (0.65, 0.19, "J9", "#0891b2")]),
        ("M₃", [(0.02, 0.20, "J5", "#059669"), (0.26, 0.30, "J2", "#d97706"), (0.60, 0.22, "J6", "#7c3aed")]),
        ("M₄", [(0.14, 0.24, "J8", "#0891b2"), (0.42, 0.26, "J5", "#059669"), (0.70, 0.14, "J3", "#2563eb")]),
        ("M₅", [(0.05, 0.22, "J3", "#2563eb"), (0.32, 0.24, "J8", "#0891b2"), (0.59, 0.25, "J4", "#7c3aed")]),
    ]
    for ri, (mlbl, bars) in enumerate(sched_bars):
        ry_m = gy + 28 + ri * 17.5
        a(f'<text x="{gx+10}" y="{ry_m+11:.1f}" font-family="{MONO}" font-size="9" font-weight="700" fill="#475569">{mlbl}</text>')
        a(f'<line x1="{tx0}" y1="{ry_m+13:.1f}" x2="{tx1}" y2="{ry_m+13:.1f}" stroke="#f1f5f9" stroke-width="1"/>')
        for start, dur, jlbl, col in bars:
            bx_s = tx0 + start * tw
            bw_s = dur * tw
            a(f'<rect x="{bx_s:.1f}" y="{ry_m+1:.1f}" width="{bw_s:.1f}" height="12" rx="2.5" fill="{col}" fill-opacity="0.86"/>')
            a(f'<text x="{bx_s+bw_s/2:.1f}" y="{ry_m+9.8:.1f}" text-anchor="middle" font-size="7.8" font-weight="700" fill="#ffffff">{jlbl}</text>')

    # Parsed scheduling groups
    ly3 = card_y + 190
    a(f'<text x="{c3x+14}" y="{ly3}" font-size="10" font-weight="700" fill="#334155">3 Deadline Variants (10 jobs × 5 mach.):</text>')
    s_groups = [
        ("e0ddr2-10-by-5-{1,4}", "19.5k v / 104k c"),
        ("enddr2-10-by-5-{1,8}", "20.7k v / 112k c"),
        ("ewddr2-10-by-5-{1,8}", "21.8k v / 121k c"),
    ]
    for i, (nm, dim) in enumerate(s_groups):
        yy = ly3 + 21 + i * 24
        a(f'<text x="{c3x+14}" y="{yy}" font-family="{MONO}" font-size="9.4" font-weight="700" fill="#0f172a">{nm}</text>')
        a(f'<text x="{c3x+c3w-14}" y="{yy}" text-anchor="end" font-family="{MONO}" font-size="8.8" fill="#475569">{dim}</text>')

    a(f'<text x="{c3x+14}" y="{card_y+290}" font-size="9.2" fill="#047857" font-weight="600">All 6 SAT · 100% Horn · k_max = 3 (α ≈ 6.0)</text>')

    # Bottom Summary Strip (y=394..442)
    sy_b = 394
    a(f'<rect x="24" y="{sy_b}" width="872" height="46" rx="8" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
    a(f'<text x="40" y="{sy_b+19}" font-size="11" font-weight="700" fill="#1e40af">1996 Beijing Suite Footprint (16 Instances, 4 Formats):</text>')
    a(f'<text x="366" y="{sy_b+19}" font-size="11" fill="#1e3a8a">Vars 125–22,500 · Clauses 310–123,329 · 15 SAT / 1 UNSAT (sole UNSAT: 2bitadd_10)</text>')
    a(f'<text x="40" y="{sy_b+36}" font-size="10" fill="#475569">All 16 formulas lie in the Over-constrained structured regime (ρ_crit = 2.50×–24.8×, 0 native XORs, 90–100% Horn clauses).</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
