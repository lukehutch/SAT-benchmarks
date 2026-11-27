#!/usr/bin/env python3
"""Check expected.tsv format, sorting, valid verdicts, 1-to-1 *-orig/ match, and root README.md counts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.common import CheckContext, CheckResult, standalone_main

CHECK_NAME = "expected"
CHECK_ORDER = 10
REQUIRES_HYGIENE_FLAG = False
DESCRIPTION = "Validate expected.tsv format, sorting, valid verdicts, 1-to-1 *-orig/ match, and root README.md counts"

ROOT_EXPECTED_SUMMARY_RE = re.compile(
    r"across \*\*(\d+)\s*/\s*(\d+)\*\* collections "
    r"\(\*\*([\d,]+) rows\*\*: `([\d,]+) SAT / ([\d,]+) UNSAT / ([\d,]+) UNKNOWN`\)"
)


def _check_root_readme_counts(
    ctx: CheckContext,
    total_cols: int,
    with_expected: int,
    tot_entries: int,
    tot_sat: int,
    tot_unsat: int,
    tot_unk: int,
) -> list[str]:
    """Verify root README.md expected.tsv summary counts match actual repository totals."""
    root_md = ctx.repo_root / "README.md"
    text = ctx.read_readme(root_md)
    if text is None:
        return []
    m = ROOT_EXPECTED_SUMMARY_RE.search(text)
    if not m:
        return []
    r_with, r_total, r_rows, r_sat, r_unsat, r_unk = (int(g.replace(",", "")) for g in m.groups())
    errors: list[str] = []
    if (r_with, r_total) != (with_expected, total_cols):
        errors.append(
            f"README.md expected.tsv collection count mismatch: "
            f"README says {r_with}/{r_total}, actual {with_expected}/{total_cols}"
        )
    if (r_rows, r_sat, r_unsat, r_unk) != (tot_entries, tot_sat, tot_unsat, tot_unk):
        errors.append(
            f"README.md expected.tsv row count mismatch: "
            f"README says {r_rows} ({r_sat} SAT / {r_unsat} UNSAT / {r_unk} UNKNOWN), "
            f"actual {tot_entries} ({tot_sat} SAT / {tot_unsat} UNSAT / {tot_unk} UNKNOWN)"
        )
    return errors


def run(ctx: CheckContext) -> CheckResult:
    """Validate expected.tsv manifests and 1-to-1 coverage against *-orig/."""
    ctx.ensure_expected()
    errors: list[str] = []

    for c in ctx.collections:
        kind, orig_keys, k_errs = ctx.orig_entries[c]
        errors.extend(k_errs)
        if kind is None or kind == "archive-uri":
            continue

        errors.extend(ctx.expected_errors.get(c, []))
        mapping = ctx.all_expected.get(c, {})
        orig_set = set(orig_keys)
        tsv_set = set(mapping.keys())
        missing = sorted(orig_set - tsv_set)
        extra = sorted(tsv_set - orig_set)
        if missing:
            errors.append(f"{c}/expected.tsv: missing {len(missing)} instance(s) from {kind}: {missing[:5]}")
        if extra:
            errors.append(f"{c}/expected.tsv: {len(extra)} extra instance(s) not in {kind}: {extra[:5]}")

    tot_entries = sum(len(m) for m in ctx.all_expected.values())
    tot_sat = sum(1 for m in ctx.all_expected.values() for v in m.values() if v == "SAT")
    tot_unsat = sum(1 for m in ctx.all_expected.values() for v in m.values() if v == "UNSAT")
    tot_unk = sum(1 for m in ctx.all_expected.values() for v in m.values() if v == "UNKNOWN")

    if ctx.is_full_repo:
        errors.extend(
            _check_root_readme_counts(
                ctx,
                total_cols=len(ctx.collections),
                with_expected=len(ctx.all_expected),
                tot_entries=tot_entries,
                tot_sat=tot_sat,
                tot_unsat=tot_unsat,
                tot_unk=tot_unk,
            )
        )

    return CheckResult(
        name=CHECK_NAME,
        errors=errors,
        stats={
            "collections": len(ctx.collections),
            "with_expected": len(ctx.all_expected),
            "total_rows": tot_entries,
            "sat": tot_sat,
            "unsat": tot_unsat,
            "unknown": tot_unk,
        },
    )


if __name__ == "__main__":
    sys.exit(standalone_main(sys.modules[__name__]))
