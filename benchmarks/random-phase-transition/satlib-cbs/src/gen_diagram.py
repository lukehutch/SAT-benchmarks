#!/usr/bin/env python3
"""Generate standalone illustrative SVG diagram for satlib-cbs."""
from __future__ import annotations

import re
from pathlib import Path

COL = Path(__file__).resolve().parent.parent
OUT = COL / "diagram.svg"

W, H = 920, 460
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def parse_cbs() -> list[tuple[int, int, int, str]]:
    """Parse (n, m, b, stem) from cnf-orig/CBS_*.cnf.xz."""
    items = []
    cnf_dir = COL / "cnf-orig"
    pat = re.compile(r"CBS_k3_n(\d+)_m(\d+)_b(\d+)_\d+")
    if cnf_dir.is_dir():
        for p in sorted(cnf_dir.glob("*.cnf.xz")):
            stem = p.name.replace(".cnf.xz", "")
            m = pat.match(stem)
            if m:
                items.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), stem))
    return sorted(items, key=lambda t: (t[1], t[2]))


def draw_assignment_grid(
    a,
    x0: float,
    y0: float,
    title: str,
    subtitle: str,
    frozen_cols: int,
    total_cols: int,
    rows_bits: list[list[int]],
    accent: str,
    accent_bg: str,
) -> None:
    cw, ch = 19, 19
    gap = 3
    box_w = 500
    box_h = 158
    a(f'<rect x="{x0}" y="{y0}" width="{box_w}" height="{box_h}" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.1"/>')
    a(f'<text x="{x0+12}" y="{y0+20}" font-size="12" font-weight="700" fill="#0f172a">{title}</text>')
    a(f'<text x="{x0+12}" y="{y0+35}" font-size="10" fill="#475569">{subtitle}</text>')

    gx = x0 + 48
    gy = y0 + 50
    # Highlight frozen backbone columns
    if frozen_cols > 0:
        fw = frozen_cols * (cw + gap) - gap + 6
        fh = len(rows_bits) * (ch + gap) - gap + 6
        a(f'<rect x="{gx-3}" y="{gy-3}" width="{fw}" height="{fh}" rx="5" fill="{accent_bg}" stroke="{accent}" stroke-width="1.4"/>')

    for r_i, bits in enumerate(rows_bits):
        ry = gy + r_i * (ch + gap)
        a(f'<text x="{gx-9}" y="{ry+13.5}" text-anchor="end" font-family="{MONO}" font-size="10" font-weight="600" fill="#475569">σ{chr(0x2081+r_i)}</text>')
        for c_i, bit in enumerate(bits):
            cx = gx + c_i * (cw + gap)
            is_frozen = c_i < frozen_cols
            if is_frozen:
                fill = "#7c3aed" if bit == 1 else "#ddd6fe"
                txt_col = "#ffffff" if bit == 1 else "#4c1d95"
                stroke = "#6d28d9"
            else:
                fill = "#eff6ff" if bit == 1 else "#f1f5f9"
                txt_col = "#1d4ed8" if bit == 1 else "#64748b"
                stroke = "#93c5fd" if bit == 1 else "#cbd5e1"
            a(f'<rect x="{cx}" y="{ry}" width="{cw}" height="{ch}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="0.9"/>')
            a(f'<text x="{cx+cw/2:.1f}" y="{ry+13.5}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="{txt_col}">{bit}</text>')

    # Bottom span labels under frozen vs free columns
    span_y = gy + len(rows_bits) * (ch + gap) + 12
    fw_end = gx + frozen_cols * (cw + gap) - gap
    free_start = fw_end + gap
    free_end = gx + total_cols * (cw + gap) - gap
    a(f'<text x="{(gx + fw_end)/2:.1f}" y="{span_y}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{accent}">Frozen ({frozen_cols*5}%)</text>')
    a(f'<text x="{(free_start + free_end)/2:.1f}" y="{span_y}" text-anchor="middle" font-size="9.5" font-weight="600" fill="#2563eb">Free ({(total_cols-frozen_cols)*5}%)</text>')


def main() -> None:
    items = parse_cbs()
    s: list[str] = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SATLIB Controlled Backbone Size random 3-SAT diagram">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    a(f'<g font-family="{FONT}">')

    # Header
    a('<text x="26" y="34" font-size="18" font-weight="700" fill="#0f172a">SATLIB Controlled Backbone Random 3-SAT (CBS, n = 100)</text>')
    a(f'<text x="26" y="54" font-size="12" fill="#475569">Backbone variables are frozen to one fixed truth value in every satisfying assignment · {len(items)} SAT samples across b ∈ {{10%, 50%, 90%}}</text>')
    a('<line x1="24" y1="66" x2="896" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left Panel: Solution-Space Backbone Comparison (b=10% vs b=90%)
    lx, ly, lw, lh = 24, 78, 524, 360
    a(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{lx+14}" y="{ly+22}" font-size="13" font-weight="700" fill="#0f172a">Solution-Space Structure: Low vs. High Backbone Fraction</text>')

    # 20 representative variables across 4 distinct models sigma_1..sigma_4
    # b=10% => 2 frozen columns (identical across all rows), 18 free columns (varying)
    rows_b10 = [
        [1, 0,  1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
        [1, 0,  0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0],
        [1, 0,  1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
        [1, 0,  0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1],
    ]
    # b=90% => 18 frozen columns (identical across all rows), 2 free columns
    core = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0]
    rows_b90 = [
        core + [1, 0],
        core + [0, 1],
        core + [1, 1],
        core + [0, 0],
    ]

    draw_assignment_grid(
        a, lx + 12, ly + 32,
        "Small Backbone (b = 10% · CBS_..._b10)",
        "90% of variables flip freely across models → wide, fluid solution cluster",
        frozen_cols=2, total_cols=20, rows_bits=rows_b10,
        accent="#7c3aed", accent_bg="#f5f3ff",
    )
    draw_assignment_grid(
        a, lx + 12, ly + 196,
        "Large Backbone (b = 90% · CBS_..._b90)",
        "90% of variables locked identically in every model → brittle frozen core",
        frozen_cols=18, total_cols=20, rows_bits=rows_b90,
        accent="#7c3aed", accent_bg="#f5f3ff",
    )

    # Right Panel: Committed (m, b) Corpus Matrix + Backbone Definition
    rx, ry, rw, rh = 562, 78, 334, 360
    a(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    a(f'<text x="{rx+14}" y="{ry+23}" font-size="13" font-weight="700" fill="#0f172a">Committed CBS Parameter Grid</text>')
    a(f'<text x="{rx+14}" y="{ry+39}" font-size="10.5" fill="#475569">Parsed from cnf-orig/ (n = 100, all 6 SAT)</text>')

    # Formal definition box
    a(f'<rect x="{rx+14}" y="{ry+50}" width="{rw-28}" height="56" rx="7" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1"/>')
    a(f'<text x="{rx+24}" y="{ry+69}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#5b21b6">Backbone(F) = {{ ℓ : ∀ σ ⊨ F, σ(ℓ) = 1 }}</text>')
    a(f'<text x="{rx+24}" y="{ry+86}" font-size="10" fill="#4c1d95">One wrong decision on a frozen backbone literal</text>')
    a(f'<text x="{rx+24}" y="{ry+99}" font-size="10" fill="#4c1d95">immediately enters an unsatisfiable subtree.</text>')

    # 6 real instances with frozen-vs-free progress bars
    list_y = ry + 124
    a(f'<text x="{rx+14}" y="{list_y}" font-size="10" font-weight="700" fill="#64748b">Instance (m, α)</text>')
    a(f'<text x="{rx+166}" y="{list_y}" font-size="10" font-weight="700" fill="#64748b">Frozen Backbone b/n</text>')
    a(f'<line x1="{rx+14}" y1="{list_y+6}" x2="{rx+rw-14}" y2="{list_y+6}" stroke="#e2e8f0" stroke-width="1"/>')

    bar_x = rx + 166
    bar_w = 114
    for i, (n, m, b, stem) in enumerate(items):
        yy = list_y + 24 + i * 33
        alpha = m / n
        frac = b / n
        a(f'<text x="{rx+14}" y="{yy}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#0f172a">m={m} b={b}%</text>')
        a(f'<text x="{rx+14}" y="{yy+12}" font-size="9" fill="#64748b">α={alpha:.2f} · ρ={alpha/4.267:.2f}×</text>')

        # Stacked bar: purple frozen + light-blue free
        a(f'<rect x="{bar_x}" y="{yy-8}" width="{bar_w}" height="16" rx="4" fill="#dbeafe" stroke="#93c5fd" stroke-width="0.9"/>')
        a(f'<rect x="{bar_x}" y="{yy-8}" width="{bar_w*frac:.1f}" height="16" rx="4" fill="#7c3aed"/>')
        a(f'<text x="{bar_x+bar_w+8}" y="{yy+4}" font-family="{MONO}" font-size="10" font-weight="700" fill="#5b21b6">{b:2d}%</text>')

    # Legend at bottom of right panel
    ly_r = ry + 338
    a(f'<rect x="{rx+16}" y="{ly_r-8}" width="12" height="12" rx="2" fill="#7c3aed"/>')
    a(f'<text x="{rx+33}" y="{ly_r+2}" font-size="10" fill="#334155">Frozen backbone</text>')
    a(f'<rect x="{rx+138}" y="{ly_r-8}" width="12" height="12" rx="2" fill="#dbeafe" stroke="#93c5fd" stroke-width="0.8"/>')
    a(f'<text x="{rx+155}" y="{ly_r+2}" font-size="10" fill="#334155">Free variables</text>')
    a(f'<text x="{rx+rw-14}" y="{ly_r+2}" text-anchor="end" font-size="9.5" fill="#059669" font-weight="700">6/6 SAT</text>')

    a("</g></svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
