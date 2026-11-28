#!/usr/bin/env python3
"""Generate standalone bespoke SVG diagram (`diagram.svg`) for brewbaker-sha256-cec.

Visualizes the FIPS 180-4 SHA-256 Combinational Equivalence Checking (CEC) miter
comparing 32-bit ripple-carry addition vs. 5-level parallel-prefix carry-lookahead
addition across R rounds + feed-forward, alongside the "abc" (616263) trace verification mode.
"""
from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagram.svg"

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def build_svg() -> str:
    digest_abc = hashlib.sha256(b"abc").hexdigest()
    assert digest_abc == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

    W, H = 960, 520
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="FIPS 180-4 SHA-256 Ripple-vs-Prefix Adder CEC Miters (brewbaker-sha256-cec)">',
        "<defs>",
        '  <marker id="arr-b" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#1d4ed8"/>',
        "  </marker>",
        '  <marker id="arr-p" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#7c3aed"/>',
        "  </marker>",
        '  <marker id="arr-r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>',
        "  </marker>",
        "</defs>",
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT}">',
        # Header
        '  <text x="26" y="34" font-size="17.5" font-weight="700" fill="#0f172a">'
        'FIPS 180-4 SHA-256 Ripple-vs-Prefix Adder CEC Miters (brewbaker-sha256-cec)</text>',
        '  <text x="26" y="53" font-size="11.6" fill="#475569">'
        'Combinational equivalence checking of two independent 32-bit adder architectures across R = 1..64 rounds + "abc" traces '
        '(Chad Brewbaker, sat_challenges.py sha256)</text>',
        '  <rect x="742" y="16" width="192" height="24" rx="12" fill="#fef2f2" stroke="#dc2626" stroke-width="1.2"/>',
        '  <text x="838" y="32" text-anchor="middle" font-size="10.8" font-weight="700" fill="#b91c1c">'
        '13 Instances &#x00B7; 2 SAT / 11 UNSAT</text>',
        '  <line x1="24" y1="65" x2="936" y2="65" stroke="#e2e8f0" stroke-width="1"/>',
    ]

    # Section 1: CEC Miter Schematic
    y1 = 78
    p.append(f'  <rect x="24" y="{y1}" width="912" height="214" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <rect x="24" y="{y1}" width="912" height="28" rx="10" fill="#1e293b"/>')
    p.append(f'  <rect x="24" y="{y1+16}" width="912" height="12" fill="#1e293b"/>')
    p.append(f'  <text x="38" y="{y1+19}" font-size="11.6" font-weight="700" fill="#ffffff">'
             '1. Combinational Equivalence Checking (CEC) Miter Architecture (sha256 R --bytes B &#x2192; Always UNSAT)</text>')

    # Input Block box
    p.append(f'  <rect x="40" y="{y1+72}" width="136" height="92" rx="8" fill="#ffffff" stroke="#475569" stroke-width="1.3"/>')
    p.append(f'  <text x="108" y="{y1+94}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#0f172a">Symbolic Input</text>')
    p.append(f'  <text x="108" y="{y1+111}" text-anchor="middle" font-family="{MONO}" font-size="9.2" fill="#1d4ed8">B bytes (8B vars)</text>')
    p.append(f'  <text x="108" y="{y1+128}" text-anchor="middle" font-size="8.6" fill="#475569">+ 0x80 || 0..0 || len64</text>')
    p.append(f'  <text x="108" y="{y1+144}" text-anchor="middle" font-size="8.6" fill="#475569">512-bit FIPS 180-4 block</text>')
    p.append(f'  <text x="108" y="{y1+157}" text-anchor="middle" font-size="8.2" fill="#64748b">Shared primary inputs</text>')

    # Split arrows to Top (Ripple) and Bottom (Prefix) pipelines
    p.append(f'  <path d="M 176 {y1+104} L 204 {y1+104} L 204 {y1+78} L 236 {y1+78}" fill="none" stroke="#1d4ed8" stroke-width="1.8" marker-end="url(#arr-b)"/>')
    p.append(f'  <path d="M 176 {y1+134} L 204 {y1+134} L 204 {y1+160} L 236 {y1+160}" fill="none" stroke="#7c3aed" stroke-width="1.8" marker-end="url(#arr-p)"/>')

    # Top Pipeline: Ripple-Carry SHA-256
    p.append(f'  <rect x="240" y="{y1+42}" width="356" height="68" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="1.3"/>')
    p.append(f'  <text x="254" y="{y1+61}" font-size="11" font-weight="700" fill="#1d4ed8">Circuit A: Ripple-Carry SHA-256 (prefix=False)</text>')
    p.append(f'  <text x="254" y="{y1+78}" font-family="{MONO}" font-size="9.2" fill="#1e293b">c[i+1] = g[i] | (p[i] &amp; c[i])   (depth 31 chain)</text>')
    p.append(f'  <text x="254" y="{y1+95}" font-size="8.8" fill="#475569">Msg schedule W[0..R-1] + R rounds (Ch, Maj, &#x03A3;0/&#x03A3;1) + IV feed-forward</text>')

    # Bottom Pipeline: Parallel-Prefix SHA-256
    p.append(f'  <rect x="240" y="{y1+126}" width="356" height="68" rx="8" fill="#faf5ff" stroke="#7c3aed" stroke-width="1.3"/>')
    p.append(f'  <text x="254" y="{y1+145}" font-size="11" font-weight="700" fill="#6d28d9">Circuit B: Parallel-Prefix SHA-256 (prefix=True)</text>')
    p.append(f'  <text x="254" y="{y1+162}" font-family="{MONO}" font-size="9.2" fill="#1e293b">5-level Kogge-Stone prefix (strides 1, 2, 4, 8, 16)</text>')
    p.append(f'  <text x="254" y="{y1+179}" font-size="8.8" fill="#475569">Identical mod-2^32 sum semantics, distinct internal carry-tree topology</text>')

    # Miter XOR + OR output stage
    p.append(f'  <path d="M 596 {y1+78} L 634 {y1+78} L 634 {y1+108} L 656 {y1+108}" fill="none" stroke="#1d4ed8" stroke-width="1.8" marker-end="url(#arr-b)"/>')
    p.append(f'  <path d="M 596 {y1+160} L 634 {y1+160} L 634 {y1+130} L 656 {y1+130}" fill="none" stroke="#7c3aed" stroke-width="1.8" marker-end="url(#arr-p)"/>')

    p.append(f'  <rect x="660" y="{y1+72}" width="114" height="92" rx="8" fill="#fff1f2" stroke="#e11d48" stroke-width="1.3"/>')
    p.append(f'  <text x="717" y="{y1+94}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#be123c">256-Bit Miter</text>')
    p.append(f'  <text x="717" y="{y1+114}" text-anchor="middle" font-family="{MONO}" font-size="9.4" font-weight="700" fill="#9f1239">d[i] = A[i] ^ B[i]</text>')
    p.append(f'  <text x="717" y="{y1+134}" text-anchor="middle" font-family="{MONO}" font-size="9.4" font-weight="700" fill="#9f1239">OR(d[0..255]) = 1</text>')
    p.append(f'  <text x="717" y="{y1+153}" text-anchor="middle" font-size="8.3" fill="#475569">Any digest mismatch</text>')

    p.append(f'  <line x1="774" y1="{y1+118}" x2="806" y2="{y1+118}" stroke="#dc2626" stroke-width="2" marker-end="url(#arr-r)"/>')

    p.append(f'  <rect x="810" y="{y1+82}" width="112" height="72" rx="8" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>')
    p.append(f'  <text x="866" y="{y1+107}" text-anchor="middle" font-size="12.5" font-weight="700" fill="#b91c1c">UNSAT</text>')
    p.append(f'  <text x="866" y="{y1+124}" text-anchor="middle" font-size="8.8" fill="#7f1d1d">Proves A(x) == B(x)</text>')
    p.append(f'  <text x="866" y="{y1+139}" text-anchor="middle" font-size="8.4" fill="#7f1d1d">for all 2^(8B) inputs</text>')

    # Section 2: Fixed-Message FIPS 180-4 Trace Mode ("abc")
    y2 = 304
    p.append(f'  <rect x="24" y="{y2}" width="912" height="78" rx="10" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y2+20}" font-size="11.4" font-weight="700" fill="#166534">'
             '2. Fixed-Message FIPS 180-4 Trace Verification Mode (--message-hex 616263 = "abc", R = 64 Rounds)</text>')
    p.append(f'  <text x="38" y="{y2+40}" font-family="{MONO}" font-size="9.6" fill="#0f172a">'
             f'SHA-256("abc") = {digest_abc}   (101,614 vars | 347,923 cls | 43,131 XORs)</text>')
    p.append(f'  <rect x="38" y="{y2+48}" width="276" height="22" rx="4" fill="#dcfce7" stroke="#4ade80" stroke-width="0.9"/>')
    p.append(f'  <text x="176" y="{y2+63}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#166534">'
             'trace_r64_abc (unconstrained): SAT (unique witness)</text>')
    p.append(f'  <rect x="326" y="{y2+48}" width="288" height="22" rx="4" fill="#dcfce7" stroke="#4ade80" stroke-width="0.9"/>')
    p.append(f'  <text x="470" y="{y2+63}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#166534">'
             'trace_r64_abc_expect_ok (...0015ad): SAT (exact match)</text>')
    p.append(f'  <rect x="626" y="{y2+48}" width="296" height="22" rx="4" fill="#fee2e2" stroke="#f87171" stroke-width="0.9"/>')
    p.append(f'  <text x="774" y="{y2+63}" text-anchor="middle" font-size="8.8" font-weight="700" fill="#b91c1c">'
             'trace_r64_abc_expect_flip (...0015ac, 1-bit flip): UNSAT</text>')

    # Section 3: Round & Byte Scaling Ladder (10 CEC Miters)
    y3 = 394
    p.append(f'  <rect x="24" y="{y3}" width="912" height="110" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')
    p.append(f'  <text x="38" y="{y3+20}" font-size="11.6" font-weight="700" fill="#0f172a">'
             '3. CEC Miter Scaling Ladder Across Rounds R = 1..64 &amp; Native XOR Density (Up to 87,076 XORs, 3.00M AIG ANDs)</text>')

    rungs = [
        ("R=1, B=4", "2.2K vars | 364 XORs", "18.3 KB .cnf.xz", "Tractable CEC", "#0f766e", "#f0fdfa"),
        ("R=2, B=2 & 4", "4.7K-6.4K vars", "887-1.3K XORs", "Sharp solver split", "#2563eb", "#eff6ff"),
        ("R=4, B=1 & 4", "12.5K-15.9K vars", "2.6K-3.3K XORs", "B=1 fast / B=4 hard", "#4f46e5", "#eef2ff"),
        ("R=8, B=1 & 4", "30.3K-33.3K vars", "6.4K-7.1K XORs", "B=1 ~1s / B=4 hard", "#7c3aed", "#faf5ff"),
        ("R=16 & R=32", "68K-154K vars", "14.7K-34.1K XORs", "Deep CEC frontier", "#d97706", "#fffbeb"),
        ("R=64, B=4", "373K vars | 1.21M cls", "87,076 native XORs", "Full FIPS 180-4 CEC", "#be123c", "#fff1f2"),
    ]
    rw = 140
    rgap = 8.8
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for i, (t1, t2, t3, t4, sc, bg) in enumerate(rungs):
        rx = 38 + i * (rw + rgap)
        p.append(f'  <rect x="{rx:.1f}" y="{y3+32}" width="{rw}" height="66" rx="7" fill="{bg}" stroke="{sc}" stroke-width="1.1"/>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y3+48}" text-anchor="middle" font-family="{MONO}" font-size="9.4" font-weight="700" fill="{sc}">{esc(t1)}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y3+63}" text-anchor="middle" font-size="8.4" font-weight="600" fill="#0f172a">{esc(t2)}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y3+77}" text-anchor="middle" font-size="8.1" fill="#334155">{esc(t3)}</text>')
        p.append(f'  <text x="{rx+rw/2:.1f}" y="{y3+91}" text-anchor="middle" font-size="7.9" fill="#475569">{esc(t4)}</text>')

    p.append("</g>\n</svg>\n")
    return "\n".join(p)


def main() -> None:
    OUT.write_text(build_svg(), encoding="utf-8")
    ET.parse(OUT)
    print(f"Wrote and XML-validated {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
