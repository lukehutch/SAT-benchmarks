#!/usr/bin/env python3
"""Generate a publication-grade SVG scaling diagram (`diagram.svg`) for the
`sha256-64r-nonce-scaling` benchmark collection.

Plots empirical single-core wall-clock solve times T(k) across k = 1..32 unknown
nonce bits of full 64-round FIPS 180-4 SHA-256 (W_0 = 0x9E3779B9, T_max = 300 s)
for all 7 solver tracks (5 SAT engines), alongside the 300 s cutoff line,
Frobenius's piecewise regimes (Stage 0C -> CompiledAig256 -> lib.rs:649 k=24->25
cliff), and shifted pure-exponential M1 best-fit / extrapolation curves.

Usage:
    python3 src/gen_diagram.py
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

OUT_SVG = Path(__file__).resolve().parent.parent / "diagram.svg"

FONT_SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Exact single-core median/measured wall-clock times (seconds) on AMD Ryzen 9 5950X (CCD 1 core 12).
# Entries after max solved k up to stopping point are the 3 consecutive 300 s timeouts.
EMPIRICAL_SEC: dict[str, list[tuple[int, float]]] = {
    "frobenius_aig": [
        (1, 0.001686), (2, 0.033934), (3, 0.034063), (4, 0.033779), (5, 0.034843),
        (6, 0.034267), (7, 0.034592), (8, 0.034702), (9, 0.037054), (10, 0.036446),
        (11, 0.036350), (12, 0.036330), (13, 0.037669), (14, 0.056949), (15, 0.057620),
        (16, 0.061724), (17, 0.074378), (18, 0.093007), (19, 0.128266), (20, 0.199301),
        (21, 0.352432), (22, 0.647786), (23, 1.274551), (24, 2.406606),
    ],
    "frobenius_cnf": [
        (1, 0.001570), (2, 0.075837), (3, 0.096869), (4, 0.098114), (5, 0.103540),
        (6, 0.108209), (7, 0.101070), (8, 0.103169), (9, 0.100112), (10, 0.101157),
        (11, 0.104747), (12, 0.116150), (13, 0.099018), (14, 0.118089), (15, 0.121198),
        (16, 0.124774), (17, 0.131637), (18, 0.145787), (19, 0.172638), (20, 0.227122),
        (21, 0.339728), (22, 0.552702), (23, 1.003170), (24, 1.902396),
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
    "frobenius_aig": [25, 26, 27],
    "frobenius_cnf": [25, 26, 27],
    "cadical_cnf": [18, 19, 20],
    "dense_cnf": [18, 19, 20],
    "kissat_cnf": [16, 17, 18],
    "cms_cnf": [13, 14, 15],
    "cms_xcnf": [12, 13, 14],
}

# Best-fit M1 curves: (c0_sec, a_sec, alpha, k_start, k_end)
M1_FITS: dict[str, tuple[float, float, float, float, float]] = {
    "frobenius_aig": (0.05384, 1.462e-7, 0.9982, 14.0, 32.0),
    "frobenius_cnf": (0.11767, 9.919e-8, 1.0039, 14.0, 32.0),
    "dense_cnf": (0.89826, 2.713e-3, 0.9708, 2.0, 18.0),
    "cadical_cnf": (0.04902, 1.054e-2, 0.8098, 2.0, 18.5),   # Tobit right-censored M1
    "kissat_cnf": (0.16666, 2.926e-3, 1.0073, 2.0, 17.0),    # Tobit right-censored M1
    "cms_cnf": (0.0, 2.981, 0.5337, 2.0, 13.5),
    "cms_xcnf": (0.0, 0.5370, 0.7905, 2.0, 12.5),            # Tobit right-censored M1
}

TRACK_STYLE = [
    ("frobenius_aig", "Frobenius 1C (.aig)",   "#059669", "24/32", "α=0.998 (2.00×/b)", "10.1 min*", "circle",   ""),
    ("frobenius_cnf", "Frobenius 1C (.cnf)",   "#0284c7", "24/32", "α=1.004 (2.01×/b)", "7.7 min*",  "diamond",  ""),
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
        "Single-core wall-clock T(k) on AMD Ryzen 9 5950X (core 12, T_max = 300 s, W₀ = 0x9E3779B9, "
        "272/272 SAT verified) · 5 engines (7 tracks)</text>".replace("T_max", "Tₘₐₓ"),
        '<line x1="22" y1="62" x2="898" y2="62" stroke="#e2e8f0" stroke-width="1.2"/>',
    ]

    # Plot frame & regime background tints
    parts.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    # Regime 1 tint: k = 1.5..13.5 (Stage 0C AVX2)
    rx_s0 = mx(1.5)
    rx_s1 = mx(13.5)
    rx_s2 = mx(24.5)
    parts.append(f'<rect x="{rx_s0:.1f}" y="{py0 + 1}" width="{rx_s1 - rx_s0:.1f}" height="{ph - 2}" fill="#eff6ff" opacity="0.55"/>')
    parts.append(f'<rect x="{rx_s1:.1f}" y="{py0 + 1}" width="{rx_s2 - rx_s1:.1f}" height="{ph - 2}" fill="#ecfdf5" opacity="0.60"/>')
    parts.append(f'<rect x="{rx_s2:.1f}" y="{py0 + 1}" width="{px1 - rx_s2 - 1:.1f}" height="{ph - 2}" fill="#fef2f2" opacity="0.45"/>')

    # Regime header badges cleanly inside top band (above 300s line, y = py0 + 13)
    parts.append(f'<text x="{(rx_s0 + rx_s1)/2:.1f}" y="{py0 + 14}" text-anchor="middle" font-size="8.4" font-weight="700" fill="#1d4ed8">Stage 0C (k=2..13)</text>')
    parts.append(f'<text x="{(rx_s1 + rx_s2)/2:.1f}" y="{py0 + 14}" text-anchor="middle" font-size="8.4" font-weight="700" fill="#047857">CompiledAig256 512-lane 2ᵏ (k=14..24)</text>')
    parts.append(f'<text x="{(rx_s2 + px1)/2:.1f}" y="{py0 + 14}" text-anchor="middle" font-size="8.4" font-weight="700" fill="#b91c1c">CDCL cap (k≥25)</text>')

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

    # Vertical dashed divider at k = 24.5 (lib.rs:649 cutoff cliff)
    parts.append(f'<line x1="{rx_s2:.1f}" y1="{py0 + 20}" x2="{rx_s2:.1f}" y2="{py1}" stroke="#dc2626" stroke-width="1.3" stroke-dasharray="4,3"/>')

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

    # Fitted M1 dashed extrapolations (Frobenius .aig & .cnf from k=14..32; CDCL capped at 300 s)
    for tid, _, color, _, _, _, _, _ in TRACK_STYLE:
        c0, a, al, ks0, ks1 = M1_FITS[tid]
        t_cap = 1000.0 if tid.startswith("frobenius") else 300.0
        pts = []
        steps = 48
        for s in range(steps + 1):
            kf = ks0 + (ks1 - ks0) * (s / steps)
            tf = c0 + a * (2.0 ** (al * kf))
            if tf <= t_cap:
                pts.append(f"{mx(kf):.1f},{my(tf):.1f}")
        if len(pts) >= 2:
            op = "0.75" if tid.startswith("frobenius") else "0.35"
            sw = "1.6" if tid.startswith("frobenius") else "1.1"
            parts.append(
                f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                f'stroke-width="{sw}" stroke-dasharray="3.5,3" opacity="{op}"/>'
            )

    # Empirical curves (draw CMS/CDCL first, Frobenius on top for maximum legibility)
    draw_order = ["cms_xcnf", "cms_cnf", "kissat_cnf", "dense_cnf", "cadical_cnf", "frobenius_cnf", "frobenius_aig"]
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
        sw = "2.25" if tid.startswith("frobenius") else "1.7"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}"{da}/>')

        # Connector up to first timeout k0 (dotted steep jump)
        k_last, t_last = data[-1]
        k_to0 = TIMEOUT_KS[tid][0]
        parts.append(
            f'<line x1="{mx(k_last):.1f}" y1="{my(t_last):.1f}" x2="{mx(k_to0):.1f}" y2="{y300:.1f}" '
            f'stroke="{color}" stroke-width="1.2" stroke-dasharray="2.5,2.5" opacity="0.65"/>'
        )

        # Markers on empirical points
        hollow = tid in ("frobenius_cnf", "cms_xcnf")
        rad = 3.0 if tid.startswith("frobenius") else 2.6
        for k, t in data:
            draw_marker(parts, shape, mx(k), my(t), color, r=rad, hollow=hollow)

        # Crisp X marker at first timeout k0 along 300 s line
        xt = mx(k_to0)
        parts.append(f'<path d="M {xt - 3.3:.1f} {y300 - 3.3:.1f} L {xt + 3.3:.1f} {y300 + 3.3:.1f} M {xt - 3.3:.1f} {y300 + 3.3:.1f} L {xt + 3.3:.1f} {y300 - 3.3:.1f}" stroke="{color}" stroke-width="1.6"/>')

    # Clean in-plot callouts (placed in open whitespace!)
    # Callout 1: k=24 -> k=25 cliff
    x_cliff = mx(24.5)
    parts.append(f'<rect x="{x_cliff - 120:.1f}" y="{my(28.0):.1f}" width="113" height="31" rx="4" fill="#ffffff" stroke="#dc2626" stroke-width="0.95" opacity="0.95"/>')
    parts.append(f'<text x="{x_cliff - 63.5:.1f}" y="{my(28.0) + 12.5:.1f}" text-anchor="middle" font-size="8.4" font-weight="700" fill="#b91c1c">lib.rs:649 k≤24 cap</text>')
    parts.append(f'<text x="{x_cliff - 63.5:.1f}" y="{my(28.0) + 24.5:.1f}" text-anchor="middle" font-size="7.9" fill="#475569">2.41 s → &gt;300 s CDCL</text>')

    # Callout 2: Dotted extrapolation to k=32 (~7.7–10.1 min)
    x_ext = mx(29.3)
    y_ext = my(7.0)
    parts.append(f'<rect x="{x_ext - 54:.1f}" y="{y_ext:.1f}" width="110" height="31" rx="4" fill="#ffffff" stroke="#059669" stroke-width="0.95" opacity="0.95"/>')
    parts.append(f'<text x="{x_ext + 1:.1f}" y="{y_ext + 12.5:.1f}" text-anchor="middle" font-size="8.3" font-weight="700" fill="#047857">Uncapped M1 fit:</text>')
    parts.append(f'<text x="{x_ext + 1:.1f}" y="{y_ext + 24.5:.1f}" text-anchor="middle" font-size="7.9" fill="#334155">T(32) ≈ 7.7–10.1 min</text>')

    # Callout 3: k=1 symbolic collapse
    parts.append(f'<text x="{mx(1.4):.1f}" y="{my(0.0014) + 3:.1f}" font-size="7.8" fill="#64748b">k=1: 0-AND collapse</text>')

    parts.append("</g>")  # end plot-clip

    # ===================== RIGHT LEGEND & FIT SUMMARY PANEL =====================
    lx, ly, lw, lh = 658, 86, 240, 326
    parts.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.1"/>')
    parts.append(f'<text x="{lx + 11}" y="{ly + 19}" font-size="10.8" font-weight="700" fill="#0f172a">7 Solver Tracks &amp; M1 Fits</text>')
    parts.append(f'<text x="{lx + 11}" y="{ly + 32}" font-size="8.1" fill="#64748b">T(k) = c₀ + a·2^(αk)   |   Solved · Extrap. T(32)</text>')
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
    parts.append(f'<text x="{lx + 11}" y="{ly + lh - 17}" font-size="7.5" fill="#64748b">*Uncapped CompiledAig256 (k=14..24 fit, R²&gt;0.9998)</text>')
    parts.append(f'<text x="{lx + 11}" y="{ly + lh - 6.5}" font-size="7.5" fill="#64748b">†Tobit right-censored M1 (+3 T/Os)  ‡Post-floor k≥5</text>')

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
            "2. Frobenius Exact 2ᵏ AVX2 Scaling",
            "• .aig k=14..24: α=0.9982, R²=0.99983 (1.7%)",
            "• .cnf k=14..24: α=1.0039, R²=0.99996 (0.6%)",
            "• 465–720× faster than CDCL on k=1..17",
            "• Lifting k≤24 cap solves k=32 in 7.7–10.1m",
        ),
        (
            616, 282, "#eff6ff", "#bfdbfe", "#1d4ed8",
            "3. AICc/BIC Model Selection (M1–M4)",
            "• Shifted pure exp M1 wins ALL 7 tracks",
            "• 0 statistical support for sub-exp (γ&lt;1)",
            "• dense α=0.971; Kissat Tobit α=1.007",
            "• 272/272 SAT models verified (0 BADSAT)",
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


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    ET.parse(OUT_SVG)
    print(f"Wrote and XML-validated {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
