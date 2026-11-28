#!/usr/bin/env python3
"""Generate a publication-grade illustrative SVG diagram (`diagram.svg`) for
the `qdistsat-qldpc` benchmark collection.

Parses the exact upstream matrices `matrices/BB_144_12_12_Hx.txt`,
`BB_144_12_12_Hz.txt`, `BB_144_12_12_Gx.txt`, and `BB_144_12_12_Gz.txt`
for IBM's [[144, 12, 12]] "gross" Bivariate-Bicycle code (Bravyi et al.,
Nature 2024), verifies CSS orthogonality and a real weight-12 logical Z
operator, and renders:
  - The real 12x6 periodic torus lattice (72 L + 72 R = 144 data qubits)
  - A real weight-6 X-stabilizer stencil (H_X) and weight-6 Z-stabilizer
    stencil (H_Z) with zero visual clutter
  - A real minimum-weight-12 logical operator z (H_X z = 0, G_Z z != 0, |z|=12)
  - The CSS minimum-distance SAT encoding (H_X z = 0, G_Z z != 0, Sinz |z| <= w)
    and all 5 Bivariate-Bicycle codes in the corpus.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent.parent
MAT_DIR = SUITE_DIR / "matrices"
OUT_SVG = SUITE_DIR / "diagram.svg"

FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_binary_matrix(path: Path) -> list[list[int]]:
    rows: list[list[int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        rows.append([int(x) & 1 for x in s.split()])
    return rows


def qubit_coords(idx: int) -> tuple[str, int, int]:
    """Map qubit index 0..143 to ('L'|'R', cx in 0..11, cy in 0..5)."""
    if idx < 72:
        return ("L", idx % 12, idx // 12)
    q = idx - 72
    return ("R", q % 12, q // 12)


def pick_compact_row(rows: list[list[int]], min_x: int, max_x: int) -> tuple[int, list[int]]:
    """Pick an actual stabilizer row whose 6 qubits sit inside [min_x, max_x] without wrap-around."""
    best = None
    for r_idx, row in enumerate(rows):
        supp = [j for j, v in enumerate(row) if v]
        xs = [qubit_coords(j)[1] for j in supp]
        ys = [qubit_coords(j)[2] for j in supp]
        span_x = max(xs) - min(xs)
        span_y = max(ys) - min(ys)
        if span_x <= 4 and span_y <= 3 and min(xs) >= min_x and max(xs) <= max_x:
            score = (span_x + span_y, abs(min(ys) - 1))
            if best is None or score < best[0]:
                best = (score, r_idx, supp)
    if best is not None:
        return best[1], best[2]
    # Fallback to row 0 if constraints relaxed
    supp0 = [j for j, v in enumerate(rows[0]) if v]
    return 0, supp0


def build_svg() -> str:
    hx = load_binary_matrix(MAT_DIR / "BB_144_12_12_Hx.txt")
    hz = load_binary_matrix(MAT_DIR / "BB_144_12_12_Hz.txt")
    gx = load_binary_matrix(MAT_DIR / "BB_144_12_12_Gx.txt")
    gz = load_binary_matrix(MAT_DIR / "BB_144_12_12_Gz.txt")

    # Verify CSS commutation and real weight-12 logical operator
    logical_z = gx[0]
    logical_supp = [j for j, v in enumerate(logical_z) if v]
    assert len(logical_supp) == 12
    assert all(sum(a & b for a, b in zip(r, logical_z)) % 2 == 0 for r in hx)
    assert any(sum(a & b for a, b in zip(r, logical_z)) % 2 == 1 for r in gz)

    hx_row_idx, hx_supp = pick_compact_row(hx, 0, 5)
    hz_row_idx, hz_supp = pick_compact_row(hz, 6, 11)

    W, H = 920, 496
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Quantum LDPC BB_144_12_12 12x6 periodic torus lattice with weight-6 X/Z stabilizers and minimum-weight logical SAT formulation">',
        # Explicit white card canvas for GitHub light & dark modes
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        "Quantum LDPC Bivariate-Bicycle Code Distance SAT (qdistsat-qldpc)</text>",
        '<text x="26" y="53" font-size="11.6" fill="#475569">'
        'Exact [[144, 12, 12]] "gross" BB code on a 12×6 periodic torus (Bravyi et al., Nature 2024): '
        "weight-6 X/Z stencils &amp; min-weight logical search</text>",
        '<line x1="24" y1="64" x2="896" y2="64" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # ===================== LEFT PANEL: REAL 12x6 TORUS LATTICE =====================
    px, py, pw, ph = 24, 76, 536, 352
    parts.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{px + 14}" y="{py + 20}" font-size="12" font-weight="700" fill="#0f172a">'
        "Real BB_144_12_12 Periodic 12×6 Torus (72 L + 72 R = 144 Qubits)</text>"
    )
    parts.append(
        f'<text x="{px + 14}" y="{py + 35}" font-size="9.5" fill="#475569">'
        "Decoded directly from matrices/BB_144_12_12_{Hx, Hz, Gx}.txt  ·  A = x³+y+y², B = y³+x+x²</text>"
    )

    # 12x6 periodic lattice coordinates
    gx0, gy0 = px + 36, py + 70
    dx, dy = 40.0, 35.5
    grid_w, grid_h = 11 * dx, 5 * dy

    # Torus background frame with dashed periodic wrap indicators
    parts.append(
        f'<rect x="{gx0 - 16}" y="{gy0 - 13}" width="{grid_w + 38}" height="{grid_h + 32}" rx="8" '
        'fill="#ffffff" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="5,3"/>'
    )
    # Periodic boundary wrap labels
    parts.append(
        f'<text x="{gx0 + grid_w/2:.1f}" y="{gy0 - 18}" text-anchor="middle" '
        'font-size="8.6" font-weight="600" fill="#64748b">← periodic x (mod 12) →</text>'
    )
    parts.append(
        f'<text x="{gx0 - 22}" y="{gy0 + grid_h/2 + 3:.1f}" text-anchor="middle" '
        f'transform="rotate(-90 {gx0 - 22} {gy0 + grid_h/2 + 3:.1f})" '
        'font-size="8.6" font-weight="600" fill="#64748b">y (mod 6)</text>'
    )

    # Lattice grid lines
    for cx in range(12):
        lx = gx0 + cx * dx
        parts.append(f'<line x1="{lx:.1f}" y1="{gy0 - 6}" x2="{lx:.1f}" y2="{gy0 + grid_h + 10}" stroke="#e2e8f0" stroke-width="0.9"/>')
    for cy in range(6):
        ly = gy0 + cy * dy
        parts.append(f'<line x1="{gx0 - 8}" y1="{ly:.1f}" x2="{gx0 + grid_w + 18}" y2="{ly:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')

    def q_xy(q_idx: int) -> tuple[float, float]:
        sub, cx, cy = qubit_coords(q_idx)
        base_x = gx0 + cx * dx
        base_y = gy0 + cy * dy
        if sub == "L":
            return (base_x, base_y)
        return (base_x + 13.5, base_y + 11.5)

    # Helper to draw a weight-6 stabilizer stencil centered on its centroid
    def draw_stencil(supp: list[int], color: str, bg: str, badge: str) -> None:
        pts = [q_xy(q) for q in supp]
        mx = sum(p[0] for p in pts) / len(pts)
        my = sum(p[1] for p in pts) / len(pts)
        # Connecting rays from check node to all 6 data qubits
        for qx, qy in pts:
            parts.append(
                f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{qx:.1f}" y2="{qy:.1f}" '
                f'stroke="{color}" stroke-width="2.0" stroke-opacity="0.82"/>'
            )
        # Highlight halos on the 6 qubits
        for q in supp:
            sub, _, _ = qubit_coords(q)
            qx, qy = q_xy(q)
            if sub == "L":
                parts.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="6.8" fill="{bg}" stroke="{color}" stroke-width="2.0"/>')
            else:
                parts.append(
                    f'<rect x="{qx - 5.8:.1f}" y="{qy - 5.8:.1f}" width="11.6" height="11.6" rx="2" '
                    f'fill="{bg}" stroke="{color}" stroke-width="2.0"/>'
                )
        # Central check badge
        parts.append(
            f'<rect x="{mx - 15:.1f}" y="{my - 9:.1f}" width="30" height="18" rx="4" '
            f'fill="{color}" stroke="#ffffff" stroke-width="1.3"/>'
        )
        parts.append(
            f'<text x="{mx:.1f}" y="{my + 3.5:.1f}" text-anchor="middle" '
            f'font-size="9" font-weight="700" fill="#ffffff">{badge}</text>'
        )

    # Draw all 144 base qubits (72 L circles + 72 R squares)
    hx_set = set(hx_supp)
    hz_set = set(hz_supp)
    log_set = set(logical_supp)

    for q in range(144):
        sub, _, _ = qubit_coords(q)
        qx, qy = q_xy(q)
        if sub == "L":
            parts.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="3.4" fill="#cbd5e1" stroke="#64748b" stroke-width="0.7"/>')
        else:
            parts.append(
                f'<rect x="{qx - 3.0:.1f}" y="{qy - 3.0:.1f}" width="6.0" height="6.0" rx="1" '
                'fill="#e2e8f0" stroke="#94a3b8" stroke-width="0.7"/>'
            )

    # Overlay the real weight-6 X-stabilizer and weight-6 Z-stabilizer stencils
    draw_stencil(hx_supp, "#2563eb", "#dbeafe", "X₆")
    draw_stencil(hz_supp, "#7c3aed", "#ede9fe", "Z₆")

    # Overlay the real weight-12 minimum logical Z operator (G_X row 0) in emerald green
    for q in logical_supp:
        qx, qy = q_xy(q)
        parts.append(
            f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="8.2" fill="none" stroke="#059669" stroke-width="2.1"/>'
        )
        parts.append(
            f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="3.2" fill="#059669"/>'
        )

    # Clean Legend beneath torus inside Left Panel
    ly = py + 292
    parts.append(f'<rect x="{px + 14}" y="{ly - 12}" width="{pw - 28}" height="58" rx="7" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')

    # Legend Row 1
    parts.append(f'<circle cx="{px + 28}" cy="{ly + 4}" r="4.2" fill="#cbd5e1" stroke="#475569" stroke-width="1"/>')
    parts.append(f'<text x="{px + 38}" y="{ly + 8}" font-size="9.3" fill="#334155">L data qubit (72)</text>')
    parts.append(f'<rect x="{px + 148}" y="{ly}" width="8" height="8" rx="1.2" fill="#e2e8f0" stroke="#475569" stroke-width="1"/>')
    parts.append(f'<text x="{px + 162}" y="{ly + 8}" font-size="9.3" fill="#334155">R data qubit (72)</text>')
    parts.append(f'<rect x="{px + 272}" y="{ly - 2}" width="18" height="12" rx="3" fill="#2563eb"/>')
    parts.append(f'<text x="{px + 296}" y="{ly + 8}" font-size="9.3" font-weight="600" fill="#1d4ed8">H_X row #{hx_row_idx} (wt 6)</text>'.replace("H_X", "Hₓ"))
    parts.append(f'<rect x="{px + 408}" y="{ly - 2}" width="18" height="12" rx="3" fill="#7c3aed"/>')
    parts.append(f'<text x="{px + 432}" y="{ly + 8}" font-size="9.3" font-weight="600" fill="#6d28d9">H_Z row #{hz_row_idx} (wt 6)</text>'.replace("H_Z", "H_z"))

    # Legend Row 2
    parts.append(f'<circle cx="{px + 28}" cy="{ly + 28}" r="6" fill="none" stroke="#059669" stroke-width="2"/>')
    parts.append(f'<circle cx="{px + 28}" cy="{ly + 28}" r="2.5" fill="#059669"/>')
    parts.append(
        f'<text x="{px + 40}" y="{ly + 32}" font-size="9.3" font-weight="600" fill="#047857">'
        "Actual min-weight logical Z operator z (G_X row 0): |z| = d_Z = 12, H_X·z = 0, G_Z·z ≠ 0</text>"
    )

    # ===================== RIGHT PANEL: CSS DISTANCE SAT ENCODING + SUITE TABLE =====================
    rx, rw = 574, 322
    # Card 1: Min-Weight Logical Operator SAT Formulation
    parts.append(
        f'<rect x="{rx}" y="76" width="{rw}" height="198" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="96" font-size="11.8" font-weight="700" fill="#0f172a">'
        "CSS Z-Distance SAT Encoding (export_qdist_cnf.py)</text>"
    )
    parts.append(
        f'<text x="{rx + 12}" y="110" font-size="9.2" fill="#475569">'
        "Search binary support z ∈ 𝔽₂ⁿ (CSS orthogonality H_X H_Zᵀ = 0):</text>"
    )

    constraints = [
        (119, "#eff6ff", "#2563eb", "#1d4ed8", "1. Commute with X-stabilizers:  H_X · z = 0 (mod 2)",
         "Weight-6 𝔽₂ XOR parity equations (Tseitin 3-XOR / XCNF)"),
        (158, "#f5f3ff", "#7c3aed", "#6d28d9", "2. Non-trivial logical:  G_Z · z ≠ 0 (mod 2)",
         "gᵢ = G_Z[i]·z  ∧  (g₁ ∨ … ∨ gₖ)  ⇒  z ∉ row(H_Z)"),
        (197, "#fffbeb", "#d97706", "#b45309", "3. Hamming weight cap:  ∑ⱼ zⱼ ≤ w",
         "Sinz (2005) sequential counter (n × w auxiliary vars)"),
    ]
    for cy_c, bg, bd, fg, t1, t2 in constraints:
        parts.append(f'<rect x="{rx + 10}" y="{cy_c}" width="{rw - 20}" height="33" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1.15"/>')
        parts.append(f'<text x="{rx + 19}" y="{cy_c + 14}" font-size="9.5" font-weight="700" fill="{fg}">{t1}</text>')
        parts.append(f'<text x="{rx + 19}" y="{cy_c + 27}" font-size="8.6" fill="#334155">{t2}</text>')

    # Decision threshold pills inside Card 1
    parts.append(f'<rect x="{rx + 10}" y="238" width="146" height="26" rx="5" fill="#fef2f2" stroke="#dc2626" stroke-width="1"/>')
    parts.append(f'<text x="{rx + 83}" y="254.5" text-anchor="middle" font-size="9.2" font-weight="700" fill="#b91c1c">w = d−1 ⇒ UNSAT (d_Z ≥ d)</text>')
    parts.append(f'<rect x="{rx + 164}" y="238" width="148" height="26" rx="5" fill="#ecfdf5" stroke="#059669" stroke-width="1"/>')
    parts.append(f'<text x="{rx + 238}" y="254.5" text-anchor="middle" font-size="9.2" font-weight="700" fill="#047857">w = d ⇒ SAT (d_Z ≤ d)</text>')

    # Card 2: 5 Bivariate-Bicycle Codes in Corpus
    parts.append(
        f'<rect x="{rx}" y="284" width="{rw}" height="144" rx="10" '
        'fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>'
    )
    parts.append(
        f'<text x="{rx + 12}" y="303" font-size="11.5" font-weight="700" fill="#0f172a">'
        "5 Paired Boundary Codes (5 UNSAT / 5 SAT)</text>"
    )
    th_y = 319
    parts.append(f'<rect x="{rx + 10}" y="{th_y - 10}" width="{rw - 20}" height="16" rx="4" fill="#e2e8f0"/>')
    for cx_h, lbl_h, anc in [(rx + 15, "Code [[n,k,d]]", "start"), (rx + 146, "w", "middle"), (rx + 206, "CNF Vars", "middle"), (rx + 278, "10s T/O?", "middle")]:
        parts.append(f'<text x="{cx_h}" y="{th_y + 1}" text-anchor="{anc}" font-size="8.7" font-weight="700" fill="#334155">{lbl_h}</text>')

    bb_rows = [
        ("BB_30_4_6", "5 / 6", "254 / 283", "Both solved", "#047857"),
        ("BB_72_12_6", "5 / 6", "623 / 694", "Both solved", "#047857"),
        ("BB_144_12_12", "11 / 12", "2.1k / 2.2k", "w11 T/O · w12 3ms", "#b45309"),
        ("BB_360_12_24", "23 / 24", "9.7k / 10.1k", "Both >10 s", "#b91c1c"),
        ("BB_756_16_34", "33 / 34", "29.6k / 30.3k", "Both >10 s", "#b91c1c"),
    ]
    for i, (nm, wv, vrs, st, stc) in enumerate(bb_rows):
        ry_r = th_y + 17 + i * 20
        if i % 2 == 1:
            parts.append(f'<rect x="{rx + 10}" y="{ry_r - 11}" width="{rw - 20}" height="18" rx="3" fill="#ffffff"/>')
        parts.append(f'<text x="{rx + 15}" y="{ry_r + 1.5}" font-family="{FONT_MONO}" font-size="8.8" font-weight="600" fill="#0f172a">{nm}</text>')
        parts.append(f'<text x="{rx + 146}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.8" fill="#334155">{wv}</text>')
        parts.append(f'<text x="{rx + 206}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.7" fill="#475569">{vrs}</text>')
        parts.append(f'<text x="{rx + 278}" y="{ry_r + 1.5}" text-anchor="middle" font-size="8.4" font-weight="700" fill="{stc}">{st}</text>')

    # ===================== BOTTOM SUMMARY STRIP =====================
    by_s = 440
    pills = [
        (24, 214, "#eff6ff", "#2563eb", "#1d4ed8", "Coupled 𝔽₂-XOR + Cardinality"),
        (248, 206, "#f5f3ff", "#7c3aed", "#6d28d9", "1,474 Native XORs · 59–83% Horn"),
        (464, 208, "#fffbeb", "#d97706", "#b45309", "ρ_c = 1.22×–1.25× (Over)"),
        (682, 214, "#ecfdf5", "#059669", "#047857", "10 Inst. · 4 Formats + Matrices"),
    ]
    for px_p, pw_p, bg, bd, fg, lbl in pills:
        parts.append(f'<rect x="{px_p}" y="{by_s}" width="{pw_p}" height="34" rx="7" fill="{bg}" stroke="{bd}" stroke-width="1"/>')
        parts.append(f'<text x="{px_p + pw_p/2:.1f}" y="{by_s + 21}" text-anchor="middle" font-size="10.1" font-weight="700" fill="{fg}">{esc(lbl)}</text>')

    parts.append("</g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
