#!/usr/bin/env python3
"""Check *-converted/ 4-format completeness, format_exclusions.tsv, compression hygiene, and <95 MB limit."""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.common import (
    BAD_COMPRESSION_EXTS,
    CONV_DIRS,
    MAX_GITHUB_FILE_BYTES,
    CheckContext,
    CheckResult,
    load_format_exclusions_tsv,
    standalone_main,
    strip_rel_exts,
)

CHECK_NAME = "formats"
CHECK_ORDER = 20
REQUIRES_HYGIENE_FLAG = False
DESCRIPTION = "Validate *-converted/ 4-format completeness, format_exclusions.tsv, compression hygiene, and <95 MB GitHub limit"

SAT_FORMATS = ("aig", "cnf", "xcnf", "anf")


def _audit_collection_formats(
    col: str,
    repo_root: Path,
    kind: str | None,
    orig_keys: list[str],
    check_file_hygiene: bool,
) -> tuple[list[str], list[str], list[str]]:
    """Return ``(format_errors, hygiene_errors, notes)`` for a single collection."""
    col_dir = repo_root / col
    format_errors: list[str] = []
    hygiene_errors: list[str] = []
    notes: list[str] = []

    if kind in ("cnf-orig", "aig-orig", "xcnf-orig"):
        orig_fmt = kind.split("-", 1)[0]
        required_conv = tuple(f"{fmt}-converted" for fmt in SAT_FORMATS if fmt != orig_fmt)
        orig_stems = {strip_rel_exts(k) for k in orig_keys}

        excl_path = col_dir / "format_exclusions.tsv"
        exclusions, ex_errs = load_format_exclusions_tsv(excl_path, repo_root=repo_root)
        format_errors.extend(ex_errs)
        for cd_name, stem_map in exclusions.items():
            if not (col_dir / cd_name).is_dir():
                format_errors.append(f"{col}/format_exclusions.tsv: references missing directory {cd_name!r}")
            for st in sorted(stem_map):
                if st not in orig_stems:
                    format_errors.append(
                        f"{col}/format_exclusions.tsv: stem {st!r} for {cd_name} does not exist in {kind}"
                    )

        for cd_name in required_conv:
            if not (col_dir / cd_name).is_dir():
                format_errors.append(f"{col}: missing required 4-format directory {cd_name}/")

        for cd_name in CONV_DIRS:
            cd = col_dir / cd_name
            if not cd.is_dir():
                continue
            cd_str = str(cd)
            conv_stems: set[str] = set()
            for dirpath, _dirnames, filenames in os.walk(cd_str):
                rel_dir = "" if dirpath == cd_str else os.path.relpath(dirpath, cd_str).replace("\\", "/")
                for fn in filenames:
                    if fn.endswith(".xz"):
                        rel = f"{rel_dir}/{fn}" if rel_dir else fn
                        conv_stems.add(strip_rel_exts(rel))

            excl_stems = set(exclusions.get(cd_name, {}).keys())
            stale_excl = sorted(excl_stems & conv_stems)
            if stale_excl:
                format_errors.append(
                    f"{col}/format_exclusions.tsv: {cd_name} stem(s) are present on disk and should not be excluded: {stale_excl[:5]}"
                )
            expected_conv_stems = orig_stems - excl_stems
            if conv_stems != expected_conv_stems:
                m_c = sorted(expected_conv_stems - conv_stems)
                e_c = sorted(conv_stems - expected_conv_stems)
                format_errors.append(
                    f"{col}/{cd_name}: stem mismatch vs {kind} (missing={m_c[:3]}, extra={e_c[:3]})"
                )
            elif excl_stems:
                notes.append(
                    f"[format exclusion] {col}/{cd_name}: {len(excl_stems)} documented omission(s) via format_exclusions.tsv"
                )

    if check_file_hygiene:
        col_str = str(col_dir)
        for dirpath, dirnames, filenames in os.walk(col_str):
            if ".git" in dirnames:
                dirnames.remove(".git")
            rel_dir = "" if dirpath == col_str else os.path.relpath(dirpath, col_str).replace("\\", "/")
            in_src = rel_dir == "src" or rel_dir.startswith("src/")
            for fn in filenames:
                full_p = os.path.join(dirpath, fn)
                try:
                    sz = os.stat(full_p).st_size
                except OSError:
                    continue
                rel_from_repo = f"{col}/{rel_dir}/{fn}" if rel_dir else f"{col}/{fn}"
                if sz > MAX_GITHUB_FILE_BYTES:
                    sz_mb = sz / (1024 * 1024)
                    hygiene_errors.append(
                        f"GitHub file-size violation (>95 MB): {rel_from_repo} ({sz_mb:.2f} MB)"
                    )
                if not in_src and fn.endswith(BAD_COMPRESSION_EXTS):
                    hygiene_errors.append(f"Compression hygiene violation: {rel_from_repo}")

    return format_errors, hygiene_errors, notes


def _formats_worker(args: tuple[str, Path, str | None, list[str], bool]) -> tuple[list[str], list[str], list[str]]:
    return _audit_collection_formats(*args)


def run(ctx: CheckContext) -> CheckResult:
    """Run 4-format parity, format_exclusions.tsv, compression, and <95 MB size checks."""
    ctx.ensure_orig_entries()
    work = [
        (col, ctx.repo_root, ctx.orig_entries[col][0], ctx.orig_entries[col][1], ctx.check_hygiene)
        for col in ctx.collections
    ]
    results = ctx.map_work(_formats_worker, work)
    format_errors: list[str] = []
    hygiene_errors: list[str] = []
    notes: list[str] = []
    for f_errs, h_errs, col_notes in results:
        format_errors.extend(f_errs)
        hygiene_errors.extend(h_errs)
        notes.extend(col_notes)

    return CheckResult(
        name=CHECK_NAME,
        errors=format_errors + hygiene_errors,
        notes=notes,
        stats={
            "format_errors": len(format_errors),
            "hygiene_errors": len(hygiene_errors),
        },
    )


if __name__ == "__main__":
    sys.exit(standalone_main(sys.modules[__name__]))
