#!/usr/bin/env python3
"""Generate illustrative SVG diagram for mata-presburger-nfa-tptp.

Directly parses real MATA automata from `mata-orig/ARI056_1.mata.xz` (6-state NFA)
and `mata-orig/NUM870_1.mata.xz` (Presburger 4-bit vector automaton), plus exact
verdict counts from `expected.tsv`, and renders ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path
from xml.sax.saxutils import escape


def parse_mata(path: Path) -> tuple[set[str], set[str], list[tuple[str, str, str]]]:
    init: set[str] = set()
    final: set[str] = set()
    trans: list[tuple[str, str, str]] = []
    with lzma.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("@"):
                continue
            if s.startswith("%Initial"):
                init.update(s.split()[1:])
            elif s.startswith("%Final"):
                final.update(s.split()[1:])
            else:
                parts = s.split()
                if len(parts) >= 3:
                    trans.append((parts[0], " ".join(parts[1:-1]), parts[-1]))
    return init, final, trans


def build_svg() -> str:
    col_dir = Path(__file__).resolve().parent.parent
    init1, final1, trans1 = parse_mata(col_dir / "mata-orig" / "ARI056_1.mata.xz")
    init2, final2, trans2 = parse_mata(col_dir / "mata-orig" / "NUM870_1.mata.xz")

    # Parse expected.tsv summary
    sat_cnt = unsat_cnt = 0
    for line in (col_dir / "expected.tsv").read_text(encoding="utf-8").splitlines():
        if "\tSAT" in line:
            sat_cnt += 1
        elif "\tUNSAT" in line:
            unsat_cnt += 1

    # Aggregate parallel transitions in NUM870_1 by (src, dst)
    num_edges: dict[tuple[str, str], list[str]] = {}
    for u, sym, v in trans2:
        num_edges.setdefault((u, v), []).append(sym)

    W, H = 940, 485
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155"/>
    </marker>
    <marker id="arr-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.6px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .st { font: 700 12px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #0f172a; }
      .lbl { font: 700 11.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #2563eb; }
      .badge-s { font: 700 11px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #047857; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">MATA Presburger Explicit-Complement NFAs — TPTP (ARI / NUM)</text>')
    out.append(f'  <text x="26" y="54" class="sub">Real finite automata parsed from mata-orig/ ({sat_cnt+unsat_cnt} NFAs: {sat_cnt} SAT non-universal / {unsat_cnt} UNSAT universal)</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # Top panel: Real parsed ARI056_1.mata.xz state diagram
    out.append('  <rect x="24" y="80" width="892" height="162" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="40" y="104" class="h3">1. Parsed Real NFA: mata-orig/ARI056_1.mata.xz (6 States, 6 Transitions, Binary Alphabet Σ = {0, 1})</text>')
    out.append('  <rect x="758" y="90" width="144" height="21" rx="10.5" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1"/>')
    out.append('  <text x="830" y="104" text-anchor="middle" class="badge-s">L(A)ᶜ ≠ ∅ (SAT)</text>')

    # Lay out the exact chain from ARI056_1: q12 -> q6 -> q3 -> q1 -> q0 (self-loop 0) -> q13 (final)
    chain = ["q12", "q6", "q3", "q1", "q0", "q13"]
    pos = {st: (110 + i * 144, 178) for i, st in enumerate(chain)}
    r_node = 22

    # Entry arrow into initial state
    for ist in sorted(init1):
        ix, iy = pos[ist]
        out.append(f'  <line x1="{ix-56}" y1="{iy}" x2="{ix-r_node-3}" y2="{iy}" stroke="#2563eb" stroke-width="2.4" marker-end="url(#arr-b)"/>')
        out.append(f'  <text x="{ix-60}" y="{iy-8}" class="mono" fill="#2563eb">init</text>')

    # Draw transitions directly from parsed trans1!
    for u, sym, v in trans1:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        if u == v:
            # Self-loop above node
            out.append(f'  <path d="M {x1-10} {y1-r_node+2} C {x1-30} {y1-r_node-44}, {x1+30} {y1-r_node-44}, {x1+10} {y1-r_node+2}" fill="none" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arr-b)"/>')
            out.append(f'  <text x="{x1}" y="{y1-r_node-36}" text-anchor="middle" class="lbl">{escape(sym)} (nondet!)</text>')
        else:
            out.append(f'  <line x1="{x1+r_node}" y1="{y1}" x2="{x2-r_node-3}" y2="{y2}" stroke="#334155" stroke-width="2.1" marker-end="url(#arr)"/>')
            out.append(f'  <text x="{(x1+x2)/2:.1f}" y="{y1-10}" text-anchor="middle" class="lbl">{escape(sym)}</text>')

    # Draw state circles
    for st in chain:
        x, y = pos[st]
        is_init = st in init1
        is_fin = st in final1
        fill = "#eff6ff" if is_init else ("#ecfdf5" if is_fin else "#ffffff")
        stroke = "#2563eb" if is_init else ("#059669" if is_fin else "#475569")
        out.append(f'  <circle cx="{x}" cy="{y}" r="{r_node}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
        if is_fin:
            out.append(f'  <circle cx="{x}" cy="{y}" r="{r_node-5}" fill="none" stroke="{stroke}" stroke-width="1.6"/>')
        out.append(f'  <text x="{x}" y="{y+4.5}" text-anchor="middle" class="st">{escape(st)}</text>')

    out.append('  <text x="40" y="228" class="body">Language L(ARI056_1) = 00110⁺ (LSB-first binary integer encoding): nondeterministic branch at q0 on symbol "0" splits into {q0, q13}.</text>')

    # Bottom Left: Parsed NUM870_1.mata.xz (4-bit Presburger track alphabet)
    out.append('  <rect x="24" y="258" width="430" height="206" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="40" y="282" class="h3">2. Multi-Track Presburger NFA: NUM870_1.mata.xz</text>')
    out.append('  <text x="40" y="300" class="body">4-bit parallel tracks (x₁, x₂, x₃, x₄) ∈ {0,1}⁴ read LSB → MSB</text>')

    # Draw q0 and q1
    q0x, q0y = 148, 386
    q1x, q1y = 356, 386
    out.append(f'  <line x1="{q0x-56}" y1="{q0y}" x2="{q0x-27}" y2="{q0y}" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arr-b)"/>')
    # Self-loop on q0
    n_self = len(num_edges.get(("q0", "q0"), []))
    n_fwd = len(num_edges.get(("q0", "q1"), []))
    out.append(f'  <path d="M {q0x-11} {q0y-22} C {q0x-34} {q0y-64}, {q0x+34} {q0y-64}, {q0x+11} {q0y-22}" fill="none" stroke="#7c3aed" stroke-width="2.2" marker-end="url(#arr)"/>')
    out.append(f'  <text x="{q0x}" y="{q0y-58}" text-anchor="middle" class="lbl" fill="#6d28d9">{n_self} vectors: **00, **11</text>')
    # Arrow q0 -> q1
    out.append(f'  <line x1="{q0x+24}" y1="{q0y}" x2="{q1x-27}" y2="{q1y}" stroke="#334155" stroke-width="2.2" marker-end="url(#arr)"/>')
    out.append(f'  <text x="{(q0x+q1x)/2:.1f}" y="{q0y-10}" text-anchor="middle" class="lbl">{n_fwd} bit-vectors</text>')
    out.append(f'  <text x="{(q0x+q1x)/2:.1f}" y="{q0y+18}" text-anchor="middle" class="mono">x₃ = x₄ (mod 2)</text>')

    out.append(f'  <circle cx="{q0x}" cy="{q0y}" r="24" fill="#eff6ff" stroke="#2563eb" stroke-width="2.2"/>')
    out.append(f'  <text x="{q0x}" y="{q0y+4.5}" text-anchor="middle" class="st">q0</text>')
    out.append(f'  <circle cx="{q1x}" cy="{q1y}" r="24" fill="#ecfdf5" stroke="#059669" stroke-width="2.2"/>')
    out.append(f'  <circle cx="{q1x}" cy="{q1y}" r="19" fill="none" stroke="#059669" stroke-width="1.6"/>')
    out.append(f'  <text x="{q1x}" y="{q1y+4.5}" text-anchor="middle" class="st">q1</text>')
    out.append('  <text x="40" y="446" class="body">Each bit-vector encodes simultaneous k-variable arithmetic digits.</text>')

    # Bottom Right: Explicit Complementation & Universality Pipeline
    out.append('  <rect x="470" y="258" width="446" height="206" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append('  <text x="486" y="282" class="h3">3. Benchmark Task: Explicit NFA Complementation</text>')
    out.append('  <text x="486" y="301" class="body">Quantifier alternation ¬∃x φ(x) in Presburger arithmetic requires L(A)ᶜ:</text>')

    stages = [
        ("Input NFA A", "|Q| states", "#2563eb", "#ffffff"),
        ("Subset DFA D", "up to 2^|Q|", "#7c3aed", "#ffffff"),
        ("Flip Finals Fᶜ", "Q_D \\ F_D", "#d97706", "#ffffff"),
        ("Emptiness?", "SAT / UNSAT", "#059669", "#ffffff"),
    ]
    for i, (st_t, st_s, col, bg) in enumerate(stages):
        bx = 486 + i * 106
        by = 318
        out.append(f'  <rect x="{bx}" y="{by}" width="94" height="54" rx="8" fill="{bg}" stroke="{col}" stroke-width="1.8"/>')
        out.append(f'  <text x="{bx+47}" y="{by+23}" text-anchor="middle" style="font:700 11px sans-serif;fill:{col};">{escape(st_t)}</text>')
        out.append(f'  <text x="{bx+47}" y="{by+40}" text-anchor="middle" class="mono">{escape(st_s)}</text>')
        if i < 3:
            out.append(f'  <line x1="{bx+94}" y1="{by+27}" x2="{bx+104}" y2="{by+27}" stroke="#475569" stroke-width="1.8" marker-end="url(#arr)"/>')

    out.append('  <text x="486" y="398" class="mono">• SAT   (17/21): ∃w ∈ Σ* \\ L(A)  (complement non-empty)</text>')
    out.append('  <text x="486" y="417" class="mono">• UNSAT  (4/21): L(A) = Σ*       (automaton is universal)</text>')
    out.append('  <text x="486" y="440" class="body">Antichain/bisimulation avoids worst-case 2^|Q| subset explosion.</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
