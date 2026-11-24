#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for guillochon-oeis-a250000-queens.

Renders the independently verified 15x15 peaceable queen armies placement (32 white + 32 black
queens, 0 mutual attacks) decoded directly from `solutions/queens_n15_m32.model.xz`.
"""
from __future__ import annotations

import lzma
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_true_vars(path: Path) -> set[int]:
    opener = lzma.open if path.suffix == ".xz" else open
    true_vars: set[int] = set()
    with opener(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ("c", "s"):
                continue
            toks = s.split()
            if toks[0] == "v":
                toks = toks[1:]
            for tok in toks:
                lit = int(tok)
                if lit > 0:
                    true_vars.add(lit)
    return true_vars


def verify_peaceable(board: list[list[str]]) -> tuple[int, int, int]:
    n = len(board)
    nw = nb = attacks = 0
    for r in range(n):
        for c in range(n):
            if board[r][c] == "W":
                nw += 1
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, -1), (-1, 1)):
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < n and 0 <= cc < n:
                        if board[rr][cc] == "B":
                            attacks += 1
                        rr += dr
                        cc += dc
            elif board[r][c] == "B":
                nb += 1
    return nw, nb, attacks


def build_svg() -> str:
    n = 15
    q_true = read_true_vars(ROOT / "solutions/queens_n15_m32.model.xz")
    board = [["." for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            w = (r * n + c + 1) in q_true
            b = (n * n + r * n + c + 1) in q_true
            assert not (w and b), f"Overlap at {(r, c)}"
            if w:
                board[r][c] = "W"
            elif b:
                board[r][c] = "B"
    nw, nb, attacks = verify_peaceable(board)
    assert nw == 32 and nb == 32 and attacks == 0, f"Invalid queens: {nw}W, {nb}B, {attacks} attacks"

    W, H = 960, 520
    els: list[str] = []
    add = els.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    add("""  <defs>
    <style>
      .title { font: 700 17.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .subtitle { font: 400 11.8px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .ptitle { font: 700 13px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .psub { font: 400 11px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #475569; }
      .mono { font: 700 9.8px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #334155; }
      .mono-sm { font: 600 8.8px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #64748b; }
      .badge { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .cap { font: 400 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #334155; }
      .cap-b { font: 700 10.5px "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; fill: #0f172a; }
    </style>
  </defs>""")

    add(f'  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    add('  <text x="24" y="33" class="title">OEIS A250000 — Peaceable Coexisting Armies of Queens</text>')
    add('  <text x="24" y="52" class="subtitle">Maximum m such that m white and m black queens fit on an n x n chessboard with zero opposing-color queen attacks</text>')
    add('  <rect x="774" y="14" width="162" height="24" rx="12" fill="#7c3aed"/>')
    add('  <text x="855" y="30" text-anchor="middle" class="badge">OPEN: n=21, m=65?</text>')

    # Left Card: Verified 15x15 Board
    add('  <rect x="20" y="68" width="496" height="432" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="36" y="90" class="ptitle">Verified Frobenius 15x15 Model: 32 White + 32 Black Queens</text>')
    add('  <text x="36" y="106" class="psub">Decoded from solutions/queens_n15_m32.model.xz (exact optimal a(15) = 32; 0 attacks)</text>')

    cell = 22.8
    bw = n * cell
    bx0 = 20 + (496 - bw) / 2.0 + 6
    by0 = 120.0
    add(f'  <rect x="{bx0-1.5:.1f}" y="{by0-1.5:.1f}" width="{bw+3:.1f}" height="{bw+3:.1f}" fill="none" stroke="#475569" stroke-width="1.5"/>')

    for i in range(n):
        add(f'  <text x="{bx0 - 8:.1f}" y="{by0 + i*cell + cell*0.66:.1f}" text-anchor="end" class="mono-sm">{i+1}</text>')
        add(f'  <text x="{bx0 + i*cell + cell/2:.1f}" y="{by0 + bw + 14:.1f}" text-anchor="middle" class="mono-sm">{chr(ord("a")+i)}</text>')

    for r in range(n):
        for c in range(n):
            x = bx0 + c * cell
            y = by0 + r * cell
            sq = "#f1f5f9" if (r + c) % 2 == 0 else "#cbd5e1"
            add(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" fill="{sq}"/>')
            cx, cy = x + cell / 2.0, y + cell / 2.0
            if board[r][c] == "W":
                add(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.2" fill="#ffffff" stroke="#0f172a" stroke-width="1.6"/>')
                add(f'  <text x="{cx:.1f}" y="{cy+3.5:.1f}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="10.5" font-weight="700" fill="#0f172a">W</text>')
            elif board[r][c] == "B":
                add(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.2" fill="#1e1b4b" stroke="#0f172a" stroke-width="1.2"/>')
                add(f'  <text x="{cx:.1f}" y="{cy+3.5:.1f}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="10.5" font-weight="700" fill="#ffffff">B</text>')

    # Legend under board
    add('  <circle cx="110" cy="487" r="6" fill="#ffffff" stroke="#0f172a" stroke-width="1.5"/>')
    add('  <text x="122" y="491" class="cap"><tspan class="cap-b">32 White queens</tspan> (same-color attacks OK)</text>')
    add('  <circle cx="344" cy="487" r="6" fill="#1e1b4b"/>')
    add('  <text x="356" y="491" class="cap"><tspan class="cap-b">32 Black queens</tspan></text>')

    # Right Top Card: Non-Attack Ray Constraints & Sinz Encoding
    add('  <rect x="532" y="68" width="408" height="210" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="90" class="ptitle">Queen Non-Attack Rays &amp; CNF Structure</text>')
    add('  <text x="548" y="106" class="psub">2n^2 board vars W(r,c), B(r,c) + Sinz sequential counters (&gt;= m each)</text>')

    # 5x5 schematic board
    mc = 26.0
    mx0, my0 = 552.0, 122.0
    for r in range(5):
        for c in range(5):
            x, y = mx0 + c * mc, my0 + r * mc
            is_ray = (r == 2 or c == 2 or abs(r - 2) == abs(c - 2)) and not (r == 2 and c == 2)
            fill = "#fee2e2" if is_ray else ("#ffffff" if (r + c) % 2 == 0 else "#e2e8f0")
            add(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{mc:.1f}" height="{mc:.1f}" fill="{fill}" stroke="#cbd5e1" stroke-width="0.8"/>')
    # Dashed attack axes through (2,2)
    qx, qy = mx0 + 2.5 * mc, my0 + 2.5 * mc
    for (x1, y1, x2, y2) in [
        (mx0 + 4, qy, mx0 + 5 * mc - 4, qy),
        (qx, my0 + 4, qx, my0 + 5 * mc - 4),
        (mx0 + 4, my0 + 4, mx0 + 5 * mc - 4, my0 + 5 * mc - 4),
        (mx0 + 4, my0 + 5 * mc - 4, mx0 + 5 * mc - 4, my0 + 4),
    ]:
        add(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ef4444" stroke-width="1.3" stroke-dasharray="3,2"/>')
    # Center W queen
    add(f'  <circle cx="{qx:.1f}" cy="{qy:.1f}" r="9" fill="#ffffff" stroke="#0f172a" stroke-width="1.6"/>')
    add(f'  <text x="{qx:.1f}" y="{qy+3.5:.1f}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="10" font-weight="700" fill="#0f172a">W</text>')
    # Allowed W on same row (2,4)
    wx, wy = mx0 + 4.5 * mc, my0 + 2.5 * mc
    add(f'  <circle cx="{wx:.1f}" cy="{wy:.1f}" r="7.5" fill="#ffffff" stroke="#059669" stroke-width="1.8"/>')
    add(f'  <text x="{wx:.1f}" y="{wy+3:.1f}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="9" font-weight="700" fill="#059669">W</text>')
    # Safe B at knight move (0,1)
    bx, by = mx0 + 1.5 * mc, my0 + 0.5 * mc
    add(f'  <circle cx="{bx:.1f}" cy="{by:.1f}" r="7.5" fill="#1e1b4b" stroke="#059669" stroke-width="1.8"/>')
    add(f'  <text x="{bx:.1f}" y="{by+3:.1f}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="9" font-weight="700" fill="#ffffff">B</text>')
    # Forbidden B mark on diagonal (4,4)
    fx, fy = mx0 + 4.5 * mc, my0 + 4.5 * mc
    add(f'  <text x="{fx:.1f}" y="{fy+4:.1f}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" fill="#dc2626">X</text>')

    # Explanations on right of mini-board
    tx = 696
    add(f'  <text x="{tx}" y="136" class="cap-b">Clause Types:</text>')
    add(f'  <text x="{tx}" y="154" class="cap">1. Cell exclusion: (~W v ~B)</text>')
    add(f'  <text x="{tx}" y="171" class="cap">2. Cross-color rays: (~W_p v ~B_q)</text>')
    add(f'  <text x="{tx}" y="186" class="cap">   along rows, cols, +/-45 deg.</text>')
    add(f'  <text x="{tx}" y="203" class="cap">3. Sinz counters: sum(W) &gt;= m</text>')
    add(f'  <text x="{tx}" y="218" class="cap">   and sum(B) &gt;= m.</text>')
    add(f'  <text x="{tx}" y="242" class="cap"><tspan fill="#059669" font-weight="700">Green ring:</tspan> legal placements</text>')
    add(f'  <text x="{tx}" y="258" class="cap"><tspan fill="#dc2626" font-weight="700">Red rays / X:</tspan> B forbidden</text>')

    # Right Bottom Card: OEIS A250000 Ladder Bar Chart
    add('  <rect x="532" y="290" width="408" height="210" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    add('  <text x="548" y="312" class="ptitle">OEIS A250000 Optimal Ladder &amp; Ainley Frontier (20 CNFs)</text>')
    add('  <text x="548" y="328" class="psub">Known optimal n &lt;= 20 (n = 16-20: Jason Davies, Nov 2026); open n = 21</text>')

    data = [
        (12, 21, False), (13, 24, False), (14, 28, False), (15, 32, False),
        (16, 37, False), (17, 42, False), (18, 47, False), (19, 52, False),
        (20, 58, False), (21, 64, True),
    ]
    base_y = 446.0
    max_h = 92.0
    bx_start = 550.0
    bar_w = 29.0
    bar_g = 9.0
    for i, (nn, mm, is_open) in enumerate(data):
        x = bx_start + i * (bar_w + bar_g)
        bh = (mm / 65.0) * max_h
        y = base_y - bh
        col = "#7c3aed" if is_open else ("#0d9488" if nn <= 15 else "#3b82f6")
        add(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="4" fill="{col}" fill-opacity="0.88"/>')
        if is_open:
            # dashed cap for open m=65
            bh65 = max_h
            add(f'  <rect x="{x:.1f}" y="{base_y-bh65-6:.1f}" width="{bar_w:.1f}" height="8" rx="2" fill="#fee2e2" stroke="#dc2626" stroke-width="1.1" stroke-dasharray="2,1"/>')
        lbl = f"{mm}+" if is_open else str(mm)
        add(f'  <text x="{x+bar_w/2:.1f}" y="{y-4 if not is_open else base_y-max_h-9:.1f}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="8.8" font-weight="700" fill="{col if not is_open else "#dc2626"}">{lbl}</text>')
        add(f'  <text x="{x+bar_w/2:.1f}" y="{base_y+14:.1f}" text-anchor="middle" class="mono-sm">{nn}</text>')

    add('  <text x="548" y="476" class="cap"><tspan fill="#0d9488" font-weight="700">Teal (n=12..15):</tspan> verified SAT models in solutions/</text>')
    add('  <text x="548" y="492" class="cap"><tspan fill="#dc2626" font-weight="700">Open queens_n21_m65:</tspan> 331,762 vars, 691,449 clauses (Ainley 1977: &gt;= 64).</text>')

    add("</svg>")
    return "\n".join(els) + "\n"


def main() -> None:
    svg = build_svg()
    out = ROOT / "diagram.svg"
    out.write_text(svg, encoding="utf-8")
    ET.parse(out)
    print(f"Wrote and XML-validated {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
