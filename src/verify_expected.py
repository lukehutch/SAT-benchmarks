#!/usr/bin/env python3
"""Programmatic Ground-Truth Verdict & Repository Verifier for SAT Benchmarks.

Thin CLI orchestrator over modular checks in ``src/checks/``:
  - ``checks/check_expected.py``     — ``expected.tsv`` format, sorting, 1-to-1 ``*-orig/`` match, root README counts
  - ``checks/check_formats.py``      — ``*-converted/`` 4-format completeness, ``format_exclusions.tsv``, ``< 95 MB`` limit
  - ``checks/check_verdicts.py``     — README verdict parity vs ``expected.tsv``, solvers-in-columns convention, cache/live runs
  - ``checks/check_layout.py``       — uniform 6-section README layout, zero root benchmark files, ``diagram.svg`` + ``src/gen_diagram.py``
  - ``checks/check_math_hygiene.py`` — GFM MathJax escaping/underscore/star hygiene, GFM tables, handle & solver formatting

Modes:
  1. Full or incremental repository verification:
       python3 src/verify_expected.py [--check-hygiene] [--jobs N]
       python3 src/verify_expected.py --collection rsa-ntt-factoring --check-hygiene
       python3 src/verify_expected.py --collection rsa-ntt-factoring --check math_hygiene
       python3 src/verify_expected.py --changed --check-hygiene
       python3 src/verify_expected.py --exclude 'guillochon-*' --exclude 'davies-*'

  2. Live solver-run verification:
       python3 src/verify_expected.py --check-run path/to/results.json
       python3 src/verify_expected.py --check-run path/to/run_logs_dir/ [--collection <name>]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from checks import discover_checks, select_checks
from checks.check_expected import run as run_check_expected
from checks.check_formats import run as run_check_formats
from checks.check_layout import run as run_check_layout
from checks.check_math_hygiene import (
    is_gfm_separator_row,
    run as run_check_math_hygiene,
    split_gfm_table_cells,
    validate_gfm_tables,
)
from checks.check_verdicts import (
    check_live_run,
    cross_check_cache_jsons,
    cross_check_readmes,
)
from checks.common import (
    ARCHIVE_ONLY_URI_COLLECTIONS,
    CONV_DIRS,
    DEFAULT_CACHE_DIR,
    KNOWN_PRECOMMIT_CACHE_ARTIFACTS,
    LEGACY_COLLECTION_MAP,
    MAX_GITHUB_FILE_BYTES,
    ORIG_DIRS,
    REPO_ROOT,
    SAT_EXTS,
    VALID_LABELS,
    CheckContext,
    CheckResult,
    build_stem_index,
    default_jobs,
    detect_changed_collections,
    discover_collections,
    get_collection_orig_entries,
    load_expected_tsv,
    load_format_exclusions_tsv,
    norm_verdict,
    strip_all_exts,
    strip_rel_exts,
)

__all__ = [
    "ARCHIVE_ONLY_URI_COLLECTIONS",
    "CONV_DIRS",
    "DEFAULT_CACHE_DIR",
    "KNOWN_PRECOMMIT_CACHE_ARTIFACTS",
    "LEGACY_COLLECTION_MAP",
    "MAX_GITHUB_FILE_BYTES",
    "ORIG_DIRS",
    "REPO_ROOT",
    "SAT_EXTS",
    "VALID_LABELS",
    "build_stem_index",
    "check_hygiene",
    "check_live_run",
    "cross_check_cache_jsons",
    "cross_check_readmes",
    "detect_changed_collections",
    "discover_collections",
    "get_collection_orig_entries",
    "is_gfm_separator_row",
    "load_expected_tsv",
    "load_format_exclusions_tsv",
    "norm_verdict",
    "split_gfm_table_cells",
    "strip_all_exts",
    "strip_rel_exts",
    "validate_collections",
    "validate_gfm_tables",
]


def validate_collections(
    repo_root: Path,
    cols: list[str],
    jobs: int = 1,
) -> tuple[dict[str, dict[str, str]], dict[str, str], list[str], list[str]]:
    """Backward-compatible wrapper validating expected.tsv coverage and 4-format parity."""
    with CheckContext(
        repo_root=repo_root,
        collections=cols,
        is_full_repo=False,
        include_root_readme=False,
        check_hygiene=False,
        jobs=jobs,
    ) as ctx:
        exp_res = run_check_expected(ctx)
        fmt_res = run_check_formats(ctx)
        return ctx.all_expected, ctx.col_kinds, exp_res.errors + fmt_res.errors, exp_res.notes + fmt_res.notes


def check_hygiene(repo_root: Path, cols: list[str], jobs: int = 1) -> list[str]:
    """Backward-compatible wrapper auditing compression, <95 MB sizes, layout, links, and GFM MathJax."""
    with CheckContext(
        repo_root=repo_root,
        collections=cols,
        is_full_repo=False,
        include_root_readme=True,
        check_hygiene=True,
        jobs=jobs,
    ) as ctx:
        fmt_res = run_check_formats(ctx)
        lay_res = run_check_layout(ctx)
        math_res = run_check_math_hygiene(ctx)
        # Return only hygiene-category errors from formats + all layout & math_hygiene errors
        hyg_count = fmt_res.stats.get("hygiene_errors", 0)
        fmt_hyg = fmt_res.errors[-hyg_count:] if hyg_count else []
        return fmt_hyg + lay_res.errors + math_res.errors


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Verify expected.tsv manifests, formats, verdicts, and repository hygiene.")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Path to SAT-benchmarks repository root")
    ap.add_argument("--collection", action="append", help="Limit check to specific collection(s) (repeatable)")
    ap.add_argument(
        "--changed",
        action="store_true",
        help="Auto-detect modified/untracked collections from 'git status --porcelain' and check only those",
    )
    ap.add_argument("--exclude", action="append", default=[], help="Exclude collection glob pattern(s) (repeatable)")
    ap.add_argument(
        "--check",
        action="append",
        help="Comma-separated subset of modular checks to run (e.g. expected,formats,verdicts,layout,math_hygiene or all)",
    )
    ap.add_argument("--list-checks", action="store_true", help="List available modular checks in src/checks/ and exit")
    ap.add_argument(
        "--jobs",
        type=int,
        default=default_jobs(),
        help="Parallel worker count for per-collection checks (default: min(4, cpu_count))",
    )
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Directory with cached frobenius JSONs")
    ap.add_argument("--skip-cache", action="store_true", help="Skip cross-checking cached JSON files")
    ap.add_argument("--strict-legacy-cache", action="store_true", help="Fail even on documented pre-commit cache artifacts")
    ap.add_argument("--check-hygiene", action="store_true", help="Also verify layout, compression, <95 MB limit, links, and GFM MathJax")
    ap.add_argument(
        "--check-run",
        type=Path,
        default=None,
        help="Verify a live solver run JSON, TSV/CSV, or output directory against expected.tsv",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    if args.list_checks:
        for mod in discover_checks():
            tag = "hygiene" if getattr(mod, "REQUIRES_HYGIENE_FLAG", False) else "core"
            desc = getattr(mod, "DESCRIPTION", "")
            print(f"  {mod.CHECK_NAME:<14} [{tag:<7}]  {desc}")
        return 0

    repo_root = args.repo_root.resolve()
    jobs = max(1, args.jobs)

    # Resolve target collection list
    root_readme_changed = False
    only: list[str] | None = [c.rstrip("/") for c in args.collection] if args.collection else None
    if args.changed:
        changed_cols, root_readme_changed = detect_changed_collections(repo_root)
        if only is not None:
            only = sorted(set(only) | set(changed_cols))
        else:
            only = changed_cols
        if not only and not root_readme_changed and args.check_run is None:
            print("No changed collections detected via git status --porcelain.")
            print("\nALL CHECKS PASSED (0 errors, 0 verdict mismatches).")
            return 0

    cols = discover_collections(repo_root, only=only, excludes=args.exclude) if (only is None or only) else []
    is_full_repo = (not args.collection) and (not args.changed) and (not args.exclude)
    include_root_readme = is_full_repo or root_readme_changed

    # Mode 2: Live run verification
    if args.check_run is not None:
        with CheckContext(
            repo_root=repo_root,
            collections=cols,
            is_full_repo=False,
            include_root_readme=False,
            check_hygiene=False,
            jobs=jobs,
        ) as ctx:
            exp_res = run_check_expected(ctx)
            fmt_res = run_check_formats(ctx)
            struct_errors = exp_res.errors + fmt_res.errors
            if struct_errors:
                print(f"WARNING: {len(struct_errors)} expected.tsv structural error(s) in repo.", file=sys.stderr)
            restrict = args.collection[0].rstrip("/") if args.collection and len(args.collection) == 1 else None
            checked, agreed, newly_solved, mismatches, warnings = check_live_run(
                args.check_run, ctx.by_col, ctx.global_idx, restrict_col=restrict
            )
        print(f"Live run check ({args.check_run}):")
        print(f"  Verdicts checked : {checked}")
        print(f"  Agreed           : {agreed}")
        print(f"  Solved UNKNOWNs  : {newly_solved}")
        print(f"  Mismatches       : {len(mismatches)}")
        for w in warnings[:20]:
            print(f"  [INFO] {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more info/warning lines")
        for m in mismatches:
            print(f"  [FAIL] {m}", file=sys.stderr)
        return 1 if mismatches else 0

    # Mode 1: Modular repository verification
    try:
        selected = select_checks(args.check, check_hygiene=args.check_hygiene)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    explicit_subset = args.check is not None
    # Enable file-level hygiene inside formats when --check-hygiene is passed OR formats is explicitly requested
    effective_hygiene = args.check_hygiene or (explicit_subset and any(m.CHECK_NAME == "formats" for m in selected))

    with CheckContext(
        repo_root=repo_root,
        collections=cols,
        is_full_repo=is_full_repo,
        include_root_readme=include_root_readme,
        check_hygiene=effective_hygiene,
        cache_dir=args.cache_dir,
        skip_cache=args.skip_cache,
        strict_legacy_cache=args.strict_legacy_cache,
        jobs=jobs,
    ) as ctx:
        results: dict[str, CheckResult] = {}
        ordered_results: list[CheckResult] = []
        for mod in selected:
            t0 = time.perf_counter()
            res = mod.run(ctx)
            res.duration_s = time.perf_counter() - t0
            results[res.name] = res
            ordered_results.append(res)

    all_errors: list[str] = []
    all_notes: list[str] = []
    for res in ordered_results:
        all_errors.extend(res.errors)
        all_notes.extend(res.notes)

    # Backward-compatible summary output when standard checks run, plus concise per-check output for --check subsets
    if not explicit_subset:
        exp_stats = results["expected"].stats if "expected" in results else {}
        fmt_res = results.get("formats")
        verd_stats = results["verdicts"].stats if "verdicts" in results else {}
        struct_err_count = (
            len(results["expected"].errors) if "expected" in results else 0
        ) + (fmt_res.stats.get("format_errors", 0) if fmt_res else 0)
        hygiene_err_count = (
            (fmt_res.stats.get("hygiene_errors", 0) if fmt_res else 0)
            + (len(results["layout"].errors) if "layout" in results else 0)
            + (len(results["math_hygiene"].errors) if "math_hygiene" in results else 0)
        )
        # Include any custom plugin check errors beyond the built-in 5
        builtin_names = {"expected", "formats", "verdicts", "layout", "math_hygiene"}
        extra_checks = [r for r in ordered_results if r.name not in builtin_names]

        print(f"Collections inspected   : {len(cols)} ({exp_stats.get('with_expected', len(ctx.all_expected))} with expected.tsv)")
        print(
            f"Total expected.tsv rows : {exp_stats.get('total_rows', 0)} "
            f"(SAT={exp_stats.get('sat', 0)}, UNSAT={exp_stats.get('unsat', 0)}, UNKNOWN={exp_stats.get('unknown', 0)})"
        )
        print(f"Structural/1-to-1 errors: {struct_err_count}")
        print(
            f"README table verdicts   : {verd_stats.get('readme_checked', 0)} checked, "
            f"{verd_stats.get('readme_mismatches', 0)} mismatches"
        )
        if not args.skip_cache:
            print(
                f"Cache JSON verdicts     : {verd_stats.get('cache_checked', 0)} checked, "
                f"{verd_stats.get('cache_mismatches', 0)} mismatches"
            )
        if args.check_hygiene:
            print(f"Hygiene errors          : {hygiene_err_count}")
        for r in extra_checks:
            print(f"Check {r.name:<18}: {len(r.errors)} error(s) ({r.duration_s:.3f}s)")
    else:
        print(f"Collections inspected   : {len(cols)}")
        for r in ordered_results:
            status = "OK" if r.ok else "FAIL"
            print(f"Check {r.name:<18}: {status} ({len(r.errors)} error(s), {r.duration_s:.3f}s)")

    for n in all_notes:
        print(f"  {n}")

    if all_errors:
        print("\nERRORS:", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nALL CHECKS PASSED (0 errors, 0 verdict mismatches).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
