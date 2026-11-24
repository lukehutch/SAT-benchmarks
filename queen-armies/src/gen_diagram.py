#!/usr/bin/env python3
"""Generate illustrative SVG diagram for queen-armies (Peaceable Queen Armies).

Renders two verified OEIS-optimal peaceable queen-army placements side-by-side:
  - Left:  A = 2 armies on 8x8, k = 9 queens/army (OEIS A250000 maximum)
  - Right: A = 3 armies on 9x9, k = 5 queens/army (OEIS A277433 maximum)
Verifies programmatically that zero queens attack any opposing-army queen along
any row, column, or diagonal, and writes ../diagram.svg using stdlib only.
"""
from __future__ import annotations

from pathlib import Path

# Verified optimal placements (solved via gen_queen_armies.py + Frobenius)
ARMIES_A2_8X8: list[list[tuple[int, int]]] = [
    [(5, 6), (5, 7), (6, 2), (6, 6), (6, 7), (7, 2), (7, 3), (7, 6), (7, 7)],
    [(0, 4), (0, 5), (1, 4), (1, 5), (2, 0), (2, 5), (3, 0), (3, 1), (4, 1)],
]

ARMIES_A3_9X9: list[list[tuple[int, int]]] = [
    [(2, 8), (8, 5), (8, 6), (8, 7), (8, 8)],
    [(5, 1), (6, 0), (6, 1), (7, 0), (7, 1)],
    [(0, 2), (0, 3), (0, 4), (1, 3), (1, 4)],
]


def verify_peaceable(rows: int, cols: int, armies: list[list[tuple[int, int]]]) -> None:
    seen: set[tuple[int, int]] = set()
    for a in armies:
        for r, c in a:
            assert 0 <= r < rows and 0 <= c < cols
            assert (r, c) not in seen
            seen.add((r, c))
    for i in range(len(armies)):
        for j in range(i + 1, len(armies)):
            for r1, c1 in armies[i]:
                for r2, c2 in armies[j]:
                    assert r1 != r2 and c1 != c2 and abs(r1 - r2) != abs(c1 - c2), (
                        f"Conflict between army {i} {(r1,c1)} and army {j} {(r2,c2)}"
                    )


def draw_board(
    out: list[str],
    bx: int,
    by: int,
    rows: int,
    cols: int,
    cell: int,
    armies: list[list[tuple[int, int]]],
    colors: list[tuple[str, str, str]],
    show_attack_tint: bool = False,
) -> None:
    """Draw chessboard, optional territory tint, and crisp queen tokens."""
    # Precompute attacked squares by each army if requested
    att_by: dict[tuple[int, int], set[int]] = {}
    if show_attack_tint:
        for ai, qs in enumerate(armies):
            for qr, qc in qs:
                for r in range(rows):
                    for c in range(cols):
                        if r == qr or c == qc or abs(r - qr) == abs(c - qc):
                            att_by.setdefault((r, c), set()).add(ai)

    out.append(f'  <rect x="{bx-3}" y="{by-3}" width="{cols*cell+6}" height="{rows*cell+6}" rx="5" fill="#334155"/>')

    occ = {(r, c): ai for ai, qs in enumerate(armies) for r, c in qs}

    for r in range(rows):
        for c in range(cols):
            x, y = bx + c * cell, by + r * cell
            is_dark = (r + c) % 2 == 1
            fill = "#e2e8f0" if is_dark else "#f8fafc"
            out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#cbd5e1" stroke-width="0.5"/>')

            if show_attack_tint and (r, c) not in occ:
                owners = att_by.get((r, c), set())
                if len(owners) == 1:
                    only_a = next(iter(owners))
                    tint = colors[only_a][1]
                    out.append(f'  <rect x="{x+1}" y="{y+1}" width="{cell-2}" height="{cell-2}" fill="{tint}" opacity="0.55"/>')

            if (r, c) in occ:
                ai = occ[(r, c)]
                main_c, soft_c, border_c = colors[ai]
                cx, cy = x + cell / 2.0, y + cell / 2.0
                rad = cell * 0.38
                out.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="{main_c}" stroke="#ffffff" stroke-width="1.8"/>')
                # Crisp vector crown silhouette (portable across all SVG renderers)
                s = cell * 0.21
                crown = (
                    f"M {cx-s:.1f},{cy+s*0.65:.1f} "
                    f"L {cx-s*1.05:.1f},{cy-s*0.55:.1f} "
                    f"L {cx-s*0.45:.1f},{cy+s*0.05:.1f} "
                    f"L {cx:.1f},{cy-s*0.85:.1f} "
                    f"L {cx+s*0.45:.1f},{cy+s*0.05:.1f} "
                    f"L {cx+s*1.05:.1f},{cy-s*0.55:.1f} "
                    f"L {cx+s:.1f},{cy+s*0.65:.1f} Z"
                )
                out.append(f'  <path d="{crown}" fill="#ffffff"/>')


def build_svg() -> str:
    verify_peaceable(8, 8, ARMIES_A2_8X8)
    verify_peaceable(9, 9, ARMIES_A3_9X9)

    W, H = 940, 505
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.8px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .badge { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Peaceable Queen Armies — Multi-Army Non-Attacking Placements</text>')
    out.append('  <text x="26" y="54" class="sub">Place A armies of ≥ k queens on an R×C board so no queen attacks a different army along any row, column, or diagonal</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Colors: (fill, soft_tint, border)
    cols_2 = [("#2563eb", "#bfdbfe", "#1d4ed8"), ("#d97706", "#fde68a", "#b45309")]
    cols_3 = [("#2563eb", "#dbeafe", "#1d4ed8"), ("#059669", "#d1fae5", "#047857"), ("#dc2626", "#fee2e2", "#b91c1c")]

    # Left panel: A=2 on 8x8, k=9
    out.append('  <rect x="24" y="80" width="438" height="328" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="40" y="104" class="h3">A = 2 Armies · 8×8 Board · k = 9 (OEIS A250000)</text>')
    out.append('  <rect x="348" y="90" width="102" height="21" rx="10.5" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append('  <text x="399" y="104" text-anchor="middle" class="badge">0 attacks ✓</text>')
    draw_board(out, 115, 118, 8, 8, 32, ARMIES_A2_8X8, cols_2, show_attack_tint=True)
    out.append('  <text x="40" y="394" class="body">Blue (9) vs Amber (9): exclusive attack corridors never cross.</text>')

    # Right panel: A=3 on 9x9, k=5
    out.append('  <rect x="478" y="80" width="438" height="328" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="494" y="104" class="h3">A = 3 Armies · 9×9 Board · k = 5 (OEIS A277433)</text>')
    out.append('  <rect x="802" y="90" width="102" height="21" rx="10.5" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append('  <text x="853" y="104" text-anchor="middle" class="badge">0 attacks ✓</text>')
    draw_board(out, 571, 118, 9, 9, 28, ARMIES_A3_9X9, cols_3, show_attack_tint=False)
    out.append('  <text x="494" y="394" class="body">Blue (5), Emerald (5), Rose (5): same-army clusters pack tightly in corners.</text>')

    # Bottom CNF encoding & suite summary bar
    out.append('  <rect x="24" y="420" width="892" height="68" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append('  <text x="40" y="442" class="mono">CNF Encoding:  q(r,c,a) ⇒ L(ℓ,a)  +  (¬L(ℓ,a) ∨ ¬L(ℓ,b)) ∀line ℓ, a&lt;b  +  Sinz counter ∑ q(r,c,a) ≥ k</text>')
    out.append('  <text x="40" y="461" class="body">Same-army queens may freely share rows, columns, and diagonals; every line ℓ belongs to at most one army.</text>')
    out.append('  <text x="40" y="478" class="body">Suite (8 instances · 4 SAT / 4 UNSAT): scales to 15×16 (A=2, k=33), 15×16 (A=3, k=16), and 14×16 (A=4, k=9).</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
