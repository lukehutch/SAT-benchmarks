#!/usr/bin/env python3
"""Check README benchmark table verdict parity vs expected.tsv, solvers-in-columns convention, cache JSONs, and live runs."""
from __future__ import annotations

import csv
import json
import lzma
import re
import sys
from pathlib import Path
from typing import Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.common import (
    KNOWN_PRECOMMIT_CACHE_ARTIFACTS,
    LEGACY_COLLECTION_MAP,
    REPO_ROOT,
    CheckContext,
    CheckResult,
    map_parallel,
    norm_verdict,
    standalone_main,
    strip_all_exts,
    strip_rel_exts,
)

CHECK_NAME = "verdicts"
CHECK_ORDER = 30
REQUIRES_HYGIENE_FLAG = False
DESCRIPTION = "Cross-check README benchmark verdicts vs expected.tsv, solvers-in-columns convention, and cached JSONs"

_SEP_ROW_RE = re.compile(r"^\s*\|[\s:\-\|]+\|\s*$")
_ITALIC_RE = re.compile(r"\*[^*]*\*")


def check_solvers_in_columns(col_name: str, text: str) -> list[str]:
    """Verify Benchmark Results tables follow the solvers-in-columns convention (rows=instances, cols=solvers)."""
    errors: list[str] = []
    lines = text.splitlines()
    in_bench = False
    for i, line in enumerate(lines):
        if line.startswith("## Benchmark Results"):
            in_bench = True
            continue
        if in_bench and line.startswith("## "):
            break
        if in_bench and line.strip().startswith("|") and i + 1 < len(lines) and _SEP_ROW_RE.match(lines[i + 1]):
            hdr = [x.strip().lower() for x in line.strip().strip("|").split("|")]
            if hdr and hdr[0] in ("solver", "solvers"):
                errors.append(
                    f"Convention violation in {col_name}/README.md:{i + 1}: "
                    f"Benchmark Results table has '{hdr[0]}' in column 0 (expected solvers in columns)"
                )
    return errors


def _cross_check_single_readme(
    col: str,
    text: str,
    is_mata: bool,
    cm: dict[str, tuple[str, str]],
) -> tuple[int, list[str]]:
    checked = 0
    mismatches: list[str] = []
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < n and _SEP_ROW_RE.match(lines[i + 1]):
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
            while j < n and lines[j].strip().startswith("|"):
                cells = [x.strip() for x in lines[j].strip().strip("|").split("|")]
                if verdict_col_idx is not None and len(cells) > verdict_col_idx:
                    c0 = cells[0].strip("`* ")
                    tok0 = c0.split()[0].strip("`* ") if c0 else ""
                    hit = cm.get(tok0) or cm.get(strip_rel_exts(tok0)) or cm.get(strip_all_exts(tok0))
                    if hit is not None:
                        raw_v = _ITALIC_RE.sub("", cells[verdict_col_idx]).replace("*", "").strip()
                        # Handle cells like "SAT *(known unique)*" -> "SAT"
                        first_word = raw_v.split()[0] if raw_v else ""
                        rv = norm_verdict(first_word) if first_word.upper() in ("SAT", "UNSAT") else None
                        if rv in ("SAT", "UNSAT"):
                            inst_key, exp_v = hit
                            checked += 1
                            if exp_v != rv:
                                mismatches.append(
                                    f"README mismatch in {col}/README.md:{j + 1} ({inst_key}): "
                                    f"README says {rv}, expected.tsv says {exp_v}"
                                )
                j += 1
            i = j
        else:
            i += 1
    return checked, mismatches


def cross_check_readmes(
    repo_root: Path,
    cols: list[str],
    col_kinds: dict[str, str],
    by_col: dict[str, dict[str, tuple[str, str]]],
    global_idx: dict[str, list[tuple[str, str, str]]],
    *,
    include_root_readme: bool = True,
    readme_reader: Callable[[Path], str | None] | None = None,
    jobs: int = 1,
) -> tuple[int, list[str]]:
    """Cross-check every verdict cell in every collection README.md and root README.md."""
    reader = readme_reader or (
        lambda p: p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
    )
    active_cols = [c for c in cols if c in by_col]

    def _worker(c: str) -> tuple[int, list[str]]:
        text = reader(repo_root / c / "README.md")
        if text is None:
            return 0, []
        return _cross_check_single_readme(c, text, col_kinds.get(c) == "mata-orig", by_col[c])

    checked = 0
    mismatches: list[str] = []
    for c_chk, c_mis in map_parallel(_worker, active_cols, jobs):
        checked += c_chk
        mismatches.extend(c_mis)

    # Also cross-check root README.md Section 6 cross-product parity table
    if include_root_readme:
        root_text = reader(repo_root / "README.md")
        if root_text is not None:
            lines = root_text.splitlines()
            n = len(lines)
            i = 0
            while i < n:
                line = lines[i]
                if (
                    line.strip().startswith("| Origin | Benchmark | Verdict |")
                    and i + 1 < n
                    and _SEP_ROW_RE.match(lines[i + 1])
                ):
                    j = i + 2
                    while j < n and lines[j].strip().startswith("|"):
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
                                            f"Root README mismatch at README.md:{j + 1} ({col}/{inst_key}): "
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
    repo_root: Path = REPO_ROOT,
) -> tuple[int, list[str], list[str]]:
    """Cross-check cached solver JSONs in ~/.cache/frobenius against expected.tsv."""
    checked = 0
    mismatches: list[str] = []
    notes: list[str] = []

    sc23_24_alias: dict[str, str] = {}
    sc_manifest = repo_root / "sat-competition-2002-2026-uris" / "src" / "sc23_24_manifest.json"
    if sc_manifest.exists():
        try:
            mdata = json.loads(sc_manifest.read_text(encoding="utf-8"))
            for entry in mdata.get("sat_competition_flat_cnfs", []):
                nm = entry.get("name")
                gh = entry.get("gbd_hash")
                if isinstance(nm, str) and isinstance(gh, str):
                    sc23_24_alias[nm] = f"{gh}.cnf"
        except Exception:
            pass

    def check_one(src_file: str, section: str, col: str, stem_or_name: str, solver: str, raw_v: object) -> None:
        nonlocal checked
        rv = norm_verdict(raw_v)
        if rv not in ("SAT", "UNSAT"):
            return
        candidate_cols = (col,) if col in by_col else LEGACY_COLLECTION_MAP.get(col, ())
        if not candidate_cols:
            return
        st = strip_all_exts(stem_or_name)
        mapped_name = sc23_24_alias.get(st)
        resolved_col: str | None = None
        hit: tuple[str, str] | None = None
        for cand in candidate_cols:
            cm = by_col.get(cand)
            if not cm:
                continue
            h = cm.get(st) or cm.get(stem_or_name) or (cm.get(mapped_name) if mapped_name else None)
            if h:
                resolved_col = cand
                hit = h
                break
        if not hit or resolved_col is None:
            return
        inst_key, exp_v = hit
        checked += 1
        if exp_v != rv:
            if not strict_legacy_cache and (src_file, section, resolved_col, st) in KNOWN_PRECOMMIT_CACHE_ARTIFACTS:
                notes.append(
                    f"[legacy pre-commit cache note] {src_file}:{section} {resolved_col}/{inst_key} ({solver}): "
                    f"recorded {rv} before commit 513ab8aa fixed export_qdist_cnf.py (expected.tsv={exp_v})"
                )
                return
            mismatches.append(
                f"Cache mismatch in {src_file}:{section} {resolved_col}/{inst_key} ({solver}): "
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
            "dense_instances_20": ["dense-solver-synthetic-chessboard", "dense-solver-synthetic-php"],
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
    sc_col = "sat-competition-2002-2026-uris"
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

    Returns ``(checked, agreed, newly_solved_unknowns, mismatches, warnings)``.
    """
    observations: list[tuple[str | None, str, str, str]] = []

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
        data = json.loads(target.read_text(encoding="utf-8"))

        def walk(obj: object, col_hint: str | None = None, solver_hint: str = "solver") -> None:
            if isinstance(obj, list):
                for item in obj:
                    walk(item, col_hint, solver_hint)
                return
            if not isinstance(obj, dict):
                return
            inst = obj.get("stem") or obj.get("file") or obj.get("instance") or obj.get("name")
            suite = obj.get("suite") or obj.get("collection") or col_hint
            if isinstance(inst, str):
                if "verdict" in obj or "status" in obj:
                    add_obs(
                        suite if isinstance(suite, str) else None,
                        inst,
                        solver_hint,
                        obj.get("verdict") or obj.get("status"),
                    )
                for sub_key in ("solvers", "results"):
                    sub = obj.get(sub_key)
                    if isinstance(sub, dict):
                        for sk, sv in sub.items():
                            if isinstance(sv, dict):
                                add_obs(
                                    suite if isinstance(suite, str) else None,
                                    inst,
                                    sk,
                                    sv.get("verdict") or sv.get("status"),
                                )
                            elif isinstance(sv, list) and sv:
                                add_obs(suite if isinstance(suite, str) else None, inst, sk, sv[0])
                            else:
                                add_obs(suite if isinstance(suite, str) else None, inst, sk, sv)
                return
            for k, v in obj.items():
                if k in ("results", "sat", "tier1", "tier3"):
                    next_col = (
                        "sat-shortcut-challenge-tier1"
                        if k == "tier1"
                        else "sat-shortcut-challenge-tier3"
                        if k == "tier3"
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
                        sub_vals = list(v.values())
                        if sub_vals and all(
                            isinstance(sv, dict) and ("verdict" in sv or "status" in sv) for sv in sub_vals
                        ):
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


def _verdict_col_worker(
    args: tuple[str, Path, bool, dict[str, tuple[str, str]] | None],
) -> tuple[int, list[str], list[str]]:
    col, repo_root, is_mata, cm = args
    md = repo_root / col / "README.md"
    if not md.exists():
        return 0, [], []
    text = md.read_text(encoding="utf-8", errors="replace")
    checked = 0
    mismatches: list[str] = []
    if cm is not None:
        checked, mismatches = _cross_check_single_readme(col, text, is_mata, cm)
    conv_errors = check_solvers_in_columns(col, text)
    return checked, mismatches, conv_errors


def run(ctx: CheckContext) -> CheckResult:
    """Cross-check README verdicts, solvers-in-columns convention, and cached solver JSONs."""
    ctx.ensure_expected()
    work = [
        (c, ctx.repo_root, ctx.col_kinds.get(c) == "mata-orig", ctx.by_col.get(c))
        for c in ctx.collections
    ]

    readme_checked = 0
    readme_mismatches: list[str] = []
    convention_errors: list[str] = []
    for c_chk, c_mis, c_conv in ctx.map_work(_verdict_col_worker, work):
        readme_checked += c_chk
        readme_mismatches.extend(c_mis)
        convention_errors.extend(c_conv)

    # Also cross-check root README.md Section 6 cross-product parity table
    if ctx.include_root_readme:
        r_chk, r_mis = cross_check_readmes(
            ctx.repo_root,
            [],
            ctx.col_kinds,
            ctx.by_col,
            ctx.global_idx,
            include_root_readme=True,
            readme_reader=ctx.read_readme,
            jobs=1,
        )
        readme_checked += r_chk
        readme_mismatches.extend(r_mis)

    cache_checked = 0
    cache_mismatches: list[str] = []
    cache_notes: list[str] = []
    if not ctx.skip_cache and ctx.cache_dir.is_dir():
        cache_checked, cache_mismatches, cache_notes = cross_check_cache_jsons(
            ctx.cache_dir,
            ctx.by_col,
            strict_legacy_cache=ctx.strict_legacy_cache,
            repo_root=ctx.repo_root,
        )

    return CheckResult(
        name=CHECK_NAME,
        errors=readme_mismatches + convention_errors + cache_mismatches,
        notes=cache_notes,
        stats={
            "readme_checked": readme_checked,
            "readme_mismatches": len(readme_mismatches),
            "convention_errors": len(convention_errors),
            "cache_checked": cache_checked,
            "cache_mismatches": len(cache_mismatches),
        },
    )


if __name__ == "__main__":
    sys.exit(standalone_main(sys.modules[__name__]))
