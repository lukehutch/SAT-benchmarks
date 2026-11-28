"""Shared constants, collection discovery, git-diff detection, and check context."""
from __future__ import annotations

import argparse
import fnmatch
import multiprocessing as mp
import os
import subprocess
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "frobenius"

VALID_LABELS = frozenset({"SAT", "UNSAT", "UNKNOWN"})
ORIG_DIRS = ("cnf-orig", "aig-orig", "xcnf-orig", "mata-orig")
CONV_DIRS = ("aig-converted", "cnf-converted", "xcnf-converted", "anf-converted")
SAT_EXTS = (
    ".cnf.xz",
    ".aig.xz",
    ".xcnf.xz",
    ".anf.xz",
    ".mata.xz",
    ".cnf",
    ".aig",
    ".xcnf",
    ".anf",
    ".mata",
    ".xz",
)
BAD_COMPRESSION_EXTS = (".gz", ".bz2", ".cnf", ".aig", ".xcnf", ".anf", ".mata")
ROOT_BENCHMARK_EXTS = (".xz", ".gz", ".bz2", ".cnf", ".aig", ".xcnf", ".anf", ".mata")
MAX_GITHUB_FILE_BYTES = 95 * 1024 * 1024

# Archive-only URI catalogs that list multi-instance .tar.gz archives rather than individual formulas.
ARCHIVE_ONLY_URI_COLLECTIONS = frozenset({"satlib-archive-uris"})

# Historical pre-commit cache artifact: new_suites_bench.json was recorded on 2026-11-22 19:23,
# 9 minutes before commit 513ab8aa (2026-11-22 19:32) fixed the Gz matrix check in
# qdistsat-qldpc/src/export_qdist_cnf.py. The committed BB_144_12_12_w11_unsat.cnf.xz is
# mathematically UNSAT (d=12, Hz*Gz^T=0, rank([Hx;Gz])=n-rank(Hz)) and times out >10s in
# post-commit all_suites_8core.json. Flagged under --strict-legacy-cache, annotated otherwise.
KNOWN_PRECOMMIT_CACHE_ARTIFACTS = frozenset({
    ("new_suites_bench.json", "qdistsat_6", "qdistsat-qldpc", "BB_144_12_12_w11_unsat"),
    ("new_suites_bench.json", "qdistsat_xcnf_6", "qdistsat-qldpc", "BB_144_12_12_w11_unsat"),
})

# Legacy collection names from pre-reorganization cache JSONs mapped to their current split/merged targets.
LEGACY_COLLECTION_MAP: dict[str, tuple[str, ...]] = {
    "dense-solver-synthetic": ("dense-solver-synthetic-chessboard", "dense-solver-synthetic-php"),
    "zed-adversarial-hub-php": ("zed-adversarial-hub", "zed-adversarial-php"),
    "vzhn-sat-inv-matrix": ("vzhn-sat-inv-matrix-int", "vzhn-sat-inv-matrix-mod"),
    "sat-competition-2023-2024-selected": ("sat-competition-2002-2026-uris",),
    "sat-competition-2024-2026-main-track": ("sat-competition-2002-2026-uris",),
    "guillochon-oeis-sat-instances": (
        "guillochon-oeis-a067782-sortnet",
        "guillochon-oeis-a171081-vdw",
        "guillochon-oeis-a250000-queens",
        "guillochon-oeis-a350304-zarankiewicz",
        "guillochon-oeis-grid-sq-any",
        "guillochon-oeis-grid-sq-axis",
        "guillochon-oeis-grid-tri-any",
        "guillochon-oeis-grid-tri-axis",
        "guillochon-oeis-grid-tri-up",
    ),
}


@dataclass
class CheckResult:
    """Result returned by a single modular check."""

    name: str
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)
    duration_s: float = 0.0

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class CheckContext:
    """Shared execution context & lazy caches for modular checks."""

    repo_root: Path
    collections: list[str]
    is_full_repo: bool = True
    include_root_readme: bool = True
    check_hygiene: bool = False
    cache_dir: Path = DEFAULT_CACHE_DIR
    skip_cache: bool = False
    strict_legacy_cache: bool = False
    jobs: int = 1

    # Lazily populated caches shared across checks
    orig_entries: dict[str, tuple[str | None, list[str], list[str]]] = field(default_factory=dict)
    col_kinds: dict[str, str] = field(default_factory=dict)
    all_expected: dict[str, dict[str, str]] = field(default_factory=dict)
    expected_errors: dict[str, list[str]] = field(default_factory=dict)
    by_col: dict[str, dict[str, tuple[str, str]]] = field(default_factory=dict)
    global_idx: dict[str, list[tuple[str, str, str]]] = field(default_factory=dict)
    _readme_cache: dict[Path, str | None] = field(default_factory=dict, repr=False)
    _orig_loaded: bool = field(default=False, repr=False)
    _expected_loaded: bool = field(default=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _pool: ProcessPoolExecutor | None = field(default=None, repr=False)

    def __enter__(self) -> CheckContext:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=True)
            self._pool = None

    def _get_pool(self) -> ProcessPoolExecutor | None:
        if self.jobs <= 1:
            return None
        if self._pool is None:
            if "fork" in mp.get_all_start_methods():
                self._pool = ProcessPoolExecutor(
                    max_workers=self.jobs,
                    mp_context=mp.get_context("fork"),
                )
        return self._pool

    def map_work(self, fn: Callable[[T], R], items: Sequence[T], min_parallel: int = 8) -> list[R]:
        """Run a top-level picklable ``fn`` across ``items`` using a shared process pool when worthwhile."""
        if self.jobs <= 1 or len(items) < min_parallel:
            return [fn(x) for x in items]
        pool = self._get_pool()
        if pool is not None:
            chunk = max(1, len(items) // (self.jobs * 2))
            return list(pool.map(fn, items, chunksize=chunk))
        return map_parallel(fn, items, self.jobs)

    def read_readme(self, md_path: Path) -> str | None:
        """Read and cache UTF-8 text for a Markdown file (thread-safe)."""
        with self._lock:
            if md_path in self._readme_cache:
                return self._readme_cache[md_path]
        if not md_path.exists():
            text: str | None = None
        else:
            text = md_path.read_text(encoding="utf-8", errors="replace")
        with self._lock:
            self._readme_cache[md_path] = text
        return text

    def ensure_orig_entries(self) -> None:
        """Populate ``orig_entries`` and ``col_kinds`` for all selected collections."""
        if self._orig_loaded:
            return
        work = [(self.repo_root, c) for c in self.collections]
        for col, res in self.map_work(_scan_orig_worker, work):
            self.orig_entries[col] = res
            if res[0] is not None:
                self.col_kinds[col] = res[0]
        self._orig_loaded = True

    def ensure_expected(self) -> None:
        """Populate ``all_expected``, ``expected_errors``, ``by_col``, and ``global_idx``."""
        if self._expected_loaded:
            return
        self.ensure_orig_entries()
        to_load = [
            (self.repo_root, c)
            for c in self.collections
            if (kind := self.col_kinds.get(c)) is not None and kind != "archive-uri"
        ]
        for col, mapping, errs in self.map_work(_load_expected_worker, to_load):
            self.all_expected[col] = mapping
            self.expected_errors[col] = errs

        self.by_col, self.global_idx = build_stem_index(self.all_expected)
        self._expected_loaded = True


def _scan_orig_worker(args: tuple[Path, str]) -> tuple[str, tuple[str | None, list[str], list[str]]]:
    repo_root, col = args
    return col, get_collection_orig_entries(repo_root / col)


def _load_expected_worker(args: tuple[Path, str]) -> tuple[str, dict[str, str], list[str]]:
    repo_root, col = args
    mapping, errs = load_expected_tsv(repo_root / col / "expected.tsv", repo_root=repo_root)
    return col, mapping, errs


def default_jobs() -> int:
    return min(4, os.cpu_count() or 1)


def map_parallel(fn: Callable[[T], R], items: Sequence[T], jobs: int) -> list[R]:
    """Apply ``fn`` across ``items`` preserving deterministic order."""
    if jobs <= 1 or len(items) <= 1:
        return [fn(x) for x in items]
    max_workers = min(jobs, len(items))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(fn, items))


def strip_all_exts(name: str) -> str:
    s = name.replace("\\", "/").rsplit("/", 1)[-1]
    for ext in SAT_EXTS:
        if s.endswith(ext):
            return s[: -len(ext)]
    return s


def strip_rel_exts(rel_path: str) -> str:
    """Strip benchmark extension(s) while preserving any POSIX subdirectory prefix."""
    p = rel_path.replace("\\", "/") if "\\" in rel_path else rel_path
    for ext in SAT_EXTS:
        if p.endswith(ext):
            return p[: -len(ext)]
    return p


def norm_verdict(raw: object) -> str | None:
    if raw is None:
        return None
    u = str(raw).strip().upper()
    if u in ("SAT", "SATISFIABLE", "S SATISFIABLE", "SAT-VERIFIED"):
        return "SAT"
    if u in ("UNSAT", "UNSATISFIABLE", "S UNSATISFIABLE", "UNSAT-VERIFIED"):
        return "UNSAT"
    if u in ("UNKNOWN", "TIMEOUT", "T/O", "OPEN", "TBD", "PENDING"):
        return "UNKNOWN"
    return None


def discover_collections(
    repo_root: Path,
    only: list[str] | None = None,
    excludes: list[str] | None = None,
) -> list[str]:
    only_set = {c.rstrip("/") for c in only} if only else None
    excludes = excludes or []
    cols: list[str] = []
    bench_root = repo_root / "benchmarks"
    if bench_root.is_dir():
        candidates = sorted(
            f"benchmarks/{cat.name}/{col.name}"
            for cat in bench_root.iterdir()
            if cat.is_dir() and not cat.name.startswith(".")
            for col in cat.iterdir()
            if col.is_dir() and not col.name.startswith(".")
        )
    else:
        candidates = sorted(
            entry.name
            for entry in repo_root.iterdir()
            if entry.is_dir() and not entry.name.startswith(".") and entry.name != "src"
        )
    for rel in candidates:
        base = rel.rsplit("/", 1)[-1]
        if only_set is not None and rel not in only_set and base not in only_set:
            continue
        if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(base, pat) for pat in excludes):
            continue
        cols.append(rel)
    return cols


def detect_changed_collections(repo_root: Path) -> tuple[list[str], bool]:
    """Detect modified or untracked collections from ``git status --porcelain``.

    Returns ``(sorted_changed_collections, root_readme_changed)``.
    """
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "-c", "core.quotepath=false", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git status failed in {repo_root}: {proc.stderr.strip()}")

    changed: set[str] = set()
    root_readme_changed = False

    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path_spec = line[3:].strip()
        # Handle renames/copies ("old -> new")
        candidates = [p.strip().strip('"') for p in path_spec.split(" -> ")]
        for rel in candidates:
            rel_norm = rel.replace("\\", "/").lstrip("./")
            if not rel_norm:
                continue
            if rel_norm == "README.md":
                root_readme_changed = True
                continue
            parts = rel_norm.split("/")
            if parts[0].startswith(".") or parts[0] == "src":
                continue
            if parts[0] == "benchmarks" and len(parts) >= 3:
                col_rel = "/".join(parts[:3])
                if (repo_root / col_rel).is_dir():
                    changed.add(col_rel)
            elif (repo_root / parts[0]).is_dir() and parts[0] != "benchmarks":
                changed.add(parts[0])

    return sorted(changed), root_readme_changed


def load_expected_tsv(tsv_path: Path, repo_root: Path = REPO_ROOT) -> tuple[dict[str, str], list[str]]:
    """Parse and strictly validate an expected.tsv file."""
    errors: list[str] = []
    mapping: dict[str, str] = {}
    try:
        disp = str(tsv_path.relative_to(repo_root))
    except ValueError:
        disp = str(tsv_path)
    if not tsv_path.exists():
        return mapping, [f"Missing {disp}"]

    raw = tsv_path.read_text(encoding="utf-8")
    if not raw:
        return mapping, [f"Empty {disp}"]
    if "\r" in raw:
        errors.append(f"{disp}: contains CRLF line endings (must be LF)")
    if not raw.endswith("\n"):
        errors.append(f"{disp}: missing trailing newline")

    keys_in_order: list[str] = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            errors.append(f"{disp}:{lineno}: blank line not allowed")
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            errors.append(
                f"{disp}:{lineno}: expected 2 tab-separated columns, got {len(parts)}: {line!r}"
            )
            continue
        inst, label = parts
        if inst != inst.strip() or label != label.strip():
            errors.append(f"{disp}:{lineno}: leading/trailing whitespace in {line!r}")
        if inst.endswith(".xz"):
            errors.append(f"{disp}:{lineno}: instance must strip .xz suffix: {inst!r}")
        if label not in VALID_LABELS:
            errors.append(
                f"{disp}:{lineno}: invalid verdict {label!r} (expected SAT|UNSAT|UNKNOWN)"
            )
            continue
        if inst in mapping:
            errors.append(f"{disp}:{lineno}: duplicate instance {inst!r}")
            continue
        mapping[inst] = label
        keys_in_order.append(inst)

    if keys_in_order != sorted(keys_in_order):
        errors.append(f"{disp}: rows are not sorted alphabetically by instance name")

    return mapping, errors


def get_collection_orig_entries(col_dir: Path) -> tuple[str | None, list[str], list[str]]:
    """Return ``(kind, expected_keys_without_xz, errors)``."""
    errors: list[str] = []
    orig_found = [d for d in ORIG_DIRS if (col_dir / d).is_dir()]
    if len(orig_found) > 1:
        errors.append(f"{col_dir.name}: multiple *-orig dirs found: {orig_found}")

    if orig_found:
        od_name = orig_found[0]
        od = col_dir / od_name
        od_str = str(od)
        keys: list[str] = []
        for dirpath, _dirnames, filenames in os.walk(od_str):
            rel_dir = "" if dirpath == od_str else os.path.relpath(dirpath, od_str).replace("\\", "/")
            for fn in filenames:
                rel = f"{rel_dir}/{fn}" if rel_dir else fn
                if not rel.endswith(".xz"):
                    errors.append(f"{col_dir.name}/{od_name}/{rel}: uncompressed benchmark file (expected .xz)")
                    continue
                keys.append(rel[:-3])
        keys.sort()
        return od_name, keys, errors

    if col_dir.name in ARCHIVE_ONLY_URI_COLLECTIONS:
        return "archive-uri", [], errors

    # Instance-level URI manifest collection (e.g. sat-competition-2002-2026-uris/uris/*.uri)
    uri_files = sorted(col_dir.rglob("*.uri"))
    if uri_files:
        hashes: set[str] = set()
        for uf in uri_files:
            for line in uf.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                tail = s.rsplit("/", 1)[-1]
                h = tail.split("-", 1)[0].split(".", 1)[0]
                hashes.add(f"{h}.cnf")
        return "instance-uri", sorted(hashes), errors

    errors.append(f"{col_dir.name}: neither *-orig/ directory nor *.uri manifest found")
    return None, [], errors


def load_format_exclusions_tsv(
    tsv_path: Path,
    repo_root: Path = REPO_ROOT,
) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Parse and strictly validate an optional ``format_exclusions.tsv`` manifest.

    Format: strict 3-column TSV, no header, LF line endings, trailing newline,
    sorted alphabetically by ``(converted_dir, rel_stem)``:

        <converted_dir>\\t<rel_stem>\\t<reason>
    """
    errors: list[str] = []
    exclusions: dict[str, dict[str, str]] = defaultdict(dict)
    if not tsv_path.exists():
        return exclusions, errors

    try:
        disp = str(tsv_path.relative_to(repo_root))
    except ValueError:
        disp = str(tsv_path)

    raw = tsv_path.read_text(encoding="utf-8")
    if not raw:
        return exclusions, [f"Empty {disp}"]
    if "\r" in raw:
        errors.append(f"{disp}: contains CRLF line endings (must be LF)")
    if not raw.endswith("\n"):
        errors.append(f"{disp}: missing trailing newline")

    keys_in_order: list[tuple[str, str]] = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            errors.append(f"{disp}:{lineno}: blank line not allowed")
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            errors.append(
                f"{disp}:{lineno}: expected 3 tab-separated columns (<conv_dir>, <rel_stem>, <reason>), got {len(parts)}"
            )
            continue
        conv_dir, rel_stem, reason = parts
        if conv_dir != conv_dir.strip() or rel_stem != rel_stem.strip() or reason != reason.strip():
            errors.append(f"{disp}:{lineno}: leading/trailing whitespace in {line!r}")
        if conv_dir not in CONV_DIRS:
            errors.append(f"{disp}:{lineno}: invalid converted dir {conv_dir!r} (expected one of {CONV_DIRS})")
            continue
        if not rel_stem or strip_rel_exts(rel_stem) != rel_stem:
            errors.append(f"{disp}:{lineno}: stem must omit benchmark/compression extensions: {rel_stem!r}")
            continue
        if not reason:
            errors.append(f"{disp}:{lineno}: missing exclusion reason for {conv_dir}/{rel_stem}")
            continue
        if rel_stem in exclusions[conv_dir]:
            errors.append(f"{disp}:{lineno}: duplicate exclusion ({conv_dir}, {rel_stem})")
            continue
        exclusions[conv_dir][rel_stem] = reason
        keys_in_order.append((conv_dir, rel_stem))

    if keys_in_order != sorted(keys_in_order):
        errors.append(f"{disp}: rows are not sorted alphabetically by (converted_dir, rel_stem)")

    return exclusions, errors


def build_stem_index(
    all_expected: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, tuple[str, str]]], dict[str, list[tuple[str, str, str]]]]:
    """Build per-collection and global stem -> (inst_no_xz, verdict) indices.

    Supports both flat names (``foo.cnf``, ``foo``) and recursive relative paths
    (``A067782/sortnet_n11_d7.cnf``, ``A067782/sortnet_n11_d7``, plus unique basenames).
    """
    by_col: dict[str, dict[str, tuple[str, str]]] = {}
    global_idx: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    for col, mapping in all_expected.items():
        cm: dict[str, tuple[str, str]] = {}
        base_counts: dict[str, int] = defaultdict(int)
        base_stem_counts: dict[str, int] = defaultdict(int)
        # Precompute (inst, rst, bn, bst) once per entry using fast string ops
        parsed: list[tuple[str, str, str, str, str]] = []
        for inst, label in mapping.items():
            rst = strip_rel_exts(inst)
            bn = inst.rsplit("/", 1)[-1] if "/" in inst else inst
            bst = strip_all_exts(bn)
            base_counts[bn] += 1
            base_stem_counts[bst] += 1
            parsed.append((inst, label, rst, bn, bst))

        for inst, label, rst, bn, bst in parsed:
            pair = (inst, label)
            cm[inst] = pair
            cm[rst] = pair
            if base_counts[bn] == 1:
                cm[bn] = pair
            if base_stem_counts[bst] == 1:
                cm[bst] = pair

            entry = (col, inst, label)
            global_idx[inst].append(entry)
            if rst != inst:
                global_idx[rst].append(entry)
            if bn != inst and bn != rst:
                global_idx[bn].append(entry)
            if bst != inst and bst != rst and bst != bn:
                global_idx[bst].append(entry)
        by_col[col] = cm
    return by_col, global_idx


def standalone_main(check_module: Any) -> int:
    """Generic standalone CLI entrypoint for any ``src/checks/check_*.py`` module."""
    ap = argparse.ArgumentParser(description=getattr(check_module, "DESCRIPTION", check_module.CHECK_NAME))
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Path to SAT-benchmarks repository root")
    ap.add_argument("--collection", action="append", help="Limit check to specific collection(s) (repeatable)")
    ap.add_argument("--changed", action="store_true", help="Check only collections modified/untracked in git status")
    ap.add_argument("--exclude", action="append", default=[], help="Exclude collection glob pattern(s) (repeatable)")
    ap.add_argument("--jobs", type=int, default=default_jobs(), help="Parallel worker count (default: min(4, cpu_count))")
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Directory with cached frobenius JSONs")
    ap.add_argument("--skip-cache", action="store_true", help="Skip cross-checking cached JSON files")
    ap.add_argument("--strict-legacy-cache", action="store_true", help="Fail on legacy pre-commit cache artifacts")
    args = ap.parse_args()

    repo_root = args.repo_root.resolve()
    root_readme_changed = False
    only = list(args.collection) if args.collection else None
    if args.changed:
        changed_cols, root_readme_changed = detect_changed_collections(repo_root)
        if only:
            only = sorted(set(only) | set(changed_cols))
        else:
            only = changed_cols
        if not only and not root_readme_changed:
            print(f"[{check_module.CHECK_NAME}] No changed collections detected (0 errors).")
            return 0

    cols = discover_collections(repo_root, only=only, excludes=args.exclude) if (only is None or only) else []
    is_full_repo = (not args.collection) and (not args.changed) and (not args.exclude)
    include_root = is_full_repo or root_readme_changed

    with CheckContext(
        repo_root=repo_root,
        collections=cols,
        is_full_repo=is_full_repo,
        include_root_readme=include_root,
        check_hygiene=True,
        cache_dir=args.cache_dir,
        skip_cache=args.skip_cache,
        strict_legacy_cache=args.strict_legacy_cache,
        jobs=max(1, args.jobs),
    ) as ctx:
        t0 = time.perf_counter()
        res: CheckResult = check_module.run(ctx)
        res.duration_s = time.perf_counter() - t0

    status = "PASS" if res.ok else "FAIL"
    print(f"[{res.name}] {status}: {len(cols)} collection(s), {len(res.errors)} error(s) ({res.duration_s:.3f}s)")
    for n in res.notes:
        print(f"  {n}")
    if res.errors:
        for e in res.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    return 0
