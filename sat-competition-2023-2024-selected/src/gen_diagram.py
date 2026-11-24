#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for sat-competition-2023-2024-selected."""
from __future__ import annotations

import json
import math
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 480
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_manifest() -> list[dict]:
    mpath = COL / "src" / "sc23_24_manifest.json"
    data = json.loads(mpath.read_text(encoding="utf-8"))
    return list(data["sat_competition_flat_cnfs"])


def group_of(fam: str) -> tuple[str, str]:
    if any(k in fam for k in ("Tseitin", "Urquhart", "Parity")):
        return "Parity / Tseitin", "#7c3aed"
    if any(k in fam for k in ("Card", "Clique", "RegAlloc")):
        return "Card. / Clique / RegAlloc", "#dc2626"
    if "Miter" in fam:
        return "Hardware Miters", "#2563eb"
    return "Crypto / SubIso / PolyMul", "#059669"


def main() -> None:
    items = parse_manifest()
    n_tot = len(items)
    n_sat = sum(1 for x in items if x["ans"] == "SAT")
    n_unsat = n_tot - n_sat
    n_23 = sum(1 for x in items if x["year"] == 2023)
    n_24 = sum(1 for x in items if x["year"] == 2024)
    tot_vars = sum(x["vars"] for x in items)
    tot_cls = sum(x["clauses"] for x in items)

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SAT Competition 2023 and 2024 selected 14-instance suite">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(f'<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SAT Competition 2023 &amp; 2024 Curated Flat-CNF Suite ({n_tot} Instances)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">11 industrial, algebraic, hardware &amp; cryptographic domains via GBD · {n_23} SC23 + {n_24} SC24 · {n_sat} SAT / {n_unsat} UNSAT · 71,848 XORs</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: All 14 instances parsed live from sc23_24_manifest.json with log-scale clause bars
    lx, ly, lw, lh = 24, 78, 566, 380
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+14}" y="{ly+23}" font-size="13" font-weight="700" fill="#0f172a">Parsed Instance Scale &amp; Verdicts (sc23_24_manifest.json)</text>')
    a(f'<text x="{lx+14}" y="{ly+38}" font-size="10" fill="#475569">Clause count m on log₁₀ scale (694 → 472,588) · color-coded by structural archetype</text>')

    # Column headers
    bar_x0 = lx + 258
    bar_max = 188
    hy = ly + 56
    a(f'<text x="{lx+14}" y="{hy}" font-size="9.2" font-weight="700" fill="#64748b">Instance (Year · Family)</text>')
    a(f'<text x="{bar_x0}" y="{hy}" font-size="9.2" font-weight="700" fill="#64748b">Clauses m (log₁₀ scale)</text>')
    a(f'<text x="{lx+lw-14}" y="{hy}" text-anchor="end" font-size="9.2" font-weight="700" fill="#64748b">Vars / Ans</text>')
    a(f'<line x1="{lx+12}" y1="{hy+5}" x2="{lx+lw-12}" y2="{hy+5}" stroke="#cbd5e1" stroke-width="1"/>')

    # Log scale: 300 .. 600,000
    lmin, lmax = math.log10(300), math.log10(650000)
    # Subtle vertical log ticks
    for tk, tlbl in [(1000, "1k"), (10000, "10k"), (100000, "100k"), (500000, "500k")]:
        tx = bar_x0 + (math.log10(tk) - lmin) / (lmax - lmin) * bar_max
        a(f'<line x1="{tx:.1f}" y1="{hy+7}" x2="{tx:.1f}" y2="{ly+362}" stroke="#e2e8f0" stroke-width="0.8" stroke-dasharray="2,2"/>')
        a(f'<text x="{tx:.1f}" y="{ly+373}" text-anchor="middle" font-size="8.4" fill="#64748b">{tlbl}</text>')

    row_step = 21.3
    for i, item in enumerate(items):
        yy = hy + 19 + i * row_step
        _, gcol = group_of(item["family"])
        nm = item["name"]
        fam_short = item["family"].replace("SC23-", "").replace("SC24-", "")
        yr = str(item["year"])[2:]
        cls = item["clauses"]
        nv = item["vars"]
        ans = item["ans"]

        # Instance name + compact family tag
        a(f'<circle cx="{lx+18}" cy="{yy-3.5:.1f}" r="3.5" fill="{gcol}"/>')
        a(f'<text x="{lx+26}" y="{yy:.1f}" font-family="{MONO}" font-size="9.4" font-weight="700" fill="#0f172a">{nm}</text>')
        a(f'<text x="{lx+250}" y="{yy:.1f}" text-anchor="end" font-size="8.4" fill="#64748b">’{yr} {fam_short}</text>')

        # Clause log bar
        bw = max(6.0, (math.log10(max(cls, 300)) - lmin) / (lmax - lmin) * bar_max)
        a(f'<rect x="{bar_x0}" y="{yy-10.5:.1f}" width="{bw:.1f}" height="11.5" rx="2.5" fill="{gcol}" fill-opacity="0.85"/>')
        c_lbl = f"{cls/1000:.0f}k" if cls >= 10000 else f"{cls:,}"
        a(f'<text x="{bar_x0+bw+4:.1f}" y="{yy-1:.1f}" font-family="{MONO}" font-size="8.2" font-weight="600" fill="#334155">{c_lbl}</text>')

        # Vars + SAT/UNSAT badge
        v_lbl = f"{nv/1000:.1f}k" if nv >= 10000 else f"{nv:,}"
        a(f'<text x="{lx+lw-60}" y="{yy:.1f}" text-anchor="end" font-family="{MONO}" font-size="8.6" fill="#475569">{v_lbl}v</text>')
        pbg = "#ecfdf5" if ans == "SAT" else "#fef2f2"
        pcol = "#059669" if ans == "SAT" else "#dc2626"
        a(f'<rect x="{lx+lw-54}" y="{yy-10:.1f}" width="42" height="12.5" rx="3" fill="{pbg}" stroke="{pcol}" stroke-width="0.7"/>')
        a(f'<text x="{lx+lw-33}" y="{yy-0.8:.1f}" text-anchor="middle" font-size="8" font-weight="700" fill="{pcol}">{ans}</text>')

    # Right Panel: 4 Structural Archetypes + Suite Totals
    rx, ry, rw, rh = 604, 78, 292, 380
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+23}" font-size="13" font-weight="700" fill="#0f172a">4 Structural CNF Archetypes</text>')
    a(f'<text x="{rx+14}" y="{ry+38}" font-size="10" fill="#475569">Diverse solver-stress structure across 11 domains</text>')

    cards = [
        ("Parity / Tseitin / Urquhart (5)", "#7c3aed", "#f5f3ff",
         "2 SAT / 3 UNSAT · 12,514 pure XORs",
         "Sparse ρ_crit = 0.37–1.06×; pure CDCL times out"),
        ("Hardware Verification Miters (3)", "#2563eb", "#eff6ff",
         "0 SAT / 3 UNSAT · 5.6k–85.2k vars",
         "33,854 gate-XORs; AIG lifting &amp; equivalence"),
        ("Card. / Clique / RegAlloc (3)", "#dc2626", "#fef2f2",
         "0 SAT / 3 UNSAT · 99–100% binary",
         "Dense AMO cliques (ρ_crit = 7.1–22.4×)"),
        ("Crypto / SubIso / PolyMul (3)", "#059669", "#ecfdf5",
         "3 SAT / 0 UNSAT · up to 472k clauses",
         "VMPC-24, 1.09M-AND SubIso, 25.5k-XOR PolyMul"),
    ]
    for idx, (title, col, bg, line1, line2) in enumerate(cards):
        cy = ry + 50 + idx * 64
        a(f'<rect x="{rx+12}" y="{cy}" width="{rw-24}" height="56" rx="7" fill="#ffffff" stroke="{col}" stroke-width="1.1"/>')
        a(f'<rect x="{rx+12}" y="{cy}" width="6" height="56" rx="3" fill="{col}"/>')
        a(f'<text x="{rx+26}" y="{cy+17}" font-size="10.8" font-weight="700" fill="{col}">{title}</text>')
        a(f'<text x="{rx+26}" y="{cy+33}" font-family="{MONO}" font-size="8.9" font-weight="600" fill="#0f172a">{line1}</text>')
        a(f'<text x="{rx+26}" y="{cy+47}" font-size="9" fill="#475569">{line2}</text>')

    # Bottom Summary Box inside Right Panel
    sy = ry + 310
    a(f'<rect x="{rx+12}" y="{sy}" width="{rw-24}" height="58" rx="8" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
    a(f'<text x="{rx+22}" y="{sy+17}" font-size="10.5" font-weight="700" fill="#1e40af">4-Format Reproducible GBD Corpus</text>')
    a(f'<text x="{rx+22}" y="{sy+33}" font-family="{MONO}" font-size="9.2" fill="#1e3a8a">Total: {tot_vars:,} vars · {tot_cls:,} clauses</text>')
    a(f'<text x="{rx+22}" y="{sy+48}" font-size="9.2" fill="#334155">CNF (3.1 MB) · AIG · XCNF (71.8k XOR) · ANF</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
