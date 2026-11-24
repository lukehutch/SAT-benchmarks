#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-planning-blocksworld.

Illustrates the classic SATPLAN Blocks World planning-as-SAT problem (including
the iconic Sussman Anomaly sequence from `anomaly.cnf.xz` and scaling up to
`bw_large.d.cnf.xz`), parsing real instance counts from `cnf-orig/`.
Writes ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path
from xml.sax.saxutils import escape


def parse_header(cnf_xz: Path) -> tuple[int, int]:
    with lzma.open(cnf_xz, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("p cnf"):
                p = line.split()
                return int(p[2]), int(p[3])
    return 0, 0


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    stats = []
    for name in ("anomaly", "medium", "huge", "bw_large.a", "bw_large.d"):
        p = col_dir / "cnf-orig" / f"{name}.cnf.xz"
        if p.exists():
            stats.append((name, *parse_header(p)))

    W, H = 940, 465
    b_cols = {
        "A": ("#2563eb", "#1d4ed8"),
        "B": ("#059669", "#047857"),
        "C": ("#d97706", "#b45309"),
    }

    # Sussman Anomaly optimal 3-step plan:
    # t=0: [A, C], [B]  -> Move(C, A, Table) -> t=1: [A], [B], [C]
    # -> Move(B, Table, C) -> t=2: [A], [C, B] -> Move(A, Table, B) -> t=3: [C, B, A]
    steps = [
        ("t = 0 (Initial)", [["A", "C"], ["B"], []], "Move(C, A → Table)"),
        ("t = 1", [["A"], ["B"], ["C"]], "Move(B, Table → C)"),
        ("t = 2", [["A"], [], ["C", "B"]], "Move(A, Table → B)"),
        ("t = 3 (Goal: A on B on C)", [[], [], ["C", "B", "A"]], None),
    ]

    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.6px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .act { font: 700 10.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1d4ed8; }
      .blk { font: 700 15px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #ffffff; }
      .tbl { font: 600 10px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #64748b; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">SATPLAN Blocks World Planning (Kautz &amp; Selman)</text>')
    out.append('  <text x="26" y="54" class="sub">Bounded-horizon STRIPS planning encoded as SAT: Sussman Anomaly interleaving &amp; multi-tower bw_large instances</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Draw 4 state panels across top
    cw, ch, gap = 200, 196, 30
    sx0, sy0 = 24, 84

    for idx, (stitle, stacks, action) in enumerate(steps):
        cx = sx0 + idx * (cw + gap)
        bg = "#ecfdf5" if idx == 3 else "#f8fafc"
        bdr = "#6ee7b7" if idx == 3 else "#e2e8f0"
        out.append(f'  <rect x="{cx}" y="{sy0}" width="{cw}" height="{ch}" rx="10" fill="{bg}" stroke="{bdr}" stroke-width="1.3"/>')
        out.append(f'  <text x="{cx+cw/2:.1f}" y="{sy0+24}" text-anchor="middle" class="h3">{escape(stitle)}</text>')

        # Table surface
        ty = sy0 + 164
        out.append(f'  <rect x="{cx+16}" y="{ty}" width="{cw-32}" height="7" rx="3" fill="#475569"/>')
        out.append(f'  <text x="{cx+cw/2:.1f}" y="{ty+21}" text-anchor="middle" class="tbl">TABLE</text>')

        # 3 stack slots
        slot_xs = [cx + 46, cx + 100, cx + 154]
        bw, bh = 38, 34
        for si, st in enumerate(stacks):
            px = slot_xs[si]
            for lvl, blk in enumerate(st):
                by = ty - (lvl + 1) * (bh + 2)
                fill, stroke = b_cols[blk]
                out.append(f'  <rect x="{px - bw/2:.1f}" y="{by:.1f}" width="{bw}" height="{bh}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
                out.append(f'  <text x="{px:.1f}" y="{by + bh/2 + 5.5:.1f}" text-anchor="middle" class="blk">{blk}</text>')

        # Action arrow between panels
        if action is not None:
            ax1 = cx + cw + 3
            ax2 = cx + cw + gap - 3
            ay = sy0 + ch / 2
            out.append(f'  <line x1="{ax1}" y1="{ay:.1f}" x2="{ax2}" y2="{ay:.1f}" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arr)"/>')
            # Action label pill centered below arrow bridge
            mx = (ax1 + ax2) / 2.0
            out.append(f'  <rect x="{mx-62:.1f}" y="{sy0+ch+8}" width="124" height="20" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>')
            out.append(f'  <text x="{mx:.1f}" y="{sy0+ch+21.5}" text-anchor="middle" class="act">{escape(action)}</text>')

    # Bottom two cards: Encoding + Suite Scaling
    out.append('  <rect x="24" y="318" width="548" height="128" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append('  <text x="40" y="342" class="h3">SATPLAN Time-Indexed Encoding (Axioms over Steps t = 0 … T)</text>')
    out.append('  <text x="40" y="363" class="mono">• Fluents:        on(x, y, t),  clear(x, t),  onTable(x, t)</text>')
    out.append('  <text x="40" y="382" class="mono">• Action axioms:  move(x, y, z, t) ⇒ clear(x,t) ∧ clear(z,t) ∧ on(x,y,t)</text>')
    out.append('  <text x="40" y="401" class="mono">• Frame axioms:   on(x,y,t) ∧ ¬on(x,y,t+1) ⇒ ∨_z move(x,y,z,t)</text>')
    out.append('  <text x="40" y="421" class="body">A satisfying assignment directly decodes into an exact parallel/sequential block plan.</text>')

    out.append('  <rect x="588" y="318" width="328" height="128" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="604" y="342" class="h3">Parsed Suite Scale (7 SAT Instances)</text>')
    for idx, (nm, nv, nc) in enumerate(stats):
        yy = 364 + idx * 16
        out.append(f'  <text x="604" y="{yy}" class="mono">{nm:11s}: {nv:5,d} vars · {nc:6,d} clauses</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
