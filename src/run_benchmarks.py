#!/usr/bin/env python3
"""Offline Reproducible Multi-Solver Benchmark Harness for SAT-benchmarks.

Zero-dependency Python 3 standard-library CLI that:
  1. `build-solvers`: creates an engines/solvers directory (if missing), clones
     and compiles CaDiCaL 3.1.0, CryptoMiniSat 5.18.0, dense-solver 0.0.4, and
     Kissat 4.0.4 from upstream GitHub repositories (and optionally builds
     Frobenius).
  2. `run`: executes an optional list of engines (`--engines`) against an
     optional list of SAT problems (`--problems`). When omitted, automatically
     discovers and runs ALL executable engines in `--engines-dir` (plus
     Frobenius from `--frobenius-dir`/`--frobenius-bin` if given) against ALL
     SAT problems found under `--benchmarks-dir` in a parallel work queue
     pinned strictly 1 job per dedicated physical CPU core (up to
     `--max-cores`), decompressing inputs before timing, verifying 100% of SAT
     models against raw CNF, and streaming complete structured JSONL records
     incrementally for live monitoring and seamless `--resume`.
  3. `summarize`: inspects an in-progress or completed JSONL file to report live
     per-collection PAR-2 tables, fairness metrics, errors, and every case where
     Frobenius is not the fastest solver.

Examples:
  # Step 1: Clone & compile all competitor solvers into ~/solvers
  python3 src/run_benchmarks.py build-solvers --engines-dir ~/solvers --jobs 8

  # Step 2a: Run ALL engines in ~/solvers (+ Frobenius) on ALL SAT problems
  python3 src/run_benchmarks.py run \\
      --engines-dir ~/solvers \\
      --frobenius-dir /path/to/papers/new/P_NE_NP/solver \\
      --max-cores 8 \\
      --output ~/sat_bench_results.jsonl

  # Step 2b: Run a specific subset of engines on specific SAT problems
  python3 src/run_benchmarks.py run \\
      --engines-dir ~/solvers \\
      --frobenius-dir /path/to/papers/new/P_NE_NP/solver \\
      --engines frobenius,kissat,cadical \\
      --problems costas_n13 costas_n14 integer-factoring/factor_karatsuba_36b \\
      --output ~/subset_results.jsonl

  # Step 3 (in another terminal, live while running or after completion):
  python3 src/run_benchmarks.py summarize --input ~/sat_bench_results.jsonl
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import fnmatch
import json
import lzma
import os
import platform
import queue
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Canonical upstream repositories and pinned release versions for reproducible builds.
UPSTREAM_SOLVERS: dict[str, dict[str, Any]] = {
    "cadical": {
        "repo": "https://github.com/arminbiere/cadical.git",
        "ref": "rel-3.1.0",
        "bin_name": "cadical",
        "display": "CaDiCaL 3.1.0",
    },
    "cryptominisat": {
        "repo": "https://github.com/msoos/cryptominisat.git",
        "ref": "5.18.0",
        "bin_name": "cryptominisat5",
        "display": "CryptoMiniSat 5.18.0",
    },
    "dense-solver": {
        "repo": "https://github.com/libdense/dense-solver.git",
        "ref": "v0.0.4",
        "bin_name": "dense-solver",
        "display": "dense-solver 0.0.4",
    },
    "kissat": {
        "repo": "https://github.com/arminbiere/kissat.git",
        "ref": "rel-4.0.4",
        "bin_name": "kissat",
        "display": "Kissat 4.0.4",
    },
}

FALLBACK_PATH_ENGINES = [
    "frobenius",
    "cadical",
    "cryptominisat5",
    "dense-solver",
    "kissat",
]

ALL_FORMATS = ("cnf", "xcnf", "aig", "anf", "mata")

FORMAT_SUBDIRS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("cnf", ("cnf-orig", "cnf-converted")),
    ("xcnf", ("xcnf-orig", "xcnf-converted")),
    ("aig", ("aig-orig", "aig-converted")),
    ("anf", ("anf-converted",)),
    ("mata", ("mata-orig",)),
)

NON_ENGINE_EXTENSIONS = {
    ".a", ".bash", ".bz2", ".c", ".cc", ".cmake", ".cpp", ".csv", ".d",
    ".gz", ".h", ".hpp", ".json", ".jsonl", ".lock", ".log", ".md", ".o",
    ".pdf", ".png", ".py", ".real", ".rs", ".sh", ".so", ".svg", ".tar",
    ".toml", ".tsv", ".txt", ".xz", ".yaml", ".yml", ".zip", ".zsh", ".zst",
}

# Proof checkers / format utilities that commonly share a bin/ dir with solvers.
NON_ENGINE_NAMES = {
    "aigtoaig", "aigtocnf", "cake_lpr", "cnf2aig",
    "drat-trim", "gratchk", "gratgen", "lrat-check", "lrat-trim",
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_load_1m() -> float:
    try:
        return round(os.getloadavg()[0], 2)
    except OSError:
        return -1.0


def cpu_model_name() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(errors="ignore").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def detect_physical_cores() -> list[int]:
    """Return one logical CPU ID per physical core (avoiding SMT sibling sharing)."""
    seen: dict[tuple[int, int], int] = {}
    sys_cpu = Path("/sys/devices/system/cpu")
    if sys_cpu.is_dir():
        for entry in sorted(sys_cpu.iterdir(), key=lambda p: p.name):
            m = re.fullmatch(r"cpu(\d+)", entry.name)
            if not m:
                continue
            cid = int(m.group(1))
            topo = entry / "topology"
            try:
                pkg = int((topo / "physical_package_id").read_text().strip())
                core = int((topo / "core_id").read_text().strip())
                seen.setdefault((pkg, core), cid)
            except OSError:
                continue
    if seen:
        return sorted(seen.values())
    n = os.cpu_count() or 1
    return list(range(n))


def flatten_list_arg(raw: list[str] | str | None) -> list[str]:
    """Parse space-separated, comma-separated, repeatable, or @file list arguments."""
    if not raw:
        return []
    chunks = [raw] if isinstance(raw, str) else list(raw)
    out: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        for part in chunk.split(","):
            s = part.strip()
            if not s:
                continue
            if s.startswith("@") and len(s) > 1:
                lf = Path(s[1:]).expanduser()
                if not lf.is_file():
                    sys.exit(f"ERROR: list file not found: {lf}")
                for ln in lf.read_text(encoding="utf-8").splitlines():
                    ln = ln.strip()
                    if ln and not ln.startswith("#") and ln not in seen:
                        seen.add(ln)
                        out.append(ln)
            elif s not in seen:
                seen.add(s)
                out.append(s)
    return out


def run_checked(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print(f"  $ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def query_solver_version(bin_path: Path, solver_key: str) -> str:
    if not bin_path.is_file():
        return "missing"
    try:
        p = subprocess.run(
            [str(bin_path), "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=5.0,
        )
        txt = p.stdout.decode("utf-8", errors="replace").strip()
        for ln in txt.splitlines():
            s = ln.strip()
            if s and not s.startswith("Usage:"):
                return s[:120]
    except Exception:
        pass
    return f"{solver_key} ({bin_path.name})"


# ============================================================================
# Mode 1: build-solvers
# ============================================================================

def clone_or_checkout(repo_url: str, ref: str, dst: Path) -> str:
    if not (dst / ".git").is_dir():
        dst.parent.mkdir(parents=True, exist_ok=True)
        run_checked(["git", "clone", "--depth", "1", "--branch", ref, repo_url, str(dst)])
    else:
        run_checked(["git", "-C", str(dst), "fetch", "--tags", "origin"])
        try:
            run_checked(["git", "-C", str(dst), "checkout", ref])
        except subprocess.CalledProcessError:
            run_checked(["git", "-C", str(dst), "checkout", "HEAD"])
    sha = subprocess.check_output(["git", "-C", str(dst), "rev-parse", "--short", "HEAD"], text=True).strip()
    return sha


def build_one_solver(name: str, solvers_dir: Path, jobs: int, rebuild: bool) -> dict[str, Any]:
    spec = UPSTREAM_SOLVERS[name]
    bin_dir = solvers_dir / "bin"
    src_dir = solvers_dir / "src" / name
    bin_dir.mkdir(parents=True, exist_ok=True)
    out_bin = bin_dir / spec["bin_name"]

    if out_bin.is_file() and not rebuild:
        ver = query_solver_version(out_bin, name)
        print(f"[build-solvers] {name}: already present at {out_bin} ({ver}); pass --rebuild to recompile.", flush=True)
        return {"binary": str(out_bin), "version": ver, "status": "cached"}

    print(f"\n[build-solvers] === Building {spec['display']} ===", flush=True)
    try:
        sha = clone_or_checkout(spec["repo"], spec["ref"], src_dir)
    except subprocess.CalledProcessError:
        if not (src_dir / ".git").is_dir():
            run_checked(["git", "clone", "--depth", "1", spec["repo"], str(src_dir)])
        sha = subprocess.check_output(["git", "-C", str(src_dir), "rev-parse", "--short", "HEAD"], text=True).strip()

    if name == "cadical":
        run_checked(["./configure"], cwd=src_dir)
        run_checked(["make", f"-j{jobs}"], cwd=src_dir)
        shutil.copy2(src_dir / "build" / "cadical", out_bin)
    elif name == "kissat":
        run_checked(["./configure"], cwd=src_dir)
        run_checked(["make", f"-j{jobs}"], cwd=src_dir)
        shutil.copy2(src_dir / "build" / "kissat", out_bin)
    elif name == "cryptominisat":
        bdir = src_dir / "build"
        bdir.mkdir(exist_ok=True)
        run_checked(
            [
                "cmake", "..",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DENABLE_TESTING=OFF",
                "-DSTATICCOMPILE=OFF",
                "-DNOPYTHON=ON",
            ],
            cwd=bdir,
        )
        run_checked(["cmake", "--build", ".", f"-j{jobs}", "--target", "cryptominisat5"], cwd=bdir)
        shutil.copy2(bdir / "cryptominisat5", out_bin)
    elif name == "dense-solver":
        if (src_dir / "Cargo.toml").is_file():
            env = os.environ.copy()
            env["CARGO_BUILD_JOBS"] = str(jobs)
            run_checked(["cargo", "build", "--release"], cwd=src_dir, env=env)
            cands = list((src_dir / "target" / "release").glob("dense*"))
            built = next(p for p in cands if p.is_file() and os.access(p, os.X_OK) and "." not in p.name)
            shutil.copy2(built, out_bin)
        elif (src_dir / "CMakeLists.txt").is_file():
            bdir = src_dir / "build"
            bdir.mkdir(exist_ok=True)
            run_checked(["cmake", "..", "-DCMAKE_BUILD_TYPE=Release"], cwd=bdir)
            run_checked(["cmake", "--build", ".", f"-j{jobs}"], cwd=bdir)
            built = next(p for p in bdir.rglob("dense*") if p.is_file() and os.access(p, os.X_OK))
            shutil.copy2(built, out_bin)
        elif (src_dir / "Makefile").is_file():
            run_checked(["make", f"-j{jobs}"], cwd=src_dir)
            built = next(p for p in src_dir.rglob("dense*") if p.is_file() and os.access(p, os.X_OK))
            shutil.copy2(built, out_bin)
        else:
            raise RuntimeError(f"Unrecognized build system in {src_dir}")
    else:
        raise ValueError(f"Unknown solver: {name}")

    os.chmod(out_bin, 0o755)
    ver = query_solver_version(out_bin, name)
    print(f"[build-solvers] OK: {out_bin} (sha={sha}, ver={ver})", flush=True)
    return {"binary": str(out_bin), "git_sha": sha, "version": ver, "status": "built"}


def cmd_build_solvers(args: argparse.Namespace) -> int:
    solvers_dir = Path(args.solvers_dir).expanduser().resolve()
    solvers_dir.mkdir(parents=True, exist_ok=True)
    want = flatten_list_arg(args.solvers) or list(UPSTREAM_SOLVERS.keys())
    alias_map = {"cryptominisat5": "cryptominisat"}
    want = [alias_map.get(s, s) for s in want]
    for s in want:
        if s not in UPSTREAM_SOLVERS:
            sys.exit(f"ERROR: unknown solver '{s}' (choices: {', '.join(UPSTREAM_SOLVERS)})")

    manifest: dict[str, Any] = {
        "built_at_utc": utc_now_iso(),
        "cpu_model": cpu_model_name(),
        "solvers_dir": str(solvers_dir),
        "solvers": {},
    }
    for s in want:
        manifest["solvers"][s] = build_one_solver(s, solvers_dir, args.jobs, args.rebuild)

    if args.frobenius_dir:
        fdir = Path(args.frobenius_dir).expanduser().resolve()
        print(f"\n[build-solvers] === Building Frobenius in {fdir} ===", flush=True)
        env = os.environ.copy()
        env["CARGO_BUILD_JOBS"] = str(args.jobs)
        if args.pgo and (fdir / "scripts" / "build_pgo.sh").is_file():
            run_checked(["./scripts/build_pgo.sh", "1"], cwd=fdir, env=env)
        else:
            run_checked(["cargo", "build", "--release"], cwd=fdir, env=env)
        fbin = fdir / "target" / "release" / "frobenius"
        manifest["solvers"]["frobenius"] = {
            "binary": str(fbin),
            "version": query_solver_version(fbin, "frobenius"),
            "status": "built_pgo" if args.pgo else "built",
        }

    mpath = solvers_dir / "solver_versions.json"
    mpath.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\n[build-solvers] Manifest written -> {mpath}")
    return 0


# ============================================================================
# Mode 2: run (Parallel Core-Pinned Work Queue + Incremental JSONL Output)
# ============================================================================

def is_engine_binary(path: Path) -> bool:
    """Return True if path is a runnable solver binary (not a doc/config/library/checker)."""
    if not path.is_file() or path.name.startswith("."):
        return False
    if path.name in NON_ENGINE_NAMES:
        return False
    if not os.access(path, os.X_OK):
        return False
    if ".so." in path.name:
        return False
    if path.suffix.lower() in NON_ENGINE_EXTENSIONS:
        return False
    return True


def engine_kind(solver: str, bin_path: Path | None = None) -> str:
    lo = solver.lower()
    b_lo = bin_path.name.lower() if bin_path else ""
    if lo == "frobenius" or lo.startswith("frobenius") or b_lo.startswith("frobenius"):
        return "frobenius"
    if "cryptominisat" in lo or "cryptominisat" in b_lo:
        return "cryptominisat"
    return "dimacs"


def engine_supports_format(solver: str, fmt: str, bin_path: Path | None = None) -> bool:
    kind = engine_kind(solver, bin_path)
    if kind == "frobenius":
        return fmt in ALL_FORMATS
    if kind == "cryptominisat":
        lo = solver.lower()
        if lo.endswith("-cnf"):
            return fmt == "cnf"
        if lo.endswith("-xcnf"):
            return fmt == "xcnf"
        return fmt in ("cnf", "xcnf")
    return fmt == "cnf"


def parse_collection_tmax(readme_text: str, col: str) -> float:
    if col in ("hard-spn", "integer-factoring", "zed-adversarial-hub"):
        return 5000.0
    if col == "davies-rectangle-free-27":
        return 600.0
    if col in ("sat-shortcut-challenge-tier3", "sha256-64r-nonce-scaling"):
        return 300.0
    for pat in (
        r"T_\{\\max\}\s*=\s*([\d,{}\s]+)\s*\\text\{\s*s\}",
        r"T_max\s*=\s*([\d,]+)\s*s",
        r"timeout\s*=?\s*([\d,]+)\s*s",
        r">\s*([\d,]+)\s*s\b",
    ):
        m = re.search(pat, readme_text)
        if m:
            s = re.sub(r"[{},\s]", "", m.group(1))
            if s.isdigit():
                return float(s)
    return 60.0


def load_expected_tsv(col_dir: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    p = col_dir / "expected.tsv"
    if p.is_file():
        for ln in p.read_text().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split("\t")
            if len(parts) >= 2:
                out[parts[0]] = parts[1].strip()
                out[Path(parts[0]).stem] = parts[1].strip()
    return out


def verify_cnf_model(cnf_path: Path, model_lits: list[int]) -> tuple[bool, str]:
    assign: dict[int, bool] = {}
    for lit in model_lits:
        if lit != 0:
            assign[abs(lit)] = lit > 0
    if not assign:
        return False, "empty model"
    cl: list[int] = []
    unsat = 0
    total = 0
    with cnf_path.open("rb") as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith((b"c", b"p")):
                continue
            if s.startswith(b"%"):
                break
            for tok in s.split():
                v = int(tok)
                if v == 0:
                    total += 1
                    if not any((x > 0 and assign.get(abs(x), False)) or (x < 0 and not assign.get(abs(x), False)) for x in cl):
                        unsat += 1
                    cl.clear()
                else:
                    cl.append(v)
    if unsat > 0:
        return False, f"{unsat}/{total} unsatisfied clauses"
    return True, f"{total}/{total} clauses verified"


def parse_solver_stats(solver: str, bin_path: Path, stdout: str) -> dict[str, Any]:
    """Extract conflicts, decisions, propagations, and internal reported time when available."""
    stats: dict[str, Any] = {
        "internal_ms": None,
        "conflicts": None,
        "decisions": None,
        "propagations": None,
    }
    if engine_kind(solver, bin_path) == "frobenius":
        m = re.search(r"time=([\d.]+)ms", stdout)
        if m:
            stats["internal_ms"] = float(m.group(1))
        for k in ("conflicts", "decisions", "propagations"):
            mk = re.search(rf"{k}=(\d+)", stdout)
            if mk:
                stats[k] = int(mk.group(1))
    else:
        for k, pats in (
            ("conflicts", [r"c\s+conflicts\s*:\s*(\d+)", r"c\s+Total conflicts\s*:\s*(\d+)"]),
            ("decisions", [r"c\s+decisions\s*:\s*(\d+)", r"c\s+Total decisions\s*:\s*(\d+)"]),
            ("propagations", [r"c\s+propagations\s*:\s*(\d+)", r"c\s+Total propagations\s*:\s*(\d+)"]),
        ):
            for pat in pats:
                mk = re.search(pat, stdout)
                if mk:
                    stats[k] = int(mk.group(1))
                    break
    return stats


def resolve_engine_bins(
    engines_dir: Path | None,
    frobenius_dir: Path | None,
    frobenius_bin: Path | None,
    requested_engines: list[str],
) -> dict[str, Path]:
    """Discover all executable engines in engines_dir (+ Frobenius), optionally filtered."""
    discovered: dict[str, Path] = {}

    # 1. Discover every executable engine in --engines-dir (/bin first, then root)
    if engines_dir is not None:
        ed = engines_dir.expanduser().resolve()
        if not ed.is_dir():
            sys.exit(f"ERROR: --engines-dir / --solvers-dir does not exist: {ed}")
        for scan_dir in (ed / "bin", ed):
            if not scan_dir.is_dir():
                continue
            for entry in sorted(scan_dir.iterdir(), key=lambda p: p.name):
                if is_engine_binary(entry):
                    discovered.setdefault(entry.name, entry.resolve())

    # 2. Add Frobenius if explicitly provided via --frobenius-bin or --frobenius-dir
    if frobenius_bin is not None:
        fb = frobenius_bin.expanduser().resolve()
        if not fb.is_file():
            sys.exit(f"ERROR: --frobenius-bin not found: {fb}")
        discovered["frobenius"] = fb
    elif frobenius_dir is not None:
        fdir = frobenius_dir.expanduser().resolve()
        found_frob = None
        for cand in (
            fdir / "target" / "release" / "frobenius",
            fdir / "target" / "fast-release" / "frobenius",
            fdir / "frobenius",
        ):
            if cand.is_file() and os.access(cand, os.X_OK):
                found_frob = cand.resolve()
                break
        if found_frob is None:
            sys.exit(f"ERROR: no compiled frobenius binary found under --frobenius-dir {fdir}")
        discovered["frobenius"] = found_frob

    # 3. If no directory flags were given at all and no explicit list, check PATH fallback
    if not discovered and engines_dir is None and not requested_engines:
        for bname in FALLBACK_PATH_ENGINES:
            w = shutil.which(bname)
            if w:
                discovered[bname] = Path(w).resolve()

    # 4. If --engines / --solvers was omitted, run ALL discovered engines
    if not requested_engines:
        ordered: dict[str, Path] = {}
        if "frobenius" in discovered:
            ordered["frobenius"] = discovered["frobenius"]
        for k in sorted(discovered):
            if k not in ordered:
                ordered[k] = discovered[k]
        return ordered

    # 5. Otherwise resolve each explicitly requested engine name or path
    selected: dict[str, Path] = {}
    for req in requested_engines:
        if req in discovered:
            selected[req] = discovered[req]
            continue
        # Legacy & convenience aliases for CryptoMiniSat
        if req in ("cryptominisat5-cnf", "cryptominisat5-xcnf") and "cryptominisat5" in discovered:
            selected[req] = discovered["cryptominisat5"]
            continue
        if req == "cryptominisat" and "cryptominisat5" in discovered:
            selected["cryptominisat5"] = discovered["cryptominisat5"]
            continue
        # Direct executable path
        req_path = Path(req).expanduser()
        if req_path.is_file() and os.access(req_path, os.X_OK):
            key = req_path.name
            if key in selected and selected[key] != req_path.resolve():
                key = str(req_path.resolve())
            selected[key] = req_path.resolve()
            continue
        # PATH lookup if --engines-dir wasn't restricting the engine set
        if engines_dir is None:
            lookup = "cryptominisat5" if req in ("cryptominisat", "cryptominisat5-cnf", "cryptominisat5-xcnf") else req
            w = shutil.which(lookup)
            if w:
                selected[req] = Path(w).resolve()
                continue
        avail = ", ".join(sorted(discovered)) or "none"
        sys.exit(f"ERROR: requested engine '{req}' not found (discovered engines: {avail})")

    return selected


def build_solver_cmd(solver: str, bin_path: Path, in_path: Path, fmt: str, core: int, timeout_s: float) -> list[str]:
    prefix = ["taskset", "-c", str(core)] if shutil.which("taskset") else []
    kind = engine_kind(solver, bin_path)
    if kind == "frobenius":
        cmd = prefix + [str(bin_path), str(in_path), "--max-cores", "1", "--timeout", f"{timeout_s:.3f}"]
        if fmt == "mata":
            cmd.append("--mata-complement")
        return cmd
    if kind == "cryptominisat":
        return prefix + [str(bin_path), "-t", "1", str(in_path)]
    return prefix + [str(bin_path), str(in_path)]


def execute_single_run(
    solver: str,
    bin_path: Path,
    solver_version: str,
    col: str,
    fmt: str,
    stem: str,
    src_path: Path,
    expected: str,
    core: int,
    timeout_s: float,
    verify_models: bool,
    tmp_root: Path,
) -> dict[str, Any]:
    tmp_file: Path | None = None
    run_path = src_path
    try:
        if src_path.name.endswith(".xz"):
            base = src_path.name[:-3]
            tmp_file = tmp_root / f"c{core}_{os.getpid()}_{threading.get_ident()}_{base}"
            with lzma.open(src_path, "rb") as src, tmp_file.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1 << 20)
            run_path = tmp_file

        cmd = build_solver_cmd(solver, bin_path, run_path, fmt, core, timeout_s)
        load_before = host_load_1m()
        t0 = time.perf_counter()
        timed_out = False
        user_ms = None
        sys_ms = None
        peak_rss_kb = None

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        out_chunks: list[bytes] = []
        err_chunks: list[bytes] = []

        def _drain(pipe, sink: list[bytes]) -> None:
            try:
                sink.append(pipe.read())
            except Exception:
                pass

        t_out = threading.Thread(target=_drain, args=(proc.stdout, out_chunks), daemon=True)
        t_err = threading.Thread(target=_drain, args=(proc.stderr, err_chunks), daemon=True)
        t_out.start()
        t_err.start()

        deadline = t0 + timeout_s
        rc = -1
        while True:
            pid, status, rusage = os.wait4(proc.pid, os.WNOHANG)
            if pid != 0:
                rc = os.waitstatus_to_exitcode(status)
                user_ms = round(rusage.ru_utime * 1000.0, 3)
                sys_ms = round(rusage.ru_stime * 1000.0, 3)
                peak_rss_kb = int(rusage.ru_maxrss)
                break
            now = time.perf_counter()
            if now >= deadline:
                timed_out = True
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    proc.kill()
                _, status, rusage = os.wait4(proc.pid, 0)
                rc = -9
                user_ms = round(rusage.ru_utime * 1000.0, 3)
                sys_ms = round(rusage.ru_stime * 1000.0, 3)
                peak_rss_kb = int(rusage.ru_maxrss)
                break
            time.sleep(min(0.01, max(0.001, deadline - now)))

        wall_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        t_out.join(timeout=5.0)
        t_err.join(timeout=5.0)
        stdout = (out_chunks[0] if out_chunks else b"").decode("utf-8", errors="replace")

        verdict = "UNKNOWN"
        if not timed_out:
            if rc == 10 or ("\ns SATISFIABLE" in stdout or stdout.startswith("s SATISFIABLE")):
                verdict = "SAT"
            elif rc == 20 or ("\ns UNSATISFIABLE" in stdout or stdout.startswith("s UNSATISFIABLE")):
                verdict = "UNSAT"

        solved = verdict in ("SAT", "UNSAT")
        par2_ms = wall_ms if solved else round(timeout_s * 2000.0, 3)
        verdict_ok = True
        if solved and expected in ("SAT", "UNSAT") and verdict != expected:
            verdict_ok = False

        model_verified: bool | None = None
        model_verify_msg = ""
        if verify_models and verdict == "SAT" and fmt == "cnf":
            lits: list[int] = []
            for ln in stdout.splitlines():
                if ln.startswith("v "):
                    for tok in ln[2:].split():
                        try:
                            lits.append(int(tok))
                        except ValueError:
                            pass
            if lits:
                model_verified, model_verify_msg = verify_cnf_model(run_path, lits)
            else:
                model_verified, model_verify_msg = None, "no v-lines printed"

        extra = parse_solver_stats(solver, bin_path, stdout)
        return {
            "timestamp_utc": utc_now_iso(),
            "collection": col,
            "instance": stem,
            "format": fmt,
            "solver": solver,
            "solver_version": solver_version,
            "core_id": core,
            "host_load_1m": load_before,
            "timeout_s": timeout_s,
            "verdict": verdict,
            "expected": expected,
            "verdict_ok": verdict_ok,
            "model_verified": model_verified,
            "model_verify_msg": model_verify_msg,
            "timed_out": timed_out,
            "wall_ms": wall_ms,
            "user_ms": user_ms,
            "sys_ms": sys_ms,
            "peak_rss_kb": peak_rss_kb,
            "par2_ms": par2_ms,
            "exit_code": rc,
            **extra,
        }
    finally:
        if tmp_file is not None:
            try:
                tmp_file.unlink()
            except OSError:
                pass


def detect_format_and_stem(fp: Path) -> tuple[str, str, str] | None:
    """Return (fmt, base_without_xz, stem) if fp is a supported SAT problem file."""
    name = fp.name
    for fmt in ALL_FORMATS:
        if name.endswith(f".{fmt}.xz"):
            base = name[:-3]
            return fmt, base, base[: -(len(fmt) + 1)]
        if name.endswith(f".{fmt}"):
            return fmt, name, name[: -(len(fmt) + 1)]
    return None


def find_structured_collections(bench_root: Path) -> list[Path]:
    """Find structured SAT-benchmarks collections under bench_root (supports 10-category, category, single, or flat layouts)."""
    all_fmt_subdirs = {sub for _, cands in FORMAT_SUBDIRS for sub in cands}

    def _is_collection_dir(d: Path) -> bool:
        if not (d / "README.md").is_file():
            return False
        return any((d / sub).is_dir() for sub in all_fmt_subdirs)

    if _is_collection_dir(bench_root):
        return [bench_root]

    found: list[Path] = []
    scan_roots: list[Path] = [bench_root / "benchmarks"] if (bench_root / "benchmarks").is_dir() else [bench_root]
    for root in scan_roots:
        for d1 in sorted(root.iterdir(), key=lambda p: p.name):
            if not d1.is_dir() or d1.name.startswith(".") or d1.name in ("src", "__pycache__"):
                continue
            if _is_collection_dir(d1):
                found.append(d1)
                continue
            for d2 in sorted(d1.iterdir(), key=lambda p: p.name):
                if not d2.is_dir() or d2.name.startswith(".") or d2.name in ("src", "__pycache__"):
                    continue
                if _is_collection_dir(d2):
                    found.append(d2)
    return found


def discover_problems(
    bench_root: Path,
    want_formats: list[str],
    timeout_override: float | None,
    skip_oeis_unknown: bool,
) -> list[tuple[str, str, str, str, Path, str, float]]:
    """Discover all SAT problems under bench_root.

    Returns tuples of: (col_rel, col_short, fmt, stem, file_path, expected, tmax).
    """
    problems: list[tuple[str, str, str, str, Path, str, float]] = []
    cols = find_structured_collections(bench_root)

    if cols:
        for cdir in cols:
            rel = cdir.relative_to(bench_root).as_posix() if cdir != bench_root else cdir.name
            col_short = cdir.name
            txt = (cdir / "README.md").read_text(errors="ignore")
            tmax = timeout_override if timeout_override is not None else parse_collection_tmax(txt, col_short)
            exp = load_expected_tsv(cdir)
            is_oeis = col_short.startswith("guillochon-oeis-")

            fmt_dirs: dict[str, Path] = {}
            for fmt, cands in FORMAT_SUBDIRS:
                if fmt not in want_formats:
                    continue
                for sub in cands:
                    p = cdir / sub
                    if p.is_dir():
                        fmt_dirs[fmt] = p
                        break

            for fmt, fdir in fmt_dirs.items():
                ext_xz = f".{fmt}.xz"
                ext_raw = f".{fmt}"
                for fp in sorted(fdir.iterdir(), key=lambda p: p.name):
                    if not fp.is_file() or not (fp.name.endswith(ext_xz) or fp.name.endswith(ext_raw)):
                        continue
                    base = fp.name[:-3] if fp.name.endswith(".xz") else fp.name
                    stem = base[: -(len(fmt) + 1)]
                    ev = exp.get(base) or exp.get(stem) or "UNKNOWN"
                    if is_oeis and skip_oeis_unknown and ev == "UNKNOWN":
                        continue
                    problems.append((rel, col_short, fmt, stem, fp.resolve(), ev, tmax))
        return problems

    # Fallback: arbitrary directory containing raw or .xz SAT problem files
    tmax = timeout_override if timeout_override is not None else 60.0
    exp_cache: dict[Path, dict[str, str]] = {}
    for root, dirs, files in os.walk(bench_root):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__pycache__")
        rpath = Path(root)
        for fname in sorted(files):
            fp = rpath / fname
            det = detect_format_and_stem(fp)
            if det is None:
                continue
            fmt, base, stem = det
            if fmt not in want_formats:
                continue
            if rpath not in exp_cache:
                exp_cache[rpath] = load_expected_tsv(rpath)
            ev = exp_cache[rpath].get(base) or exp_cache[rpath].get(stem) or "UNKNOWN"
            rel_dir = rpath.relative_to(bench_root).as_posix() if rpath != bench_root else bench_root.name
            problems.append((rel_dir, rpath.name, fmt, stem, fp.resolve(), ev, tmax))
    return problems


def filter_problems(
    all_problems: list[tuple[str, str, str, str, Path, str, float]],
    bench_root: Path,
    want_problems: list[str],
    want_cols: set[str] | None,
    excl_cols: set[str],
    want_formats: list[str],
    timeout_override: float | None,
) -> list[tuple[str, str, str, str, Path, str, float]]:
    """Filter discovered SAT problems by --collections / --exclude-collections / --problems."""
    pool = all_problems
    if want_cols is not None:
        pool = [
            p for p in pool
            if p[0] in want_cols
            or p[1] in want_cols
            or any(part in want_cols for part in Path(p[0]).parts)
        ]
    if excl_cols:
        pool = [
            p for p in pool
            if p[0] not in excl_cols
            and p[1] not in excl_cols
            and not any(part in excl_cols for part in Path(p[0]).parts)
        ]

    if not want_problems:
        return pool

    by_resolved_path = {p[4]: p for p in pool}
    selected: list[tuple[str, str, str, str, Path, str, float]] = []
    selected_paths: set[Path] = set()

    def _add(p: tuple[str, str, str, str, Path, str, float]) -> None:
        if p[4] not in selected_paths:
            selected_paths.add(p[4])
            selected.append(p)

    for spec in want_problems:
        matched_any = False

        # 1. Direct file or directory path (relative to CWD or relative to bench_root)
        path_cands = [Path(spec).expanduser()]
        if not path_cands[0].is_absolute():
            path_cands.append(bench_root / spec)
        resolved_hit: Path | None = None
        for cand in path_cands:
            if cand.exists():
                resolved_hit = cand.resolve()
                break

        if resolved_hit is not None:
            if resolved_hit.is_file():
                if resolved_hit in by_resolved_path:
                    _add(by_resolved_path[resolved_hit])
                    matched_any = True
                else:
                    det = detect_format_and_stem(resolved_hit)
                    if det is not None:
                        fmt, base, stem = det
                        exp = load_expected_tsv(resolved_hit.parent)
                        ev = exp.get(base) or exp.get(stem) or "UNKNOWN"
                        col_rel = (
                            resolved_hit.parent.relative_to(bench_root).as_posix()
                            if resolved_hit.is_relative_to(bench_root)
                            else resolved_hit.parent.name
                        )
                        tmax = timeout_override if timeout_override is not None else 60.0
                        _add((col_rel, resolved_hit.parent.name, fmt, stem, resolved_hit, ev, tmax))
                        matched_any = True
            elif resolved_hit.is_dir():
                for p in pool:
                    if p[4].is_relative_to(resolved_hit):
                        _add(p)
                        matched_any = True
                if not matched_any:
                    # Directory outside bench_root or containing standalone SAT files
                    extra_probs = discover_problems(
                        resolved_hit,
                        want_formats=want_formats,
                        timeout_override=timeout_override,
                        skip_oeis_unknown=False,
                    )
                    for p in extra_probs:
                        _add(p)
                        matched_any = True

        if matched_any:
            continue

        # 2. Match by collection, category, <collection>/<stem>, filename, stem, or glob pattern
        is_glob = any(ch in spec for ch in "*?[")
        norm_spec = spec.strip("/")
        for p in pool:
            col_rel, col_short, fmt, stem, fp, _ev, _tmax = p
            base = fp.name[:-3] if fp.name.endswith(".xz") else fp.name
            rel_file = fp.relative_to(bench_root).as_posix() if fp.is_relative_to(bench_root) else fp.name
            parts = Path(col_rel).parts
            cat_candidates = []
            if len(parts) >= 2 and parts[0] == "benchmarks":
                cat_candidates = [parts[1], f"benchmarks/{parts[1]}"]
            keys = (
                col_rel,
                col_short,
                *cat_candidates,
                f"{col_short}/{stem}",
                f"{col_rel}/{stem}",
                f"{col_short}/{fp.name}",
                f"{col_rel}/{fp.name}",
                f"{col_short}/{base}",
                stem,
                base,
                fp.name,
                rel_file,
            )
            hit = any(fnmatch.fnmatch(k, norm_spec) for k in keys) if is_glob else (norm_spec in keys)
            if hit:
                _add(p)
                matched_any = True

        if not matched_any:
            sys.exit(f"ERROR: --problems selector '{spec}' matched 0 SAT problems under {bench_root}")

    return selected


def build_task_queue(args: argparse.Namespace, bins: dict[str, Path]) -> list[tuple[str, str, str, Path, str, float, str]]:
    bench_root = Path(args.benchmarks_dir).expanduser().resolve() if args.benchmarks_dir else REPO_ROOT
    if not bench_root.is_dir():
        sys.exit(f"ERROR: --benchmarks-dir does not exist: {bench_root}")

    raw_formats = flatten_list_arg(args.formats)
    if not raw_formats or "all" in raw_formats:
        want_formats = list(ALL_FORMATS)
    else:
        for f in raw_formats:
            if f not in ALL_FORMATS:
                sys.exit(f"ERROR: unknown format '{f}' (choices: {', '.join(ALL_FORMATS)}, all)")
        want_formats = raw_formats

    want_cols_list = flatten_list_arg(args.collections)
    want_cols = set(want_cols_list) if want_cols_list else None
    excl_cols = set(flatten_list_arg(args.exclude_collections))
    want_problems = flatten_list_arg(args.problems)

    all_problems = discover_problems(
        bench_root=bench_root,
        want_formats=want_formats,
        timeout_override=args.timeout,
        skip_oeis_unknown=args.skip_oeis_unknown,
    )
    problems = filter_problems(
        all_problems=all_problems,
        bench_root=bench_root,
        want_problems=want_problems,
        want_cols=want_cols,
        excl_cols=excl_cols,
        want_formats=want_formats,
        timeout_override=args.timeout,
    )

    tasks: list[tuple[str, str, str, Path, str, float, str]] = []
    for col_rel, _col_short, fmt, stem, fp, ev, tmax in problems:
        for sname, bpath in bins.items():
            if not engine_supports_format(sname, fmt, bpath):
                continue
            tasks.append((col_rel, fmt, stem, fp, ev, tmax, sname))
    return tasks


def load_completed_keys(jsonl_path: Path) -> set[tuple[str, str, str, str]]:
    done: set[tuple[str, str, str, str]] = set()
    if not jsonl_path.is_file():
        return done
    for ln in jsonl_path.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
            done.add((rec["collection"], rec["format"], rec["instance"], rec["solver"]))
        except Exception:
            continue
    return done


def write_summary_files(jsonl_path: Path, quiet: bool = False) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    if jsonl_path.is_file():
        for ln in jsonl_path.read_text().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                records.append(json.loads(ln))
            except Exception:
                continue

    latest: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for r in records:
        latest[(r["collection"], r["format"], r["instance"], r["solver"])] = r
    recs = list(latest.values())

    by_col_fmt: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = {}
    disagrees = []
    badsats = []
    for r in recs:
        by_col_fmt.setdefault((r["collection"], r["format"]), {}).setdefault(r["solver"], []).append(r)
        if not r.get("verdict_ok", True):
            disagrees.append(f"{r['collection']}/{r['format']}/{r['instance']} ({r['solver']}: got {r['verdict']} exp {r['expected']})")
        if r.get("model_verified") is False:
            badsats.append(f"{r['collection']}/{r['format']}/{r['instance']} ({r['solver']}: {r.get('model_verify_msg')})")

    col_rows = []
    col_deficits = []
    inst_deficits = []
    for (col, fmt), smap in sorted(by_col_fmt.items()):
        solver_stats = {}
        for sname, srows in sorted(smap.items()):
            solved = sum(1 for r in srows if r["verdict"] in ("SAT", "UNSAT"))
            par2 = round(sum(r["par2_ms"] for r in srows), 2)
            solver_stats[sname] = {"n": len(srows), "solved": solved, "par2_ms": par2}
        frob = solver_stats.get("frobenius")
        comps = {k: v for k, v in solver_stats.items() if k != "frobenius"}
        best_comp_k = min(comps, key=lambda k: comps[k]["par2_ms"]) if comps else None
        col_rows.append({"collection": col, "format": fmt, "solvers": solver_stats})
        if frob and best_comp_k:
            bc = comps[best_comp_k]
            if frob["par2_ms"] > bc["par2_ms"] * 1.02:
                col_deficits.append({
                    "collection": col, "format": fmt,
                    "frob_solved": frob["solved"], "frob_par2_ms": frob["par2_ms"],
                    "best_comp": best_comp_k, "comp_solved": bc["solved"], "comp_par2_ms": bc["par2_ms"],
                    "ratio": round(frob["par2_ms"] / max(bc["par2_ms"], 0.01), 3),
                })

        by_inst: dict[str, dict[str, dict[str, Any]]] = {}
        for sname, srows in smap.items():
            for r in srows:
                by_inst.setdefault(r["instance"], {})[sname] = r
        for inst, imap in sorted(by_inst.items()):
            fr = imap.get("frobenius")
            if not fr:
                continue
            best_c = None
            for k, cr in imap.items():
                if k == "frobenius" or cr["verdict"] not in ("SAT", "UNSAT"):
                    continue
                if best_c is None or cr["wall_ms"] < best_c["wall_ms"]:
                    best_c = cr
            if best_c is not None:
                f_unsolved = fr["verdict"] not in ("SAT", "UNSAT")
                if f_unsolved or (fr["wall_ms"] > best_c["wall_ms"] * 1.10 and (fr["wall_ms"] - best_c["wall_ms"]) >= 5.0):
                    inst_deficits.append({
                        "collection": col, "format": fmt, "instance": inst,
                        "frob_verdict": fr["verdict"], "frob_ms": fr["wall_ms"],
                        "best_comp": best_c["solver"], "comp_verdict": best_c["verdict"], "comp_ms": best_c["wall_ms"],
                        "ratio": round(fr["par2_ms"] / max(best_c["wall_ms"], 0.01), 2),
                    })

    summary = {
        "updated_at_utc": utc_now_iso(),
        "total_records": len(recs),
        "collections_seen": len(by_col_fmt),
        "disagrees": disagrees,
        "badsats": badsats,
        "col_deficits": sorted(col_deficits, key=lambda d: -d["ratio"]),
        "inst_deficits": sorted(inst_deficits, key=lambda d: -d["ratio"]),
        "collections": col_rows,
    }
    sum_json = jsonl_path.with_suffix(".summary.json")
    sum_md = jsonl_path.with_suffix(".summary.md")
    sum_json.write_text(json.dumps(summary, indent=2) + "\n")

    md_lines = [
        f"# SAT-benchmarks Live Run Summary ({summary['updated_at_utc']})",
        "",
        f"- **Records:** `{len(recs)}` across `{len(by_col_fmt)}` `(collection, format)` groups",
        f"- **Verdict Disagreements:** `{len(disagrees)}` | **BADSAT:** `{len(badsats)}`",
        f"- **Collection-level Frobenius deficits (>1.02x PAR-2):** `{len(col_deficits)}`",
        f"- **Instance-level Frobenius deficits (>1.10x & >=5ms, or T/O):** `{len(inst_deficits)}`",
        "",
    ]
    if col_deficits:
        md_lines.extend([
            "## Collection-Level Deficits",
            "",
            "| Collection | Format | Frobenius PAR-2 | Fastest Competitor | Ratio |",
            "|---|---|---:|---|---:|",
        ])
        for d in summary["col_deficits"]:
            md_lines.append(
                f"| `{d['collection']}` | `{d['format']}` | {d['frob_par2_ms']:.1f} ms ({d['frob_solved']}) "
                f"| `{d['best_comp']}`: {d['comp_par2_ms']:.1f} ms ({d['comp_solved']}) | {d['ratio']:.2f}x |"
            )
        md_lines.append("")
    if inst_deficits:
        md_lines.extend([
            "## Top 30 Instance-Level Deficits",
            "",
            "| Collection / Instance | Format | Frobenius | Fastest Competitor | Ratio |",
            "|---|---|---:|---|---:|",
        ])
        for d in summary["inst_deficits"][:30]:
            md_lines.append(
                f"| `{d['collection']}/{d['instance']}` | `{d['format']}` | {d['frob_ms']:.2f} ms ({d['frob_verdict']}) "
                f"| `{d['best_comp']}`: {d['comp_ms']:.2f} ms ({d['comp_verdict']}) | {d['ratio']:.2f}x |"
            )
        md_lines.append("")

    sum_md.write_text("\n".join(md_lines))
    if not quiet:
        print("\n".join(md_lines))
    return summary


def cmd_run(args: argparse.Namespace) -> int:
    engines_dir = Path(args.engines_dir) if args.engines_dir else None
    frobenius_dir = Path(args.frobenius_dir) if args.frobenius_dir else None
    frobenius_bin = Path(args.frobenius_bin) if args.frobenius_bin else None
    requested_engines = flatten_list_arg(args.engines)

    bins = resolve_engine_bins(engines_dir, frobenius_dir, frobenius_bin, requested_engines)
    if not bins:
        sys.exit("ERROR: no engine binaries found; pass --engines-dir and/or --frobenius-dir/--frobenius-bin")

    versions = {k: query_solver_version(p, k) for k, p in bins.items()}
    print("[run] Resolved engine binaries:", flush=True)
    for k, p in bins.items():
        print(f"  {k:20s} -> {p} ({versions[k]})", flush=True)

    if args.cores:
        cores = [int(c.strip()) for c in args.cores.split(",") if c.strip()]
    else:
        phys = detect_physical_cores()
        cores = phys[: max(1, min(args.max_cores, len(phys)))]
    if len(cores) > args.max_cores:
        cores = cores[: args.max_cores]

    tasks = build_task_queue(args, bins)
    out_path = Path(args.output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    done_keys = load_completed_keys(out_path) if args.resume else set()
    if done_keys:
        before = len(tasks)
        tasks = [t for t in tasks if (t[0], t[1], t[2], t[6]) not in done_keys]
        print(f"[run] --resume skipped {before - len(tasks)} already-completed runs ({len(tasks)} remaining).", flush=True)

    tasks.sort(key=lambda t: (-t[5], t[0], t[2], t[6]))
    print(f"[run] Queue: {len(tasks)} runs | Cores ({len(cores)}): {cores} | Output: {out_path}", flush=True)

    if args.dry_run:
        cols_seen = sorted({t[0] for t in tasks})
        probs_seen = sorted({(t[0], t[1], t[2]) for t in tasks})
        print(f"[dry-run] {len(cols_seen)} collections, {len(probs_seen)} problems, {len(bins)} engines -> {len(tasks)} runs ready. First 10 tasks:")
        for t in tasks[:10]:
            print(f"  {t[0]}/{t[1]}/{t[2]} engine={t[6]} timeout={t[5]}s exp={t[4]}")
        return 0

    if args.load_guard > 0:
        while True:
            ld = host_load_1m()
            if ld < 0 or ld <= args.load_guard:
                break
            print(f"[run] Host 1m load {ld:.2f} > --load-guard {args.load_guard:.2f}; waiting 15s...", flush=True)
            time.sleep(15)

    tmp_base = Path(args.tmp_dir) if args.tmp_dir else (Path("/dev/shm") if Path("/dev/shm").is_dir() else Path(tempfile.gettempdir()))
    tmp_root = Path(tempfile.mkdtemp(prefix="sat_bench_run_", dir=str(tmp_base)))

    core_q: queue.Queue[int] = queue.Queue()
    for c in cores:
        core_q.put(c)

    write_lock = threading.Lock()
    completed = 0
    errors = 0
    t_start = time.perf_counter()

    def _worker(task: tuple[str, str, str, Path, str, float, str]) -> dict[str, Any]:
        col, fmt, stem, fp, ev, tmax, sname = task
        core = core_q.get()
        try:
            return execute_single_run(
                solver=sname,
                bin_path=bins[sname],
                solver_version=versions[sname],
                col=col,
                fmt=fmt,
                stem=stem,
                src_path=fp,
                expected=ev,
                core=core,
                timeout_s=tmax,
                verify_models=args.verify_models,
                tmp_root=tmp_root,
            )
        finally:
            core_q.put(core)

    try:
        mode = "a" if args.resume else "w"
        with out_path.open(mode, encoding="utf-8") as fout:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(cores)) as ex:
                futs = [ex.submit(_worker, t) for t in tasks]
                for fut in concurrent.futures.as_completed(futs):
                    rec = fut.result()
                    line = json.dumps(rec, separators=(",", ":")) + "\n"
                    with write_lock:
                        fout.write(line)
                        fout.flush()
                        os.fsync(fout.fileno())
                        completed += 1
                        if (not rec["verdict_ok"]) or (rec["model_verified"] is False):
                            errors += 1
                            print(
                                f"  [ALERT] {rec['collection']}/{rec['instance']} ({rec['solver']}): "
                                f"verdict={rec['verdict']} exp={rec['expected']} verified={rec['model_verified']}",
                                flush=True,
                            )
                        if completed % args.log_every == 0 or completed == len(tasks):
                            el = time.perf_counter() - t_start
                            rate = completed / max(el, 0.001)
                            eta = (len(tasks) - completed) / max(rate, 1e-6)
                            print(
                                f"[run] {completed}/{len(tasks)} ({100.0*completed/max(len(tasks),1):.1f}%) "
                                f"elapsed={el:.1f}s eta={eta:.0f}s load={host_load_1m():.2f} errors={errors}",
                                flush=True,
                            )
                        if args.summary_every > 0 and completed % args.summary_every == 0:
                            write_summary_files(out_path, quiet=True)

        write_summary_files(out_path, quiet=False)
        print(f"\n[run] Finished {completed} runs in {time.perf_counter() - t_start:.1f}s -> {out_path}", flush=True)
        return 1 if errors > 0 else 0
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def cmd_summarize(args: argparse.Namespace) -> int:
    in_path = Path(args.input).expanduser().resolve()
    if not in_path.is_file():
        sys.exit(f"ERROR: file not found: {in_path}")
    write_summary_files(in_path, quiet=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="run_benchmarks.py",
        description="Offline reproducible multi-solver builder & parallel core-pinned benchmark runner for SAT-benchmarks.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # build-solvers
    p_b = sub.add_parser("build-solvers", help="Clone and compile competitor solvers (and optionally Frobenius) into --engines-dir.")
    p_b.add_argument("--engines-dir", "--solvers-dir", dest="solvers_dir", required=True, help="Directory to create/populate with src/ and bin/ for all solvers.")
    p_b.add_argument("--engines", "--solvers", dest="solvers", nargs="+", default=None, help="Optional list of engines to build (default: all upstream competitors).")
    p_b.add_argument("--frobenius-dir", default="", help="Optional path to Frobenius solver/ crate to compile as well.")
    p_b.add_argument("--pgo", action="store_true", help="If --frobenius-dir is given, build via ./scripts/build_pgo.sh 1.")
    p_b.add_argument("--jobs", type=int, default=max(1, min(8, os.cpu_count() or 1)), help="Parallel make/cargo build jobs.")
    p_b.add_argument("--rebuild", action="store_true", help="Force recompile even if binary already exists in --engines-dir/bin/.")
    p_b.set_defaults(func=cmd_build_solvers)

    # run
    p_r = sub.add_parser("run", help="Run benchmarks in parallel (1 task per dedicated physical core) and stream JSONL output.")
    p_r.add_argument("--engines-dir", "--solvers-dir", dest="engines_dir", default="", help="Directory containing engine binaries (scans <dir>/bin/ and <dir>/).")
    p_r.add_argument("--benchmarks-dir", default="", help="SAT benchmarks root directory (default: this SAT-benchmarks repository).")
    p_r.add_argument("--frobenius-dir", default="", help="Optional path to Frobenius solver/ directory (auto-finds target/release/frobenius).")
    p_r.add_argument("--frobenius-bin", default="", help="Optional direct path to frobenius binary (overrides --frobenius-dir).")
    p_r.add_argument("--engines", "--solvers", dest="engines", nargs="+", default=None, help="Optional list of engines to run (names or paths; comma- or space-separated). Default: ALL engines in --engines-dir (+ Frobenius if provided).")
    p_r.add_argument("--problems", "--instances", dest="problems", nargs="+", default=None, help="Optional list of SAT problems to run (paths, dirs, collections, <col>/<stem>, stems, globs, or @file). Default: ALL SAT problems in --benchmarks-dir.")
    p_r.add_argument("--output", required=True, help="Output JSONL path (written & fsynced incrementally after every run).")
    p_r.add_argument("--max-cores", type=int, default=max(1, len(detect_physical_cores()) - 1), help="Maximum parallel physical cores (1 job/core).")
    p_r.add_argument("--cores", default="", help="Optional explicit comma-separated CPU core IDs (e.g. 0,1,2,3,4,5,6,7).")
    p_r.add_argument("--formats", default="cnf", help="Comma-separated formats (cnf,xcnf,aig,anf,mata, or 'all').")
    p_r.add_argument("--collections", nargs="+", default=None, help="Optional subset of collection or category names.")
    p_r.add_argument("--exclude-collections", nargs="+", default=None, help="Optional collections or categories to skip.")
    p_r.add_argument("--timeout", type=float, default=None, help="Global timeout override in seconds (default: per-collection README T_max).")
    p_r.add_argument("--resume", action="store_true", help="Resume by skipping (collection, format, instance, solver) tuples already in --output.")
    p_r.add_argument("--load-guard", type=float, default=0.0, help="If >0, pause before starting until 1m host load average <= value.")
    p_r.add_argument("--tmp-dir", default="", help="Temp dir for decompressed inputs (default: /dev/shm if present, else /tmp).")
    p_r.add_argument("--no-verify-models", dest="verify_models", action="store_false", help="Disable raw-CNF SAT model verification.")
    p_r.add_argument("--include-oeis-unknown", dest="skip_oeis_unknown", action="store_false", help="Also run UNKNOWN rows in guillochon-oeis-*.")
    p_r.add_argument("--log-every", type=int, default=25, help="Print progress every N completed runs.")
    p_r.add_argument("--summary-every", type=int, default=100, help="Refresh <output>.summary.{md,json} every N runs.")
    p_r.add_argument("--dry-run", action="store_true", help="Show resolved engines and task queue without running solvers.")
    p_r.set_defaults(func=cmd_run, verify_models=True, skip_oeis_unknown=True)

    # summarize
    p_s = sub.add_parser("summarize", help="Inspect an in-progress or completed JSONL file and print live PAR-2 & deficit tables.")
    p_s.add_argument("--input", required=True, help="Path to JSONL output file produced by `run`.")
    p_s.set_defaults(func=cmd_summarize)

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
