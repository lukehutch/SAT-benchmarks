#!/usr/bin/env python3
"""Generate illustrative SVG diagram for satlib-planning-logistics.

Illustrates the SATPLAN multi-city Logistics domain (trucks inside cities,
airplanes between airports, parallel load/drive/fly/unload actions across time
steps) and parses real CNF headers from cnf-orig/logistics.a..d.cnf.xz.
Writes ../diagram.svg using stdlib only.
"""
from __future__ import annotations

import lzma
from pathlib import Path


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
    for name in ("logistics.a", "logistics.b", "logistics.c", "logistics.d"):
        p = col_dir / "cnf-orig" / f"{name}.cnf.xz"
        if p.exists():
            stats.append((name, *parse_header(p)))

    W, H = 940, 470
    out: list[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    out.append("""  <defs>
    <marker id="arr-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <marker id="arr-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
    </marker>
    <marker id="arr-p" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>
    </marker>
    <style>
      .title { font: 700 18px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .sub { font: 400 12.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #475569; }
      .h3 { font: 700 13.5px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .body { font: 400 11.6px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #334155; }
      .mono { font: 600 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #1e293b; }
      .loc { font: 700 12px system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: #0f172a; }
      .tag { font: 700 10.5px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; fill: #ffffff; }
      .edge { font: 700 11px ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace; }
    </style>
  </defs>""")

    out.append(f'  <rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>')
    out.append('  <text x="26" y="34" class="title">SATPLAN Multi-City Logistics Planning (logistics.a – logistics.d)</text>')
    out.append('  <text x="26" y="54" class="sub">Parallel Graphplan-to-SAT encoding: coordinate intra-city trucks &amp; inter-city airplanes to deliver packages by horizon T</text>')
    out.append(f'  <line x1="24" y1="66" x2="{W-24}" y2="66" stroke="#e2e8f0" stroke-width="1"/>')

    # City 1 box (left)
    out.append('  <rect x="28" y="84" width="330" height="218" rx="12" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.4" stroke-dasharray="6,3"/>')
    out.append('  <text x="44" y="106" class="h3" fill="#1d4ed8">City 1 (Origin Hub)</text>')

    # Post Office 1
    out.append('  <rect x="48" y="124" width="122" height="72" rx="9" fill="#ffffff" stroke="#2563eb" stroke-width="1.5"/>')
    out.append('  <text x="109" y="148" text-anchor="middle" class="loc">Post Office 1</text>')
    out.append('  <rect x="66" y="160" width="86" height="22" rx="5" fill="#d97706"/>')
    out.append('  <text x="109" y="175" text-anchor="middle" class="tag">Pkg p1 (t=0)</text>')

    # Airport 1
    out.append('  <rect x="218" y="124" width="122" height="72" rx="9" fill="#ffffff" stroke="#7c3aed" stroke-width="1.5"/>')
    out.append('  <text x="279" y="148" text-anchor="middle" class="loc">Airport 1</text>')
    out.append('  <rect x="236" y="160" width="86" height="22" rx="5" fill="#7c3aed"/>')
    out.append('  <text x="279" y="175" text-anchor="middle" class="tag">Plane A1</text>')

    # Truck 1 arrow PO1 -> Airport1
    out.append('  <line x1="170" y1="160" x2="215" y2="160" stroke="#2563eb" stroke-width="2.4" marker-end="url(#arr-b)"/>')
    out.append('  <rect x="64" y="218" width="258" height="66" rx="8" fill="#ffffff" stroke="#bfdbfe" stroke-width="1"/>')
    out.append('  <text x="78" y="238" class="edge" fill="#1d4ed8">Truck T1 (City 1 only):</text>')
    out.append('  <text x="78" y="256" class="mono">t=0: Load(p1, T1, PO1)</text>')
    out.append('  <text x="78" y="272" class="mono">t=1: Drive(T1, PO1 → Air1) + Unload</text>')

    # Inter-city flight bridge
    out.append('  <path d="M 342 152 Q 470 96 594 152" fill="none" stroke="#7c3aed" stroke-width="2.8" marker-end="url(#arr-p)"/>')
    out.append('  <rect x="382" y="102" width="176" height="44" rx="8" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1.2"/>')
    out.append('  <text x="470" y="121" text-anchor="middle" class="edge" fill="#6d28d9">Air Corridor (t = 2..3)</text>')
    out.append('  <text x="470" y="137" text-anchor="middle" class="mono">Load → Fly(A1, Air1→Air2)</text>')

    # Parallelism callout in middle
    out.append('  <rect x="382" y="192" width="176" height="92" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    out.append('  <text x="470" y="213" text-anchor="middle" class="h3">Parallel Actions</text>')
    out.append('  <text x="394" y="233" class="body">Non-interfering trucks,</text>')
    out.append('  <text x="394" y="249" class="body">planes &amp; packages move</text>')
    out.append('  <text x="394" y="265" class="body">simultaneously per step</text>')
    out.append('  <text x="394" y="279" class="mono">¬(aᵢ(t) ∧ aⱼ(t)) mutex</text>')

    # City 2 box (right)
    out.append('  <rect x="582" y="84" width="330" height="218" rx="12" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.4" stroke-dasharray="6,3"/>')
    out.append('  <text x="598" y="106" class="h3" fill="#047857">City 2 (Destination Hub)</text>')

    # Airport 2
    out.append('  <rect x="600" y="124" width="122" height="72" rx="9" fill="#ffffff" stroke="#7c3aed" stroke-width="1.5"/>')
    out.append('  <text x="661" y="148" text-anchor="middle" class="loc">Airport 2</text>')
    out.append('  <rect x="618" y="160" width="86" height="22" rx="5" fill="#059669"/>')
    out.append('  <text x="661" y="175" text-anchor="middle" class="tag">Truck T2</text>')

    # Post Office 2
    out.append('  <rect x="770" y="124" width="122" height="72" rx="9" fill="#ffffff" stroke="#059669" stroke-width="1.5"/>')
    out.append('  <text x="831" y="148" text-anchor="middle" class="loc">Post Office 2</text>')
    out.append('  <rect x="788" y="160" width="86" height="22" rx="5" fill="#047857"/>')
    out.append('  <text x="831" y="175" text-anchor="middle" class="tag">Pkg p1 (Goal)</text>')

    # Truck 2 arrow Airport2 -> PO2
    out.append('  <line x1="722" y1="160" x2="767" y2="160" stroke="#059669" stroke-width="2.4" marker-end="url(#arr-g)"/>')
    out.append('  <rect x="616" y="218" width="258" height="66" rx="8" fill="#ffffff" stroke="#a7f3d0" stroke-width="1"/>')
    out.append('  <text x="630" y="238" class="edge" fill="#047857">Truck T2 (City 2 only):</text>')
    out.append('  <text x="630" y="256" class="mono">t=4: Unload(p1,A1) + Load(p1,T2)</text>')
    out.append('  <text x="630" y="272" class="mono">t=5: Drive(T2, Air2→PO2) + Unload</text>')

    # Bottom two cards: Encoding + Parsed instances
    out.append('  <rect x="28" y="318" width="538" height="132" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1.2"/>')
    out.append('  <text x="44" y="342" class="h3">Graphplan-Based SAT Encoding (Kautz &amp; Selman, 1996)</text>')
    out.append('  <text x="44" y="363" class="mono">• Fact layers:   at(obj, loc, t),  in(pkg, vehicle, t)</text>')
    out.append('  <text x="44" y="382" class="mono">• Action layers: load / unload / drive / fly at step t</text>')
    out.append('  <text x="44" y="401" class="mono">• Backward support: fact(t+1) ⇒ ∨ { act(t) adding fact } ∨ noop(t)</text>')
    out.append('  <text x="44" y="420" class="mono">• Mutex clauses: ¬(act₁(t) ∧ act₂(t)) for conflicting preconditions</text>')
    out.append('  <text x="44" y="438" class="body">Allows compact parallel plans (e.g., 11–14 time steps for 8–10 packages across 3–4 cities).</text>')

    out.append('  <rect x="582" y="318" width="330" height="132" rx="10" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.2"/>')
    out.append('  <text x="598" y="342" class="h3">Parsed Benchmark Suite (4 SAT)</text>')
    for idx, (nm, nv, nc) in enumerate(stats):
        yy = 368 + idx * 20
        out.append(f'  <text x="598" y="{yy}" class="mono">{nm:12s}: {nv:5,d} vars · {nc:6,d} cls</text>')

    out.append('</svg>\n')
    return "\n".join(out)


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "diagram.svg"
    target.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
