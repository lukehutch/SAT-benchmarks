#!/usr/bin/env python3
"""16-Configuration Frobenius Matrix Benchmark Runner (4 Exec Modes x 4 Formats).

Runs Frobenius across the full cross-product of:
  - Execution modes (4):
      Phase 1 (sequential, 1 job at a time using 8 dedicated physical cores):
        1. `8c_cpu`  (--max-cores 8 --no-gpu)
        2. `8c_gpu`  (--max-cores 8 --gpu)
      Phase 2 (dynamic work queue pooling 8 dedicated physical core slots, 8 jobs at once):
        3. `1c_cpu`  (--max-cores 1 --no-gpu)
        4. `1c_gpu`  (--max-cores 1 --gpu)
  - Input formats (4):
      `.cnf`, `.xcnf`, `.aig`, `.anf`

Every completed run is immediately flushed & fsynced to `--output <FILE.jsonl>` with
full telemetry (`wall_ms`, `user_ms`, `sys_ms`, `internal_ms`, `peak_rss_kb`, `par2_ms`,
`verdict`, `expected`, `verdict_ok`, `model_verified`, `gpu_used`, `core_mask`,
`host_load_1m`, `conflicts`, `decisions`, `propagations`, `exit_code`), and live
16-column pivot tables are refreshed into:
  - `<output>.summary.md`   (human-readable per-collection & overall 16-config summary)
  - `<output>.summary.json` (structured per-collection & per-benchmark matrix)
  - `<output>.matrix.tsv`   (per-benchmark 16-column TSV: every instance x all 16 configs)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import lzma
import os
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

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
import run_benchmarks as rb  # noqa: E402

FORMATS_4 = ("cnf", "xcnf", "aig", "anf")
PHASE1_MODES = (
    ("8c_cpu", 8, False),
    ("8c_gpu", 8, True),
)
PHASE2_MODES = (
    ("1c_cpu", 1, False),
    ("1c_gpu", 1, True),
)
ALL_16_COLS = [
    f"{m}:{f}"
    for m in ("1c_cpu", "8c_cpu", "1c_gpu", "8c_gpu")
    for f in FORMATS_4
]


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_load_1m() -> float:
    try:
        return round(os.getloadavg()[0], 2)
    except OSError:
        return -1.0


def parse_frobenius_extra(stdout: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "internal_ms": None,
        "conflicts": None,
        "decisions": None,
        "propagations": None,
        "gpu_used": False,
        "gpu_info": "",
    }
    m = re.search(r"time=([\d.]+)ms", stdout)
    if m:
        out["internal_ms"] = float(m.group(1))
    for k in ("conflicts", "decisions", "propagations"):
        mk = re.search(rf"{k}=(\d+)", stdout)
        if mk:
            out[k] = int(mk.group(1))
    mg = re.search(r"^c\s+gpu[=:\s](.+)$", stdout, re.M)
    if mg:
        out["gpu_used"] = True
        out["gpu_info"] = mg.group(1).strip()[:120]
    return out


def run_one(
    frob_bin: Path,
    mode_name: str,
    max_cores: int,
    use_gpu: bool,
    core_mask: str,
    col: str,
    fmt: str,
    stem: str,
    src_path: Path,
    expected: str,
    timeout_s: float,
    verify_models: bool,
    tmp_root: Path,
) -> dict[str, Any]:
    tmp_file: Path | None = None
    run_path = src_path
    try:
        if src_path.name.endswith(".xz"):
            base = src_path.name[:-3]
            tmp_file = tmp_root / f"{mode_name}_{core_mask.replace(',', '_')}_{os.getpid()}_{threading.get_ident()}_{base}"
            with lzma.open(src_path, "rb") as src, tmp_file.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1 << 20)
            run_path = tmp_file

        prefix = ["taskset", "-c", core_mask] if shutil.which("taskset") else []
        gpu_flag = "--gpu" if use_gpu else "--no-gpu"
        cmd = prefix + [
            str(frob_bin),
            str(run_path),
            "--max-cores",
            str(max_cores),
            gpu_flag,
            "--timeout",
            f"{timeout_s:.3f}",
        ]
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

        # Hard wall deadline = timeout_s + 2.0s grace so solver can emit clean stats/model
        deadline = t0 + timeout_s + 2.0
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
        if not solved and wall_ms >= timeout_s * 950.0:
            timed_out = True
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
                model_verified, model_verify_msg = rb.verify_cnf_model(run_path, lits)
            else:
                model_verified, model_verify_msg = None, "no v-lines"

        extra = parse_frobenius_extra(stdout)
        return {
            "timestamp_utc": utc_now_iso(),
            "mode": mode_name,
            "max_cores": max_cores,
            "gpu_enabled": use_gpu,
            "core_mask": core_mask,
            "collection": col,
            "instance": stem,
            "format": fmt,
            "config_key": f"{mode_name}:{fmt}",
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


def load_done_keys(jsonl_path: Path) -> set[tuple[str, str, str, str]]:
    done: set[tuple[str, str, str, str]] = set()
    if not jsonl_path.is_file():
        return done
    for ln in jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
            done.add((r["mode"], r["format"], r["collection"], r["instance"]))
        except Exception:
            continue
    return done


def write_matrix_reports(jsonl_path: Path, quiet: bool = False) -> dict[str, Any]:
    latest: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    if jsonl_path.is_file():
        for ln in jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
                latest[(r["mode"], r["format"], r["collection"], r["instance"])] = r
            except Exception:
                continue
    recs = list(latest.values())

    disagrees: list[str] = []
    badsats: list[str] = []
    by_cfg: dict[str, list[dict[str, Any]]] = {k: [] for k in ALL_16_COLS}
    by_col_cfg: dict[str, dict[str, list[dict[str, Any]]]] = {}
    by_inst_cfg: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}

    for r in recs:
        ck = f"{r['mode']}:{r['format']}"
        by_cfg.setdefault(ck, []).append(r)
        by_col_cfg.setdefault(r["collection"], {}).setdefault(ck, []).append(r)
        by_inst_cfg.setdefault((r["collection"], r["instance"]), {})[ck] = r
        if not r.get("verdict_ok", True):
            disagrees.append(f"{r['collection']}/{r['instance']} [{ck}]: got {r['verdict']} exp {r['expected']}")
        if r.get("model_verified") is False:
            badsats.append(f"{r['collection']}/{r['instance']} [{ck}]: {r.get('model_verify_msg')}")

    # 1. Per-benchmark 16-column TSV
    tsv_path = jsonl_path.with_suffix(".matrix.tsv")
    tsv_lines = ["collection\tinstance\texpected\t" + "\t".join(ALL_16_COLS)]
    for (col, inst), cmap in sorted(by_inst_cfg.items()):
        exp = next((v.get("expected", "UNKNOWN") for v in cmap.values() if v.get("expected") in ("SAT", "UNSAT")), "UNKNOWN")
        cells = []
        for ck in ALL_16_COLS:
            r = cmap.get(ck)
            if r is None:
                cells.append("-")
            elif r["verdict"] in ("SAT", "UNSAT"):
                cells.append(f"{r['wall_ms']:.2f}ms({r['verdict']})")
            else:
                cells.append(f"TO({r['timeout_s']:.0f}s)")
        tsv_lines.append(f"{col}\t{inst}\t{exp}\t" + "\t".join(cells))
    tsv_path.write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

    # 2. Overall 16-config summary
    cfg_summary: dict[str, Any] = {}
    for ck in ALL_16_COLS:
        rows = by_cfg.get(ck, [])
        solved = sum(1 for r in rows if r["verdict"] in ("SAT", "UNSAT"))
        par2_s = round(sum(r["par2_ms"] for r in rows) / 1000.0, 3)
        solved_s = round(sum(r["wall_ms"] for r in rows if r["verdict"] in ("SAT", "UNSAT")) / 1000.0, 3)
        gpu_hits = sum(1 for r in rows if r.get("gpu_used"))
        cfg_summary[ck] = {
            "total": len(rows),
            "solved": solved,
            "par2_s": par2_s,
            "solved_wall_s": solved_s,
            "gpu_used_runs": gpu_hits,
        }

    # 3. Markdown report
    md = [
        f"# Frobenius 16-Configuration Matrix Report ({utc_now_iso()})",
        "",
        f"- **Completed Runs:** `{len(recs)}` across `{len(by_col_cfg)}` collections / `{len(by_inst_cfg)}` unique benchmark stems",
        f"- **Verdict Disagreements:** `{len(disagrees)}` | **BADSAT:** `{len(badsats)}`",
        f"- **Per-Benchmark 16-Column TSV:** `{tsv_path}`",
        "",
        "## Overall 4 Modes × 4 Formats Summary",
        "",
        "| Mode | `.cnf` (Solved / PAR-2) | `.xcnf` (Solved / PAR-2) | `.aig` (Solved / PAR-2) | `.anf` (Solved / PAR-2) |",
        "|---|---:|---:|---:|---:|",
    ]
    for m in ("1c_cpu", "8c_cpu", "1c_gpu", "8c_gpu"):
        row_cells = [f"**`{m}`**"]
        for f in FORMATS_4:
            s = cfg_summary[f"{m}:{f}"]
            if s["total"] == 0:
                row_cells.append("—")
            else:
                row_cells.append(f"{s['solved']}/{s['total']} (`{s['par2_s']:.1f}s`)")
        md.append("| " + " | ".join(row_cells) + " |")
    md.append("")
    md.append("## Per-Collection Breakdown (Solved / PAR-2 s)")
    md.append("")
    md.append("| Collection | `1c_cpu:cnf` | `8c_cpu:cnf` | `1c_gpu:cnf` | `8c_gpu:cnf` | `1c_cpu:aig` | `8c_cpu:aig` | `1c_gpu:aig` | `8c_gpu:aig` |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    show_cols = ("1c_cpu:cnf", "8c_cpu:cnf", "1c_gpu:cnf", "8c_gpu:cnf", "1c_cpu:aig", "8c_cpu:aig", "1c_gpu:aig", "8c_gpu:aig")
    for col, cmap in sorted(by_col_cfg.items()):
        short = Path(col).name
        cells = [f"`{short}`"]
        for ck in show_cols:
            rows = cmap.get(ck, [])
            if not rows:
                cells.append("—")
            else:
                sv = sum(1 for r in rows if r["verdict"] in ("SAT", "UNSAT"))
                p2 = sum(r["par2_ms"] for r in rows) / 1000.0
                cells.append(f"{sv}/{len(rows)} ({p2:.1f}s)")
        md.append("| " + " | ".join(cells) + " |")
    md.append("")

    sum_md = jsonl_path.with_suffix(".summary.md")
    sum_json = jsonl_path.with_suffix(".summary.json")
    summary_obj = {
        "updated_at_utc": utc_now_iso(),
        "total_records": len(recs),
        "collections": len(by_col_cfg),
        "unique_benchmarks": len(by_inst_cfg),
        "disagrees": disagrees,
        "badsats": badsats,
        "configs": cfg_summary,
    }
    sum_md.write_text("\n".join(md), encoding="utf-8")
    sum_json.write_text(json.dumps(summary_obj, indent=2) + "\n", encoding="utf-8")
    if not quiet:
        print("\n".join(md[:30]))
    return summary_obj


def main() -> int:
    ap = argparse.ArgumentParser(description="Run Frobenius 16-configuration matrix (8C first, then 8x1C dynamic pool).")
    ap.add_argument("--frobenius-bin", required=True, help="Path to frobenius executable.")
    ap.add_argument("--benchmarks-dir", default=str(REPO_ROOT), help="SAT-benchmarks root directory.")
    ap.add_argument("--output", required=True, help="Incremental JSONL output file.")
    ap.add_argument("--cores-pool", default="0,1,2,3,4,5,6,7", help="8 dedicated physical cores (default: CCD0 0..7, leaving Core 15 untouched).")
    ap.add_argument("--formats", default="cnf,xcnf,aig,anf", help="Comma-separated formats.")
    ap.add_argument("--collections", nargs="+", default=None, help="Optional subset of collections/categories.")
    ap.add_argument("--problems", nargs="+", default=None, help="Optional subset of problems.")
    ap.add_argument("--timeout-cap", type=float, default=0.0, help="Optional max timeout cap in seconds (0 = full README T_max).")
    ap.add_argument("--timeout-override", type=float, default=None, help="Override every instance timeout with fixed seconds.")
    ap.add_argument("--resume", action="store_true", help="Skip (mode, format, collection, instance) already in --output.")
    ap.add_argument("--include-oeis-unknown", dest="skip_oeis_unknown", action="store_false", help="Include UNKNOWN rows in guillochon-oeis-*.")
    ap.add_argument("--no-verify-models", dest="verify_models", action="store_false", help="Skip raw-CNF SAT model verification.")
    ap.add_argument("--log-every", type=int, default=50, help="Print progress every N completed runs.")
    ap.add_argument("--summary-every", type=int, default=200, help="Refresh summary/TSV every N runs.")
    ap.add_argument("--dry-run", action="store_true", help="Print queue counts without executing.")
    ap.set_defaults(skip_oeis_unknown=True, verify_models=True)
    args = ap.parse_args()

    frob_bin = Path(args.frobenius_bin).expanduser().resolve()
    if not frob_bin.is_file():
        sys.exit(f"ERROR: frobenius binary not found: {frob_bin}")
    bench_root = Path(args.benchmarks_dir).expanduser().resolve()
    pool_cores = [int(c.strip()) for c in args.cores_pool.split(",") if c.strip()]
    mask_8c = ",".join(str(c) for c in pool_cores)
    want_formats = rb.flatten_list_arg(args.formats)
    want_cols = set(rb.flatten_list_arg(args.collections)) if args.collections else None
    want_probs = rb.flatten_list_arg(args.problems)

    all_probs = rb.discover_problems(
        bench_root=bench_root,
        want_formats=want_formats,
        timeout_override=args.timeout_override,
        skip_oeis_unknown=args.skip_oeis_unknown,
    )
    probs = rb.filter_problems(
        all_problems=all_probs,
        bench_root=bench_root,
        want_problems=want_probs,
        want_cols=want_cols,
        excl_cols=set(),
        want_formats=want_formats,
        timeout_override=args.timeout_override,
    )

    out_path = Path(args.output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_keys(out_path) if args.resume else set()

    def _cap(tmax: float) -> float:
        if args.timeout_cap > 0.0:
            return min(tmax, args.timeout_cap)
        return tmax

    phase1_tasks = []
    for mode_name, mc, use_gpu in PHASE1_MODES:
        for col_rel, _cs, fmt, stem, fp, ev, tmax in probs:
            if (mode_name, fmt, col_rel, stem) in done:
                continue
            phase1_tasks.append((mode_name, mc, use_gpu, col_rel, fmt, stem, fp, ev, _cap(tmax)))

    phase2_tasks = []
    for mode_name, mc, use_gpu in PHASE2_MODES:
        for col_rel, _cs, fmt, stem, fp, ev, tmax in probs:
            if (mode_name, fmt, col_rel, stem) in done:
                continue
            phase2_tasks.append((mode_name, mc, use_gpu, col_rel, fmt, stem, fp, ev, _cap(tmax)))

    # Order Phase 2 LPT (longest timeouts first) for optimal 8-worker pool load balance
    phase2_tasks.sort(key=lambda t: (-t[8], t[0], t[4], t[3], t[5]))

    total_runs = len(phase1_tasks) + len(phase2_tasks)
    print(f"[matrix] Binary: {frob_bin}", flush=True)
    print(f"[matrix] Pool ({len(pool_cores)} physical cores): {pool_cores} | 8C mask: {mask_8c}", flush=True)
    print(f"[matrix] Problems: {len(probs)} across formats {want_formats} | Skipped (--resume): {len(done)}", flush=True)
    print(f"[matrix] Phase 1 (8-core sequential: 8c_cpu + 8c_gpu): {len(phase1_tasks)} runs", flush=True)
    print(f"[matrix] Phase 2 (1-core 8-way dynamic pool: 1c_cpu + 1c_gpu): {len(phase2_tasks)} runs", flush=True)
    print(f"[matrix] Total pending runs: {total_runs} -> {out_path}", flush=True)

    if args.dry_run:
        return 0

    tmp_base = Path("/dev/shm") if Path("/dev/shm").is_dir() else Path(tempfile.gettempdir())
    tmp_root = Path(tempfile.mkdtemp(prefix="frob_matrix_", dir=str(tmp_base)))
    write_lock = threading.Lock()
    completed = 0
    errors = 0
    t_start = time.perf_counter()

    def _record(fout, rec: dict[str, Any], phase_lbl: str) -> None:
        nonlocal completed, errors
        line = json.dumps(rec, separators=(",", ":")) + "\n"
        with write_lock:
            fout.write(line)
            fout.flush()
            os.fsync(fout.fileno())
            completed += 1
            if (not rec["verdict_ok"]) or (rec["model_verified"] is False):
                errors += 1
                print(
                    f"  [ALERT] {rec['collection']}/{rec['instance']} [{rec['config_key']}]: "
                    f"verdict={rec['verdict']} exp={rec['expected']} verified={rec['model_verified']}",
                    flush=True,
                )
            if completed % args.log_every == 0 or completed == total_runs:
                el = time.perf_counter() - t_start
                rate = completed / max(el, 0.001)
                eta = (total_runs - completed) / max(rate, 1e-6)
                print(
                    f"[{phase_lbl}] {completed}/{total_runs} ({100.0*completed/max(total_runs,1):.1f}%) "
                    f"elapsed={el:.1f}s eta={eta:.0f}s load={host_load_1m():.2f} errors={errors}",
                    flush=True,
                )
            if args.summary_every > 0 and completed % args.summary_every == 0:
                write_matrix_reports(out_path, quiet=True)

    try:
        file_mode = "a" if args.resume else "w"
        with out_path.open(file_mode, encoding="utf-8") as fout:
            # PHASE 1: All 8-core benchmarks FIRST (1 job at a time using full 8-core pool!)
            if phase1_tasks:
                print(f"\n=== PHASE 1: Running {len(phase1_tasks)} 8-core benchmarks sequentially on cores {mask_8c} ===", flush=True)
                for mode_name, mc, use_gpu, col_rel, fmt, stem, fp, ev, tmax in phase1_tasks:
                    rec = run_one(
                        frob_bin=frob_bin,
                        mode_name=mode_name,
                        max_cores=mc,
                        use_gpu=use_gpu,
                        core_mask=mask_8c,
                        col=col_rel,
                        fmt=fmt,
                        stem=stem,
                        src_path=fp,
                        expected=ev,
                        timeout_s=tmax,
                        verify_models=args.verify_models,
                        tmp_root=tmp_root,
                    )
                    _record(fout, rec, "P1-8C")
                write_matrix_reports(out_path, quiet=True)

            # PHASE 2: All 1-core benchmarks in a dynamic 8-worker work queue pooling 8 cores!
            if phase2_tasks:
                print(f"\n=== PHASE 2: Running {len(phase2_tasks)} 1-core benchmarks across {len(pool_cores)}-core dynamic pool ===", flush=True)
                core_q: queue.Queue[int] = queue.Queue()
                for c in pool_cores:
                    core_q.put(c)

                def _worker_1c(task):
                    mode_name, mc, use_gpu, col_rel, fmt, stem, fp, ev, tmax = task
                    cid = core_q.get()
                    try:
                        return run_one(
                            frob_bin=frob_bin,
                            mode_name=mode_name,
                            max_cores=mc,
                            use_gpu=use_gpu,
                            core_mask=str(cid),
                            col=col_rel,
                            fmt=fmt,
                            stem=stem,
                            src_path=fp,
                            expected=ev,
                            timeout_s=tmax,
                            verify_models=args.verify_models,
                            tmp_root=tmp_root,
                        )
                    finally:
                        core_q.put(cid)

                with concurrent.futures.ThreadPoolExecutor(max_workers=len(pool_cores)) as ex:
                    futs = [ex.submit(_worker_1c, t) for t in phase2_tasks]
                    for fut in concurrent.futures.as_completed(futs):
                        _record(fout, fut.result(), "P2-1C")

        write_matrix_reports(out_path, quiet=False)
        print(f"\n[matrix] Finished {completed} runs in {time.perf_counter() - t_start:.1f}s -> {out_path}", flush=True)
        return 1 if errors > 0 else 0
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
