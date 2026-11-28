#!/usr/bin/env python3
"""Check uniform 6-section README layout, zero benchmark files at collection root, diagram.svg + src/gen_diagram.py, and relative links."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.common import (
    ROOT_BENCHMARK_EXTS,
    CheckContext,
    CheckResult,
    standalone_main,
)

CHECK_NAME = "layout"
CHECK_ORDER = 40
REQUIRES_HYGIENE_FLAG = True
DESCRIPTION = "Validate uniform 6-section README layout, zero root benchmark files, diagram.svg + src/gen_diagram.py, and relative links"

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _check_relative_links(md: Path, repo_root: Path, text: str) -> list[str]:
    errors: list[str] = []
    rel = str(md.relative_to(repo_root))
    md_parent = md.parent
    for m in _LINK_RE.finditer(text):
        t = m.group(1).strip()
        if t.startswith(("http://", "https://", "mailto:", "#")):
            continue
        tp = t.split("#", 1)[0]
        if tp and not (md_parent / tp).resolve().exists():
            errors.append(f"Broken relative link in {rel}: {t}")
    return errors


def _layout_worker(args: tuple[str, Path]) -> list[str]:
    col, repo_root = args
    errors: list[str] = []
    col_dir = repo_root / col

    # 1. Zero benchmark files directly at collection root
    try:
        with os.scandir(col_dir) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith(ROOT_BENCHMARK_EXTS):
                    errors.append(
                        f"Layout violation in {col}: benchmark file at collection root ({col}/{entry.name})"
                    )
    except OSError as exc:
        errors.append(f"Cannot scan {col}: {exc}")
        return errors

    # 2. Required reproducible diagram + generator + README
    if not (col_dir / "diagram.svg").is_file():
        errors.append(f"Layout violation in {col}: missing diagram.svg")
    if not (col_dir / "src" / "gen_diagram.py").is_file():
        errors.append(f"Layout violation in {col}: missing src/gen_diagram.py")

    md = col_dir / "README.md"
    if not md.exists():
        errors.append(f"Layout violation in {col}: missing README.md")
        return errors

    text = md.read_text(encoding="utf-8", errors="replace")
    rel = f"{col}/README.md"
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        errors.append(f"README structure error in {rel}: line 1 must be H1 '# ...'")
    if len(lines) < 3 or not (lines[2].startswith("![") and "diagram.svg" in lines[2]):
        errors.append(
            f"README structure error in {rel}: figure '![...](diagram.svg)' must appear directly below title (line 3), above Provenance & Credit"
        )

    h2s = [line for line in lines if line.startswith("## ")]
    exp_analysis = (
        "## Automata Structural Analysis"
        if Path(col).name.startswith("mata-presburger-nfa-")
        else "## Phase-Transition & Structural Analysis"
    )
    exp_h2s = [
        "## Provenance & Credit",
        "## Problem Description",
        "## Corpus & Data Sizes",
        "## Benchmark Results",
        exp_analysis,
        "## References",
    ]
    if h2s != exp_h2s:
        errors.append(f"README section structure mismatch in {rel}: got {h2s}, expected {exp_h2s}")
    elif "## Provenance & Credit" in lines and "## Problem Description" in lines:
        pi = lines.index("## Provenance & Credit")
        pdi = lines.index("## Problem Description")
        top_b = [line for line in lines[pi + 1 : pdi] if line.startswith("- ")]
        rec_idxs = [i for i, b in enumerate(top_b) if "recommended by" in b.lower()]
        if rec_idxs and rec_idxs != [len(top_b) - 1]:
            errors.append(f"README Provenance error in {rel}: 'Recommended by' bullet must be last")

    # 3. Relative Markdown links
    errors.extend(_check_relative_links(md, repo_root, text))
    return errors


def audit_collection_layout(col: str, ctx: CheckContext) -> list[str]:
    """Validate directory layout, required files, 6-section README structure, and relative links for one collection."""
    return _layout_worker((col, ctx.repo_root))


def run(ctx: CheckContext) -> CheckResult:
    """Validate layout, diagram files, 6-section README structure, and relative links."""
    work = [(c, ctx.repo_root) for c in ctx.collections]
    errors: list[str] = []
    for col_errs in ctx.map_work(_layout_worker, work):
        errors.extend(col_errs)

    if ctx.include_root_readme:
        root_md = ctx.repo_root / "README.md"
        root_text = ctx.read_readme(root_md)
        if root_text is not None:
            errors.extend(_check_relative_links(root_md, ctx.repo_root, root_text))

    return CheckResult(
        name=CHECK_NAME,
        errors=errors,
        stats={"collections": len(ctx.collections)},
    )


if __name__ == "__main__":
    sys.exit(standalone_main(sys.modules[__name__]))
