#!/usr/bin/env python3
"""Generate publication-grade SVG scaling diagrams (`diagram.svg` and
`growth_analysis.svg`) for the `sha256-64r-nonce-scaling` benchmark collection.

Plots empirical single-core wall-clock solve times T(k) across k = 1..32 unknown
nonce bits of full 64-round FIPS 180-4 SHA-256 (W_0 = 0x9E3779B9, T_max = 300 s)
for all 7 solver tracks (5 SAT engines), alongside the 300 s cutoff line,
Frobenius's cliff-free piecewise regimes (Stage 0C -> Stage 0F 2048-lane AVX2 ->
shortcut-probe + 2048-lane escalation solving all 32/32 instances inside 300 s),
and shifted pure-exponential M1 best-fit curves.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"
OUT_GROWTH_SVG = Path(__file__).resolve().parent.parent / "growth_analysis.svg"

FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Exact single-core median/measured wall-clock times (seconds) on AMD Ryzen 9 5950X (CCD 1 core 12).
# Frobenius tracks evaluated at commit 5f04ce8 (cliff-free shortcut-first + 2048-lane early-exit AVX2).
EMPIRICAL_SEC: dict[str, list[tuple[int, float]]] = {
    "frobenius_aig": [
        (1, 0.001321), (2, 0.033381), (3, 0.033151), (4, 0.033307), (5, 0.034022),
        (6, 0.033720), (7, 0.034650), (8, 0.034016), (9, 0.041996), (10, 0.041965),
        (11, 0.041342), (12, 0.041891), (13, 0.042581), (14, 0.059082), (15, 0.059635),
        (16, 0.062983), (17, 0.065768), (18, 0.072797), (19, 0.087792), (20, 0.118281),
        (21, 0.175609), (22, 0.290589), (23, 0.528345), (24, 0.984260), (25, 2.514567),
        (26, 4.362111), (27, 8.083584), (28, 15.464652), (29, 30.176542), (30, 59.670022),
        (31, 124.634344), (32, 249.845147),
    ],
    "frobenius_cnf": [
        (1, 0.001483), (2, 0.080112), (3, 0.104678), (4, 0.103452), (5, 0.102904),
        (6, 0.103139), (7, 0.102652), (8, 0.105553), (9, 0.110794), (10, 0.108892),
        (11, 0.108415), (12, 0.109714), (13, 0.110023), (14, 0.125245), (15, 0.128901),
        (16, 0.127796), (17, 0.130443), (18, 0.136945), (19, 0.146381), (20, 0.169332),
        (21, 0.215628), (22, 0.307270), (23, 0.502963), (24, 0.859386), (25, 2.269195),
        (26, 3.687928), (27, 6.821121), (28, 12.674746), (29, 30.148723), (30, 54.117110),
        (31, 108.417972), (32, 197.827524),
    ],
    "cadical_cnf": [
        (1, 0.002081), (2, 0.089583), (3, 0.104077), (4, 0.104277), (5, 0.347259),
        (6, 0.445009), (7, 0.271790), (8, 0.851340), (9, 2.043298), (10, 2.207571),
        (11, 12.503513), (12, 13.917853), (13, 6.706187), (14, 40.003453),
        (15, 159.393456), (16, 89.397970), (17, 6.479862),
    ],
    "dense_cnf": [
        (1, 0.001140), (2, 0.970620), (3, 0.928940), (4, 0.936922), (5, 0.967432),
        (6, 1.064030), (7, 1.233144), (8, 1.439140), (9, 2.066041), (10, 2.440858),
        (11, 4.468282), (12, 12.905532), (13, 14.294957), (14, 34.907152),
        (15, 178.356930), (16, 101.827280), (17, 159.706510),
    ],
    "kissat_cnf": [
        (1, 0.001367), (2, 0.055549), (3, 0.307450), (4, 0.376759), (5, 0.381713),
        (6, 0.559233), (7, 0.639200), (8, 0.785569), (9, 1.699290), (10, 7.214650),
        (11, 1.062626), (12, 21.920612), (13, 21.363960), (14, 50.916730),
        (15, 35.789470),
    ],
    "cms_cnf": [
        (1, 0.005344), (2, 5.930960), (3, 9.359480), (4, 12.216410), (5, 25.673170),
        (6, 22.648440), (7, 45.035320), (8, 59.249060), (9, 55.511880),
        (10, 112.351140), (11, 255.404030), (12, 230.644910),
    ],
    "cms_xcnf": [
        (1, 0.005147), (2, 0.299242), (3, 5.732680), (4, 7.388100), (5, 27.690830),
        (6, 21.630030), (7, 27.904410), (8, 44.648470), (9, 32.804260),
        (10, 62.934870), (11, 138.605350),
    ],
}

TIMEOUT_KS: dict[str, list[int]] = {
    "frobenius_aig": [],
    "frobenius_cnf": [],
    "cadical_cnf": [18, 19, 20],
    "dense_cnf": [18, 19, 20],
    "kissat_cnf": [16, 17, 18],
    "cms_cnf": [13, 14, 15],
    "cms_xcnf": [12, 13, 14],
}

# Best-fit M1 curves: (c0_sec, a_sec, alpha, k_start, k_end)
M1_FITS: dict[str, tuple[float, float, float, float, float]] = {
    "frobenius_aig": (0.05751, 6.1818e-8, 0.9973, 14.0, 32.0),
    "frobenius_cnf": (0.12257, 4.6245e-8, 1.0042, 14.0, 32.0),
    "dense_cnf": (0.89826, 2.713e-3, 0.9708, 2.0, 18.0),
    "cadical_cnf": (0.04902, 1.054e-2, 0.8098, 2.0, 18.5),   # Tobit right-censored M1
    "kissat_cnf": (0.16666, 2.926e-3, 1.0073, 2.0, 17.0),    # Tobit right-censored M1
    "cms_cnf": (0.0, 2.981, 0.5337, 2.0, 13.5),
    "cms_xcnf": (0.0, 0.5370, 0.7905, 2.0, 12.5),            # Tobit right-censored M1
}

TRACK_STYLE = [
    ("frobenius_cnf", "Frobenius 1C (.cnf)",   "#0284c7", "32/32", "α=1.004 (2.01×/b)", "3.30 min*", "diamond",  ""),
    ("frobenius_aig", "Frobenius 1C (.aig)",   "#059669", "32/32", "α=0.997 (2.00×/b)", "4.16 min*", "circle",   ""),
    ("cadical_cnf",   "CaDiCaL 3.1.0 (.cnf)",  "#d97706", "17/32", "α=0.810† (1.75×)",  "7.7 d†",    "square",   ""),
    ("dense_cnf",     "dense-solver 0.0.4",    "#7c3aed", "17/32", "α=0.971 (1.96×/b)", "70.6 d",    "triangle", ""),
    ("kissat_cnf",    "Kissat 4.0.4 (.cnf)",   "#dc2626", "15/32", "α=1.007† (2.01×)",  "171 d†",    "circle",   ""),
    ("cms_cnf",       "CMS 5.18.0 (.cnf)",     "#475569", "12/32", "α=0.707‡ (1.63×)",  "55.3 d‡",   "square",   ""),
    ("cms_xcnf",      "CMS 5.18.0 (.xcnf)",    "#db2777", "11/32", "α=0.791† (1.73×)",  "256 d†",    "diamond",  "4,2"),
]


def draw_marker(parts: list[str], shape: str, cx: float, cy: float, color: str, r: float = 3.0, hollow: bool = False) -> None:
    fill = "#ffffff" if hollow else color
    sw = "1.4" if hollow else "0.8"
    stroke = color if hollow else "#ffffff"
    if shape == "circle":
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    elif shape == "square":
        parts.append(f'<rect x="{cx - r + 0.3:.1f}" y="{cy - r + 0.3:.1f}" width="{2 * (r - 0.3):.1f}" height="{2 * (r - 0.3):.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    elif shape == "diamond":
        d = r + 0.6
        pts = f"{cx:.1f},{cy - d:.1f} {cx + d:.1f},{cy:.1f} {cx:.1f},{cy + d:.1f} {cx - d:.1f},{cy:.1f}"
        parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    elif shape == "triangle":
        d = r + 0.5
        pts = f"{cx:.1f},{cy - d:.1f} {cx + d:.1f},{cy + d * 0.85:.1f} {cx - d:.1f},{cy + d * 0.85:.1f}"
        parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def build_svg() -> str:
    W, H = 920, 560
    px0, py0, pw, ph = 78, 86, 568, 326
    px1, py1 = px0 + pw, py0 + ph

    # Coordinate mappers: k in [0.5, 32.8], log10(T_sec) in [-3.1, 3.15] (0.8 ms .. 1,412 s)
    k_min, k_max = 0.5, 32.8
    ly_min, ly_max = -3.1, 3.15

    def mx(k: float) -> float:
        return px0 + (k - k_min) / (k_max - k_min) * pw

    def my(t_sec: float) -> float:
        ly = math.log10(max(t_sec, 1e-4))
        ly = max(ly_min, min(ly_max, ly))
        return py1 - (ly - ly_min) / (ly_max - ly_min) * ph

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="FIPS 180-4 64-round SHA-256 nonce-scaling benchmark log-scale runtime curves across 7 solver tracks">',
        "<defs>",
        f'  <clipPath id="plot-clip"><rect x="{px0}" y="{py0}" width="{pw}" height="{ph}"/></clipPath>',
        "</defs>",
        # White outer card
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="24" y="32" font-size="16.8" font-weight="700" fill="#0f172a">'
        "FIPS 180-4 SHA-256 (64-Round) Nonce Scaling: k = 1..32 Unknown Bits</text>",
        '<text x="24" y="51" font-size="11.1" fill="#475569">'
        "Single-core wall-clock T(k) on AMD Ryzen 9 5950X (core 12, Tₘₐₓ = 300 s, W₀ = 0x9E3779B9, "
        "290/290 SAT verified) · 5 engines (7 tracks)</text>",
        '<line x1="22" y1="62" x2="898" y2="62" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # Plot frame & cliff-free regime background tints (smooth Stage 0C -> unified CompiledAig256 k=14..32)
    parts.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    rx_s0 = mx(1.5)
    rx_s1 = mx(13.5)
    parts.append(f'<rect x="{rx_s0:.1f}" y="{py0 + 1}" width="{rx_s1 - rx_s0:.1f}" height="{ph - 2}" fill="#eff6ff" opacity="0.55"/>')
    parts.append(f'<rect x="{rx_s1:.1f}" y="{py0 + 1}" width="{px1 - rx_s1 - 1:.1f}" height="{ph - 2}" fill="#ecfdf5" opacity="0.62"/>')

    # Regime header badges cleanly inside top band (above 300s line, y = py0 + 14)
    parts.append(f'<text x="{(rx_s0 + rx_s1)/2:.1f}" y="{py0 + 14}" text-anchor="middle" font-size="8.3" font-weight="700" fill="#1d4ed8">Stage 0C (k=2..13)</text>')
    parts.append(f'<text x="{(rx_s1 + px1)/2:.1f}" y="{py0 + 14}" text-anchor="middle" font-size="8.3" font-weight="700" fill="#047857">Unified 2048-lane CompiledAig256 AVX2 (k=14..32, zero k≤24 cliff)</text>')

    # Horizontal grid lines & Y-axis labels
    y_ticks = [
        (1e-3, "1 ms"),
        (1e-2, "10 ms"),
        (1e-1, "100 ms"),
        (1.0,  "1 s"),
        (10.0, "10 s"),
        (100.0, "100 s"),
        (1000.0, "1,000 s"),
    ]
    for tv, lbl in y_ticks:
        yy = my(tv)
        parts.append(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px1}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="0.9"/>')
        parts.append(f'<line x1="{px0 - 4}" y1="{yy:.1f}" x2="{px0}" y2="{yy:.1f}" stroke="#64748b" stroke-width="1"/>')
        parts.append(f'<text x="{px0 - 7}" y="{yy + 3.2:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="9.0" fill="#334155">{lbl}</text>')

    # Vertical grid lines & X-axis labels
    for kv in [1, 4, 8, 12, 16, 20, 24, 28, 32]:
        xx = mx(kv)
        parts.append(f'<line x1="{xx:.1f}" y1="{py0}" x2="{xx:.1f}" y2="{py1}" stroke="#e2e8f0" stroke-width="0.8"/>')
        parts.append(f'<line x1="{xx:.1f}" y1="{py1}" x2="{xx:.1f}" y2="{py1 + 4}" stroke="#64748b" stroke-width="1"/>')
        parts.append(f'<text x="{xx:.1f}" y="{py1 + 16}" text-anchor="middle" font-family="{FONT_MONO}" font-size="9.2" fill="#334155">{kv}</text>')

    # Horizontal T_max = 300 s cutoff line
    y300 = my(300.0)
    parts.append(f'<line x1="{px0}" y1="{y300:.1f}" x2="{px1}" y2="{y300:.1f}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="6,3.5"/>')
    parts.append(f'<rect x="{px0 + 6}" y="{y300 - 15.5:.1f}" width="112" height="13.5" rx="3" fill="#fef2f2" stroke="#fca5a5" stroke-width="0.8"/>')
    parts.append(f'<text x="{px0 + 11}" y="{y300 - 5.5:.1f}" font-size="8.4" font-weight="700" fill="#b91c1c">Tₘₐₓ = 300 s cutoff</text>')

    # Axis titles
    parts.append(f'<text x="{(px0 + px1)/2:.1f}" y="{py1 + 31}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#0f172a">Unknown Nonce Bits k  (LSB prefix of W₀ = 0x9E3779B9)</text>')
    parts.append(f'<text x="20" y="{(py0 + py1)/2:.1f}" text-anchor="middle" font-size="10.4" font-weight="700" fill="#0f172a" transform="rotate(-90 20 {(py0 + py1)/2:.1f})">Wall-Clock Runtime T(k)  [log scale]</text>')

    # Clipped plot contents: fitted curves first (subtle dashed), then empirical curves & markers
    parts.append('<g clip-path="url(#plot-clip)">')

    # Fitted M1 dashed curves (Frobenius .aig & .cnf over k=14..32; CDCL capped at 300 s)
    for tid, _, color, _, _, _, _, _ in TRACK_STYLE:
        c0, a, al, ks0, ks1 = M1_FITS[tid]
        t_cap = 300.0
        pts = []
        steps = 48
        for s in range(steps + 1):
            kf = ks0 + (ks1 - ks0) * (s / steps)
            tf = c0 + a * (2.0 ** (al * kf))
            if tf <= t_cap:
                pts.append(f"{mx(kf):.1f},{my(tf):.1f}")
        if len(pts) >= 2:
            op = "0.55" if tid.startswith("frobenius") else "0.35"
            sw = "1.4" if tid.startswith("frobenius") else "1.1"
            parts.append(
                f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                f'stroke-width="{sw}" stroke-dasharray="3.5,3" opacity="{op}"/>'
            )

    # Empirical curves (draw CMS/CDCL first, Frobenius on top for maximum legibility)
    draw_order = ["cms_xcnf", "cms_cnf", "kissat_cnf", "dense_cnf", "cadical_cnf", "frobenius_aig", "frobenius_cnf"]
    style_by_id = {row[0]: row for row in TRACK_STYLE}
    for tid in draw_order:
        _, _, color, _, _, _, shape, dash = style_by_id[tid]
        data = EMPIRICAL_SEC[tid]
        # Connect k >= 2 continuously; k=1 connected with thin dotted segment (0-AND symbolic collapse)
        p1 = data[0]
        p2 = data[1]
        parts.append(
            f'<line x1="{mx(p1[0]):.1f}" y1="{my(p1[1]):.1f}" x2="{mx(p2[0]):.1f}" y2="{my(p2[1]):.1f}" '
            f'stroke="{color}" stroke-width="1.1" stroke-dasharray="2,2" opacity="0.55"/>'
        )
        pts = " ".join(f"{mx(k):.1f},{my(t):.1f}" for k, t in data[1:])
        sw = "2.2" if tid.startswith("frobenius") else "1.7"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}"{da}/>')

        # Connector up to first timeout k0 (dotted steep jump) — only for tracks with timeouts!
        to_ks = TIMEOUT_KS[tid]
        if to_ks:
            k_last, t_last = data[-1]
            k_to0 = to_ks[0]
            parts.append(
                f'<line x1="{mx(k_last):.1f}" y1="{my(t_last):.1f}" x2="{mx(k_to0):.1f}" y2="{y300:.1f}" '
                f'stroke="{color}" stroke-width="1.2" stroke-dasharray="2.5,2.5" opacity="0.65"/>'
            )

        # Markers on empirical points
        hollow = tid in ("frobenius_cnf", "cms_xcnf")
        rad = 2.8 if tid.startswith("frobenius") else 2.5
        for k, t in data:
            draw_marker(parts, shape, mx(k), my(t), color, r=rad, hollow=hollow)

        # Crisp X marker at first timeout k0 along 300 s line
        if to_ks:
            xt = mx(to_ks[0])
            parts.append(f'<path d="M {xt - 3.3:.1f} {y300 - 3.3:.1f} L {xt + 3.3:.1f} {y300 + 3.3:.1f} M {xt - 3.3:.1f} {y300 + 3.3:.1f} L {xt + 3.3:.1f} {y300 - 3.3:.1f}" stroke="{color}" stroke-width="1.6"/>')

    # Clean in-plot callouts (placed in guaranteed open whitespace!)
    # Callout 1: Smooth fixed-floor -> 2^k search crossover knee around k* ≈ 19.8 (.aig) / 21.3 (.cnf)
    cx1 = mx(18.6)
    cy1 = my(38.0)
    parts.append(f'<rect x="{cx1:.1f}" y="{cy1:.1f}" width="154" height="31" rx="4" fill="#ffffff" stroke="#047857" stroke-width="0.95" opacity="0.96"/>')
    parts.append(f'<text x="{cx1 + 77:.1f}" y="{cy1 + 12.5:.1f}" text-anchor="middle" font-size="8.1" font-weight="700" fill="#047857">Overhead → 2ᵏ knee (k*≈20–21)</text>')
    parts.append(f'<text x="{cx1 + 77:.1f}" y="{cy1 + 24.5:.1f}" text-anchor="middle" font-size="7.7" fill="#334155">a·2ᵏ* = c₀ (58–123 ms floor)</text>')

    # Callout 2: Full 32-bit T(32) solved inside 300 s (open lower-right whitespace below k=25..32 curve)
    cx2 = mx(24.7)
    cy2 = my(0.085)
    parts.append(f'<rect x="{cx2:.1f}" y="{cy2:.1f}" width="136" height="31" rx="4" fill="#ffffff" stroke="#0284c7" stroke-width="0.95" opacity="0.96"/>')
    parts.append(f'<text x="{cx2 + 68:.1f}" y="{cy2 + 12.5:.1f}" text-anchor="middle" font-size="8.2" font-weight="700" fill="#0369a1">32/32 solved (&lt;300 s, 1C!)</text>')
    parts.append(f'<text x="{cx2 + 68:.1f}" y="{cy2 + 24.5:.1f}" text-anchor="middle" font-size="7.8" fill="#334155">T(32): 3.30m .cnf · 4.16m .aig</text>')

    # Callout 3: k=1 symbolic collapse
    parts.append(f'<text x="{mx(1.4):.1f}" y="{my(0.00125) + 3:.1f}" font-size="7.8" fill="#64748b">k=1: 0-AND collapse</text>')

    parts.append("</g>")  # end plot-clip

    # ===================== RIGHT LEGEND & FIT SUMMARY PANEL =====================
    lx, ly, lw, lh = 658, 86, 240, 326
    parts.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    parts.append(f'<text x="{lx + 11}" y="{ly + 19}" font-size="10.8" font-weight="700" fill="#0f172a">7 Solver Tracks &amp; M1 Fits</text>')
    parts.append(f'<text x="{lx + 11}" y="{ly + 32}" font-size="8.0" fill="#64748b">T(k) = c₀ + a·2^(αk)   |   Solved · T(32) 1C</text>')
    parts.append(f'<line x1="{lx + 10}" y1="{ly + 38}" x2="{lx + lw - 10}" y2="{ly + 38}" stroke="#e2e8f0" stroke-width="1"/>')

    row_y0 = ly + 52
    row_dy = 35.5
    for idx, (tid, label, color, solved, exp_s, t32_s, shape, dash) in enumerate(TRACK_STYLE):
        ry = row_y0 + idx * row_dy
        if idx % 2 == 1:
            parts.append(f'<rect x="{lx + 6}" y="{ry - 11}" width="{lw - 12}" height="{row_dy - 2:.1f}" rx="4" fill="#ffffff"/>')
        da = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<line x1="{lx + 13}" y1="{ry - 1}" x2="{lx + 31}" y2="{ry - 1}" stroke="{color}" stroke-width="2.2"{da}/>')
        draw_marker(parts, shape, lx + 22, ry - 1, color, r=2.8, hollow=(tid in ("frobenius_cnf", "cms_xcnf")))
        parts.append(f'<text x="{lx + 37}" y="{ry + 2}" font-size="9.4" font-weight="700" fill="#0f172a">{label}</text>')
        parts.append(f'<text x="{lx + lw - 11}" y="{ry + 2}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.7" font-weight="700" fill="{color}">{solved}</text>')
        parts.append(f'<text x="{lx + 37}" y="{ry + 14.5}" font-family="{FONT_MONO}" font-size="8.1" fill="#475569">{exp_s}</text>')
        parts.append(f'<text x="{lx + lw - 11}" y="{ry + 14.5}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.1" fill="#334155">T₃₂:{t32_s}</text>')

    parts.append(f'<line x1="{lx + 10}" y1="{ly + lh - 29}" x2="{lx + lw - 10}" y2="{ly + lh - 29}" stroke="#e2e8f0" stroke-width="1"/>')
    parts.append(f'<text x="{lx + 11}" y="{ly + lh - 17}" font-size="7.4" fill="#64748b">*Actual measured 1C T(32) (&lt;300s, k=14..32 R²&gt;0.999)</text>')
    parts.append(f'<text x="{lx + 11}" y="{ly + lh - 6.5}" font-size="7.4" fill="#64748b">†Tobit right-censored M1 (+3 T/Os)  ‡Post-floor k≥5</text>')

    # ===================== BOTTOM 3 CALLOUT CARDS =====================
    by, bh = 456, 86
    cards = [
        (
            24, 280, "#f8fafc", "#cbd5e1", "#0f172a",
            "1. Zero-Bias FIPS 180-4 Specification",
            "• 32 SAT instances: k = 1..32 LSBs of W₀",
            "• W₀ = 0x9E3779B9 (floor(2³²/φ), 20/32 popcnt)",
            "• Bit-rev anchor ≈ 0.616 → zero lucky bias",
            "• 4 formats: .aig/.cnf/.xcnf/.anf (50.7 MB)",
        ),
        (
            318, 284, "#ecfdf5", "#a7f3d0", "#047857",
            "2. Cliff-Free 2048-Lane AVX2 (32/32)",
            "• .cnf: 32/32, T(32)=3.30m (12.8M evals/s)",
            "• .aig: 32/32, T(32)=4.16m (11.2M evals/s)",
            "• k=14..32 M1: α=0.997 (.aig) / 1.004 (.cnf)",
            "• 22.2–30.9× lower PAR-2 than all CDCL tracks",
        ),
        (
            616, 282, "#eff6ff", "#bfdbfe", "#1d4ed8",
            "3. AICc/BIC Model Selection (M1–M4)",
            "• Pure exp M1 wins every single-codepath fit",
            "• +0.6s probe step at k=25 (&lt;0.3% at k=32)",
            "• 3,367–111,922× faster T(32) than CDCL",
            "• 290/290 SAT models verified (0 BADSAT)",
        ),
    ]
    for cx, cw, bg, bd, hdr_c, title, l1, l2, l3, l4 in cards:
        parts.append(f'<rect x="{cx}" y="{by}" width="{cw}" height="{bh}" rx="8" fill="{bg}" stroke="{bd}" stroke-width="1.1"/>')
        parts.append(f'<text x="{cx + 11}" y="{by + 18}" font-size="10.2" font-weight="700" fill="{hdr_c}">{title}</text>')
        for li, txt in enumerate([l1, l2, l3, l4]):
            parts.append(f'<text x="{cx + 11}" y="{by + 34 + li * 13.5:.1f}" font-size="8.6" fill="#334155">{txt}</text>')

    parts.append("</g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def build_growth_analysis_svg() -> str:
    """Build a 3-panel publication-grade SVG chart (`growth_analysis.svg`):
    - Top-Left:  Doubling exponent alpha (uncensored M1 vs right-censored Tobit MLE) vs exact 2^k
    - Top-Right: Measured (Frobenius) vs extrapolated (CDCL) full 32-bit nonce time T(32) on log scale
    - Bottom:    Model selection Delta-AICc (M2/M3/M4 vs shifted pure exponential M1)
    """
    W, H = 920, 620
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Growth-curve analysis: doubling exponents, 32-bit nonce inversion times, and AICc model selection across 7 SAT tracks">',
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="12" '
        'fill="#ffffff" stroke="#d0d7de" stroke-width="1.5"/>',
        f'<g font-family="{FONT_SANS}">',
        # Header
        '<text x="24" y="31" font-size="16.4" font-weight="700" fill="#0f172a">'
        "Growth-Curve Fits, 32-Bit Nonce Inversion Times &amp; Sub-Exponential Model Selection</text>",
        '<text x="24" y="49" font-size="10.8" fill="#475569">'
        "Shifted pure exponential M1: T(k) = c₀ + a·2^(αk) vs. polynomial (M2), √k (M3), and stretched-exp (M4) · 64-round FIPS 180-4 SHA-256 (1C)</text>",
        '<line x1="22" y1="60" x2="898" y2="60" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # Track data ordered by T(32) / performance (matching README Table 2 exact numbers)
    # (short_label, color, alpha_ols, alpha_tobit_or_none, t32_sec, t32_label, speedup_vs_frob_cnf, daicc_m2, daicc_m3, daicc_m4)
    # Note: Panel C plots full k=14..32 for Frobenius (.aig) and single-codepath k=14..24 / k=25..32 note vs k=14..32 seam for .cnf.
    # Here we show exact k=14..32 Delta-AICc for both Frobenius tracks (transparently showing the +2.08 seam blip on .cnf at k=25).
    rows = [
        ("Frobenius (.cnf)", "#0284c7", 1.0042, None,   197.83,      "3.30 min*",  "1.0×",     +2.08, +2.08, +2.08),
        ("Frobenius (.aig)", "#059669", 0.9973, None,   249.85,      "4.16 min*",  "1.3×",     -0.85, -0.89, -0.91),
        ("CaDiCaL (.cnf)",   "#d97706", 0.6916, 0.8098, 7.71*86400,  "7.71 d†",    "3,367×",   -2.27, -3.04, -2.43),
        ("CMS (.cnf)",       "#475569", 0.5337, 0.5438, 55.29*86400, "55.3 d‡",    "24,149×",  -7.33, -7.33, -7.32),
        ("dense (.cnf)",     "#7c3aed", 0.9708, 0.9753, 70.61*86400, "70.6 d",     "30,838×",  -2.26, -2.85, -2.35),
        ("Kissat (.cnf)",    "#dc2626", 0.7613, 1.0073, 171.19*86400,"171.2 d†",   "74,766×",  -5.00, -4.88, -4.59),
        ("CMS (.xcnf)",      "#db2777", 0.7096, 0.7905, 256.27*86400,"256.3 d†",   "111,922×", -1.66, -5.75, -2.96),
    ]

    # ===================== PANEL A (TOP-LEFT): DOUBLING EXPONENT alpha =====================
    ax0, ay0, aw, ah = 24, 74, 424, 286
    parts.append(f'<rect x="{ax0}" y="{ay0}" width="{aw}" height="{ah}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    parts.append(f'<text x="{ax0 + 12}" y="{ay0 + 20}" font-size="11.4" font-weight="700" fill="#0f172a">A. Fitted Scaling Exponent α  (base b = 2^α per bit)</text>')
    parts.append(f'<text x="{ax0 + 12}" y="{ay0 + 34}" font-size="8.6" fill="#64748b">Solid bar: uncensored M1 (Frobenius k=14..32) · Diamond: Tobit MLE (+3 T/Os)</text>')

    px0, py0, pw, ph = ax0 + 114, ay0 + 48, 294, 206
    def ax_map(a: float) -> float:
        return px0 + (a / 1.32) * pw

    parts.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="3" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    for av in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]:
        xx = ax_map(av)
        sc = "#dc2626" if abs(av - 1.0) < 1e-6 else "#e2e8f0"
        sw = "1.4" if abs(av - 1.0) < 1e-6 else "0.9"
        da = ' stroke-dasharray="4,3"' if abs(av - 1.0) < 1e-6 else ""
        parts.append(f'<line x1="{xx:.1f}" y1="{py0}" x2="{xx:.1f}" y2="{py0 + ph}" stroke="{sc}" stroke-width="{sw}"{da}/>')
        lbl = "1.0 (2ᵏ)" if abs(av - 1.0) < 1e-6 else f"{av:.1f}"
        fc = "#b91c1c" if abs(av - 1.0) < 1e-6 else "#475569"
        fw = "700" if abs(av - 1.0) < 1e-6 else "400"
        parts.append(f'<text x="{xx:.1f}" y="{py0 + ph + 14}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.3" font-weight="{fw}" fill="{fc}">{lbl}</text>')

    row_h = ph / len(rows)
    for i, (lbl, col, a_ols, a_tob, _, _, _, _, _, _) in enumerate(rows):
        cy = py0 + (i + 0.5) * row_h
        parts.append(f'<text x="{px0 - 7}" y="{cy + 3.2:.1f}" text-anchor="end" font-size="9.0" font-weight="600" fill="#1e293b">{lbl}</text>')
        bw = ax_map(a_ols) - px0
        parts.append(f'<rect x="{px0}" y="{cy - 7.5:.1f}" width="{bw:.1f}" height="15" rx="3" fill="{col}" opacity="0.84"/>')
        if a_tob is not None:
            xt = ax_map(a_tob)
            if abs(xt - ax_map(a_ols)) > 4:
                parts.append(f'<line x1="{ax_map(a_ols):.1f}" y1="{cy:.1f}" x2="{xt:.1f}" y2="{cy:.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="2,2"/>')
            draw_marker(parts, "diamond", xt, cy, col, r=4.2, hollow=True)
            tx = max(ax_map(a_ols), xt) + 7
            if 0.90 <= max(a_ols, a_tob) <= 1.02:
                tx = max(tx, ax_map(1.0) + 6)
            val_txt = "0.53→0.54 (0.71‡)" if lbl == "CMS (.cnf)" else f"{a_ols:.2f}→{a_tob:.2f}"
        else:
            tx = max(ax_map(a_ols) + 6, ax_map(1.0) + 6)
            val_txt = f"{a_ols:.3f}"
        if tx + len(val_txt) * 4.7 > px0 + pw - 2:
            parts.append(f'<text x="{ax_map(a_ols) - 5:.1f}" y="{cy + 3.0:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="7.9" font-weight="700" fill="#ffffff">{val_txt}</text>')
        else:
            parts.append(f'<text x="{tx:.1f}" y="{cy + 3.0:.1f}" font-family="{FONT_MONO}" font-size="7.9" font-weight="700" fill="#334155">{val_txt}</text>')

    # ===================== PANEL B (TOP-RIGHT): FULL 32-BIT NONCE TIME T(32) =====================
    bx0, by0, bw_box, bh_box = 462, 74, 434, 286
    parts.append(f'<rect x="{bx0}" y="{by0}" width="{bw_box}" height="{bh_box}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    parts.append(f'<text x="{bx0 + 12}" y="{by0 + 20}" font-size="11.4" font-weight="700" fill="#0f172a">B. Full 32-Bit Nonce Inversion Time T(32)  [log scale]</text>')
    parts.append(f'<text x="{bx0 + 12}" y="{by0 + 34}" font-size="8.6" fill="#64748b">Measured 1C (3.3–4.2 min) vs. Extrapolated CDCL (days) · 3,367×–111,922× gap</text>')

    qpx0, qpy0, qpw, qph = bx0 + 112, by0 + 48, 304, 206
    # log10(T32 in sec) from 10^1.8 s (63 s) to 10^8.3 s (~6.3 years)
    lt_min, lt_max = 1.8, 8.3
    def bx_map(t_sec: float) -> float:
        lt = max(lt_min, min(lt_max, math.log10(t_sec)))
        return qpx0 + (lt - lt_min) / (lt_max - lt_min) * qpw

    parts.append(f'<rect x="{qpx0}" y="{qpy0}" width="{qpw}" height="{qph}" rx="3" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    time_ticks = [
        (300.0, "5m"),
        (3600.0, "1h"),
        (86400.0, "1d"),
        (10 * 86400.0, "10d"),
        (100 * 86400.0, "100d"),
        (365 * 86400.0, "1y"),
    ]
    for tv, tlbl in time_ticks:
        xx = bx_map(tv)
        is_cut = abs(tv - 300.0) < 1e-6
        sc = "#dc2626" if is_cut else "#e2e8f0"
        sw = "1.3" if is_cut else "0.9"
        da = ' stroke-dasharray="4,3"' if is_cut else ""
        parts.append(f'<line x1="{xx:.1f}" y1="{qpy0}" x2="{xx:.1f}" y2="{qpy0 + qph}" stroke="{sc}" stroke-width="{sw}"{da}/>')
        fc = "#b91c1c" if is_cut else "#475569"
        fw = "700" if is_cut else "400"
        parts.append(f'<text x="{xx:.1f}" y="{qpy0 + qph + 14}" text-anchor="middle" font-family="{FONT_MONO}" font-size="8.4" font-weight="{fw}" fill="{fc}">{tlbl}</text>')

    for i, (lbl, col, _, _, t32_s, t32_lbl, sp_lbl, _, _, _) in enumerate(rows):
        cy = qpy0 + (i + 0.5) * row_h
        parts.append(f'<text x="{qpx0 - 7}" y="{cy + 3.2:.1f}" text-anchor="end" font-size="9.0" font-weight="600" fill="#1e293b">{lbl}</text>')
        bar_w = max(4.0, bx_map(t32_s) - qpx0)
        parts.append(f'<rect x="{qpx0}" y="{cy - 7.5:.1f}" width="{bar_w:.1f}" height="15" rx="3" fill="{col}" opacity="0.86"/>')
        txt = f"{t32_lbl} ({sp_lbl})" if i >= 2 else f"{t32_lbl} (&lt;5m)"
        tx = qpx0 + bar_w + 6
        if i < 2:
            # Place cleanly right of the red 5m cutoff line so text never crosses the dashed line!
            tx = max(tx, bx_map(300.0) + 6)
        if tx + len(txt) * 4.7 > qpx0 + qpw - 2:
            parts.append(f'<text x="{qpx0 + bar_w - 5:.1f}" y="{cy + 3.0:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="7.8" font-weight="700" fill="#ffffff">{txt}</text>')
        else:
            parts.append(f'<text x="{tx:.1f}" y="{cy + 3.0:.1f}" font-family="{FONT_MONO}" font-size="7.8" font-weight="700" fill="#334155">{txt}</text>')

    # ===================== PANEL C (BOTTOM): AICc MODEL SELECTION =====================
    cx0, cy0, cw, ch = 24, 374, 872, 226
    parts.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    parts.append(f'<text x="{cx0 + 12}" y="{cy0 + 20}" font-size="11.4" font-weight="700" fill="#0f172a">C. Sub-Exponential Hypothesis Test: ΔAICc = AICc(M1) − AICc(Mⱼ)  (Values &gt; +2 Required to Beat Pure Exponential M1)</text>')
    parts.append(f'<text x="{cx0 + 12}" y="{cy0 + 34}" font-size="8.5" fill="#64748b">Pure exponential M1 wins 6/7 full tracks directly; .cnf k=14..32 (+2.1§) is solely the +0.6s k=25 probe seam (single-path k=14..24: −3.6, k=25..32: −15.9)</text>')

    cpx0, cpy0, cpw, cph = cx0 + 58, cy0 + 48, 796, 126
    # y in [-9.0, +4.2] (cleanly accommodates +2.1 seam bar + label above it without clipping)
    dy_min, dy_max = -9.0, 4.2
    def cy_map(v: float) -> float:
        vc = max(dy_min, min(dy_max, v))
        return cpy0 + cph - (vc - dy_min) / (dy_max - dy_min) * cph

    parts.append(f'<rect x="{cpx0}" y="{cpy0}" width="{cpw}" height="{cph}" rx="3" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>')
    # Highlight green "+2 support" zone at top
    y_p2 = cy_map(2.0)
    y_0 = cy_map(0.0)
    parts.append(f'<rect x="{cpx0 + 1}" y="{cpy0 + 1}" width="{cpw - 2}" height="{y_p2 - cpy0 - 1:.1f}" fill="#dcfce7" opacity="0.7"/>')
    parts.append(f'<text x="{cpx0 + cpw - 6}" y="{y_p2 - 2.5:.1f}" text-anchor="end" font-size="7.8" font-weight="700" fill="#15803d">Support threshold (+2)</text>')

    for yv in [2, 0, -2, -4, -6, -8]:
        yy = cy_map(yv)
        sc = "#16a34a" if yv == 2 else ("#0f172a" if yv == 0 else "#e2e8f0")
        sw = "1.2" if yv in (0, 2) else "0.8"
        da = ' stroke-dasharray="4,3"' if yv == 2 else ""
        parts.append(f'<line x1="{cpx0}" y1="{yy:.1f}" x2="{cpx0 + cpw}" y2="{yy:.1f}" stroke="{sc}" stroke-width="{sw}"{da}/>')
        parts.append(f'<text x="{cpx0 - 6}" y="{yy + 3.0:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="8.3" fill="#475569">{yv:+d}</text>')

    # Grouped bars (3 bars per track: M2, M3, M4)
    mod_colors = [("#2563eb", "M2: k^β·2^(αk)"), ("#7c3aed", "M3: 2^(αk + δ√k)"), ("#ea580c", "M4: exp(c₁·k^γ)")]
    group_w = cpw / len(rows)
    bar_w3 = 23.0
    gap3 = 3.5
    for i, (lbl, _, _, _, _, _, _, d2, d3, d4) in enumerate(rows):
        gx = cpx0 + (i + 0.5) * group_w
        parts.append(f'<text x="{gx:.1f}" y="{cpy0 + cph + 15}" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1e293b">{lbl}</text>')
        for m_idx, dv in enumerate([d2, d3, d4]):
            bx = gx - 1.5 * bar_w3 - gap3 + m_idx * (bar_w3 + gap3)
            yv = cy_map(dv)
            if dv >= 0.0:
                bh = max(3.0, y_0 - yv)
                parts.append(f'<rect x="{bx:.1f}" y="{yv:.1f}" width="{bar_w3:.1f}" height="{bh:.1f}" rx="2.5" fill="{mod_colors[m_idx][0]}" opacity="0.84"/>')
                parts.append(f'<text x="{bx + bar_w3/2:.1f}" y="{yv - 3.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="7.1" font-weight="600" fill="#334155">+{dv:.1f}</text>')
            else:
                bh = max(3.0, yv - y_0)
                parts.append(f'<rect x="{bx:.1f}" y="{y_0:.1f}" width="{bar_w3:.1f}" height="{bh:.1f}" rx="2.5" fill="{mod_colors[m_idx][0]}" opacity="0.84"/>')
                parts.append(f'<text x="{bx + bar_w3/2:.1f}" y="{yv + 9.5:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="7.2" font-weight="600" fill="#334155">{dv:.1f}</text>')

    # Small clean annotation below the positive Frobenius (.cnf) bars noting the k=25 probe seam
    gx0 = cpx0 + 0.5 * group_w
    parts.append(f'<text x="{gx0:.1f}" y="{y_0 + 13:.1f}" text-anchor="middle" font-size="7.3" font-weight="700" fill="#0369a1">§ k=25 probe seam</text>')
    parts.append(f'<text x="{gx0:.1f}" y="{y_0 + 23:.1f}" text-anchor="middle" font-size="7.0" fill="#475569">(split: −3.6 / −15.9)</text>')

    # Compact legend + footnote strip at bottom of Panel C
    leg_y = cy0 + ch - 13
    lx_cur = cpx0
    for mc, mlbl in mod_colors:
        parts.append(f'<rect x="{lx_cur:.1f}" y="{leg_y - 8}" width="10" height="10" rx="2" fill="{mc}" opacity="0.85"/>')
        parts.append(f'<text x="{lx_cur + 14:.1f}" y="{leg_y + 0.5}" font-size="8.4" font-weight="600" fill="#334155">{mlbl}</text>')
        lx_cur += 128
    parts.append(f'<text x="{cpx0 + cpw:.1f}" y="{leg_y + 0.5}" text-anchor="end" font-size="7.6" fill="#64748b">*Measured 1C T(32) · †Tobit censored (+3 T/Os) · ‡Post-floor k≥5 · §k=24→25 +0.6s seam</text>')

    parts.append("</g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")

    gsvg = build_growth_analysis_svg()
    OUT_GROWTH_SVG.write_text(gsvg, encoding="utf-8")
    ET.parse(OUT_GROWTH_SVG)
    print(f"Wrote and XML-validated {OUT_GROWTH_SVG} ({OUT_GROWTH_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
