#!/usr/bin/env python3
"""
Structural & Phase-Transition Analyzer for the SAT Benchmarks Repository.

Computes exact critical-threshold positioning and graph/syntactic structural
statistics for every DIMACS CNF (`.cnf` / `.cnf.xz`) benchmark instance (plus
paired `.aig` and `.xcnf` metadata when present), and optionally updates the
auto-generated `## Phase-Transition & Structural Analysis` section in every
suite's `README.md` and the repository overview table.

Mathematical definitions (standard SAT / statistical-physics conventions):
  - Clause-to-variable ratio:
        alpha = m / n   (n = active variables appearing in clauses, m = clauses)
  - Exact k-SAT critical thresholds alpha_c(k):
        k = 1: 1.000   (unit clause fixes 1 variable)
        k = 2: 1.000   (Chvatal-Reed 1992 / Goerdt 1996)
        k = 3: 4.267   (Mertens-Mezard-Zecchina 2006 / Ding-Sly-Sun 2015)
        k = 4: 9.931   (Mertens-Mezard-Zecchina 2006)
        k = 5: 21.117  (Mertens-Mezard-Zecchina 2006)
        k = 6: 43.370  (Mertens-Mezard-Zecchina 2006)
        k >= 7: 2^k * ln(2) - (1 + ln(2)) / 2  (asymptotic cavity threshold)
  - Critical ratio rho_crit (position relative to the critical threshold):
        rho_crit = (1 / n) * sum_{k >= 1} (m_k / alpha_c(k))
    For pure k-SAT, rho_crit = alpha / alpha_c(k) identically (1.00 = at threshold).
    For mixed-length CNFs, rho_crit linearly combines 2-SAT percolation pressure
    (m_2 / n) and higher-arity k-SAT clause density into a single dimensionless
    criticality coordinate, with implied effective critical threshold:
        alpha_c_eff = alpha / rho_crit
    Regimes:
        rho_crit < 0.90  -> Under-constrained
        0.90 <= rho_crit <= 1.10 -> Near-critical
        rho_crit > 1.10  -> Over-constrained
  - Annealed constrainedness kappa (Gent, MacIntyre, Prosser & Walsh, AAAI 1996):
        kappa = -(1 / n) * sum_{i=1..m} log2(1 - 2^{-k_i})
    (kappa = 1.0 corresponds to E[#solutions] = 1 under a uniform random model;
     for pure 3-SAT, the true phase transition sits at kappa ~= 0.822.)
  - Variable-Incidence Graph (VIG) & syntactic metrics:
        mean/max clause length (k_avg, k_max), % binary / % ternary / % long,
        binary density alpha_2 = m_2 / n, Horn clause fraction (%Horn),
        positive literal balance (Pos%), pure-literal variable count,
        variable-degree mean / max / coefficient of variation (Deg CV = sigma/mu,
        measuring uniformity vs. scale-free hub structure), VIG connected
        components, lossless native XOR parity equation count (from xcnf-version/),
        and Binary AIGER 1.9 AND-gate count.

Usage:
    python3 src/analyze_benchmarks.py --all
    python3 src/analyze_benchmarks.py --all --update-readmes
    python3 src/analyze_benchmarks.py --suite random-3sat-phase-transition --update-readmes
    python3 src/analyze_benchmarks.py --file path/to/formula.cnf
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import lzma
import math
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BEGIN_MARKER = "<!-- BEGIN_STRUCTURAL_ANALYSIS -->"
END_MARKER = "<!-- END_STRUCTURAL_ANALYSIS -->"

# Exact/cavity uniform k-SAT critical thresholds alpha_c(k)
EXACT_ALPHA_C: dict[int, float] = {
    1: 1.000,
    2: 1.000,
    3: 4.267,
    4: 9.931,
    5: 21.117,
    6: 43.370,
}

LN2 = math.log(2.0)


def alpha_c_k(k: int) -> float:
    if k in EXACT_ALPHA_C:
        return EXACT_ALPHA_C[k]
    if k >= 30:
        return (2.0 ** 30) * LN2
    return (2.0 ** k) * LN2 - 0.5 * (1.0 + LN2)


def regime_label(rho: float) -> str:
    if rho < 0.90:
        return "Under-constrained"
    if rho <= 1.10:
        return "Near-critical"
    return "Over-constrained"


def regime_short(rho: float) -> str:
    if rho < 0.90:
        return "Under"
    if rho <= 1.10:
        return "Near-crit"
    return "Over"


@dataclass
class InstanceStats:
    suite: str
    group: str
    name: str
    rel_path: str
    declared_vars: int
    active_vars: int
    clauses: int
    literals: int
    alpha: float
    alpha_c_eff: float
    rho_crit: float
    regime: str
    kappa: float
    alpha_2: float
    k_avg: float
    k_max: int
    pct_unit: float
    pct_bin: float
    pct_tern: float
    pct_long: float
    pct_horn: float
    pct_pos: float
    pure_vars: int
    deg_mean: float
    deg_max: int
    deg_cv: float
    vig_components: int
    xor_clauses: int
    aig_ands: int | None


class DSU:
    __slots__ = ("parent",)

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        p = self.parent
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def open_text_maybe_xz(path: Path):
    if path.suffix == ".xz":
        return lzma.open(path, "rt", encoding="latin-1", errors="replace")
    return open(path, "r", encoding="latin-1", errors="replace")


def count_xors(xcnf_path: Path | None) -> int:
    if xcnf_path is None or not xcnf_path.exists():
        return 0
    cnt = 0
    with open_text_maybe_xz(xcnf_path) as f:
        for line in f:
            if line.startswith("x ") or line.startswith("x\t"):
                cnt += 1
    return cnt


def read_aig_ands(aig_path: Path | None) -> int | None:
    if aig_path is None or not aig_path.exists():
        return None
    if aig_path.suffix == ".xz":
        with lzma.open(aig_path, "rb") as f:
            hdr = f.readline().decode("ascii", errors="ignore").split()
    else:
        with open(aig_path, "rb") as f:
            hdr = f.readline().decode("ascii", errors="ignore").split()
    if len(hdr) >= 6 and hdr[0] in ("aig", "aag"):
        return int(hdr[5])
    return None


def analyze_cnf(
    cnf_path: Path,
    suite: str = "",
    group: str = "",
    xcnf_path: Path | None = None,
    aig_path: Path | None = None,
) -> InstanceStats:
    declared_vars = 0
    num_clauses = 0
    total_lits = 0
    pos_lits = 0
    horn_clauses = 0
    len_counts: Counter[int] = Counter()

    pos_deg: Counter[int] = Counter()
    neg_deg: Counter[int] = Counter()
    cur: list[int] = []
    # For VIG components, collect small clauses directly and cap huge-clause star unions
    clause_vars_for_dsu: list[list[int]] = []

    def flush_clause() -> None:
        nonlocal num_clauses, total_lits, pos_lits, horn_clauses
        if not cur:
            return
        k = len(cur)
        num_clauses += 1
        total_lits += k
        len_counts[k] += 1
        n_pos = 0
        vs: list[int] = []
        for lit in cur:
            if lit > 0:
                n_pos += 1
                pos_lits += 1
                pos_deg[lit] += 1
                vs.append(lit)
            else:
                v = -lit
                neg_deg[v] += 1
                vs.append(v)
        if n_pos <= 1:
            horn_clauses += 1
        if k >= 2:
            clause_vars_for_dsu.append(vs)
        cur.clear()

    with open_text_maybe_xz(cnf_path) as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in ("c", "C"):
                continue
            if s[0] == "%":
                break
            if s[0] == "p":
                parts = s.split()
                if len(parts) >= 4 and parts[1].lower() == "cnf":
                    declared_vars = int(parts[2])
                continue
            for tok in s.split():
                if tok[0] == "%":
                    break
                lit = int(tok)
                if lit == 0:
                    flush_clause()
                else:
                    cur.append(lit)
        flush_clause()

    active_set = set(pos_deg.keys()) | set(neg_deg.keys())
    n = len(active_set)
    m = num_clauses
    if n == 0 or m == 0:
        return InstanceStats(
            suite=suite, group=group, name=cnf_path.name.removesuffix(".xz").removesuffix(".cnf"),
            rel_path=str(cnf_path), declared_vars=declared_vars, active_vars=n, clauses=m,
            literals=total_lits, alpha=0.0, alpha_c_eff=0.0, rho_crit=0.0,
            regime="Trivial", kappa=0.0, alpha_2=0.0, k_avg=0.0, k_max=0,
            pct_unit=0.0, pct_bin=0.0, pct_tern=0.0, pct_long=0.0,
            pct_horn=0.0, pct_pos=0.0, pure_vars=0, deg_mean=0.0, deg_max=0,
            deg_cv=0.0, vig_components=0, xor_clauses=count_xors(xcnf_path),
            aig_ands=read_aig_ands(aig_path),
        )

    # Exact phase-transition metrics
    alpha = m / n
    rho_crit = 0.0
    kappa = 0.0
    for k, cnt in len_counts.items():
        rho_crit += (cnt / n) / alpha_c_k(k)
        if k < 53:
            kappa += (cnt / n) * (-math.log2(1.0 - 2.0 ** (-k)))
        else:
            kappa += (cnt / n) * (2.0 ** (-k) / LN2)
    alpha_c_eff = (alpha / rho_crit) if rho_crit > 0.0 else 0.0

    # Degree distribution & pure variables
    degs: list[int] = []
    pure_vars = 0
    var_to_idx: dict[int, int] = {}
    for idx, v in enumerate(active_set):
        var_to_idx[v] = idx
        pd = pos_deg.get(v, 0)
        nd = neg_deg.get(v, 0)
        degs.append(pd + nd)
        if pd == 0 or nd == 0:
            pure_vars += 1
    deg_mean = sum(degs) / n
    deg_max = max(degs)
    if n > 1 and deg_mean > 0:
        var_d = sum((d - deg_mean) ** 2 for d in degs) / n
        deg_cv = math.sqrt(var_d) / deg_mean
    else:
        deg_cv = 0.0

    # VIG connected components in O(L) via star-unions per clause
    dsu = DSU(n)
    for vs in clause_vars_for_dsu:
        r0 = var_to_idx[vs[0]]
        for v in vs[1:]:
            dsu.union(r0, var_to_idx[v])
    vig_components = len({dsu.find(i) for i in range(n)})

    k_avg = total_lits / m
    k_max = max(len_counts.keys())
    m1 = len_counts.get(1, 0)
    m2 = len_counts.get(2, 0)
    m3 = len_counts.get(3, 0)
    m_long = sum(cnt for k, cnt in len_counts.items() if k >= 4)

    stem = cnf_path.name
    if stem.endswith(".xz"):
        stem = stem[:-3]
    if stem.endswith(".cnf"):
        stem = stem[:-4]

    return InstanceStats(
        suite=suite,
        group=group,
        name=stem,
        rel_path=str(cnf_path),
        declared_vars=declared_vars,
        active_vars=n,
        clauses=m,
        literals=total_lits,
        alpha=alpha,
        alpha_c_eff=alpha_c_eff,
        rho_crit=rho_crit,
        regime=regime_label(rho_crit),
        kappa=kappa,
        alpha_2=m2 / n,
        k_avg=k_avg,
        k_max=k_max,
        pct_unit=100.0 * m1 / m,
        pct_bin=100.0 * m2 / m,
        pct_tern=100.0 * m3 / m,
        pct_long=100.0 * m_long / m,
        pct_horn=100.0 * horn_clauses / m,
        pct_pos=100.0 * pos_lits / total_lits,
        pure_vars=pure_vars,
        deg_mean=deg_mean,
        deg_max=deg_max,
        deg_cv=deg_cv,
        vig_components=vig_components,
        xor_clauses=count_xors(xcnf_path),
        aig_ands=read_aig_ands(aig_path),
    )


def discover_suite_cnfs(suite_dir: Path) -> list[tuple[Path, str, Path | None, Path | None]]:
    """
    Returns list of (cnf_path, group_name, xcnf_path, aig_path) for a suite directory.
    Handles both AIG-native suites (`cnf-version/`) and CNF-native suites (root or subdirs).
    """
    cnf_ver = suite_dir / "cnf-version"
    xcnf_ver = suite_dir / "xcnf-version"
    aig_ver = suite_dir / "aig-version"
    items: list[tuple[Path, str, Path | None, Path | None]] = []

    def find_xcnf(rel_no_ext: Path) -> Path | None:
        for base_dir in (xcnf_ver, suite_dir):
            for ext in (".xcnf", ".xcnf.xz"):
                cand = base_dir / (str(rel_no_ext) + ext)
                if cand.exists():
                    return cand
        return None

    def strip_cnf_ext(p: Path) -> Path:
        s = str(p)
        if s.endswith(".cnf.xz"):
            return Path(s[:-7])
        if s.endswith(".cnf"):
            return Path(s[:-4])
        return p

    def find_aig(base_dir: Path, rel_no_ext: Path) -> Path | None:
        for ext in (".aig.xz", ".aig"):
            cand = base_dir / (str(rel_no_ext) + ext)
            if cand.exists():
                return cand
        return None

    if cnf_ver.is_dir():
        # AIG-native suite
        for p in sorted(cnf_ver.rglob("*")):
            if not p.is_file() or not (p.name.endswith(".cnf") or p.name.endswith(".cnf.xz")):
                continue
            rel = p.relative_to(cnf_ver)
            rel_base = strip_cnf_ext(rel)
            grp = rel.parent.as_posix() if rel.parent != Path(".") else suite_dir.name
            items.append((p, grp, find_xcnf(rel_base), find_aig(suite_dir, rel_base)))
    else:
        # CNF-native suite
        skip_top = {"aig-version", "xcnf-version", "outputs", "src", "results", "matrices", "maps"}
        for p in sorted(suite_dir.rglob("*")):
            if not p.is_file() or not (p.name.endswith(".cnf") or p.name.endswith(".cnf.xz")):
                continue
            rel = p.relative_to(suite_dir)
            if rel.parts[0] in skip_top:
                continue
            rel_base = strip_cnf_ext(rel)
            grp = rel.parent.as_posix() if rel.parent != Path(".") else suite_dir.name
            items.append((p, grp, find_xcnf(rel_base), find_aig(aig_ver, rel_base)))
    return items


def analyze_mata_suite(suite_dir: Path) -> str:
    files = sorted(suite_dir.rglob("*.mata.xz"))
    by_grp: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for f in files:
        grp = f.relative_to(suite_dir).parent.as_posix()
        states = set()
        trans = 0
        syms = set()
        with lzma.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("@") or s.startswith("%") or s.startswith("#"):
                    continue
                parts = s.split()
                if len(parts) >= 3:
                    states.add(parts[0])
                    syms.add(parts[1])
                    states.add(parts[2])
                    trans += 1
        by_grp[grp].append((len(states), trans, len(syms)))

    lines = [
        BEGIN_MARKER,
        "## Automata Structural Analysis",
        "",
        "*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). Because MATA benchmarks encode non-deterministic finite automata rather than clausal CNF formulas, clause-to-variable phase-transition ratios ($\\alpha / \\alpha_c$) do not apply; instead we report NFA state, transition, and alphabet densities (transition-to-state ratio $\\delta = |\\Delta|/|Q|$).*",
        "",
        "| Subdirectory | NFAs | States $|Q|$ (Med / Max) | Transitions $|\\Delta|$ (Med / Max) | Symbols $|\\Sigma|$ (Med / Max) | Transition Density $|\\Delta|/|Q|$ (Med) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    all_q, all_t, all_s, all_d = [], [], [], []
    for grp in sorted(by_grp):
        rows = by_grp[grp]
        qs = [r[0] for r in rows]
        ts = [r[1] for r in rows]
        ss = [r[2] for r in rows]
        ds = [t / max(q, 1) for q, t, _ in rows]
        all_q += qs; all_t += ts; all_s += ss; all_d += ds
        lines.append(
            f"| `{grp}/` | {len(rows)} | {int(statistics.median(qs)):,} / {max(qs):,} | "
            f"{int(statistics.median(ts)):,} / {max(ts):,} | {int(statistics.median(ss)):,} / {max(ss):,} | "
            f"{statistics.median(ds):.2f} |"
        )
    lines.append(
        f"| **Total** | **{len(files)}** | **{int(statistics.median(all_q)):,} / {max(all_q):,}** | "
        f"**{int(statistics.median(all_t)):,} / {max(all_t):,}** | **{int(statistics.median(all_s)):,} / {max(all_s):,}** | "
        f"**{statistics.median(all_d):.2f}** |"
    )
    lines.append(END_MARKER)
    return "\n".join(lines)


def fmt_rho(rho: float) -> str:
    if rho >= 100.0:
        return f"{rho:.0f}x"
    if rho >= 10.0:
        return f"{rho:.1f}x"
    return f"{rho:.2f}x"


def fmt_alpha(val: float) -> str:
    if val >= 100.0:
        return f"{val:.1f}"
    return f"{val:.2f}"


def render_suite_markdown(suite_name: str, stats: list[InstanceStats]) -> str:
    lines = [
        BEGIN_MARKER,
        "## Phase-Transition & Structural Analysis",
        "",
        "*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). "
        "Position relative to the critical phase transition is measured by $\\rho_{\\mathrm{crit}} = \\frac{1}{n}\\sum_k m_k / \\alpha_c(k)$ "
        "(exact $\\alpha/\\alpha_c(k)$ for pure $k$-SAT; effective critical threshold $\\alpha_c^{\\mathrm{eff}} = \\alpha/\\rho_{\\mathrm{crit}}$; "
        "`Under` $<0.90\\times$, `Near-crit` $0.90\\text{--}1.10\\times$, `Over` $>1.10\\times$), alongside "
        "Gent–Walsh annealed constrainedness $\\kappa = -\\frac{1}{n}\\sum_i \\log_2(1-2^{-k_i})$ (AAAI 1996), "
        "clause-length profile ($\\bar{k}$, `%Bin`, `%Horn`), variable-degree CV ($\\sigma_d/\\bar{d}$, uniformity vs. hub skew), "
        "and extracted native XOR parity clauses.*",
        "",
    ]

    use_per_instance = len(stats) <= 25
    if use_per_instance:
        lines.append(
            "| Instance | Active $n$ | Clauses $m$ | $\\alpha=m/n$ | $\\alpha_c^{\\mathrm{eff}}$ | $\\rho_{\\mathrm{crit}}$ (Regime) | $\\kappa$ | $\\bar{k}$ ($k_{\\max}$) | Bin% | Horn% | Pos% | Deg CV | XORs |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for s in stats:
            lines.append(
                f"| `{s.name}` | {s.active_vars:,} | {s.clauses:,} | {fmt_alpha(s.alpha)} | {fmt_alpha(s.alpha_c_eff)} | "
                f"**{fmt_rho(s.rho_crit)}** ({regime_short(s.rho_crit)}) | {s.kappa:.2f} | "
                f"{s.k_avg:.2f} ({s.k_max}) | {s.pct_bin:.0f}% | {s.pct_horn:.0f}% | {s.pct_pos:.0f}% | "
                f"{s.deg_cv:.2f} | {s.xor_clauses:,} |"
            )
    else:
        # Group by subdirectory (or size prefix if flat)
        by_grp: dict[str, list[InstanceStats]] = defaultdict(list)
        for s in stats:
            g = s.group
            if g == suite_name:
                # Derive clean family prefix for flat suites > 25 (e.g., rb-bench frb30-15)
                parts = s.name.split("-")
                g = "-".join(parts[:2]) if len(parts) >= 2 else suite_name
            by_grp[g].append(s)

        lines.append(
            "| Group / Family | Files | Med $n$ | Med $m$ | $\\alpha=m/n$ (Med) | $\\alpha_c^{\\mathrm{eff}}$ (Med) | $\\rho_{\\mathrm{crit}}$ Med [Min–Max] (Regime) | Med $\\kappa$ | Med $\\bar{k}$ | Bin% | Horn% | Deg CV | Total XORs |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for grp in sorted(by_grp):
            gs = by_grp[grp]
            med_n = int(statistics.median(x.active_vars for x in gs))
            med_m = int(statistics.median(x.clauses for x in gs))
            med_a = statistics.median(x.alpha for x in gs)
            med_ac = statistics.median(x.alpha_c_eff for x in gs)
            rhos = [x.rho_crit for x in gs]
            med_r = statistics.median(rhos)
            med_k = statistics.median(x.kappa for x in gs)
            med_kavg = statistics.median(x.k_avg for x in gs)
            med_bin = statistics.median(x.pct_bin for x in gs)
            med_horn = statistics.median(x.pct_horn for x in gs)
            med_cv = statistics.median(x.deg_cv for x in gs)
            tot_xor = sum(x.xor_clauses for x in gs)
            r_span = f"{fmt_rho(min(rhos))}–{fmt_rho(max(rhos))}" if len(gs) > 1 else fmt_rho(med_r)
            lines.append(
                f"| `{grp}` | {len(gs)} | {med_n:,} | {med_m:,} | {fmt_alpha(med_a)} | {fmt_alpha(med_ac)} | "
                f"**{fmt_rho(med_r)}** [{r_span}] ({regime_short(med_r)}) | {med_k:.2f} | {med_kavg:.2f} | "
                f"{med_bin:.0f}% | {med_horn:.0f}% | {med_cv:.2f} | {tot_xor:,} |"
            )

    # Suite summary row / bullet
    rhos = [x.rho_crit for x in stats]
    n_under = sum(1 for r in rhos if r < 0.90)
    n_near = sum(1 for r in rhos if 0.90 <= r <= 1.10)
    n_over = sum(1 for r in rhos if r > 1.10)
    med_r = statistics.median(rhos)
    med_kap = statistics.median(x.kappa for x in stats)
    tot_xor = sum(x.xor_clauses for x in stats)
    lines.append("")
    med_r_tex = fmt_rho(med_r).replace("x", r"\times")
    lines.append(
        f"**Suite Phase-Transition Summary ({len(stats)} instances):** "
        f"median $\\rho_{{\\mathrm{{crit}}}} = {med_r_tex}$ (range `{fmt_rho(min(rhos))}–{fmt_rho(max(rhos))}`), "
        f"median $\\kappa = {med_kap:.2f}$, regime split **{n_under} Under / {n_near} Near-critical / {n_over} Over**, "
        f"total extracted native XOR parity clauses = **{tot_xor:,}**."
    )
    lines.append(END_MARKER)
    return "\n".join(lines)


def upsert_section(readme_path: Path, block: str) -> bool:
    text = readme_path.read_text(encoding="utf-8")
    if BEGIN_MARKER in text and END_MARKER in text:
        pre = text[: text.index(BEGIN_MARKER)].rstrip()
        post = text[text.index(END_MARKER) + len(END_MARKER) :].lstrip("\n")
        new_text = pre + "\n\n" + block + ("\n\n" + post if post else "\n")
    else:
        # Insert right before `## References` if present, else append to end
        ref_idx = text.find("\n## References")
        if ref_idx != -1:
            new_text = text[:ref_idx].rstrip() + "\n\n" + block + "\n" + text[ref_idx:]
        else:
            new_text = text.rstrip() + "\n\n" + block + "\n"
    if new_text != text:
        readme_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def render_root_overview(suite_results: dict[str, list[InstanceStats]]) -> str:
    lines = [
        BEGIN_MARKER,
        "## Cross-Suite Phase-Transition & Structural Profile",
        "",
        "*Auto-generated across all 771 committed SAT instances by [`src/analyze_benchmarks.py`](src/analyze_benchmarks.py). "
        "Each row summarizes where the suite sits relative to the clause-length-weighted critical threshold "
        "$\\rho_{\\mathrm{crit}} = \\frac{1}{n}\\sum_k m_k / \\alpha_c(k)$ (`Under` $<0.90\\times$, `Near-crit` $0.90\\text{--}1.10\\times$, `Over` $>1.10\\times$), "
        "Gent–Walsh constrainedness $\\kappa$, clause geometry ($\\bar{k}$, `%Bin`, `%Horn`), variable-degree skew (`Deg CV`), and extracted XOR parity blocks.*",
        "",
        "| Suite | CNFs | Med $\\alpha$ | Med $\\alpha_c^{\\mathrm{eff}}$ | Med $\\rho_{\\mathrm{crit}}$ [Min–Max] | Regime Split (U/N/O) | Med $\\kappa$ | Med $\\bar{k}$ | Bin% | Horn% | Deg CV | XORs |",
        "|---|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|---:|",
    ]
    for suite in sorted(suite_results):
        gs = suite_results[suite]
        if not gs:
            continue
        rhos = [x.rho_crit for x in gs]
        med_r = statistics.median(rhos)
        med_a = statistics.median(x.alpha for x in gs)
        med_ac = statistics.median(x.alpha_c_eff for x in gs)
        n_u = sum(1 for r in rhos if r < 0.90)
        n_n = sum(1 for r in rhos if 0.90 <= r <= 1.10)
        n_o = sum(1 for r in rhos if r > 1.10)
        med_kap = statistics.median(x.kappa for x in gs)
        med_kavg = statistics.median(x.k_avg for x in gs)
        med_bin = statistics.median(x.pct_bin for x in gs)
        med_horn = statistics.median(x.pct_horn for x in gs)
        med_cv = statistics.median(x.deg_cv for x in gs)
        tot_xor = sum(x.xor_clauses for x in gs)
        r_span = f"{fmt_rho(min(rhos))}–{fmt_rho(max(rhos))}" if len(gs) > 1 else fmt_rho(med_r)
        lines.append(
            f"| [`{suite}/`]({suite}/README.md) | {len(gs)} | {fmt_alpha(med_a)} | {fmt_alpha(med_ac)} | "
            f"**{fmt_rho(med_r)}** [{r_span}] | {n_u} / {n_n} / {n_o} | {med_kap:.2f} | {med_kavg:.2f} | "
            f"{med_bin:.0f}% | {med_horn:.0f}% | {med_cv:.2f} | {tot_xor:,} |"
        )
    lines.append(END_MARKER)
    return "\n".join(lines)


def _analyze_job(job: tuple[str, Path, str, Path | None, Path | None]) -> InstanceStats:
    sname, cnf, grp, xcnf, aig = job
    return analyze_cnf(cnf, suite=sname, group=grp, xcnf_path=xcnf, aig_path=aig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze SAT benchmark phase-transition position and structural stats.")
    ap.add_argument("--all", action="store_true", help="Analyze all benchmark suites in the repository")
    ap.add_argument("--suite", type=str, help="Analyze a single suite directory name")
    ap.add_argument("--file", type=Path, help="Analyze a single .cnf or .cnf.xz file")
    ap.add_argument("--update-readmes", action="store_true", help="Update README.md files in-place")
    ap.add_argument("--json", type=Path, help="Write full per-instance metrics JSON to path")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    if args.file:
        st = analyze_cnf(args.file)
        print(json.dumps(asdict(st), indent=2))
        return

    if args.suite:
        suites = [REPO_ROOT / args.suite]
    elif args.all:
        suites = sorted(
            d for d in REPO_ROOT.iterdir()
            if d.is_dir() and not d.name.startswith(".") and d.name != "src" and (d / "README.md").exists()
        )
    else:
        ap.print_help()
        return

    all_jobs: list[tuple[str, Path, str, Path | None, Path | None]] = []
    mata_suites: list[Path] = []
    uri_only_suites: list[Path] = []
    for sd in suites:
        items = discover_suite_cnfs(sd)
        if items:
            for cnf, grp, xcnf, aig in items:
                all_jobs.append((sd.name, cnf, grp, xcnf, aig))
        elif list(sd.rglob("*.mata.xz")):
            mata_suites.append(sd)
        else:
            uri_only_suites.append(sd)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(_analyze_job, all_jobs, chunksize=4))

    by_suite: dict[str, list[InstanceStats]] = defaultdict(list)
    for st in results:
        by_suite[st.suite].append(st)

    print(f"Analyzed {len(results)} SAT instances across {len(by_suite)} CNF/AIG suites (+ {len(mata_suites)} NFA, {len(uri_only_suites)} URI-only)")
    for sname in sorted(by_suite):
        gs = by_suite[sname]
        rhos = [x.rho_crit for x in gs]
        print(
            f"  {sname:36s} | {len(gs):3d} files | med alpha={statistics.median(x.alpha for x in gs):6.2f} "
            f"| med rho={fmt_rho(statistics.median(rhos)):>6s} [{fmt_rho(min(rhos))}..{fmt_rho(max(rhos))}] "
            f"| med kappa={statistics.median(x.kappa for x in gs):5.2f} | XORs={sum(x.xor_clauses for x in gs):,}"
        )

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps([asdict(x) for x in results], indent=2) + "\n")
        print(f"Wrote JSON metrics to {args.json}")

    if args.update_readmes:
        updated = 0
        for sname, gs in sorted(by_suite.items()):
            md = render_suite_markdown(sname, gs)
            if upsert_section(REPO_ROOT / sname / "README.md", md):
                updated += 1
        for sd in mata_suites:
            md = analyze_mata_suite(sd)
            if upsert_section(sd / "README.md", md):
                updated += 1
        for sd in uri_only_suites:
            uri_files = sorted(sd.glob("*.uri"))
            total_uris = sum(len([l for l in u.read_text().splitlines() if l.strip()]) for u in uri_files)
            md = "\n".join([
                BEGIN_MARKER,
                "## Phase-Transition & Structural Analysis",
                "",
                f"*Auto-generated by [`../src/analyze_benchmarks.py`](../src/analyze_benchmarks.py). "
                f"This directory stores **{total_uris:,} immutable GBD URI entries** across {len(uri_files)} manifest(s) "
                f"rather than raw multi-gigabyte CNFs; run `python3 ../src/analyze_benchmarks.py --file <downloaded.cnf.xz>` "
                f"on any downloaded instance, or see [`../sat-competition-2023-2024-selected/README.md`](../sat-competition-2023-2024-selected/README.md) "
                f"for structural and phase-transition metrics on 14 curated SAT Competition Main Track CNFs.*",
                END_MARKER,
            ])
            if upsert_section(sd / "README.md", md):
                updated += 1

        if args.all:
            root_md = render_root_overview(by_suite)
            # Insert right before `## Format Conventions` in root README if not already marked
            root_readme = REPO_ROOT / "README.md"
            text = root_readme.read_text(encoding="utf-8")
            if BEGIN_MARKER in text and END_MARKER in text:
                if upsert_section(root_readme, root_md):
                    updated += 1
            else:
                idx = text.find("\n## Format Conventions")
                if idx != -1:
                    new_text = text[:idx].rstrip() + "\n\n" + root_md + "\n" + text[idx:]
                    root_readme.write_text(new_text, encoding="utf-8")
                    updated += 1
                elif upsert_section(root_readme, root_md):
                    updated += 1
        print(f"Updated {updated} README.md files.")


if __name__ == "__main__":
    main()
