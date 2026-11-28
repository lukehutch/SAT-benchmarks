#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for sat-shortcut-challenge-tier1."""
from __future__ import annotations

import collections
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 480
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_tier1() -> tuple[dict[str, tuple[int, int]], int, int]:
    """Return per-family (sat, unsat) counts parsed directly from expected.tsv."""
    counts: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    sat_tot = unsat_tot = 0
    exp = COL / "expected.tsv"
    if exp.exists():
        for line in exp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            name, v = line.split("\t")[:2]
            v = v.strip()
            if v == "SAT":
                sat_tot += 1
            else:
                unsat_tot += 1
            if name.startswith("tseitin"):
                fam = "tseitin"
            elif name.startswith("xor_plus"):
                fam = "xor_plus"
            elif name.startswith("cec_adder"):
                fam = "cec_adder"
            elif name.startswith("cec_mult"):
                fam = "cec_mult"
            elif name.startswith("mult_target"):
                fam = "mult_target"
            elif name.startswith("php_"):
                fam = "php"
            elif name.startswith("chessboard"):
                fam = "chessboard"
            elif name.startswith("ham_"):
                fam = "ham"
            else:
                fam = "random3sat"
            counts[fam][0 if v == "SAT" else 1] += 1
    return {k: (v[0], v[1]) for k, v in counts.items()}, sat_tot, unsat_tot


def main() -> None:
    c, sat_tot, unsat_tot = parse_tier1()
    tot = sat_tot + unsat_tot

    def su(keys: list[str]) -> tuple[int, int]:
        return sum(c.get(k, (0, 0))[0] for k in keys), sum(c.get(k, (0, 0))[1] for k in keys)

    p1_s, p1_u = su(["tseitin", "xor_plus"])
    p2_s, p2_u = su(["cec_adder", "cec_mult", "mult_target"])
    p3_s, p3_u = su(["php", "chessboard"])
    p4_s, p4_u = su(["ham", "random3sat"])

    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SAT Shortcut Challenge Tier 1 4-pillar structured map">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a(f'<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SAT Shortcut Challenge — Tier 1 Structured Suite ({tot} Instances, 9 Families)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">Separating polynomial-time structural shortcuts from unstructured search (Keith Adler) · {sat_tot} SAT / {unsat_tot} UNSAT across 4 pillars</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # 2x2 Pillar Cards: width=430, height=160, gap=12
    cw, ch = 430, 162
    x_l, x_r = 24, 466
    y_t, y_b = 78, 252

    # --- Pillar 1 (Top-Left, Purple): F2 Parity & XOR Systems ---
    a(f'<rect x="{x_l}" y="{y_t}" width="{cw}" height="{ch}" rx="10" fill="#f8fafc" stroke="#c4b5fd" stroke-width="1.4"/>')
    a(f'<rect x="{x_l}" y="{y_t}" width="{cw}" height="28" rx="10" fill="#7c3aed"/>')
    a(f'<rect x="{x_l}" y="{y_t+16}" width="{cw}" height="12" fill="#7c3aed"/>')
    a(f'<text x="{x_l+14}" y="{y_t+19}" font-size="12" font-weight="700" fill="#ffffff">1. 𝔽₂ Parity &amp; Linear Systems ({p1_s+p1_u}: {p1_s} SAT / {p1_u} UNSAT)</text>')

    # Mini Tseitin XOR graph icon on left
    ix, iy = x_l + 16, y_t + 40
    a(f'<rect x="{ix}" y="{iy}" width="112" height="108" rx="7" fill="#ffffff" stroke="#ddd6fe" stroke-width="1"/>')
    pts = [(ix+56, iy+20), (ix+92, iy+46), (ix+78, iy+82), (ix+34, iy+82), (ix+20, iy+46)]
    for u, v in [(0,1),(1,2),(2,3),(3,4),(4,0),(0,2),(1,4)]:
        a(f'<line x1="{pts[u][0]}" y1="{pts[u][1]}" x2="{pts[v][0]}" y2="{pts[v][1]}" stroke="#7c3aed" stroke-width="1.3"/>')
    charges = ["⊕1", "⊕0", "⊕0", "⊕1", "⊕1"]
    for (px, py), chg in zip(pts, charges):
        a(f'<circle cx="{px}" cy="{py}" r="11" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.2"/>')
        a(f'<text x="{px}" y="{py+3.5}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#5b21b6">{chg}</text>')
    a(f'<text x="{ix+56}" y="{iy+101}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#dc2626">Σ charges ≡ 1 (UNSAT)</text>')

    # Pillar 1 family list
    tx = x_l + 140
    ts_s, ts_u = c.get("tseitin", (0, 0))
    xp_s, xp_u = c.get("xor_plus", (0, 0))
    a(f'<text x="{tx}" y="{y_t+52}" font-size="11" font-weight="700" fill="#0f172a">• Tseitin Parity (n = 20..200)</text>')
    a(f'<text x="{tx+10}" y="{y_t+66}" font-size="9.5" fill="#475569">{ts_s+ts_u} instances ({ts_s} SAT / {ts_u} UNSAT) · pure XOR cycles</text>')
    a(f'<text x="{tx}" y="{y_t+88}" font-size="11" font-weight="700" fill="#0f172a">• XOR System + Random 3-Clauses</text>')
    a(f'<text x="{tx+10}" y="{y_t+102}" font-size="9.5" fill="#475569">{xp_s+xp_u} instances ({xp_s} SAT / {xp_u} UNSAT) · n = 100–240</text>')
    a(f'<rect x="{tx}" y="{y_t+116}" width="276" height="32" rx="6" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="0.9"/>')
    a(f'<text x="{tx+10}" y="{y_t+130}" font-size="9.5" font-weight="700" fill="#5b21b6">Shortcut: Gaussian Elimination over 𝔽₂ (O(n³))</text>')
    a(f'<text x="{tx+10}" y="{y_t+142}" font-size="9" fill="#6d28d9">6,793 native XORs extracted; CDCL times out &gt;300 s</text>')

    # --- Pillar 2 (Top-Right, Blue): Arithmetic Circuits & Miters ---
    a(f'<rect x="{x_r}" y="{y_t}" width="{cw}" height="{ch}" rx="10" fill="#f8fafc" stroke="#93c5fd" stroke-width="1.4"/>')
    a(f'<rect x="{x_r}" y="{y_t}" width="{cw}" height="28" rx="10" fill="#2563eb"/>')
    a(f'<rect x="{x_r}" y="{y_t+16}" width="{cw}" height="12" fill="#2563eb"/>')
    a(f'<text x="{x_r+14}" y="{y_t+19}" font-size="12" font-weight="700" fill="#ffffff">2. Arithmetic Circuits &amp; Miters ({p2_s+p2_u}: {p2_s} SAT / {p2_u} UNSAT)</text>')

    # Mini Miter icon
    ix2 = x_r + 16
    a(f'<rect x="{ix2}" y="{iy}" width="112" height="108" rx="7" fill="#ffffff" stroke="#bfdbfe" stroke-width="1"/>')
    a(f'<rect x="{ix2+10}" y="{iy+16}" width="54" height="24" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="1.1"/>')
    a(f'<text x="{ix2+37}" y="{iy+31}" text-anchor="middle" font-size="9" font-weight="700" fill="#1e40af">Ripple/Arr</text>')
    a(f'<rect x="{ix2+10}" y="{iy+54}" width="54" height="24" rx="4" fill="#ecfeff" stroke="#0891b2" stroke-width="1.1"/>')
    a(f'<text x="{ix2+37}" y="{iy+69}" text-anchor="middle" font-size="9" font-weight="700" fill="#0e7490">KS / Wal</text>')
    a(f'<line x1="{ix2+64}" y1="{iy+28}" x2="{ix2+84}" y2="{iy+46}" stroke="#475569" stroke-width="1.3"/>')
    a(f'<line x1="{ix2+64}" y1="{iy+66}" x2="{ix2+84}" y2="{iy+50}" stroke="#475569" stroke-width="1.3"/>')
    a(f'<circle cx="{ix2+92}" cy="{iy+48}" r="11" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>')
    a(f'<text x="{ix2+92}" y="{iy+52}" text-anchor="middle" font-size="11" font-weight="700" fill="#dc2626">⊕</text>')
    a(f'<text x="{ix2+56}" y="{iy+98}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#1e3a8a">Miter: C₁(x) ⊕ C₂(x)</text>')

    tx2 = x_r + 140
    ad_s, ad_u = c.get("cec_adder", (0, 0))
    mu_s, mu_u = c.get("cec_mult", (0, 0))
    mt_s, mt_u = c.get("mult_target", (0, 0))
    a(f'<text x="{tx2}" y="{y_t+50}" font-size="10.8" font-weight="700" fill="#0f172a">• Adder CEC: Ripple vs. Kogge–Stone (8–64b)</text>')
    a(f'<text x="{tx2+10}" y="{y_t+63}" font-size="9.3" fill="#475569">{ad_s+ad_u} UNSAT equivalence miters</text>')
    a(f'<text x="{tx2}" y="{y_t+79}" font-size="10.8" font-weight="700" fill="#0f172a">• Mult CEC: Array vs. Wallace (5×5–10×10)</text>')
    a(f'<text x="{tx2+10}" y="{y_t+92}" font-size="9.3" fill="#475569">{mu_s+mu_u} UNSAT miters (up to 10×10 hard wall)</text>')
    a(f'<text x="{tx2}" y="{y_t+108}" font-size="10.8" font-weight="700" fill="#0f172a">• Mult Target Inversion (28b–36b)</text>')
    a(f'<text x="{tx2+10}" y="{y_t+121}" font-size="9.3" fill="#475569">{mt_s+mt_u} instances ({mt_s} SAT / {mt_u} UNSAT)</text>')
    a(f'<rect x="{tx2}" y="{y_t+128}" width="276" height="22" rx="5" fill="#eff6ff" stroke="#93c5fd" stroke-width="0.9"/>')
    a(f'<text x="{tx2+10}" y="{y_t+142.5}" font-size="9.2" font-weight="700" fill="#1e40af">Shortcut: AIG structural hashing &amp; FA/HA lifting</text>')

    # --- Pillar 3 (Bottom-Left, Red/Amber): Combinatorial Counting & Parity Invariants ---
    a(f'<rect x="{x_l}" y="{y_b}" width="{cw}" height="{ch}" rx="10" fill="#f8fafc" stroke="#fca5a5" stroke-width="1.4"/>')
    a(f'<rect x="{x_l}" y="{y_b}" width="{cw}" height="28" rx="10" fill="#dc2626"/>')
    a(f'<rect x="{x_l}" y="{y_b+16}" width="{cw}" height="12" fill="#dc2626"/>')
    a(f'<text x="{x_l+14}" y="{y_b+19}" font-size="12" font-weight="700" fill="#ffffff">3. Counting &amp; Coloring Invariants ({p3_s+p3_u}: {p3_s} SAT / {p3_u} UNSAT)</text>')

    # Mini Mutilated 4x4 Chessboard icon
    iy3 = y_b + 40
    a(f'<rect x="{ix}" y="{iy3}" width="112" height="108" rx="7" fill="#ffffff" stroke="#fecaca" stroke-width="1"/>')
    sq = 19
    bx0, by0 = ix + 18, iy3 + 10
    for r in range(4):
        for col_i in range(4):
            sx_c = bx0 + col_i * sq
            sy_c = by0 + r * sq
            if (r, col_i) in ((0, 0), (3, 3)):
                a(f'<rect x="{sx_c}" y="{sy_c}" width="{sq-1}" height="{sq-1}" rx="2" fill="#fef2f2" stroke="#dc2626" stroke-width="1" stroke-dasharray="2,2"/>')
                a(f'<text x="{sx_c+(sq-1)/2:.1f}" y="{sy_c+12.5}" text-anchor="middle" font-size="10" font-weight="700" fill="#dc2626">×</text>')
            else:
                dark = (r + col_i) % 2 == 1
                a(f'<rect x="{sx_c}" y="{sy_c}" width="{sq-1}" height="{sq-1}" rx="1.5" fill="{"#334155" if dark else "#e2e8f0"}"/>')
    a(f'<text x="{ix+56}" y="{iy3+99}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#b91c1c">8 Dark ≠ 6 Light</text>')

    ph_s, ph_u = c.get("php", (0, 0))
    ch_s, ch_u = c.get("chessboard", (0, 0))
    a(f'<text x="{tx}" y="{y_b+52}" font-size="11" font-weight="700" fill="#0f172a">• Pigeonhole Principle (PHP 8_7 .. 13_12)</text>')
    a(f'<text x="{tx+10}" y="{y_b+66}" font-size="9.5" fill="#475569">{ph_s+ph_u} UNSAT instances · n+1 pigeons into n holes</text>')
    a(f'<text x="{tx}" y="{y_b+88}" font-size="11" font-weight="700" fill="#0f172a">• Mutilated Chessboard (6×6 .. 14×14)</text>')
    a(f'<text x="{tx+10}" y="{y_b+102}" font-size="9.5" fill="#475569">{ch_s+ch_u} instances ({ch_s} SAT / {ch_u} UNSAT) · domino tiling</text>')
    a(f'<rect x="{tx}" y="{y_b+116}" width="276" height="32" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.9"/>')
    a(f'<text x="{tx+10}" y="{y_b+130}" font-size="9.5" font-weight="700" fill="#b91c1c">Shortcut: Cardinality / Bipartite Counting (2–5 ms)</text>')
    a(f'<text x="{tx+10}" y="{y_b+142}" font-size="9" fill="#991b1b">Resolution requires 2^Ω(n) steps on php_13_12</text>')

    # --- Pillar 4 (Bottom-Right, Green/Teal): Graph Structure & Random 3-SAT Control ---
    a(f'<rect x="{x_r}" y="{y_b}" width="{cw}" height="{ch}" rx="10" fill="#f8fafc" stroke="#6ee7b7" stroke-width="1.4"/>')
    a(f'<rect x="{x_r}" y="{y_b}" width="{cw}" height="28" rx="10" fill="#059669"/>')
    a(f'<rect x="{x_r}" y="{y_b+16}" width="{cw}" height="12" fill="#059669"/>')
    a(f'<text x="{x_r+14}" y="{y_b+19}" font-size="12" font-weight="700" fill="#ffffff">4. Graph Obstructions &amp; 3-SAT Control ({p4_s+p4_u}: {p4_s} SAT / {p4_u} UNSAT)</text>')

    # Mini Cut-Vertex Obstruction icon
    a(f'<rect x="{ix2}" y="{iy3}" width="112" height="108" rx="7" fill="#ffffff" stroke="#a7f3d0" stroke-width="1"/>')
    # Left triangle + cut vertex + right triangle
    gn = [(ix2+20, iy3+28), (ix2+20, iy3+68), (ix2+56, iy3+48), (ix2+92, iy3+28), (ix2+92, iy3+68)]
    for u, v in [(0,1),(0,2),(1,2),(2,3),(2,4),(3,4)]:
        a(f'<line x1="{gn[u][0]}" y1="{gn[u][1]}" x2="{gn[v][0]}" y2="{gn[v][1]}" stroke="#059669" stroke-width="1.5"/>')
    for idx_g, (gx, gy_g) in enumerate(gn):
        is_cut = idx_g == 2
        a(f'<circle cx="{gx}" cy="{gy_g}" r="{9 if is_cut else 7}" fill="{"#fef2f2" if is_cut else "#ecfdf5"}" stroke="{"#dc2626" if is_cut else "#059669"}" stroke-width="1.5"/>')
        if is_cut:
            a(f'<text x="{gx}" y="{gy_g+3.5}" text-anchor="middle" font-size="9" font-weight="700" fill="#dc2626">v*</text>')
    a(f'<text x="{ix2+56}" y="{iy3+98}" text-anchor="middle" font-size="8.6" font-weight="700" fill="#047857">Cut-vertex → No Ham.</text>')

    hm_s, hm_u = c.get("ham", (0, 0))
    r3_s, r3_u = c.get("random3sat", (0, 0))
    a(f'<text x="{tx2}" y="{y_b+52}" font-size="11" font-weight="700" fill="#0f172a">• Hamiltonian Cycle (Planted, Bipartite, Cut-v)</text>')
    a(f'<text x="{tx2+10}" y="{y_b+66}" font-size="9.5" fill="#475569">{hm_s+hm_u} instances ({hm_s} SAT / {hm_u} UNSAT) · graph invariants</text>')
    a(f'<text x="{tx2}" y="{y_b+88}" font-size="11" font-weight="700" fill="#0f172a">• Uniform Random 3-SAT Control (n = 150–250)</text>')
    a(f'<text x="{tx2+10}" y="{y_b+102}" font-size="9.5" fill="#475569">{r3_s+r3_u} instances ({r3_s} SAT / {r3_u} UNSAT) · zero shortcuts</text>')
    a(f'<rect x="{tx2}" y="{y_b+116}" width="276" height="32" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="0.9"/>')
    a(f'<text x="{tx2+10}" y="{y_b+130}" font-size="9.5" font-weight="700" fill="#047857">Shortcut: Biconnectivity / Bipartite Balance Check</text>')
    a(f'<text x="{tx2+10}" y="{y_b+142}" font-size="9" fill="#065f46">Random 3-SAT calibrates raw CDCL vs. shortcut gains</text>')

    # Bottom Summary Strip (y=424..464)
    sy_b = 424
    a(f'<rect x="24" y="{sy_b}" width="872" height="40" rx="8" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>')
    a(f'<text x="40" y="{sy_b+17}" font-size="10.8" font-weight="700" fill="#0f172a">Tier 1 Corpus Totals (SHA-256 Verified, 4 Formats):</text>')
    a(f'<text x="336" y="{sy_b+17}" font-size="10.5" fill="#334155">{tot} CNFs ({sat_tot} SAT / {unsat_tot} UNSAT) · Vars 30–3,370 · Clauses 80–115,281 · 6,793 native XORs</text>')
    a(f'<text x="40" y="{sy_b+32}" font-size="9.6" fill="#475569">Companion Challenge Tiers: Tier 2 Neutral Corpus (SC 2024–2026 Main Track, 1,166 CNFs) · Tier 3 Unstructured Random 3-SAT (n = 300–500, α = 4.26)</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
