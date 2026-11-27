#!/usr/bin/env python3
"""Check GFM MathJax hygiene, GFM table structure, @tavisrudd spelling, and solver name/version formatting."""
from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.common import CheckContext, CheckResult, standalone_main

CHECK_NAME = "math_hygiene"
CHECK_ORDER = 50
REQUIRES_HYGIENE_FLAG = True
DESCRIPTION = "Validate GFM MathJax escaping/underscore/star hygiene, GFM tables, handle spelling, and solver formatting"

# Pre-compiled regexes for fast parallel Markdown scanning
_MATH_INLINE_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)(?<!\$)\$(?!\$)")
_CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")
_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_SEP_CELL_RE = re.compile(r"^:?-+:?$")
_SEP_LINE_RE = re.compile(r"^\s*\|[\s:\-\|]+\|\s*$")
_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")

_TRAVIS_RE = re.compile("tr" + "avisrudd", re.I)
_CMS_VERSION_RE = re.compile(r"CryptoMiniSat(?:\]\([^)]+\))?\s+5\.18(?!\.0)")
_INLINE_CODE_STRIP_RE = re.compile(r"`[^`\n]*`")
_MATH_ANY_RE = re.compile(
    r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<!\\)\$(?!\s)([^$\n]+?)(?<!\s)(?<!\\)\$",
    re.S,
)
_CURRENCY_RE = re.compile(r"^\d")
_MATH_OP_RE = re.compile(r"[\\^_{}=<>+\-*/]")
_GFM_UNSAFE_ESCAPE_RE = re.compile(r"\\([;,:!_%{}|])")
_TEX_TEXT_CMD_RE = re.compile(r"\\(?:text|texttt|textbf|textit|mbox)\{([^{}]*)\}")
_DOUBLE_SUBSCRIPT_RE = re.compile(r"\}_\{")
_ITALIC_TABLE_MATH_RE = re.compile(r"\*\([^*\n]*\$[^$\n]+\$[^*\n]*\)\*")
_BACKTICK_RE = re.compile(r"`([^`]+)`")
_SOLVER_WORD_RE = re.compile(
    r"\b(frobenius|cadical|kissat|cryptominisat\d*|dense-solver|probsat|satsuma|lymphosat)\b",
    re.I,
)

_ALLOWED_BACKTICKED_COLLECTION_TOKENS = frozenset({
    "dense-solver-public",
    "dense-solver-synthetic",
    "dense-solver-synthetic-chessboard",
    "dense-solver-synthetic-php",
    "f2-frobenius-circulants",
    "frobenius-challenge-v2",
})
_ALLOWED_FILE_SUFFIXES = (
    ".py",
    ".c",
    ".rs",
    ".xz",
    ".cnf",
    ".aig",
    ".xcnf",
    ".anf",
    ".mata",
    ".json",
    ".tsv",
    ".csv",
    ".uri",
    ".gz",
    ".md",
)


def split_gfm_table_cells(line: str) -> list[str]:
    """Split a GFM Markdown table row on unescaped '|', stripping optional outer pipes."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells: list[str] = []
    cur: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n and s[i + 1] == "|":
            cur.append("\\|")
            i += 2
        elif ch == "|":
            cells.append("".join(cur).strip())
            cur = []
            i += 1
        else:
            cur.append(ch)
            i += 1
    cells.append("".join(cur).strip())
    return cells


def is_gfm_separator_row(line: str) -> bool:
    s = line.strip()
    if "|" not in s:
        return False
    cells = split_gfm_table_cells(s)
    return bool(cells) and all(_SEP_CELL_RE.match(c) for c in cells)


def validate_gfm_tables(md: Path, repo_root: Path, text: str | None = None) -> list[str]:
    """Strictly validate every GFM Markdown table in ``md``.

    Catches:
      - Any '|' inside inline math ``$...$`` on a table row (use ``\\lvert...\\rvert``,
        ``\\mid``, or ``\\lVert...\\rVert`` so GitHub GFM never splits the cell).
      - Unescaped '|' inside backtick code spans or Markdown links on a table row.
      - Header vs. separator vs. body column-count mismatches.
      - Orphan or malformed separator rows.
      - Missing blank lines immediately before or after a table.
    """
    errors: list[str] = []
    rel = str(md.relative_to(repo_root))
    raw = text if text is not None else md.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    in_fence = False
    fence_char = ""
    fence_len = 0
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        fm = _FENCE_RE.match(line)
        if fm:
            marker = fm.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                in_fence = False
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        if "|" in line and i + 1 < n and is_gfm_separator_row(lines[i + 1]):
            hdr_cells = split_gfm_table_cells(line)
            sep_cells = split_gfm_table_cells(lines[i + 1])

            if i > 0 and lines[i - 1].strip() != "" and not lines[i - 1].strip().startswith("<!--"):
                errors.append(f"GFM table at {rel}:{i + 1}: missing blank line before table")

            if len(hdr_cells) != len(sep_cells):
                errors.append(
                    f"GFM table at {rel}:{i + 1}: header/separator column count mismatch "
                    f"(header={len(hdr_cells)}, separator={len(sep_cells)})"
                )

            j = i
            while j < n and lines[j].strip().startswith("|"):
                row = lines[j]
                if j >= i + 2:
                    body_cells = split_gfm_table_cells(row)
                    if len(body_cells) != len(sep_cells):
                        errors.append(
                            f"GFM table at {rel}:{j + 1}: row column count mismatch "
                            f"(row={len(body_cells)}, separator={len(sep_cells)})"
                        )
                if j != i + 1:
                    if "$" in row:
                        for m in _MATH_INLINE_RE.finditer(row):
                            if "|" in m.group(1):
                                errors.append(
                                    f"GFM table at {rel}:{j + 1}: '|' inside inline math `${m.group(1)}$` "
                                    "(use \\lvert...\\rvert, \\mid, or \\lVert...\\rVert)"
                                )
                    if "`" in row:
                        for m in _CODE_SPAN_RE.finditer(row):
                            if _UNESCAPED_PIPE_RE.search(m.group(1)):
                                errors.append(
                                    f"GFM table at {rel}:{j + 1}: unescaped '|' inside code span `{m.group(1)}`"
                                )
                    if "](" in row:
                        for m in _LINK_RE.finditer(row):
                            if _UNESCAPED_PIPE_RE.search(m.group(1)) or _UNESCAPED_PIPE_RE.search(m.group(2)):
                                errors.append(
                                    f"GFM table at {rel}:{j + 1}: unescaped '|' inside Markdown link `{m.group(0)}`"
                                )
                j += 1

            if j < n and lines[j].strip() != "" and not lines[j].strip().startswith("<!--"):
                errors.append(f"GFM table ending at {rel}:{j}: missing blank line after table")

            i = j
            continue

        # Flag orphan or malformed separator rows (e.g. missing dashes or detached from a header)
        if line.strip().startswith("|") and _SEP_LINE_RE.match(line):
            errors.append(f"GFM table at {rel}:{i + 1}: orphan or malformed separator row `{line.strip()[:80]}`")

        i += 1

    return errors


def audit_markdown_hygiene(md: Path, repo_root: Path, text: str | None = None) -> list[str]:
    """Audit GFM MathJax, GFM tables, handle spelling, and solver formatting in a single Markdown file."""
    errors: list[str] = []
    rel = str(md.relative_to(repo_root))
    raw = text if text is not None else md.read_text(encoding="utf-8", errors="replace")

    if _TRAVIS_RE.search(raw):
        errors.append(f"Misspelled '@tavisrudd' handle in {rel}")
    if _CMS_VERSION_RE.search(raw):
        errors.append(f"Inconsistent version 'CryptoMiniSat 5.18' (missing .0) in {rel}")

    errors.extend(validate_gfm_tables(md, repo_root, text=raw))

    # GFM MathJax hygiene: catch backslash-punctuation escapes stripped by cmark-gfm before MathJax
    # (\; \, \: \! \_ \% \{ \} \|), unescaped _/^ inside \text{...}, and raw * inside inline math.
    in_fence = False
    cleaned_lines: list[str] = []
    for raw_line in raw.splitlines(True):
        if raw_line.strip().startswith("```"):
            in_fence = not in_fence
            cleaned_lines.append("\n")
        elif in_fence:
            cleaned_lines.append("\n")
        else:
            cleaned_lines.append(raw_line)
    body_nc = _INLINE_CODE_STRIP_RE.sub(lambda m: " " * len(m.group(0)), "".join(cleaned_lines))

    if "$" in body_nc:
        for mm in _MATH_ANY_RE.finditer(body_nc):
            is_disp = mm.group(1) is not None
            expr = mm.group(1) if is_disp else mm.group(2)
            if not is_disp and _CURRENCY_RE.match(expr) and not _MATH_OP_RE.search(expr):
                continue
            mln = body_nc.count("\n", 0, mm.start()) + 1
            for pm in _GFM_UNSAFE_ESCAPE_RE.finditer(expr):
                errors.append(
                    f"GFM-unsafe math escape '{pm.group(0)}' in {rel}:{mln} "
                    "(use alphabetic TeX macro or \\text{ ...})"
                )
            for tm in _TEX_TEXT_CMD_RE.finditer(expr):
                if "_" in tm.group(1) or "^" in tm.group(1):
                    errors.append(f"Unescaped _/^ inside {tm.group(0)} in {rel}:{mln}")
            if not is_disp and "*" in expr:
                errors.append(f"Raw '*' in inline math (GFM italic hazard; use \\ast) in {rel}:{mln}")
            if expr.count("{") != expr.count("}"):
                errors.append(f"Unbalanced braces in math expression in {rel}:{mln}")

    for mln, raw_line in enumerate(body_nc.splitlines(), 1):
        if "}_{" in raw_line and len(_DOUBLE_SUBSCRIPT_RE.findall(raw_line)) >= 2:
            errors.append(
                f"Multiple '}}_{{' on same line (GFM emphasis hazard; move subscript inside \\mathrm{{...}}) in {rel}:{mln}"
            )
        if raw_line.lstrip().startswith("|") and "$" in raw_line and _ITALIC_TABLE_MATH_RE.search(raw_line):
            errors.append(f"Inline $...$ inside italicized table parenthesis *(...)* in {rel}:{mln}")

    for lineno, line in enumerate(raw.splitlines(), 1):
        if "`" not in line:
            continue
        for m in _BACKTICK_RE.finditer(line):
            tok = m.group(1)
            if not _SOLVER_WORD_RE.search(tok):
                continue
            if (
                "/" in tok
                or "_" in tok
                or tok.startswith(("--", "./"))
                or tok.endswith(_ALLOWED_FILE_SUFFIXES)
                or tok in _ALLOWED_BACKTICKED_COLLECTION_TOKENS
            ):
                continue
            errors.append(f"Backticked solver name `{tok}` in {rel}:{lineno}")

    return errors


def _audit_md_worker(args: tuple[Path, Path]) -> list[str]:
    md, repo_root = args
    return audit_markdown_hygiene(md, repo_root)


def run(ctx: CheckContext) -> CheckResult:
    """Audit GFM MathJax, GFM tables, handle spelling, and solver formatting across READMEs."""
    targets: list[Path] = []
    for c in ctx.collections:
        md = ctx.repo_root / c / "README.md"
        if md.exists():
            targets.append(md)
    if ctx.include_root_readme:
        root_md = ctx.repo_root / "README.md"
        if root_md.exists():
            targets.append(root_md)

    work = [(md, ctx.repo_root) for md in targets]
    errors: list[str] = []
    for md_errs in ctx.map_work(_audit_md_worker, work):
        errors.extend(md_errs)

    return CheckResult(
        name=CHECK_NAME,
        errors=errors,
        stats={"readmes_checked": len(targets)},
    )


if __name__ == "__main__":
    sys.exit(standalone_main(sys.modules[__name__]))
