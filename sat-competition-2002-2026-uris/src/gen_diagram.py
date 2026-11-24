#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for sat-competition-2002-2026-uris.

Parses all 62 track-year manifests in ``uris/*.uri`` and ``expected.tsv`` live to
render a 25-year (2002–2026) multi-track timeline, track-family SAT/UNSAT/UNKNOWN
distribution, non-main & SC 2024–2026 ``cake_lpr`` certification card, and pipeline.
"""
from __future__ import annotations

import collections
import html
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
URIS_DIR = COL / "uris"
OUT = COL / "diagram.svg"

W, H = 980, 580
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return html.escape(s, quote=False)

# Track super-groups for clean 25-year stacked visualization
SUPERGROUPS = [
    ("core", "Main / App / Ind", ("main", "application", "industrial"), "#2563eb"),
    ("crafted", "Crafted / Handmade", ("crafted", "handmade"), "#7c3aed"),
    ("random", "Random", ("random",), "#d97706"),
    ("special", "Agile & Special", ("agile", "mus", "portfolio", "parallel", "planning", "crypto"), "#0891b2"),
    ("archive", "Anni 2022 / Subm. 22–26", ("anni", "submissions"), "#059669"),
]

CAT_TO_GROUP = {cat: gid for gid, _, cats, _ in SUPERGROUPS for cat in cats}


def parse_archive():
    verdicts: dict[str, str] = {}
    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            fn, v = line.split("\t")[:2]
            verdicts[fn.strip().removesuffix(".cnf")] = v.strip()

    year_group_counts: dict[int, dict[str, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
    group_hashes: dict[str, set[str]] = collections.defaultdict(set)
    group_files: dict[str, int] = collections.defaultdict(int)
    all_hashes: set[str] = set()
    total_slots = 0
    total_files = 0
    categories: set[str] = set()

    for uf in sorted(URIS_DIR.glob("*.uri")):
        stem = uf.stem
        cat, yr_s = stem.rsplit("_", 1)
        yr = int(yr_s)
        gid = CAT_TO_GROUP[cat]
        categories.add(cat)
        total_files += 1
        group_files[gid] += 1
        hs = [
            l.strip().rsplit("/", 1)[-1].split("-")[0].split(".")[0]
            for l in uf.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        year_group_counts[yr][gid] += len(hs)
        group_hashes[gid].update(hs)
        all_hashes.update(hs)
        total_slots += len(hs)

    def verdict_counts(hset: set[str]) -> dict[str, int]:
        c = collections.Counter(verdicts.get(h, "UNKNOWN") for h in hset)
        return {"SAT": c["SAT"], "UNSAT": c["UNSAT"], "UNKNOWN": c["UNKNOWN"], "TOTAL": len(hset)}

    group_stats = {gid: verdict_counts(group_hashes[gid]) for gid, _, _, _ in SUPERGROUPS}
    total_stats = verdict_counts(all_hashes)
    return (
        year_group_counts,
        group_stats,
        group_files,
        total_stats,
        total_slots,
        total_files,
        len(categories),
    )


def main() -> None:
    (
        yr_grp,
        grp_stats,
        grp_files,
        tot_stats,
        tot_slots,
        tot_files,
        num_cats,
    ) = parse_archive()

    years = list(range(2002, 2027))
    tot_uniq = tot_stats["TOTAL"]

    s: list[str] = []
    a = s.append

    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="SAT Competition and SAT-Race 2002-2026 Archive URI Corpus">'
    )
    a("<defs>")
    a(
        '  <marker id="arr-p" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>'
    )
    a("</defs>")

    # Explicit light-card background
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(
        f'<text x="24" y="33" font-size="18" font-weight="700" fill="#0f172a">'
        f"SAT Competition &amp; SAT-Race Archive (2002–2026 · {tot_uniq:,} Unique CNFs)</text>"
    )
    a(
        f'<text x="24" y="53" font-size="11.8" fill="#475569">'
        f"{tot_files} track-year GBD URI manifests across 25 years &amp; {num_cats} track types "
        f"({tot_slots:,} slots → {tot_uniq:,} unique) · "
        f'{tot_stats["SAT"]:,} SAT / {tot_stats["UNSAT"]:,} UNSAT / {tot_stats["UNKNOWN"]:,} UNKNOWN</text>'
    )
    a(f'<line x1="24" y1="65" x2="{W-24}" y2="65" stroke="#e2e8f0" stroke-width="1"/>')

    # =========================================================================
    # PANEL 1: 25-Year Competition Timeline (2002–2026) — Sqrt-Scaled Stacked Bars
    # =========================================================================
    tx, ty, tw, th = 24, 76, W - 48, 224
    a(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(
        f'<text x="{tx+14}" y="{ty+22}" font-size="12.5" font-weight="700" fill="#0f172a">'
        f"25-Year Track-Slot Timeline (2002–2026, Parsed Live from uris/*.uri)</text>"
    )
    a(
        f'<text x="{tx+tw-14}" y="{ty+22}" text-anchor="end" font-size="9.8" fill="#64748b">'
        f"Bar height proportional to √(track-slots) so 100-instance SAT-Races &amp; 6,414-slot 2022 are both legible</text>"
    )

    # Legend row at top of Panel 1
    leg_x = tx + 14
    leg_y = ty + 39
    leg_offsets = [0, 146, 294, 384, 514]
    for (gid, glbl, _, col), dx in zip(SUPERGROUPS, leg_offsets):
        lx0 = leg_x + dx
        a(f'<rect x="{lx0}" y="{leg_y-8}" width="10" height="10" rx="2" fill="{col}"/>')
        a(f'<text x="{lx0+14}" y="{leg_y+0.5}" font-size="9.6" font-weight="600" fill="#334155">{esc(glbl)}</text>')

    # Plot area inside Panel 1
    px0 = tx + 52
    pw = tw - 68
    py_top = ty + 58
    py_bot = ty + 190
    ph = py_bot - py_top

    max_yr_tot = max(sum(yr_grp[y].values()) for y in years)
    max_sqrt = math.sqrt(max_yr_tot)

    # Horizontal sqrt gridlines
    for tick in (100, 400, 1000, 2500, 5000):
        yy = py_bot - ph * (math.sqrt(tick) / max_sqrt)
        a(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px0+pw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="0.9" stroke-dasharray="3,3"/>')
        a(f'<text x="{px0-6}" y="{yy+3.2:.1f}" text-anchor="end" font-family="{MONO}" font-size="8.6" fill="#64748b">{tick:,}</text>')
    a(f'<line x1="{px0}" y1="{py_bot}" x2="{px0+pw}" y2="{py_bot}" stroke="#94a3b8" stroke-width="1.1"/>')

    step = pw / len(years)
    bar_w = step * 0.68
    peak_labels = {2002, 2005, 2006, 2012, 2016, 2017, 2022, 2024, 2026}

    for idx, y in enumerate(years):
        cx = px0 + (idx + 0.5) * step
        bx = cx - bar_w / 2.0
        ytot = sum(yr_grp[y].values())
        bh_tot = ph * (math.sqrt(ytot) / max_sqrt) if ytot > 0 else 0.0

        cur_y = py_bot
        for gid, _, _, col in SUPERGROUPS:
            cnt = yr_grp[y].get(gid, 0)
            if cnt <= 0:
                continue
            seg_h = bh_tot * (cnt / ytot)
            cur_y -= seg_h
            a(f'<rect x="{bx:.1f}" y="{cur_y:.1f}" width="{bar_w:.1f}" height="{max(seg_h, 0.8):.1f}" fill="{col}"/>')

        # Year label
        yr_str = f"'{str(y)[2:]}"
        fw = "700" if y in (2002, 2006, 2012, 2017, 2022, 2026) else "500"
        a(f'<text x="{cx:.1f}" y="{py_bot+13}" text-anchor="middle" font-family="{MONO}" font-size="8.8" font-weight="{fw}" fill="#334155">{yr_str}</text>')

        # Total count above notable peaks / milestones
        if y in peak_labels:
            a(
                f'<text x="{cx:.1f}" y="{py_bot - bh_tot - 4:.1f}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="8.0" font-weight="700" fill="#0f172a">{ytot:,}</text>'
            )

    # Era annotations along bottom of Panel 1
    eras = [
        (2002, 2008, "Early Ind / Hand / Rand & SAT-Races"),
        (2009, 2016, "App / Crafted / MUS / Portfolio / Agile"),
        (2017, 2021, "Unified Main + Agile / Plan / Crypto"),
        (2022, 2026, "20th Anni + Main + Subm. + AI Sub-Tracks"),
    ]
    for y0, y1, lbl in eras:
        x_mid = px0 + ((y0 - 2002) + (y1 - 2002) + 1) * 0.5 * step
        a(f'<text x="{x_mid:.1f}" y="{ty+th-8}" text-anchor="middle" font-size="8.6" fill="#64748b">{esc(lbl)}</text>')

    # =========================================================================
    # PANEL 2 (Mid-Left): Track-Family Ground-Truth Verdict Distribution
    # =========================================================================
    lx, ly, lw, lh = 24, 312, 540, 168
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(
        f'<text x="{lx+14}" y="{ly+21}" font-size="12" font-weight="700" fill="#0f172a">'
        f"Verdict Breakdown by Track Family (Deduplicated Unique CNFs)</text>"
    )

    bar_x0 = lx + 168
    bar_w2 = 270
    rows_bar = [
        ("Main / App / Ind", grp_stats["core"], grp_files["core"]),
        ("Crafted / Handmade", grp_stats["crafted"], grp_files["crafted"]),
        ("Random (2002–18)", grp_stats["random"], grp_files["random"]),
        ("Agile & Special", grp_stats["special"], grp_files["special"]),
        ("Anni 22 / Subm. 22–26", grp_stats["archive"], grp_files["archive"]),
        ("All Unique (2002–26)", tot_stats, tot_files),
    ]
    for idx, (lbl, d, nf) in enumerate(rows_bar):
        yy = ly + 33 + idx * 19 + (4 if idx == 5 else 0)
        if idx == 5:
            a(f'<line x1="{lx+12}" y1="{yy-4}" x2="{lx+lw-12}" y2="{yy-4}" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3,2"/>')
        tot = max(d["TOTAL"], 1)
        ws = bar_w2 * d["SAT"] / tot
        wu = bar_w2 * d["UNSAT"] / tot
        wk = bar_w2 - ws - wu
        fw = "700" if idx == 5 else "600"
        a(f'<text x="{lx+14}" y="{yy+11}" font-size="9.6" font-weight="{fw}" fill="#0f172a">{esc(lbl)}</text>')
        a(f'<text x="{bar_x0-6}" y="{yy+11}" text-anchor="end" font-family="{MONO}" font-size="8.6" fill="#64748b">{d["TOTAL"]:,}</text>')

        a(f'<rect x="{bar_x0}" y="{yy}" width="{ws:.1f}" height="14" rx="2" fill="#059669"/>')
        a(f'<rect x="{bar_x0+ws:.1f}" y="{yy}" width="{wu:.1f}" height="14" fill="#dc2626"/>')
        a(f'<rect x="{bar_x0+ws+wu:.1f}" y="{yy}" width="{wk:.1f}" height="14" rx="2" fill="#94a3b8"/>')

        if ws >= 30:
            a(f'<text x="{bar_x0+ws/2:.1f}" y="{yy+10}" text-anchor="middle" font-size="8.0" font-weight="700" fill="#ffffff">{d["SAT"]:,}</text>')
        if wu >= 30:
            a(f'<text x="{bar_x0+ws+wu/2:.1f}" y="{yy+10}" text-anchor="middle" font-size="8.0" font-weight="700" fill="#ffffff">{d["UNSAT"]:,}</text>')
        if wk >= 30:
            a(f'<text x="{bar_x0+ws+wu+wk/2:.1f}" y="{yy+10}" text-anchor="middle" font-size="8.0" font-weight="700" fill="#ffffff">{d["UNKNOWN"]:,}</text>')

        a(
            f'<text x="{bar_x0+bar_w2+8}" y="{yy+10.5}" font-family="{MONO}" font-size="8.2" fill="#475569">'
            f'{100*d["SAT"]/tot:2.0f}%S/{100*d["UNSAT"]/tot:2.0f}%U</text>'
        )

    # Verdict Legend at bottom of Panel 2
    lby = ly + lh - 10
    a(f'<rect x="{lx+14}" y="{lby-8}" width="10" height="10" rx="2" fill="#059669"/>')
    a(f'<text x="{lx+28}" y="{lby}" font-size="9.0" fill="#334155">SAT ({tot_stats["SAT"]:,})</text>')
    a(f'<rect x="{lx+118}" y="{lby-8}" width="10" height="10" rx="2" fill="#dc2626"/>')
    a(f'<text x="{lx+132}" y="{lby}" font-size="9.0" fill="#334155">UNSAT ({tot_stats["UNSAT"]:,})</text>')
    a(f'<rect x="{lx+236}" y="{lby-8}" width="10" height="10" rx="2" fill="#94a3b8"/>')
    a(f'<text x="{lx+250}" y="{lby}" font-size="9.0" fill="#334155">UNKNOWN ({tot_stats["UNKNOWN"]:,}) · 0 conflicts across 9 sources</text>')

    # =========================================================================
    # PANEL 3 (Mid-Right): Non-Main Tracks & 3-Year cake_lpr Certification Card
    # =========================================================================
    rx, ry, rw, rh = 578, 312, 378, 168
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+21}" font-size="12" font-weight="700" fill="#0f172a">Non-Main Tracks &amp; Formal Certification</text>')

    # Sub-card 1: Non-Main & Shared Sub-Tracks
    a(f'<rect x="{rx+12}" y="{ry+30}" width="{rw-24}" height="64" rx="6" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    a(f'<text x="{rx+20}" y="{ry+45}" font-size="9.6" font-weight="700" fill="#1d4ed8">Dedicated Non-Main + Shared Sub-Tracks</text>')
    a(f'<text x="{rx+20}" y="{ry+59}" font-size="8.7" fill="#334155">• Dedicated CNFs: Agile (3,959), Anni 22 (5,355), MUS (299),</text>')
    a(f'<text x="{rx+20}" y="{ry+72}" font-size="8.7" fill="#334155">  Portfolio (599), Parallel 15 (96), Plan 20 (200), Crypto 21 (200)</text>')
    a(f'<text x="{rx+20}" y="{ry+85}" font-size="8.7" fill="#334155">• Shared Main CNFs: SC 26 AI-Gen/AI-Tuned, Cloud, Parallel, Hack</text>')

    # Sub-card 2: 3-Year SC 2024–2026 cake_lpr Certification
    a(f'<rect x="{rx+12}" y="{ry+101}" width="{rw-24}" height="57" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1"/>')
    a(f'<text x="{rx+20}" y="{ry+116}" font-size="9.6" font-weight="700" fill="#065f46">SC 2024–2026 Formal Certification (cake_lpr, T=300 s)</text>')
    a(f'<text x="{rx+20}" y="{ry+131}" font-family="{MONO}" font-size="8.4" fill="#064e3b">SC24: 146 (88S/58U, 408.46s) · SC25: 173 (93S/80U, 363.03s)</text>')
    a(f'<text x="{rx+20}" y="{ry+146}" font-family="{MONO}" font-size="8.4" font-weight="700" fill="#064e3b">SC26: 135 (62S/73U, 417.49s) · Uniq: 441/1,166 (0 err)</text>')

    # =========================================================================
    # PANEL 4 (Bottom): 4-Stage On-Demand Fetch → Convert → Verify Pipeline
    # =========================================================================
    px, py, pw4, ph4 = 24, 492, W - 48, 74
    a(f'<rect x="{px}" y="{py}" width="{pw4}" height="{ph4}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')

    stages = [
        ("1. 62 GBD URI Lists", "uris/<track>_<yr>.uri", "32,194 slots → 20,225 unique", "#2563eb"),
        ("2. On-Demand Fetch", "src/download_sc_main.py", "Direct HTTPS .cnf.xz cache", "#0891b2"),
        ("3. Multi-Format Convert", "cnf2aig.py / to_anf.py", ".cnf · .aig · .xcnf · .anf", "#7c3aed"),
        ("4. Ground-Truth Audit", "expected.tsv + cake_lpr", "13,610 known · 0 conflicts", "#059669"),
    ]
    bw4 = 208
    gap4 = 24
    sx0 = px + 14
    sy_b = py + 11
    bh4 = 52
    for idx, (title, script, sub, col) in enumerate(stages):
        bx = sx0 + idx * (bw4 + gap4)
        a(f'<rect x="{bx}" y="{sy_b}" width="{bw4}" height="{bh4}" rx="7" fill="#ffffff" stroke="{col}" stroke-width="1.3"/>')
        a(f'<rect x="{bx}" y="{sy_b}" width="{bw4}" height="18" rx="7" fill="{col}"/>')
        a(f'<rect x="{bx}" y="{sy_b+10}" width="{bw4}" height="8" fill="{col}"/>')
        a(f'<text x="{bx+bw4/2:.1f}" y="{sy_b+12.5}" text-anchor="middle" font-size="9.4" font-weight="700" fill="#ffffff">{esc(title)}</text>')
        a(f'<text x="{bx+bw4/2:.1f}" y="{sy_b+31}" text-anchor="middle" font-family="{MONO}" font-size="8.5" font-weight="700" fill="{col}">{esc(script)}</text>')
        a(f'<text x="{bx+bw4/2:.1f}" y="{sy_b+44}" text-anchor="middle" font-size="8.4" fill="#475569">{esc(sub)}</text>')
        if idx < len(stages) - 1:
            ax0 = bx + bw4 + 3
            ax1 = bx + bw4 + gap4 - 3
            ay = sy_b + bh4 / 2.0
            a(f'<line x1="{ax0}" y1="{ay:.1f}" x2="{ax1}" y2="{ay:.1f}" stroke="#2563eb" stroke-width="1.8" marker-end="url(#arr-p)"/>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
