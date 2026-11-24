#!/usr/bin/env python3
"""Programmatic Ground-Truth Verdict Verifier for SAT Benchmarks.

Convention for ``expected.tsv`` (uniform across every collection):
  - Location: ``<collection>/expected.tsv`` (top-level inside the collection directory).
  - Format: Strict 2-column tab-separated file, NO header row, sorted alphabetically
    by column 1 (ASCII / Python ``sorted()``), UTF-8, LF line endings, trailing newline:

        <instance_without_.xz>\\t<SAT|UNSAT|UNKNOWN>

  - Column 1 naming:
      * File-backed collections (``cnf-orig/``, ``aig-orig/``, ``xcnf-orig/``, ``mata-orig/``):
        the exact relative POSIX path inside the primary ``*-orig/`` directory with the
        trailing ``.xz`` stripped (flat: ``foo.cnf``, ``bar.aig``, ``w5.solved.xcnf``,
        ``ARI056_1.mata``; nested: ``A067782/sortnet_n11_d7.cnf``), uniquely identifying
        the original instance regardless of format.
      * URI-manifest instance collections (e.g. ``sat-competition-2024-2026-main-track/``):
        ``<hash>.cnf`` matching every unique instance URI entry in ``*.uri``.
      * Archive-level ``.tar.gz`` URI catalogs (``satlib-archive-uris/``): no
        per-instance ``expected.tsv`` (its 331 committed instances live across the
        22 standalone ``satlib-*/`` collections, each with its own ``expected.tsv``).
  - Column 2 labels:
      * ``SAT``     — Proven satisfiable (verified model or constructive proof).
      * ``UNSAT``   — Proven unsatisfiable (verified refutation / formal proof / theorem).
      * ``UNKNOWN`` — Open or uncertified instance (never guessed).
      * For MATA NFA collections (``mata-orig/``), ``expected.tsv`` records the
        complementation / non-universality verdict (``SAT`` iff complement is non-empty,
        ``UNSAT`` iff L(A) = Sigma*, matching ``--mata-complement`` and
        ``--mata-explicit-complement``).

Modes:
  1. Repository verification (default):
       python3 src/verify_expected.py
       python3 src/verify_expected.py --collection knights-tour-obstacles
       python3 src/verify_expected.py --exclude 'guillochon-*' --exclude 'davies-*' --exclude 'vzhn-*'
     Validates:
       (a) Every collection's ``expected.tsv`` syntax, sorting, valid labels, and exact
           1-to-1 coverage against ``*-orig/**/*.xz`` (plus 4-format ``*-converted/`` parity,
           respecting any strictly validated ``format_exclusions.tsv`` manifest for files
           omitted due to GitHub's 95 MB per-file size limit).
       (b) Cross-checks ALL solver verdicts recorded in every collection's ``README.md``
           tables (and root ``README.md`` cross-product table) against ``expected.tsv``.
       (c) Cross-checks cached solver run JSONs in ``--cache-dir`` (default
           ``~/.cache/frobenius``: ``all_suites_8core.json``, ``gap_fill_8core.json``,
           ``shortcut_300s.json``, ``new_suites_bench.json``, ``shortcut_tier3_solo.json``)
           against ``expected.tsv``.
       (d) Optional ``--check-hygiene`` audits compression (0 ``.gz``/``.bz2``/uncompressed
           benchmark files), GitHub ``<= 95 MB`` per-file size limit, strict GFM Markdown tables
           (unescaped ``|`` in math/code/links, header/separator/body column counts, surrounding
           blank lines), solver name/version formatting, and relative Markdown links.

  2. Live solver-run verification:
       python3 src/verify_expected.py --check-run path/to/results.json
       python3 src/verify_expected.py --check-run path/to/run_logs_dir/ [--collection <name>]
     Verifies any JSON, TSV/CSV, or solver log directory against ``expected.tsv``,
     exiting non-zero if ANY verdict contradicts ground truth.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import lzma
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "frobenius"

VALID_LABELS = frozenset({"SAT", "UNSAT", "UNKNOWN"})
ORIG_DIRS = ("cnf-orig", "aig-orig", "xcnf-orig", "mata-orig")
CONV_DIRS = ("aig-converted", "cnf-converted", "xcnf-converted", "anf-converted")
SAT_EXTS = (".cnf.xz", ".aig.xz", ".xcnf.xz", ".anf.xz", ".mata.xz", ".cnf", ".aig", ".xcnf", ".anf", ".mata", ".xz")
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


def strip_all_exts(name: str) -> str:
    s = Path(name).name
    for ext in SAT_EXTS:
        if s.endswith(ext):
            s = s[: -len(ext)]
            break
    return s


def strip_rel_exts(rel_path: str) -> str:
    """Strip benchmark extension(s) while preserving any POSIX subdirectory prefix."""
    p = rel_path.replace("\\", "/")
    for ext in SAT_EXTS:
        if p.endswith(ext):
            p = p[: -len(ext)]
            break
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
    excludes = excludes or []
    cols: list[str] = []
    for entry in sorted(repo_root.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name == "src":
            continue
        if only and entry.name not in only:
            continue
        if any(fnmatch.fnmatch(entry.name, pat) for pat in excludes):
            continue
        cols.append(entry.name)
    return cols


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
    """Return (kind, expected_keys_without_xz, errors)."""
    errors: list[str] = []
    orig_found = [d for d in ORIG_DIRS if (col_dir / d).is_dir()]
    if len(orig_found) > 1:
        errors.append(f"{col_dir.name}: multiple *-orig dirs found: {orig_found}")

    if orig_found:
        od_name = orig_found[0]
        od = col_dir / od_name
        keys: list[str] = []
        for f in sorted(od.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(od).as_posix()
            if not rel.endswith(".xz"):
                errors.append(f"{col_dir.name}/{od_name}/{rel}: uncompressed benchmark file (expected .xz)")
                continue
            keys.append(rel[:-3])
        return od_name, sorted(keys), errors

    if col_dir.name in ARCHIVE_ONLY_URI_COLLECTIONS:
        return "archive-uri", [], errors

    # Instance-level URI manifest collection (e.g. sat-competition-2024-2026-main-track)
    uri_files = sorted(col_dir.glob("*.uri"))
    if uri_files:
        hashes: set[str] = set()
        for uf in uri_files:
            for line in uf.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                tail = s.rsplit("/", 1)[-1]
                h = tail.split("-")[0].split(".")[0]
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


def validate_collections(
    repo_root: Path,
    cols: list[str],
) -> tuple[dict[str, dict[str, str]], dict[str, str], list[str], list[str]]:
    """Validate expected.tsv coverage and 4-format parity across collections."""
    all_expected: dict[str, dict[str, str]] = {}
    col_kinds: dict[str, str] = {}
    errors: list[str] = []
    notes: list[str] = []

    for c in cols:
        col_dir = repo_root / c
        kind, orig_keys, k_errs = get_collection_orig_entries(col_dir)
        errors.extend(k_errs)
        if kind is None:
            continue
        col_kinds[c] = kind

        if kind == "archive-uri":
            continue

        tsv_path = col_dir / "expected.tsv"
        mapping, t_errs = load_expected_tsv(tsv_path, repo_root=repo_root)
        errors.extend(t_errs)
        all_expected[c] = mapping

        orig_set = set(orig_keys)
        tsv_set = set(mapping.keys())
        missing = sorted(orig_set - tsv_set)
        extra = sorted(tsv_set - orig_set)
        if missing:
            errors.append(f"{c}/expected.tsv: missing {len(missing)} instance(s) from {kind}: {missing[:5]}")
        if extra:
            errors.append(f"{c}/expected.tsv: {len(extra)} extra instance(s) not in {kind}: {extra[:5]}")

        # For SAT collections, also verify converted directories match orig relative stems 1-to-1,
        # honoring any strictly validated format_exclusions.tsv entries (e.g. >95 MB GitHub limit).
        if kind in ("cnf-orig", "aig-orig", "xcnf-orig"):
            orig_stems = {strip_rel_exts(k) for k in orig_keys}
            excl_path = col_dir / "format_exclusions.tsv"
            exclusions, ex_errs = load_format_exclusions_tsv(excl_path, repo_root=repo_root)
            errors.extend(ex_errs)
            for cd_name, stem_map in exclusions.items():
                if not (col_dir / cd_name).is_dir():
                    errors.append(f"{c}/format_exclusions.tsv: references missing directory {cd_name!r}")
                for st in sorted(stem_map):
                    if st not in orig_stems:
                        errors.append(
                            f"{c}/format_exclusions.tsv: stem {st!r} for {cd_name} does not exist in {kind}"
                        )
            for cd_name in CONV_DIRS:
                cd = col_dir / cd_name
                if not cd.is_dir():
                    continue
                conv_stems = {
                    strip_rel_exts(f.relative_to(cd).as_posix())
                    for f in cd.rglob("*")
                    if f.is_file() and f.name.endswith(".xz")
                }
                excl_stems = set(exclusions.get(cd_name, {}).keys())
                stale_excl = sorted(excl_stems & conv_stems)
                if stale_excl:
                    errors.append(
                        f"{c}/format_exclusions.tsv: {cd_name} stem(s) are present on disk and should not be excluded: {stale_excl[:5]}"
                    )
                expected_conv_stems = orig_stems - excl_stems
                if conv_stems != expected_conv_stems:
                    m_c = sorted(expected_conv_stems - conv_stems)
                    e_c = sorted(conv_stems - expected_conv_stems)
                    errors.append(
                        f"{c}/{cd_name}: stem mismatch vs {kind} (missing={m_c[:3]}, extra={e_c[:3]})"
                    )
                elif excl_stems:
                    notes.append(
                        f"[format exclusion] {c}/{cd_name}: {len(excl_stems)} documented omission(s) via format_exclusions.tsv"
                    )

    return all_expected, col_kinds, errors, notes


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
        for inst in mapping:
            base_counts[Path(inst).name] += 1
            base_stem_counts[strip_all_exts(inst)] += 1

        for inst, label in mapping.items():
            rst = strip_rel_exts(inst)
            bn = Path(inst).name
            bst = strip_all_exts(inst)
            cm[inst] = (inst, label)
            cm[rst] = (inst, label)
            if base_counts[bn] == 1:
                cm[bn] = (inst, label)
            if base_stem_counts[bst] == 1:
                cm[bst] = (inst, label)

            seen_g: set[str] = set()
            for key in (inst, rst, bn, bst):
                if key not in seen_g:
                    seen_g.add(key)
                    global_idx[key].append((col, inst, label))
        by_col[col] = cm
    return by_col, global_idx


def cross_check_readmes(
    repo_root: Path,
    cols: list[str],
    col_kinds: dict[str, str],
    by_col: dict[str, dict[str, tuple[str, str]]],
    global_idx: dict[str, list[tuple[str, str, str]]],
) -> tuple[int, list[str]]:
    """Cross-check every verdict cell in every collection README.md and root README.md."""
    checked = 0
    mismatches: list[str] = []

    for c in cols:
        if c not in by_col:
            continue
        md = repo_root / c / "README.md"
        if not md.exists():
            continue
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        cm = by_col[c]
        is_mata = col_kinds.get(c) == "mata-orig"

        i = 0
        while i < len(lines):
            line = lines[i]
            if (
                line.strip().startswith("|")
                and i + 1 < len(lines)
                and re.match(r"^\s*\|[\s:\-\|]+\|\s*$", lines[i + 1])
            ):
                hdr = [x.strip() for x in line.strip().strip("|").split("|")]
                verdict_col_idx: int | None = None
                for idx, h in enumerate(hdr):
                    hl = h.lower()
                    if is_mata:
                        if "complement verdict" in hl:
                            verdict_col_idx = idx
                            break
                    else:
                        if any(k in hl for k in ("verdict", "status", "ans", "expected")):
                            verdict_col_idx = idx
                            break
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    cells = [x.strip() for x in lines[j].strip().strip("|").split("|")]
                    if verdict_col_idx is not None and len(cells) > verdict_col_idx:
                        c0 = cells[0].strip("`* ")
                        tok0 = c0.split()[0].strip("`* ") if c0 else ""
                        hit = cm.get(tok0) or cm.get(strip_rel_exts(tok0)) or cm.get(strip_all_exts(tok0))
                        if hit is not None:
                            raw_v = re.sub(r"\*[^*]*\*", "", cells[verdict_col_idx]).replace("*", "").strip()
                            # Handle cells like "SAT *(known unique)*" -> "SAT"
                            first_word = raw_v.split()[0] if raw_v else ""
                            rv = norm_verdict(first_word) if first_word.upper() in ("SAT", "UNSAT") else None
                            if rv in ("SAT", "UNSAT"):
                                inst_key, exp_v = hit
                                checked += 1
                                if exp_v != rv:
                                    mismatches.append(
                                        f"README mismatch in {c}/README.md:{j+1} ({inst_key}): "
                                        f"README says {rv}, expected.tsv says {exp_v}"
                                    )
                    j += 1
                i = j
            else:
                i += 1

    # Also cross-check root README.md Section 6 cross-product parity table
    root_md = repo_root / "README.md"
    if root_md.exists():
        lines = root_md.read_text(encoding="utf-8", errors="replace").splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if (
                line.strip().startswith("| Origin | Benchmark | Verdict |")
                and i + 1 < len(lines)
                and re.match(r"^\s*\|[\s:\-\|]+\|\s*$", lines[i + 1])
            ):
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    cells = [x.strip() for x in lines[j].strip().strip("|").split("|")]
                    if len(cells) >= 3:
                        tok = cells[1].split()[0].strip("`* ")
                        st = strip_all_exts(tok)
                        rv = norm_verdict(cells[2])
                        matches = global_idx.get(st, [])
                        if rv in ("SAT", "UNSAT") and matches:
                            for col, inst_key, exp_v in matches:
                                checked += 1
                                if exp_v != rv:
                                    mismatches.append(
                                        f"Root README mismatch at README.md:{j+1} ({col}/{inst_key}): "
                                        f"README says {rv}, expected.tsv says {exp_v}"
                                    )
                    j += 1
                i = j
            else:
                i += 1

    return checked, mismatches


def cross_check_cache_jsons(
    cache_dir: Path,
    by_col: dict[str, dict[str, tuple[str, str]]],
    strict_legacy_cache: bool = False,
) -> tuple[int, list[str], list[str]]:
    """Cross-check cached solver JSONs in ~/.cache/frobenius against expected.tsv."""
    checked = 0
    mismatches: list[str] = []
    notes: list[str] = []

    def check_one(src_file: str, section: str, col: str, stem_or_name: str, solver: str, raw_v: object) -> None:
        nonlocal checked
        rv = norm_verdict(raw_v)
        if rv not in ("SAT", "UNSAT"):
            return
        if col not in by_col:
            return
        st = strip_all_exts(stem_or_name)
        hit = by_col[col].get(st) or by_col[col].get(stem_or_name)
        if not hit:
            return
        inst_key, exp_v = hit
        checked += 1
        if exp_v != rv:
            if not strict_legacy_cache and (src_file, section, col, st) in KNOWN_PRECOMMIT_CACHE_ARTIFACTS:
                notes.append(
                    f"[legacy pre-commit cache note] {src_file}:{section} {col}/{inst_key} ({solver}): "
                    f"recorded {rv} before commit 513ab8aa fixed export_qdist_cnf.py (expected.tsv={exp_v})"
                )
                return
            mismatches.append(
                f"Cache mismatch in {src_file}:{section} {col}/{inst_key} ({solver}): "
                f"solver={rv}, expected.tsv={exp_v}"
            )

    # 1. all_suites_8core.json
    p = cache_dir / "all_suites_8core.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        for col, cdata in d.get("sat", {}).items():
            for item in cdata.get("items", []):
                st = item.get("stem", "")
                check_one(p.name, "sat", col, st, "consensus", item.get("verdict"))
                for solver, sres in item.get("solvers", {}).items():
                    if isinstance(sres, dict):
                        check_one(p.name, "sat", col, st, solver, sres.get("verdict"))
        for col, cdata in d.get("mata", {}).items():
            for item in cdata.get("items", []):
                st = item.get("stem", "")
                modes = item.get("modes", {})
                for mode in ("antichain_complement", "explicit_complement"):
                    if mode in modes:
                        check_one(p.name, "mata", col, st, mode, modes[mode].get("verdict"))
                if "emptiness" in modes:
                    ev = norm_verdict(modes["emptiness"].get("verdict"))
                    if ev == "UNSAT":
                        mismatches.append(f"Cache MATA emptiness unexpected UNSAT in {col}/{st}")
                    elif ev == "SAT":
                        checked += 1

    # 2. gap_fill_8core.json
    p = cache_dir / "gap_fill_8core.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        for col, cdata in d.get("dense", {}).items():
            for item in cdata.get("items", []):
                check_one(p.name, "dense", col, item.get("stem", ""), "dense-solver", item.get("verdict"))
        for col, cdata in d.get("heule60", {}).items():
            for item in cdata.get("items", []):
                st = item.get("stem", "")
                check_one(p.name, "heule60", col, st, "consensus", item.get("verdict"))
                for solver, sres in item.get("solvers", {}).items():
                    if isinstance(sres, dict):
                        check_one(p.name, "heule60", col, st, solver, sres.get("verdict"))

    # 3. shortcut_300s.json
    p = cache_dir / "shortcut_300s.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        for key, col in (("tier1", "sat-shortcut-challenge-tier1"), ("tier3", "sat-shortcut-challenge-tier3")):
            for st, sdict in d.get(key, {}).items():
                if isinstance(sdict, dict):
                    for solver, sres in sdict.items():
                        if isinstance(sres, dict):
                            check_one(p.name, key, col, st, solver, sres.get("verdict"))
        for st in d.get("probsat_tier3", {}):
            check_one(p.name, "probsat_tier3", "sat-shortcut-challenge-tier3", st, "probSAT", "SAT")

    # 4. shortcut_tier3_solo.json
    p = cache_dir / "shortcut_tier3_solo.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        for st, rec in d.get("frobenius_sat_solo_core0", {}).items():
            if isinstance(rec, dict):
                check_one(p.name, "solo_sat", "sat-shortcut-challenge-tier3", st, "frobenius", rec.get("verdict"))
        for st, sdict in d.get("n300_unsat_solo_ccd", {}).items():
            if isinstance(sdict, dict):
                for solver, rec in sdict.items():
                    if isinstance(rec, dict):
                        check_one(p.name, "solo_unsat", "sat-shortcut-challenge-tier3", st, solver, rec.get("verdict"))

    # 5. new_suites_bench.json
    p = cache_dir / "new_suites_bench.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        map_col = {
            "dense_public_30": ["dense-solver-public"],
            "dense_instances_20": ["dense-solver-synthetic"],
            "pretolani_8": ["pretolani-pret"],
            "qdistsat_6": ["qdistsat-qldpc"],
            "qdistsat_xcnf_6": ["qdistsat-qldpc"],
            "mod_circuit_9": ["mod-circuit-sat"],
            "aloul_fpga_21": ["aloul-fpga-sb-sat", "aloul-fpga-sb-uns"],
            "rb_frb30_5": ["rb-bench-model-rb"],
            "vlsat2_10": ["vlsat-2"],
            "shortcut_n300_5": ["sat-shortcut-challenge-tier3"],
        }
        for section, arr in d.items():
            cols_k = map_col.get(section, [])
            if not isinstance(arr, list):
                continue
            for row in arr:
                fn = row.get("file", "")
                st = strip_all_exts(fn)
                target_col = None
                for cand in cols_k:
                    if cand in by_col and (st in by_col[cand] or fn in by_col[cand]):
                        target_col = cand
                        break
                if target_col is None:
                    continue
                for solver, res in row.get("results", {}).items():
                    rv = res[0] if isinstance(res, list) and res else (res.get("verdict") if isinstance(res, dict) else res)
                    check_one(p.name, section, target_col, fn, solver, rv)

    # 6. Certified SC 2024-2026 JSONs (optional if present)
    sc_col = "sat-competition-2024-2026-main-track"
    if sc_col in by_col:
        for fn in ("sc25_26_cake_lpr_300s.json", "sc24_cake_lpr_300s.json"):
            p = cache_dir / fn
            if not p.exists():
                continue
            try:
                jd = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            for h, rec in jd.get("results", {}).items():
                if isinstance(rec, dict) and rec.get("verified") is True:
                    check_one(fn, "results", sc_col, f"{h}.cnf", "frobenius-verified", rec.get("status"))

    return checked, mismatches, notes


def check_live_run(
    target: Path,
    by_col: dict[str, dict[str, tuple[str, str]]],
    global_idx: dict[str, list[tuple[str, str, str]]],
    restrict_col: str | None = None,
) -> tuple[int, int, int, list[str], list[str]]:
    """Verify a live solver run (JSON file, TSV/CSV file, or directory of logs/models).

    Returns (checked, agreed, newly_solved_unknowns, mismatches, warnings).
    """
    observations: list[tuple[str | None, str, str, str]] = []  # (col_hint, inst_name, solver_label, verdict)

    def add_obs(col_hint: str | None, inst_name: str, solver: str, raw_v: object) -> None:
        rv = norm_verdict(raw_v)
        if rv in ("SAT", "UNSAT"):
            observations.append((col_hint, inst_name, solver, rv))

    if target.is_dir():
        for f in sorted(target.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix not in (".log", ".out", ".txt", ".model", ".xz"):
                continue
            try:
                if f.suffix == ".xz":
                    text = lzma.open(f, "rt", encoding="utf-8", errors="replace").read(1024 * 1024)
                else:
                    text = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            verdict = None
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("s SATISFIABLE") or s == "SAT":
                    verdict = "SAT"
                    break
                if s.startswith("s UNSATISFIABLE") or s == "UNSAT":
                    verdict = "UNSAT"
                    break
            if verdict:
                # Strip .model.xz / .log / .out / .txt
                stem = f.name
                for suf in (".model.xz", ".log", ".out", ".txt", ".model"):
                    if stem.endswith(suf):
                        stem = stem[: -len(suf)]
                        break
                add_obs(restrict_col, stem, f.parent.name, verdict)
    elif target.suffix.lower() in (".tsv", ".csv"):
        delim = "\t" if target.suffix.lower() == ".tsv" else ","
        with target.open(encoding="utf-8", errors="replace") as fh:
            for row in csv.reader(fh, delimiter=delim):
                if len(row) < 2:
                    continue
                if row[0].strip().lower() in ("instance", "file", "name", "stem", "id"):
                    continue
                add_obs(restrict_col, row[0].strip(), target.name, row[1].strip())
    else:
        # Generic JSON parser supporting all known Frobenius & solver harness formats
        data = json.loads(target.read_text(encoding="utf-8"))

        def walk(obj: object, col_hint: str | None = None, solver_hint: str = "solver") -> None:
            if isinstance(obj, list):
                for item in obj:
                    walk(item, col_hint, solver_hint)
                return
            if not isinstance(obj, dict):
                return
            # Record with explicit stem/file + verdict/status or solvers/results
            inst = obj.get("stem") or obj.get("file") or obj.get("instance") or obj.get("name")
            suite = obj.get("suite") or obj.get("collection") or col_hint
            if isinstance(inst, str):
                if "verdict" in obj or "status" in obj:
                    add_obs(suite if isinstance(suite, str) else None, inst, solver_hint, obj.get("verdict") or obj.get("status"))
                for sub_key in ("solvers", "results"):
                    sub = obj.get(sub_key)
                    if isinstance(sub, dict):
                        for sk, sv in sub.items():
                            if isinstance(sv, dict):
                                add_obs(suite if isinstance(suite, str) else None, inst, sk, sv.get("verdict") or sv.get("status"))
                            elif isinstance(sv, list) and sv:
                                add_obs(suite if isinstance(suite, str) else None, inst, sk, sv[0])
                            else:
                                add_obs(suite if isinstance(suite, str) else None, inst, sk, sv)
                return
            # Mapping of suite/instance/results
            for k, v in obj.items():
                if k in ("results", "sat", "tier1", "tier3"):
                    next_col = (
                        "sat-shortcut-challenge-tier1" if k == "tier1"
                        else "sat-shortcut-challenge-tier3" if k == "tier3"
                        else col_hint
                    )
                    walk(v, next_col, solver_hint)
                elif k in by_col:
                    walk(v, k, solver_hint)
                elif isinstance(v, dict):
                    if "verdict" in v or "status" in v:
                        add_obs(col_hint, k, solver_hint, v.get("verdict") or v.get("status"))
                    elif "items" in v and isinstance(v["items"], list):
                        walk(v["items"], k if k in by_col else col_hint, solver_hint)
                    else:
                        # Could be {inst: {solver: {verdict: ...}}}
                        sub_vals = list(v.values())
                        if sub_vals and all(isinstance(sv, dict) and ("verdict" in sv or "status" in sv) for sv in sub_vals):
                            for sk, sv in v.items():
                                add_obs(col_hint, k, sk, sv.get("verdict") or sv.get("status"))
                        else:
                            walk(v, col_hint, k)
                elif isinstance(v, list):
                    walk(v, col_hint, k)

        walk(data, restrict_col, "solver")

    checked = agreed = newly_solved = 0
    mismatches: list[str] = []
    warnings: list[str] = []

    for col_hint, inst_name, solver, rv in observations:
        rst = strip_rel_exts(inst_name)
        st = strip_all_exts(inst_name)
        col = restrict_col or col_hint
        hits: list[tuple[str, str, str]] = []
        if col and col in by_col:
            h = by_col[col].get(inst_name) or by_col[col].get(rst) or by_col[col].get(st)
            if h:
                hits = [(col, h[0], h[1])]
        if not hits:
            hits = global_idx.get(inst_name) or global_idx.get(rst) or global_idx.get(st, [])
            if restrict_col:
                hits = [x for x in hits if x[0] == restrict_col]
        if not hits:
            warnings.append(f"Unrecognized instance {inst_name!r} (solver={solver}, verdict={rv})")
            continue
        # If stem appears in multiple collections (e.g. hole6 in dense-solver-public & satlib-dimacs-phole),
        # check all of them (they agree on ground truth!).
        checked += 1
        all_match = True
        for c_hit, inst_key, exp_v in hits:
            if exp_v == "UNKNOWN":
                newly_solved += 1
                warnings.append(
                    f"Instance {c_hit}/{inst_key} marked UNKNOWN in expected.tsv was solved as {rv} by {solver}"
                )
            elif exp_v != rv:
                all_match = False
                mismatches.append(
                    f"MISMATCH on {c_hit}/{inst_key} (solver={solver}): got {rv}, expected {exp_v}"
                )
        if all_match and all(h[2] != "UNKNOWN" for h in hits):
            agreed += 1

    return checked, agreed, newly_solved, mismatches, warnings


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
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("\\|")
            i += 2
        elif s[i] == "|":
            cells.append("".join(cur).strip())
            cur = []
            i += 1
        else:
            cur.append(s[i])
            i += 1
    cells.append("".join(cur).strip())
    return cells


def is_gfm_separator_row(line: str) -> bool:
    s = line.strip()
    if "|" not in s:
        return False
    cells = split_gfm_table_cells(s)
    return bool(cells) and all(re.match(r"^:?-+:?$", c) for c in cells)


def validate_gfm_tables(md: Path, repo_root: Path) -> list[str]:
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
    lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    math_re = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)(?<!\$)\$(?!\$)")
    code_re = re.compile(r"`([^`\n]+)`")
    link_re = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")
    fence_re = re.compile(r"^\s{0,3}(`{3,}|~{3,})")

    in_fence = False
    fence_char = ""
    fence_len = 0
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        fm = fence_re.match(line)
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
            hdr_line = line
            sep_line = lines[i + 1]
            hdr_cells = split_gfm_table_cells(hdr_line)
            sep_cells = split_gfm_table_cells(sep_line)

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
                    for m in math_re.finditer(row):
                        if "|" in m.group(1):
                            errors.append(
                                f"GFM table at {rel}:{j + 1}: '|' inside inline math `${m.group(1)}$` "
                                "(use \\lvert...\\rvert, \\mid, or \\lVert...\\rVert)"
                            )
                    for m in code_re.finditer(row):
                        if re.search(r"(?<!\\)\|", m.group(1)):
                            errors.append(
                                f"GFM table at {rel}:{j + 1}: unescaped '|' inside code span `{m.group(1)}`"
                            )
                    for m in link_re.finditer(row):
                        if re.search(r"(?<!\\)\|", m.group(1)) or re.search(r"(?<!\\)\|", m.group(2)):
                            errors.append(
                                f"GFM table at {rel}:{j + 1}: unescaped '|' inside Markdown link `{m.group(0)}`"
                            )
                j += 1

            if j < n and lines[j].strip() != "" and not lines[j].strip().startswith("<!--"):
                errors.append(f"GFM table ending at {rel}:{j}: missing blank line after table")

            i = j
            continue

        # Flag orphan or malformed separator rows (e.g. missing dashes or detached from a header)
        if line.strip().startswith("|") and re.match(r"^\s*\|[\s:\-\|]+\|\s*$", line):
            errors.append(f"GFM table at {rel}:{i + 1}: orphan or malformed separator row `{line.strip()[:80]}`")

        i += 1

    return errors


def check_hygiene(repo_root: Path, cols: list[str]) -> list[str]:
    """Audit compression hygiene, @tavisrudd spelling, GFM tables, solver formatting, and relative links."""
    errors: list[str] = []
    bad_exts = (".gz", ".bz2", ".cnf", ".aig", ".xcnf", ".anf", ".mata")
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    bt_re = re.compile(r"`([^`]+)`")
    solver_word_re = re.compile(
        r"\b(frobenius|cadical|kissat|cryptominisat\d*|dense-solver|probsat|satsuma|lymphosat)\b",
        re.I,
    )

    def audit_md(md: Path) -> None:
        rel = str(md.relative_to(repo_root))
        text = md.read_text(encoding="utf-8", errors="replace")
        if re.search("tr" + "avisrudd", text, re.I):
            errors.append(f"Misspelled '@tavisrudd' handle in {rel}")
        if re.search(r"CryptoMiniSat(?:\]\([^)]+\))?\s+5\.18(?!\.0)", text):
            errors.append(f"Inconsistent version 'CryptoMiniSat 5.18' (missing .0) in {rel}")
        errors.extend(validate_gfm_tables(md, repo_root))
        for m in link_re.finditer(text):
            t = m.group(1).strip()
            if t.startswith(("http://", "https://", "mailto:", "#")):
                continue
            tp = t.split("#")[0]
            if tp and not (md.parent / tp).resolve().exists():
                errors.append(f"Broken relative link in {rel}: {t}")
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in bt_re.finditer(line):
                tok = m.group(1)
                if not solver_word_re.search(tok):
                    continue
                if (
                    "/" in tok
                    or "_" in tok
                    or tok.startswith(("--", "./"))
                    or tok.endswith((".py", ".c", ".rs", ".xz", ".cnf", ".aig", ".xcnf", ".anf", ".mata", ".json", ".tsv", ".csv", ".uri", ".gz", ".md"))
                    or tok in ("dense-solver-public", "dense-solver-synthetic", "f2-frobenius-circulants", "frobenius-challenge-v2")
                ):
                    continue
                errors.append(f"Backticked solver name `{tok}` in {rel}:{lineno}")

    for c in cols:
        col_dir = repo_root / c
        for f in col_dir.rglob("*"):
            if not f.is_file() or ".git" in f.parts:
                continue
            if f.stat().st_size > MAX_GITHUB_FILE_BYTES:
                sz_mb = f.stat().st_size / (1024 * 1024)
                errors.append(
                    f"GitHub file-size violation (>95 MB): {f.relative_to(repo_root)} ({sz_mb:.2f} MB)"
                )
            if "src" in f.relative_to(col_dir).parts:
                continue
            if f.name.endswith(bad_exts):
                errors.append(f"Compression hygiene violation: {f.relative_to(repo_root)}")

        md = col_dir / "README.md"
        if md.exists():
            audit_md(md)

    root_md = repo_root / "README.md"
    if root_md.exists():
        audit_md(root_md)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify expected.tsv manifests and solver verdicts.")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Path to SAT-benchmarks repository root")
    ap.add_argument("--collection", action="append", help="Limit check to specific collection(s) (repeatable)")
    ap.add_argument("--exclude", action="append", default=[], help="Exclude collection glob pattern(s) (repeatable)")
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Directory with cached frobenius JSONs")
    ap.add_argument("--skip-cache", action="store_true", help="Skip cross-checking cached JSON files")
    ap.add_argument("--strict-legacy-cache", action="store_true", help="Fail even on documented pre-commit cache artifacts")
    ap.add_argument("--check-hygiene", action="store_true", help="Also verify compression, links, and @tavisrudd spelling")
    ap.add_argument(
        "--check-run",
        type=Path,
        default=None,
        help="Verify a live solver run JSON, TSV/CSV, or output directory against expected.tsv",
    )
    args = ap.parse_args()

    repo_root = args.repo_root.resolve()
    cols = discover_collections(repo_root, only=args.collection, excludes=args.exclude)
    all_expected, col_kinds, struct_errors, struct_notes = validate_collections(repo_root, cols)
    by_col, global_idx = build_stem_index(all_expected)

    # Mode 2: Live run verification
    if args.check_run is not None:
        if struct_errors:
            print(f"WARNING: {len(struct_errors)} expected.tsv structural error(s) in repo.", file=sys.stderr)
        restrict = args.collection[0] if args.collection and len(args.collection) == 1 else None
        checked, agreed, newly_solved, mismatches, warnings = check_live_run(
            args.check_run, by_col, global_idx, restrict_col=restrict
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

    # Mode 1: Full repository verification
    readme_checked, readme_mismatches = cross_check_readmes(repo_root, cols, col_kinds, by_col, global_idx)

    cache_checked = 0
    cache_mismatches: list[str] = []
    cache_notes: list[str] = []
    if not args.skip_cache and args.cache_dir.is_dir():
        cache_checked, cache_mismatches, cache_notes = cross_check_cache_jsons(
            args.cache_dir, by_col, strict_legacy_cache=args.strict_legacy_cache
        )

    hygiene_errors = check_hygiene(repo_root, cols) if args.check_hygiene else []

    # Summary stats
    tot_entries = sum(len(m) for m in all_expected.values())
    tot_sat = sum(1 for m in all_expected.values() for v in m.values() if v == "SAT")
    tot_unsat = sum(1 for m in all_expected.values() for v in m.values() if v == "UNSAT")
    tot_unk = sum(1 for m in all_expected.values() for v in m.values() if v == "UNKNOWN")

    print(f"Collections inspected   : {len(cols)} ({len(all_expected)} with expected.tsv)")
    print(f"Total expected.tsv rows : {tot_entries} (SAT={tot_sat}, UNSAT={tot_unsat}, UNKNOWN={tot_unk})")
    print(f"Structural/1-to-1 errors: {len(struct_errors)}")
    print(f"README table verdicts   : {readme_checked} checked, {len(readme_mismatches)} mismatches")
    if not args.skip_cache:
        print(f"Cache JSON verdicts     : {cache_checked} checked, {len(cache_mismatches)} mismatches")
    if args.check_hygiene:
        print(f"Hygiene errors          : {len(hygiene_errors)}")

    for n in struct_notes:
        print(f"  {n}")
    for n in cache_notes:
        print(f"  {n}")

    all_errors = struct_errors + readme_mismatches + cache_mismatches + hygiene_errors
    if all_errors:
        print("\nERRORS:", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nALL CHECKS PASSED (0 errors, 0 verdict mismatches).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
