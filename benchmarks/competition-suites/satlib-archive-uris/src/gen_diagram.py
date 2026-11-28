#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-archive-uris."""
from __future__ import annotations

import collections
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 500
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_satlib_uris() -> tuple[int, dict[str, int]]:
    uri_path = COL / "satlib_all_97_archives.uri"
    by_dir: dict[str, int] = collections.Counter()
    total = 0
    if uri_path.exists():
        for line in uri_path.read_text(encoding="utf-8").splitlines():
            st = line.strip()
            if not st or st.startswith("#"):
                continue
            total += 1
            rel = st.split("/SAT/")[-1]
            parts = rel.split("/")
            key = "/".join(parts[:-1])
            by_dir[key] += 1
    return total, dict(by_dir)


def main() -> None:
    total_uris, by_dir = parse_satlib_uris()

    # Exact reconciliation of all 97 UBC SATLIB archives -> 22 satlib-* collections (+ pretolani-pret)
    ensembles = [
        ("CBS", "satlib-cbs", by_dir.get("CBS", 40), 6),
        ("RND3SAT", "satlib-rnd3sat", by_dir.get("RND3SAT", 19), 10),
        ("SW-GCP", "satlib-sw-gcp", by_dir.get("SW-GCP", 10), 5),
        ("GCP (Flat)", "satlib-flat-gcp", by_dir.get("GCP", 8), 8),
        ("BMS / RTI", "satlib-bms-rti", by_dir.get("BMS", 2), 4),
    ]
    dimacs_full = [
        ("AIM", "dimacs-aim", 72),
        ("JNH", "dimacs-jnh", 50),
        ("II", "dimacs-ii", 41),
        ("PARITY", "dimacs-parity", 30),
        ("DUBOIS", "dimacs-dubois", 13),
        ("SSA", "dimacs-ssa", 8),
        ("PHOLE", "dimacs-phole", 5),
        ("BF", "dimacs-bf", 4),
        ("GCP-Lg", "dimacs-gcp-large", 4),
        ("LRAN", "dimacs-lran", 3),
        ("HANOI", "dimacs-hanoi", 2),
    ]
    verif_plan = [
        ("QG (Latin Sq.)", "satlib-qg", 22),
        ("Beijing '96", "satlib-beijing", 16),
        ("BMC (Model Chk)", "satlib-bmc", 13),
        ("Blocks World", "planning-blocksworld", 7),
        ("AIS (All-Int)", "satlib-ais", 4),
        ("Logistics", "planning-logistics", 4),
    ]

    ens_arch = sum(e[2] for e in ensembles)
    ens_inst = sum(e[3] for e in ensembles)
    dim_arch = sum(v for k, v in by_dir.items() if k.startswith("DIMACS/"))
    dim_inst = sum(d[2] for d in dimacs_full)
    vp_arch = sum(by_dir.get(k, 1) for k in ("QG", "Bejing", "BMC", "PLANNING/BlocksWorld", "AIS", "PLANNING/Logistics"))
    vp_inst = sum(v[2] for v in verif_plan)
    tot_cols = len(ensembles) + len(dimacs_full) + len(verif_plan)
    tot_inst = ens_inst + dim_inst + vp_inst

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="UBC SATLIB 97-archive taxonomy mapping into 22 collections">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(f'<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">UBC SATLIB Complete {total_uris}-Archive Taxonomy → {tot_cols} Committed Collections</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">All {total_uris} official .tar.gz archives (50,000+ raw CNFs) mapped into {tot_cols} standalone 4-format satlib-* collections ({tot_inst} CNFs) + pretolani-pret</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Root Node (x=24..192, y=196..328)
    rx, ry, rw, rh = 24, 198, 168, 128
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ry+28}" text-anchor="middle" font-size="13.5" font-weight="700" fill="#ffffff">UBC SATLIB</text>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ry+47}" text-anchor="middle" font-family="{MONO}" font-size="11.5" font-weight="700" fill="#93c5fd">{total_uris} .tar.gz URIs</text>')
    a(f'<line x1="{rx+18}" y1="{ry+58}" x2="{rx+rw-18}" y2="{ry+58}" stroke="#334155" stroke-width="1"/>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ry+75}" text-anchor="middle" font-size="9.5" fill="#cbd5e1">satlib_all_97_archives.uri</text>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ry+91}" text-anchor="middle" font-family="{MONO}" font-size="9" fill="#a7f3d0">src/fetch_satlib.py</text>')
    a(f'<text x="{rx+rw/2:.1f}" y="{ry+112}" text-anchor="middle" font-size="9" fill="#94a3b8">Hoos &amp; Stützle (SAT 2000)</text>')

    # Branch target box bounds (x=248..896)
    bx = 248
    bw = 648
    b1_y, b1_h = 78, 108
    b2_y, b2_h = 198, 140
    b3_y, b3_h = 350, 94

    # Smooth cubic Bezier taxonomy connectors from Root -> 3 Branches
    r_out_x = rx + rw
    r_out_y = ry + rh / 2
    for by, bh, col in [(b1_y, b1_h, "#d97706"), (b2_y, b2_h, "#2563eb"), (b3_y, b3_h, "#059669")]:
        ty = by + bh / 2
        c1x = r_out_x + 28
        c2x = bx - 28
        a(f'<path d="M {r_out_x},{r_out_y:.1f} C {c1x},{r_out_y:.1f} {c2x},{ty:.1f} {bx},{ty:.1f}" fill="none" stroke="{col}" stroke-width="2.2"/>')
        a(f'<circle cx="{bx}" cy="{ty:.1f}" r="4" fill="{col}"/>')

    # --- Branch 1 (Amber): 5 Synthetic Ensembles (79 archives -> 33 sampled instances) ---
    a(f'<rect x="{bx}" y="{b1_y}" width="{bw}" height="{b1_h}" rx="10" fill="#fffbeb" stroke="#fcd34d" stroke-width="1.3"/>')
    a(f'<text x="{bx+14}" y="{b1_y+21}" font-size="12" font-weight="700" fill="#92400e">A. Synthetic Ensembles — {ens_arch} Archives → 5 Stratified Collections ({ens_inst} Sampled / 50,000+ Raw)</text>')

    # 5 equal chips inside Branch 1
    chip_w = 118
    chip_gap = 8
    for i, (lbl, col_dir, n_arch, n_inst) in enumerate(ensembles):
        cx = bx + 14 + i * (chip_w + chip_gap)
        cy = b1_y + 32
        a(f'<rect x="{cx}" y="{cy}" width="{chip_w}" height="64" rx="7" fill="#ffffff" stroke="#f59e0b" stroke-width="1"/>')
        a(f'<text x="{cx+chip_w/2:.1f}" y="{cy+17}" text-anchor="middle" font-size="10.8" font-weight="700" fill="#92400e">{lbl}</text>')
        a(f'<text x="{cx+chip_w/2:.1f}" y="{cy+33}" text-anchor="middle" font-family="{MONO}" font-size="9.2" font-weight="700" fill="#b45309">{n_arch} arch → {n_inst} CNFs</text>')
        a(f'<text x="{cx+chip_w/2:.1f}" y="{cy+51}" text-anchor="middle" font-family="{MONO}" font-size="8.2" fill="#64748b">{col_dir}</text>')

    # --- Branch 2 (Blue): 12 DIMACS Archives -> 11 Full satlib-dimacs-* + pretolani-pret ---
    a(f'<rect x="{bx}" y="{b2_y}" width="{bw}" height="{b2_h}" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.3"/>')
    a(f'<text x="{bx+14}" y="{b2_y+21}" font-size="12" font-weight="700" fill="#1e40af">B. Second DIMACS Challenge Classics — {dim_arch} Archives → 11 Full Collections ({dim_inst} CNFs) + PRET</text>')

    # 6 chips on top row + 5 chips + 1 PRET callout on bottom row (2 rows of 6)
    cw2 = 98
    cg2 = 6.5
    all_b2 = [(nm, slug, f"{cnt} CNFs", False) for nm, slug, cnt in dimacs_full] + [("PRET", "pretolani-pret", "8 CNFs*", True)]
    for i, (nm, slug, cnt_s, is_ext) in enumerate(all_b2):
        row = i // 6
        col_i = i % 6
        cx = bx + 14 + col_i * (cw2 + cg2)
        cy = b2_y + 32 + row * 50
        bg = "#f5f3ff" if is_ext else "#ffffff"
        strk = "#7c3aed" if is_ext else "#3b82f6"
        dash = ' stroke-dasharray="3,2"' if is_ext else ""
        tcol = "#5b21b6" if is_ext else "#1d4ed8"
        a(f'<rect x="{cx:.1f}" y="{cy}" width="{cw2}" height="43" rx="6" fill="{bg}" stroke="{strk}" stroke-width="1"{dash}/>')
        a(f'<text x="{cx+cw2/2:.1f}" y="{cy+16}" text-anchor="middle" font-size="10.2" font-weight="700" fill="{tcol}">{nm}</text>')
        a(f'<text x="{cx+cw2/2:.1f}" y="{cy+32}" text-anchor="middle" font-family="{MONO}" font-size="8.8" fill="#334155">{cnt_s}</text>')

    # --- Branch 3 (Green): 6 Verification, Planning & Combinatorics Archives -> 6 Full Collections ---
    a(f'<rect x="{bx}" y="{b3_y}" width="{bw}" height="{b3_h}" rx="10" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.3"/>')
    a(f'<text x="{bx+14}" y="{b3_y+21}" font-size="12" font-weight="700" fill="#065f46">C. Verification, Planning &amp; Combinatorics — {vp_arch} Archives → 6 Full Collections ({vp_inst} CNFs)</text>')

    cw3 = 98
    cg3 = 6.5
    for i, (nm, slug, cnt) in enumerate(verif_plan):
        cx = bx + 14 + i * (cw3 + cg3)
        cy = b3_y + 32
        a(f'<rect x="{cx:.1f}" y="{cy}" width="{cw3}" height="50" rx="6" fill="#ffffff" stroke="#10b981" stroke-width="1"/>')
        a(f'<text x="{cx+cw3/2:.1f}" y="{cy+18}" text-anchor="middle" font-size="9.8" font-weight="700" fill="#047857">{nm}</text>')
        a(f'<text x="{cx+cw3/2:.1f}" y="{cy+36}" text-anchor="middle" font-family="{MONO}" font-size="9.4" font-weight="700" fill="#0f172a">{cnt} CNFs</text>')

    # Footer Reconciliation Bar (y=456..488)
    fy = 456
    a(f'<rect x="24" y="{fy}" width="872" height="32" rx="7" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>')
    a(f'<text x="460" y="{fy+20}" text-anchor="middle" font-size="10.4" fill="#1e293b"><tspan font-weight="700">Reconciliation:</tspan> {ens_arch} ensemble + {dim_arch} DIMACS + {vp_arch} verif/plan = <tspan font-weight="700">{total_uris} archives</tspan>  ·  <tspan font-weight="700">{tot_cols} satlib-* collections</tspan> = {tot_inst} CNFs (235 SAT / 96 UNSAT) × 4 formats  ·  *PRET in ../pretolani-pret/</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
