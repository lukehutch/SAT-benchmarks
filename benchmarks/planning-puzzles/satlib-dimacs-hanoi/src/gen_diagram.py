#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-dimacs-hanoi.

Computes the exact optimal 15-move Towers of Hanoi trajectory for hanoi4
(4 disks, 3 pegs) and parses real CNF statistics from cnf-orig/hanoi4.cnf.xz
and hanoi5.cnf.xz to render ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path
from xml.sax.saxutils import escape


def parse_dimacs_header(cnf_xz: Path) -> tuple[int, int]:
    with lzma.open(cnf_xz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("p cnf"):
                p = line.split()
                return int(p[2]), int(p[3])
    return 0, 0


def hanoi_states(n_disks: int) -> list[tuple[list[list[int]], tuple[int, int, int] | None]]:
    """Return sequence of (pegs, move=(disk, src, dst)) for optimal 2^n - 1 moves."""
    pegs: list[list[int]] = [list(range(n_disks, 0, -1)), [], []]
    seq: list[tuple[list[list[int]], tuple[int, int, int] | None]] = [
        ([list(p) for p in pegs], None)
    ]

    def solve(k: int, src: int, aux: int, dst: int) -> None:
        if k == 0:
            return
        solve(k - 1, src, dst, aux)
        d = pegs[src].pop()
        assert not pegs[dst] or pegs[dst][-1] > d
        pegs[dst].append(d)
        seq.append(([list(p) for p in pegs], (d, src, dst)))
        solve(k - 1, aux, src, dst)

    solve(n_disks, 0, 1, 2)
    return seq


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    v4, c4 = parse_dimacs_header(col_dir / "cnf-orig" / "hanoi4.cnf.xz")
    v5, c5 = parse_dimacs_header(col_dir / "cnf-orig" / "hanoi5.cnf.xz")

    states = hanoi_states(4)
    # 5 milestone snapshots from the exact 15-step optimal plan
    milestones = [
        (0, "t = 0 (Initial)", "All 4 disks on Peg A"),
        (3, "t = 3", "Disks 1–2 stacked on C"),
        (7, "t = 7 (Subgoal)", "Top 3 disks moved to B"),
        (8, "t = 8 (Pivot)", "Disk 4 moves A → C"),
        (15, "t = 15 (Goal)", "All 4 disks on Peg C"),
    ]

    W, H = 940, 445
    disk_colors = {
        1: ("#2563eb", "#1d4ed8"),  # smallest (blue)
        2: ("#059669", "#047857"),  # emerald
        3: ("#d97706", "#b45309"),  # amber
        4: ("#7c3aed", "#6d28d9"),  # largest (purple)
    }

    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>
    </marker>
    <marker id="arr-p" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .stitle { font: 700 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .ssub { font: 400 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .peg { font: 700 10.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #64748b; }
      .dnum { font: 700 9.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .h3 { font: 700 13px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">Towers of Hanoi Planning-as-SAT (hanoi4 &amp; hanoi5)</text>')
    out.append('  <text x="26" y="54" class="sub">Optimal 2ⁿ − 1 move sequence for 4 disks (15 steps) and 5 disks (31 steps) encoded as time-indexed propositional SAT</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Draw 5 state cards horizontally
    card_w, card_h, gap = 166, 206, 15
    start_x, top_y = 24, 82

    for idx, (step_t, lbl, desc) in enumerate(milestones):
        pegs, last_move = states[step_t]
        cx = start_x + idx * (card_w + gap)
        highlight = step_t in (0, 8, 15)
        bg = "#f5f3ff" if step_t == 8 else ("#ecfdf5" if step_t == 15 else "#f8fafc")
        bdr = "#c4b5fd" if step_t == 8 else ("#6ee7b7" if step_t == 15 else "#e2e8f0")
        out.append(f'  <rect x="{cx}" y="{top_y}" width="{card_w}" height="{card_h}" rx="10" fill="{bg}" stroke="{bdr}" stroke-width="1.3"/>')
        out.append(f'  <text x="{cx + card_w/2:.1f}" y="{top_y + 22}" text-anchor="middle" class="stitle">{escape(lbl)}</text>')
        out.append(f'  <text x="{cx + card_w/2:.1f}" y="{top_y + 38}" text-anchor="middle" class="ssub">{escape(desc)}</text>')

        # Base platform and 3 pegs
        base_y = top_y + 168
        out.append(f'  <rect x="{cx+12}" y="{base_y}" width="{card_w-24}" height="7" rx="3" fill="#475569"/>')
        peg_xs = [cx + 35, cx + 83, cx + 131]
        for pi, px in enumerate(peg_xs):
            out.append(f'  <rect x="{px-2.5:.1f}" y="{base_y-82}" width="5" height="82" rx="2" fill="#94a3b8"/>')
            out.append(f'  <text x="{px:.1f}" y="{base_y+21}" text-anchor="middle" class="peg">{chr(65+pi)}</text>')
            # Disks on this peg
            for level, disk in enumerate(pegs[pi]):
                dw = 16 + disk * 7.5
                dh = 14
                dy = base_y - (level + 1) * (dh + 1.5)
                fill, stroke = disk_colors[disk]
                out.append(f'  <rect x="{px - dw/2:.1f}" y="{dy:.1f}" width="{dw:.1f}" height="{dh}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
                out.append(f'  <text x="{px:.1f}" y="{dy+10.5:.1f}" text-anchor="middle" class="dnum">{disk}</text>')

        # Special curved move arrow for pivot step t=8 (disk 4 A -> C)
        if step_t == 8:
            x_a, x_c = peg_xs[0], peg_xs[2]
            out.append(f'  <path d="M {x_a:.1f} {top_y+74} Q {peg_xs[1]:.1f} {top_y+48} {x_c:.1f} {top_y+74}" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="4,2" marker-end="url(#arr-p)"/>')

        # Transition arrow to next card
        if idx < len(milestones) - 1:
            ax1 = cx + card_w + 2
            ax2 = cx + card_w + gap - 2
            ay = top_y + card_h / 2
            out.append(f'  <line x1="{ax1}" y1="{ay:.1f}" x2="{ax2}" y2="{ay:.1f}" stroke="#64748b" stroke-width="1.8" marker-end="url(#arr)"/>')

    # Bottom two cards: Encoding Rules + Real Dataset Scale
    out.append('  <rect x="24" y="304" width="538" height="122" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append('  <text x="40" y="328" class="h3">SATPLAN Propositional Encoding (Selman &amp; Kautz, 1996)</text>')
    out.append('  <text x="40" y="348" class="body">State atoms on(d, x, t) and move actions move(d, src, dst, t) over time steps t ∈ {0, …, 2ⁿ − 1}:</text>')
    out.append('  <text x="40" y="370" class="mono">• Preconditions:  move(d, a, b, t) ⇒ clear(d, t) ∧ clear(b, t) ∧ smaller(d, b)</text>')
    out.append('  <text x="40" y="389" class="mono">• Effects &amp; Frame: move(d, a, b, t) ⇒ on(d, b, t+1) ∧ ¬on(d, a, t+1)</text>')
    out.append('  <text x="40" y="408" class="mono">• Exactly-one action per step t; initial state at t=0, goal state at t=T</text>')

    out.append('  <rect x="578" y="304" width="338" height="122" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="594" y="328" class="h3">Benchmark Instances (Parsed Headers)</text>')
    out.append(f'  <text x="594" y="352" class="mono">hanoi4.cnf:  4 disks · 15 steps</text>')
    out.append(f'  <text x="606" y="369" class="body">{v4:,} vars · {c4:,} clauses · SAT</text>')
    out.append(f'  <text x="594" y="394" class="mono">hanoi5.cnf:  5 disks · 31 steps</text>')
    out.append(f'  <text x="606" y="411" class="body">{v5:,} vars · {c5:,} clauses · SAT</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
