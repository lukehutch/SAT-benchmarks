#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-dimacs-ii."""
from __future__ import annotations

import collections
import lzma
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_ii() -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {
        "ii8": {"cnt": 0, "vmin": 10**9, "vmax": 0, "cmin": 10**9, "cmax": 0},
        "ii16": {"cnt": 0, "vmin": 10**9, "vmax": 0, "cmin": 10**9, "cmax": 0},
        "ii32": {"cnt": 0, "vmin": 10**9, "vmax": 0, "cmin": 10**9, "cmax": 0},
    }
    cnf_dir = COL / "cnf-orig"
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*.cnf.xz")):
            stem = p.name.replace(".cnf.xz", "")
            fam = "ii32" if stem.startswith("ii32") else ("ii16" if stem.startswith("ii16") else "ii8")
            nv = nc = 0
            with lzma.open(p, "rt", errors="replace") as f:
                for line in f:
                    if line.startswith("p cnf"):
                        parts = line.split()
                        nv, nc = int(parts[2]), int(parts[3])
                        break
            d = stats[fam]
            d["cnt"] += 1
            d["vmin"] = min(d["vmin"], nv)
            d["vmax"] = max(d["vmax"], nv)
            d["cmin"] = min(d["cmin"], nc)
            d["cmax"] = max(d["cmax"], nc)
    return stats


def main() -> None:
    stats = parse_ii()
    total = sum(d["cnt"] for d in stats.values())

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB Inductive Inference Boolean classifier synthesis diagram">')
    a('<defs>')
    a('  <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/></marker>')
    a('  <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker>')
    a('</defs>')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB Inductive Inference — Boolean Classifier Synthesis (ii8 / ii16 / ii32)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">Synthesizing a compact k-term DNF formula from labeled positive (+) and negative (−) bit-vectors · {total} SAT instances (Kamath et al.)</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Panel 1 (Left): Labeled Training Examples (E+ and E-)
    lx, ly, lw, lh = 24, 78, 286, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+14}" y="{ly+23}" font-size="12.5" font-weight="700" fill="#0f172a">1. Labeled Bit-Vector Examples</text>')
    a(f'<text x="{lx+14}" y="{ly+38}" font-size="10" fill="#475569">Input attributes u ∈ {{0, 1}}ᵈ (d = 8, 16, 32)</text>')

    # Column headers u1..u8 + label
    bit_x0 = lx + 18
    bit_step = 24
    hy = ly + 60
    for i in range(8):
        a(f'<text x="{bit_x0 + i*bit_step + 9}" y="{hy}" text-anchor="middle" font-family="{MONO}" font-size="9" font-weight="700" fill="#64748b">u{chr(0x2081+i)}</text>')
    a(f'<text x="{lx+lw-34}" y="{hy}" text-anchor="middle" font-size="9" font-weight="700" fill="#475569">Class</text>')
    a(f'<line x1="{lx+14}" y1="{hy+6}" x2="{lx+lw-14}" y2="{hy+6}" stroke="#cbd5e1" stroke-width="1"/>')

    # Positive examples (match T1=(u1∧¬u2∧u3) or T2=(¬u1∧u4∧u6))
    examples = [
        ([1, 0, 1, 1, 0, 0, 1, 0], "+"),
        ([1, 0, 1, 0, 1, 1, 0, 1], "+"),
        ([0, 1, 0, 1, 0, 1, 1, 0], "+"),
        ([0, 0, 1, 1, 1, 1, 0, 1], "+"),
        ([0, 1, 1, 0, 1, 0, 1, 1], "−"),
        ([1, 1, 1, 1, 0, 1, 0, 0], "−"),
        ([0, 0, 0, 1, 1, 0, 1, 0], "−"),
        ([1, 0, 0, 0, 1, 1, 1, 1], "−"),
    ]
    for r_i, (bits, cls) in enumerate(examples):
        ry = hy + 15 + r_i * 25 + (8 if r_i >= 4 else 0)
        if r_i == 4:
            a(f'<line x1="{lx+14}" y1="{ry-6}" x2="{lx+lw-14}" y2="{ry-6}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,2"/>')
        is_pos = cls == "+"
        for c_i, b in enumerate(bits):
            bx = bit_x0 + c_i * bit_step
            fill = "#eff6ff" if b == 1 else "#ffffff"
            strk = "#93c5fd" if b == 1 else "#cbd5e1"
            tc = "#1d4ed8" if b == 1 else "#64748b"
            a(f'<rect x="{bx}" y="{ry}" width="19" height="19" rx="3" fill="{fill}" stroke="{strk}" stroke-width="0.9"/>')
            a(f'<text x="{bx+9.5}" y="{ry+13}" text-anchor="middle" font-family="{MONO}" font-size="9.5" font-weight="700" fill="{tc}">{b}</text>')
        p_bg = "#ecfdf5" if is_pos else "#fef2f2"
        p_col = "#059669" if is_pos else "#dc2626"
        a(f'<rect x="{lx+lw-56}" y="{ry}" width="42" height="19" rx="4" fill="{p_bg}" stroke="{p_col}" stroke-width="0.9"/>')
        a(f'<text x="{lx+lw-35}" y="{ry+13.5}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{p_col}">{cls}1</text>')

    # Goal box at bottom of Panel 1
    gy = ly + 292
    a(f'<rect x="{lx+12}" y="{gy}" width="{lw-24}" height="56" rx="7" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    a(f'<text x="{lx+22}" y="{gy+18}" font-size="10.2" font-weight="700" fill="#0f172a">Inductive Synthesis Objective</text>')
    a(f'<text x="{lx+22}" y="{gy+33}" font-size="9.5" fill="#334155">Find k-term DNF f(u) = T₁ ∨ … ∨ T_k with:</text>')
    a(f'<text x="{lx+22}" y="{gy+47}" font-family="{MONO}" font-size="9.3" fill="#047857">f(E⁺) = 1</text>')
    a(f'<text x="{lx+94}" y="{gy+47}" font-size="9.5" fill="#64748b">and</text>')
    a(f'<text x="{lx+120}" y="{gy+47}" font-family="{MONO}" font-size="9.3" fill="#b91c1c">f(E⁻) = 0</text>')

    # Arrow 1 -> 2
    a(f'<line x1="{lx+lw+2}" y1="{ly+180}" x2="{lx+lw+20}" y2="{ly+180}" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-blue)"/>')

    # Panel 2 (Center): SAT Encoding -> Synthesized k-DNF Logic Circuit
    cx, cy, cw, ch = 334, 78, 322, 360
    a(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{cx+14}" y="{cy+23}" font-size="12.5" font-weight="700" fill="#0f172a">2. SAT Encoding → k-DNF Classifier</text>')
    a(f'<text x="{cx+14}" y="{cy+38}" font-size="10" fill="#475569">Boolean vars choose which literals enter each term Tⱼ</text>')

    # Top sub-box: SAT Clause Structure
    sx, sy, sw, sh = cx + 12, cy + 48, cw - 24, 120
    a(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    a(f'<text x="{sx+10}" y="{sy+18}" font-size="10.8" font-weight="700" fill="#1e40af">SAT Decision Variables &amp; Clauses</text>')
    a(f'<text x="{sx+10}" y="{sy+35}" font-size="9.4" fill="#334155">• <tspan font-family="{MONO}" font-weight="700" fill="#0f172a">s(j,i), s̄(j,i)</tspan>: include uᵢ or ¬uᵢ in term Tⱼ</text>')
    a(f'<text x="{sx+10}" y="{sy+52}" font-size="9.4" fill="#334155">• <tspan font-weight="700" fill="#2563eb">Binary exclusions (93% cls):</tspan></text>')
    a(f'<text x="{sx+20}" y="{sy+65}" font-family="{MONO}" font-size="9" fill="#475569">(¬s(j,i) ∨ ¬s̄(j,i)) &amp; positive-hit links</text>')
    a(f'<text x="{sx+10}" y="{sy+83}" font-size="9.4" fill="#334155">• <tspan font-weight="700" fill="#dc2626">Negative rejection (length d):</tspan></text>')
    a(f'<text x="{sx+20}" y="{sy+96}" font-family="{MONO}" font-size="9" fill="#475569">∀ u∈E⁻, ∀ j: at least 1 literal falsifies Tⱼ(u)</text>')
    a(f'<text x="{sx+10}" y="{sy+112}" font-size="9.4" fill="#334155">• <tspan font-weight="700" fill="#059669">Positive cover (length k):</tspan> ∃ Tⱼ with Tⱼ(u)=1</text>')

    # Down arrow from SAT box to synthesized DNF circuit
    a(f'<line x1="{cx+cw/2:.1f}" y1="{sy+sh+2}" x2="{cx+cw/2:.1f}" y2="{sy+sh+22}" stroke="#475569" stroke-width="2" marker-end="url(#arr-slate)"/>')
    a(f'<text x="{cx+cw/2+8:.1f}" y="{sy+sh+16}" font-size="9" font-weight="700" fill="#475569">SAT Model → DNF</text>')

    # Bottom sub-box: Synthesized 2-level AND-OR DNF circuit
    dx, dy, dw, dh = cx + 12, sy + sh + 26, cw - 24, 152
    a(f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="8" fill="#ffffff" stroke="#6ee7b7" stroke-width="1.2"/>')
    a(f'<text x="{dx+10}" y="{dy+18}" font-size="10.8" font-weight="700" fill="#047857">Synthesized 2-Term DNF Circuit f(u)</text>')

    # Inputs on left -> two AND boxes -> one OR box -> output
    # Term 1: (u1 ∧ ¬u2 ∧ u3)
    t1y, t2y = dy + 54, dy + 106
    a(f'<rect x="{dx+12}" y="{t1y-17}" width="118" height="34" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.2"/>')
    a(f'<text x="{dx+71}" y="{t1y-2}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1e40af">Term T₁ (AND)</text>')
    a(f'<text x="{dx+71}" y="{t1y+11}" text-anchor="middle" font-family="{MONO}" font-size="9.3" fill="#0f172a">u₁ ∧ ¬u₂ ∧ u₃</text>')

    # Term 2: (¬u1 ∧ u4 ∧ u6)
    a(f'<rect x="{dx+12}" y="{t2y-17}" width="118" height="34" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>')
    a(f'<text x="{dx+71}" y="{t2y-2}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#5b21b6">Term T₂ (AND)</text>')
    a(f'<text x="{dx+71}" y="{t2y+11}" text-anchor="middle" font-family="{MONO}" font-size="9.3" fill="#0f172a">¬u₁ ∧ u₄ ∧ u₆</text>')

    # OR Gate box
    or_x, or_y = dx + 166, (t1y + t2y) / 2
    a(f'<line x1="{dx+130}" y1="{t1y}" x2="{or_x-2}" y2="{or_y-8:.1f}" stroke="#2563eb" stroke-width="1.6"/>')
    a(f'<line x1="{dx+130}" y1="{t2y}" x2="{or_x-2}" y2="{or_y+8:.1f}" stroke="#7c3aed" stroke-width="1.6"/>')
    a(f'<rect x="{or_x}" y="{or_y-20:.1f}" width="54" height="40" rx="8" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>')
    a(f'<text x="{or_x+27}" y="{or_y-2:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">OR</text>')
    a(f'<text x="{or_x+27}" y="{or_y+12:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#065f46">∨</text>')

    # Output arrow -> classification
    a(f'<line x1="{or_x+54}" y1="{or_y:.1f}" x2="{dx+dw-56}" y2="{or_y:.1f}" stroke="#059669" stroke-width="1.8"/>')
    a(f'<rect x="{dx+dw-56}" y="{or_y-16:.1f}" width="46" height="32" rx="6" fill="#059669"/>')
    a(f'<text x="{dx+dw-33}" y="{or_y-1:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">f(u)</text>')
    a(f'<text x="{dx+dw-33}" y="{or_y+11:.1f}" text-anchor="middle" font-size="8.2" fill="#d1fae5">0 / 1</text>')

    a(f'<text x="{dx+dw/2:.1f}" y="{dy+142}" text-anchor="middle" font-size="9.2" fill="#065f46">100% consistent with all training vectors (E⁺ → 1, E⁻ → 0)</text>')

    # Panel 3 (Right): Parsed Corpus Breakdown (ii8 / ii16 / ii32)
    rx, ry, rw, rh = 670, 78, 226, 360
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+12}" y="{ry+23}" font-size="12.5" font-weight="700" fill="#0f172a">3. Parsed Corpus ({total} SAT)</text>')
    a(f'<text x="{rx+12}" y="{ry+38}" font-size="9.8" fill="#475569">3 input-width families in cnf-orig/</text>')

    fam_meta = [
        ("ii8", "8-bit inputs", "#059669", "#ecfdf5"),
        ("ii16", "16-bit inputs", "#2563eb", "#eff6ff"),
        ("ii32", "32-bit inputs", "#7c3aed", "#f5f3ff"),
    ]
    for i, (fam, desc, col, bg) in enumerate(fam_meta):
        d = stats[fam]
        yy = ry + 54 + i * 74
        a(f'<rect x="{rx+12}" y="{yy}" width="{rw-24}" height="64" rx="8" fill="#ffffff" stroke="{col}" stroke-width="1.1"/>')
        a(f'<text x="{rx+22}" y="{yy+18}" font-family="{MONO}" font-size="12" font-weight="700" fill="{col}">{fam}</text>')
        a(f'<text x="{rx+64}" y="{yy+18}" font-size="9.5" fill="#475569">({desc})</text>')
        a(f'<rect x="{rx+rw-60}" y="{yy+6}" width="38" height="15" rx="3" fill="{bg}" stroke="{col}" stroke-width="0.7"/>')
        a(f'<text x="{rx+rw-41}" y="{yy+17}" text-anchor="middle" font-size="9" font-weight="700" fill="{col}">{d["cnt"]} SAT</text>')
        a(f'<text x="{rx+22}" y="{yy+37}" font-family="{MONO}" font-size="9.2" fill="#334155">Vars: {d["vmin"]:,}–{d["vmax"]:,}</text>')
        a(f'<text x="{rx+22}" y="{yy+52}" font-family="{MONO}" font-size="9.2" fill="#334155">Cls:  {d["cmin"]:,}–{d["cmax"]:,}</text>')

    # Structural Signature Footer in Panel 3
    fy = ry + 282
    a(f'<rect x="{rx+12}" y="{fy}" width="{rw-24}" height="66" rx="7" fill="#fffbeb" stroke="#fcd34d" stroke-width="1"/>')
    a(f'<text x="{rx+20}" y="{fy+17}" font-size="10.2" font-weight="700" fill="#92400e">CNF Structural Signature</text>')
    a(f'<text x="{rx+20}" y="{fy+32}" font-size="9.2" fill="#78350f">• 93% binary · 97% Horn clauses</text>')
    a(f'<text x="{rx+20}" y="{fy+46}" font-size="9.2" fill="#78350f">• Long clauses at k = 8, 16, 32</text>')
    a(f'<text x="{rx+20}" y="{fy+60}" font-size="9.2" fill="#78350f">• Median ρ_crit = 9.37× (Over)</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
