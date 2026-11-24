#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-qg (Quasigroup / Latin Squares).

Renders a verified order-7 idempotent QG1 Latin square decoded directly from the
real benchmark instance `cnf-orig/qg1-07.cnf.xz`, verifies all Latin-square,
idempotence (a*a = a), and QG1 orthogonality axioms programmatically, and writes
../diagram.svg using stdlib only.
"""
from __future__ import annotations

from pathlib import Path

# Verified order-7 idempotent QG1 quasigroup decoded from cnf-orig/qg1-07.cnf.xz
QG1_07: list[list[int]] = [
    [0, 6, 4, 1, 3, 2, 5],
    [3, 1, 6, 5, 2, 4, 0],
    [5, 4, 2, 6, 0, 3, 1],
    [4, 0, 5, 3, 6, 1, 2],
    [2, 5, 1, 0, 4, 6, 3],
    [6, 3, 0, 2, 1, 5, 4],
    [1, 2, 3, 4, 5, 0, 6],
]


def verify_qg1(grid: list[list[int]]) -> None:
    n = len(grid)
    for r in range(n):
        assert sorted(grid[r]) == list(range(n)), f"Row {r} not a permutation"
        assert grid[r][r] == r, f"Not idempotent at ({r},{r})"
    for c in range(n):
        assert sorted(grid[r][c] for r in range(n)) == list(range(n)), f"Col {c} not a permutation"
    # Verify QG1 identity: (x*y = u, z*w = u, v*y = x, v*w = z) => (x = z and y = w)
    # Equivalently, the (3,2,1)-conjugate pairs (a*b, c) where c*b = a? Check orthogonality:
    # For QG1: for all a, b, unique x, y with x*y = a and ... actually verify standard Zhang QG1:
    # (x*y = u ∧ z*w = u) and (v*y = x ∧ v*w = z) -> x=z, y=w
    # Let f(x, y) = x * y; solve for unique v with v*y = x -> check pair (x*y, v) is unique across all (x, y)!
    inv_right = {}
    for v in range(n):
        for y in range(n):
            inv_right[(grid[v][y], y)] = v
    pairs = set()
    for x in range(n):
        for y in range(n):
            u = grid[x][y]
            v = inv_right[(x, y)]
            pairs.add((u, v))
    assert len(pairs) == n * n, f"QG1 orthogonality failed: {len(pairs)} != {n*n}"


def build_svg() -> str:
    verify_qg1(QG1_07)
    n = 7

    # Soft, high-contrast color palette for symbols 0..6
    sym_colors = [
        ("#dbeafe", "#1d4ed8"),  # 0 blue
        ("#d1fae5", "#047857"),  # 1 emerald
        ("#fef3c7", "#b45309"),  # 2 amber
        ("#ede9fe", "#6d28d9"),  # 3 purple
        ("#fee2e2", "#b91c1c"),  # 4 rose
        ("#cffafe", "#0e7490"),  # 5 cyan
        ("#fce7f3", "#be185d"),  # 6 pink
    ]

    W, H = 940, 480
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.8px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .hdr { font: 700 12.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #475569; }
      .cell { font: 700 15px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; }
      .badge { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Quasigroup Existence &amp; Latin Squares — Decoded Real Model qg1-07</text>')
    out.append('  <text x="26" y="54" class="sub">Order-7 idempotent Latin square (a * a = a) satisfying QG1 orthogonality, decoded from cnf-orig/qg1-07.cnf.xz</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Left panel: 7x7 Cayley multiplication table
    lx, ly, lw, lh = 24, 80, 412, 378
    out.append(f'  <rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{lx+16}" y="{ly+24}" class="h3">Cayley Table a * b (Order n = 7)</text>')
    out.append(f'  <rect x="{lx+lw-118}" y="{ly+10}" width="104" height="21" rx="10.5" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append(f'  <text x="{lx+lw-66}" y="{ly+24}" text-anchor="middle" class="badge">QG1 Verified ✓</text>')

    gx, gy, cs = lx + 68, ly + 56, 40
    # Operator corner & row/col headers
    out.append(f'  <text x="{gx-20}" y="{gy-10}" text-anchor="middle" class="hdr">*</text>')
    for i in range(n):
        out.append(f'  <text x="{gx + i*cs + cs/2:.1f}" y="{gy-10}" text-anchor="middle" class="hdr">{i}</text>')
        out.append(f'  <text x="{gx - 20}" y="{gy + i*cs + cs/2 + 4.5:.1f}" text-anchor="middle" class="hdr">{i}</text>')

    # Draw 7x7 Latin cells
    for r in range(n):
        for c in range(n):
            v = QG1_07[r][c]
            bg, fg = sym_colors[v]
            x, y = gx + c * cs, gy + r * cs
            is_diag = r == c
            stroke = "#0f172a" if is_diag else "#ffffff"
            sw = "2.2" if is_diag else "1.6"
            out.append(f'  <rect x="{x+2}" y="{y+2}" width="{cs-4}" height="{cs-4}" rx="6" fill="{bg}" stroke="{stroke}" stroke-width="{sw}"/>')
            out.append(f'  <text x="{x+cs/2:.1f}" y="{y+cs/2+5.5:.1f}" text-anchor="middle" class="cell" fill="{fg}">{v}</text>')

    out.append(f'  <text x="{lx+16}" y="{ly+lh-14}" class="body">Bold diagonal = idempotence (a*a = a); rows &amp; cols bijective.</text>')

    # Right side: Two panels (Axioms + QG1..QG7 family map)
    rx, rw = 454, 462

    # Card 1: CNF Encoding
    out.append(f'  <rect x="{rx}" y="80" width="{rw}" height="156" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="104" class="h3">Boolean CNF Encoding (n³ Variables: x(a, b, c) ⇔ a*b = c)</text>')
    out.append(f'  <text x="{rx+16}" y="126" class="mono">1. Cell bijection:   ∀a,b: ∑c x(a,b,c) = 1</text>')
    out.append(f'  <text x="{rx+16}" y="145" class="mono">2. Row uniqueness:   ∀a,c: ∑b x(a,b,c) = 1</text>')
    out.append(f'  <text x="{rx+16}" y="164" class="mono">3. Col uniqueness:   ∀b,c: ∑a x(a,b,c) = 1</text>')
    out.append(f'  <text x="{rx+16}" y="183" class="mono">4. Idempotence:      ∀a:   x(a,a,a) = 1   (unit clauses)</text>')
    out.append(f'  <text x="{rx+16}" y="202" class="mono">5. Algebraic Law:    QG1–QG7 horn/4-clauses (68,083 in qg1-07)</text>')
    out.append(f'  <text x="{rx+16}" y="223" class="body">Each order-n quasigroup uses n³ Boolean variables (n=7 → 343, n=13 → 2,197).</text>')

    # Card 2: The 7 Quasigroup Families in Zhang's SATLIB suite
    out.append(f'  <rect x="{rx}" y="250" width="{rw}" height="208" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append(f'  <text x="{rx+16}" y="274" class="h3">Zhang\'s Quasigroup Families (22 Instances: 10 SAT / 12 UNSAT)</text>')
    fams = [
        ("QG1", "(3,2,1)-conjugate orthogonal", "n=7,8 SAT"),
        ("QG2", "(3,1,2)-conjugate orthogonal", "n=7,8 SAT"),
        ("QG3", "(a*b)*(b*a) = a  (Stein\'s 1st law)", "n=8 SAT · n=9 UNSAT"),
        ("QG4", "(b*a)*(a*b) = a  (Stein\'s 2nd law)", "n=8 UNSAT · n=9 SAT"),
        ("QG5", "((b*a)*b)*b = a  (Schröder)", "n=11 SAT · n=9,10,12,13 UNSAT"),
        ("QG6", "(a*b)*b = a*(a*b)  (Stein\'s 3rd)", "n=9 SAT · n=10..12 UNSAT"),
        ("QG7", "(b*a)*b = a*(b*a)  (Stein\'s 4th)", "n=9,13 SAT · n=10..12 UNSAT"),
    ]
    for idx, (tag, law, verdicts) in enumerate(fams):
        yy = 298 + idx * 23
        out.append(f'  <rect x="{rx+16}" y="{yy-12}" width="38" height="17" rx="4" fill="#2563eb"/>')
        out.append(f'  <text x="{rx+35}" y="{yy}" text-anchor="middle" style="font:700 10px monospace;fill:#ffffff;">{tag}</text>')
        out.append(f'  <text x="{rx+62}" y="{yy}" class="mono">{law}</text>')
        out.append(f'  <text x="{rx+rw-14}" y="{yy}" text-anchor="end" class="body">{verdicts}</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
