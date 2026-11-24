#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for sat-competition-2024-2026-main-track."""
from __future__ import annotations

import collections
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_sc_main() -> tuple[dict[int, dict[str, int]], dict[str, int], dict[str, int]]:
    verdicts: dict[str, str] = {}
    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            fn, v = line.split("\t")[:2]
            verdicts[fn.strip()] = v.strip()

    yr_sets: dict[int, set[str]] = {}
    yr_counts: dict[int, dict[str, int]] = {}
    for y in (2024, 2025, 2026):
        up = COL / f"main_{y}.uri"
        hashes: list[str] = []
        if up.exists():
            for line in up.read_text(encoding="utf-8").splitlines():
                st = line.strip()
                if st:
                    hashes.append(st.split("/")[-1].replace(".cnf.xz", ""))
        yr_sets[y] = set(hashes)
        cnt = collections.Counter(verdicts.get(h + ".cnf", "UNKNOWN") for h in hashes)
        yr_counts[y] = {"SAT": cnt["SAT"], "UNSAT": cnt["UNSAT"], "UNKNOWN": cnt["UNKNOWN"], "TOTAL": len(hashes)}

    s24, s25, s26 = yr_sets[2024], yr_sets[2025], yr_sets[2026]
    union_all = s24 | s25 | s26
    u_cnt = collections.Counter(verdicts.get(h + ".cnf", "UNKNOWN") for h in union_all)
    union_stats = {"SAT": u_cnt["SAT"], "UNSAT": u_cnt["UNSAT"], "UNKNOWN": u_cnt["UNKNOWN"], "TOTAL": len(union_all)}
    overlaps = {
        "only24": len(s24 - s25 - s26),
        "only25": len(s25 - s24 - s26),
        "only26": len(s26 - s24 - s25),
        "o24_25": len((s24 & s25) - s26),
        "o25_26": len((s25 & s26) - s24),
        "o24_26": len((s24 & s26) - s25),
        "o_all": len(s24 & s25 & s26),
        "dup": sum(len(s) for s in yr_sets.values()) - len(union_all),
    }
    return yr_counts, union_stats, overlaps


def main() -> None:
    yr_counts, u_stats, ov = parse_sc_main()
    tot_entries = sum(yr_counts[y]["TOTAL"] for y in (2024, 2025, 2026))
    tot_uniq = u_stats["TOTAL"]

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SAT Competition 2024-2026 Main Track 1,200-URI corpus and pipeline">')
    a('<defs>')
    a('  <marker id="arr-p" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>')
    a('</defs>')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(f'<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SAT Competition 2024–2026 Main Track Corpus ({tot_uniq:,} Unique CNFs)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">{tot_entries:,} immutable GBD URI entries (400/year, {ov["dup"]} cross-year overlaps, ~11 GiB upstream) · {u_stats["SAT"]} SAT / {u_stats["UNSAT"]} UNSAT / {u_stats["UNKNOWN"]} UNKNOWN</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Top-Left Panel: 3-Year Verdict Stacked Bar Breakdown (Parsed Live)
    lx, ly, lw, lh = 24, 78, 520, 198
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+14}" y="{ly+23}" font-size="12.5" font-weight="700" fill="#0f172a">3-Year Track Breakdown (Parsed from main_202*.uri &amp; expected.tsv)</text>')

    bar_x0 = lx + 104
    bar_w = 310
    rows_bar = [
        ("SC 2024", yr_counts[2024]),
        ("SC 2025", yr_counts[2025]),
        ("SC 2026", yr_counts[2026]),
        ("Unique", u_stats),
    ]
    for idx, (lbl, d) in enumerate(rows_bar):
        yy = ly + 42 + idx * 33 + (4 if idx == 3 else 0)
        if idx == 3:
            a(f'<line x1="{lx+14}" y1="{yy-7}" x2="{lx+lw-14}" y2="{yy-7}" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3,2"/>')
        tot = max(d["TOTAL"], 1)
        ws = bar_w * d["SAT"] / tot
        wu = bar_w * d["UNSAT"] / tot
        wk = bar_w - ws - wu

        fw = "700" if idx == 3 else "600"
        a(f'<text x="{lx+16}" y="{yy+14}" font-size="11" font-weight="{fw}" fill="#0f172a">{lbl}</text>')
        a(f'<text x="{lx+94}" y="{yy+14}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="#64748b">({d["TOTAL"]})</text>')

        # Stacked segments
        a(f'<rect x="{bar_x0}" y="{yy}" width="{ws:.1f}" height="20" rx="3" fill="#059669"/>')
        a(f'<rect x="{bar_x0+ws:.1f}" y="{yy}" width="{wu:.1f}" height="20" fill="#dc2626"/>')
        a(f'<rect x="{bar_x0+ws+wu:.1f}" y="{yy}" width="{wk:.1f}" height="20" rx="3" fill="#94a3b8"/>')
        # Segment labels if wide enough
        if ws >= 32:
            a(f'<text x="{bar_x0+ws/2:.1f}" y="{yy+13.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#ffffff">{d["SAT"]}</text>')
        if wu >= 32:
            a(f'<text x="{bar_x0+ws+wu/2:.1f}" y="{yy+13.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#ffffff">{d["UNSAT"]}</text>')
        if wk >= 28:
            a(f'<text x="{bar_x0+ws+wu+wk/2:.1f}" y="{yy+13.5}" text-anchor="middle" font-size="9.2" font-weight="700" fill="#ffffff">{d["UNKNOWN"]}</text>')

        a(f'<text x="{bar_x0+bar_w+10}" y="{yy+13.5}" font-family="{MONO}" font-size="8.8" fill="#475569">{100*d["SAT"]/tot:.0f}%S/{100*d["UNSAT"]/tot:.0f}%U</text>')

    # Legend inside Top-Left Panel
    lby = ly + 183
    a(f'<rect x="{lx+16}" y="{lby-8}" width="11" height="11" rx="2" fill="#059669"/>')
    a(f'<text x="{lx+32}" y="{lby+1}" font-size="9.6" fill="#334155">SAT ({u_stats["SAT"]})</text>')
    a(f'<rect x="{lx+114}" y="{lby-8}" width="11" height="11" rx="2" fill="#dc2626"/>')
    a(f'<text x="{lx+130}" y="{lby+1}" font-size="9.6" fill="#334155">UNSAT ({u_stats["UNSAT"]})</text>')
    a(f'<rect x="{lx+226}" y="{lby-8}" width="11" height="11" rx="2" fill="#94a3b8"/>')
    a(f'<text x="{lx+242}" y="{lby+1}" font-size="9.6" fill="#334155">UNKNOWN / Unsolved ({u_stats["UNKNOWN"]})</text>')

    # Top-Right Panel: 3-Year Cross-Overlap Venn Diagram (Parsed Live)
    rx, ry, rw, rh = 558, 78, 338, 198
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+23}" font-size="12.5" font-weight="700" fill="#0f172a">Cross-Year GBD Deduplication</text>')
    a(f'<text x="{rx+14}" y="{ry+38}" font-size="10" fill="#475569">1,200 URI lines − {ov["dup"]} pairwise overlaps = {tot_uniq:,} unique</text>')

    # 3 translucent circles arranged cleanly with generous pairwise overlap lenses
    c24 = (rx + 137, ry + 102)
    c26 = (rx + 201, ry + 102)
    c25 = (rx + 169, ry + 144)
    rad = 48
    a(f'<circle cx="{c24[0]}" cy="{c24[1]}" r="{rad}" fill="#2563eb" fill-opacity="0.16" stroke="#2563eb" stroke-width="1.6"/>')
    a(f'<circle cx="{c26[0]}" cy="{c26[1]}" r="{rad}" fill="#7c3aed" fill-opacity="0.16" stroke="#7c3aed" stroke-width="1.6"/>')
    a(f'<circle cx="{c25[0]}" cy="{c25[1]}" r="{rad}" fill="#059669" fill-opacity="0.16" stroke="#059669" stroke-width="1.6"/>')

    # Circle labels (outer)
    a(f'<text x="{c24[0]-52}" y="{c24[1]-22}" text-anchor="end" font-size="10.5" font-weight="700" fill="#1d4ed8">SC 2024</text>')
    a(f'<text x="{c26[0]+52}" y="{c26[1]-22}" text-anchor="start" font-size="10.5" font-weight="700" fill="#6d28d9">SC 2026</text>')
    a(f'<text x="{c25[0]+56}" y="{c25[1]+34}" text-anchor="start" font-size="10.5" font-weight="700" fill="#047857">SC 2025</text>')

    # Exact counts inside Venn regions
    a(f'<text x="{c24[0]-18}" y="{c24[1]-5}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="#1e3a8a">{ov["only24"]}</text>')
    a(f'<text x="{c26[0]+18}" y="{c26[1]-5}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="#4c1d95">{ov["only26"]}</text>')
    a(f'<text x="{c25[0]}" y="{c25[1]+26}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="#065f46">{ov["only25"]}</text>')

    # Pairwise intersection numbers cleanly inside each lens
    a(f'<text x="{(c24[0]+c26[0])/2:.1f}" y="{c24[1]-14}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#1e293b">{ov["o24_26"]}</text>')
    a(f'<text x="{c24[0]+6}" y="{c25[1]-10}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#1e293b">{ov["o24_25"]}</text>')
    a(f'<text x="{c26[0]-6}" y="{c25[1]-10}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#1e293b">{ov["o25_26"]}</text>')
    a(f'<text x="{c25[0]}" y="{c24[1]+16}" text-anchor="middle" font-family="{MONO}" font-size="9.5" font-weight="700" fill="#64748b">{ov["o_all"]}</text>')

    # Bottom Panel: End-to-End 5-Stage Reproducible Pipeline (x=24..896, y=290..438)
    px, py, pw, ph = 24, 290, 872, 148
    a(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{px+16}" y="{py+24}" font-size="13" font-weight="700" fill="#0f172a">On-Demand Reproducible Fetch → 4-Format Conversion → Verification Pipeline</text>')

    stages = [
        ("1. GBD URI Manifests", "main_2024..2026.uri", "1,200 immutable MD5", "benchmark-database.de", "#2563eb", "#eff6ff"),
        ("2. Parallel Fetch", "download_sc_main.py", "1,166 .cnf.xz cached", "~/.cache/sc-main-cnfs", "#0891b2", "#ecfeff"),
        ("3. 4-Format Convert", "cnf2aig / to_anf.py", ".cnf · .aig · .xcnf", ".anf (degree ≤ 3)", "#7c3aed", "#f5f3ff"),
        ("4. 1-Core Benchmark", "run_sc_main.py", "SAT model verified", "0 disagreements", "#059669", "#ecfdf5"),
        ("5. PAR-2 Audit", "analyze_sc_main.py", "vs. official SC CSVs", "expected.tsv ground truth", "#d97706", "#fffbeb"),
    ]
    bw = 152
    gap = 20
    sx0 = px + 16
    sy_box = py + 38
    bh = 94
    for idx, (title, script, l1, l2, col, bg) in enumerate(stages):
        bx = sx0 + idx * (bw + gap)
        a(f'<rect x="{bx}" y="{sy_box}" width="{bw}" height="{bh}" rx="8" fill="#ffffff" stroke="{col}" stroke-width="1.3"/>')
        a(f'<rect x="{bx}" y="{sy_box}" width="{bw}" height="24" rx="8" fill="{col}"/>')
        a(f'<rect x="{bx}" y="{sy_box+14}" width="{bw}" height="10" fill="{col}"/>')
        a(f'<text x="{bx+bw/2:.1f}" y="{sy_box+16}" text-anchor="middle" font-size="10.2" font-weight="700" fill="#ffffff">{title}</text>')
        a(f'<rect x="{bx+8}" y="{sy_box+31}" width="{bw-16}" height="17" rx="3" fill="{bg}"/>')
        a(f'<text x="{bx+bw/2:.1f}" y="{sy_box+43}" text-anchor="middle" font-family="{MONO}" font-size="8.6" font-weight="700" fill="{col}">{script}</text>')
        a(f'<text x="{bx+bw/2:.1f}" y="{sy_box+64}" text-anchor="middle" font-size="9.2" font-weight="600" fill="#1e293b">{l1}</text>')
        a(f'<text x="{bx+bw/2:.1f}" y="{sy_box+80}" text-anchor="middle" font-size="8.8" fill="#64748b">{l2}</text>')

        if idx < len(stages) - 1:
            ax0 = bx + bw + 2
            ax1 = bx + bw + gap - 3
            ay_m = sy_box + bh / 2
            a(f'<line x1="{ax0}" y1="{ay_m:.1f}" x2="{ax1}" y2="{ay_m:.1f}" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-p)"/>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
