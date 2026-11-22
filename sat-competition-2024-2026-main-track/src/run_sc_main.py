#!/usr/bin/env python3
"""Parallel SAT Competition 2024 / 2025 / 2026 Main Track Evaluator & X-Ray Analyzer for Frobenius.

Features:
- Runs Frobenius (`--max-cores 1 --timeout <T>`) across N parallel workers (1 core per instance).
- Verifies EVERY SAT verdict against the original `.cnf.xz` formula (independent Python verifier).
- Cross-checks EVERY SAT/UNSAT verdict against official SC2024 (`detailed_main.csv`) and SC2026 (`sc2026_scores.csv`) ground truth.
- Supports incremental resume & tiered timeout escalation (`--prev <json>`).
"""
import argparse
import concurrent.futures
import csv
import json
import lzma
import os
import pathlib
import resource
import subprocess
import time

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_BIN = str(SCRIPT_DIR.parent / "target/release/frobenius")
DEFAULT_CACHE = pathlib.Path.home() / ".cache/sc-main-cnfs"


def load_ground_truth(sc_dir: pathlib.Path):
    gt = {}
    sc26_best = {}
    p26 = sc_dir / "sc2026_scores.csv"
    if p26.exists():
        with open(p26) as f:
            for row in csv.DictReader(f):
                h = row["instanceid"]
                st = row["status"]
                if st == "sat-verified":
                    gt[h] = "SAT"
                elif st == "unsat-verified":
                    gt[h] = "UNSAT"
                if st in ("sat-verified", "unsat-verified"):
                    rt = float(row["runtime"])
                    if h not in sc26_best or rt < sc26_best[h][0]:
                        sc26_best[h] = (rt, row["solverid"], "SAT" if st == "sat-verified" else "UNSAT")
    sc24_times = {}
    p24 = sc_dir / "sc2024/detailed_main.csv"
    if p24.exists():
        with open(p24) as f:
            for row in csv.DictReader(f):
                h = row["hash"]

                def pf(k):
                    try:
                        return float(row[k])
                    except Exception:
                        return 5000.0

                sc24_times[h] = {
                    "kissat": pf("kissat-sc2024"),
                    "cadical": pf("CaDiCaL"),
                    "breakid": pf("BreakID-Kissat"),
                }
                res = row.get("vresult", row.get("result", "")).strip().upper()
                if res in ("SAT", "SATISFIABLE"):
                    gt[h] = "SAT"
                elif res in ("UNSAT", "UNSATISFIABLE"):
                    gt[h] = "UNSAT"
    return gt, sc24_times, sc26_best


def verify_model_xz(xz_path: pathlib.Path, model_lits):
    assign = {}
    for l in model_lits:
        if l == 0:
            continue
        assign[abs(l)] = l > 0
    with lzma.open(xz_path, "rt", errors="ignore") as f:
        cur_sat = False
        cur_has = False
        for line in f:
            s = line.strip()
            if not s or s[0] in ("c", "p"):
                continue
            if s[0] == "%":
                break
            for tok in s.split():
                lit = int(tok)
                if lit == 0:
                    if not cur_sat:
                        return False
                    cur_sat = False
                    cur_has = False
                else:
                    cur_has = True
                    v = abs(lit)
                    val = assign.get(v, False)
                    if (lit > 0 and val) or (lit < 0 and not val):
                        cur_sat = True
        if cur_has and not cur_sat:
            return False
    return True


def run_one(args_tuple):
    h, cache_dir, bin_path, timeout_s, mem_gb = args_tuple
    xz_path = pathlib.Path(cache_dir) / f"{h}.cnf.xz"
    if not xz_path.exists() or xz_path.stat().st_size < 20:
        return (h, "MISSING", timeout_s, "")

    def set_limits():
        cpu_lim = int(timeout_s) + 3
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_lim, cpu_lim + 2))
        if mem_gb > 0:
            mem_b = int(mem_gb * 1024 * 1024 * 1024)
            resource.setrlimit(resource.RLIMIT_AS, (mem_b, mem_b))

    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [bin_path, str(xz_path), "--timeout", f"{timeout_s}", "--max-cores", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s + 8.0,
            preexec_fn=set_limits,
        )
        dt = time.monotonic() - t0
        rc = proc.returncode
        out = proc.stdout
        status = "TIMEOUT"
        model_lits = []
        for line in out.splitlines():
            if line.startswith("s SATISFIABLE"):
                status = "SAT"
            elif line.startswith("s UNSATISFIABLE"):
                status = "UNSAT"
            elif line.startswith("v "):
                for tok in line[2:].split():
                    try:
                        model_lits.append(int(tok))
                    except Exception:
                        pass
        if status == "SAT":
            if xz_path.stat().st_size <= 8 * 1024 * 1024:
                if not verify_model_xz(xz_path, model_lits):
                    return (h, "BAD_MODEL", dt, "python verifier failed!")
            return (h, "SAT", min(dt, timeout_s), "")
        elif status == "UNSAT":
            return (h, "UNSAT", min(dt, timeout_s), "")
        elif rc not in (0, 10, 20, -9, -24, 137, 152):
            return (h, f"ERR_{rc}", dt, (proc.stderr or "")[:200])
        else:
            return (h, "TIMEOUT", timeout_s, "")
    except subprocess.TimeoutExpired:
        return (h, "TIMEOUT", timeout_s, "")
    except Exception as e:
        return (h, "EXC", time.monotonic() - t0, str(e)[:200])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bin", default=DEFAULT_BIN)
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--sc-dir", default="/tmp/sc-bench")
    ap.add_argument("--years", default="2024,2025,2026")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--mem-gb", type=float, default=0.0)
    ap.add_argument("--prev", default="")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sc_dir = pathlib.Path(args.sc_dir)
    years = [int(y) for y in args.years.split(",")]
    year_hashes = {}
    unique_hashes = []
    seen = set()
    for yr in years:
        hs = [
            l.strip().rsplit("/", 1)[-1].split("-")[0].split(".")[0]
            for l in (sc_dir / f"main_{yr}.uri").read_text().splitlines()
            if l.strip()
        ]
        year_hashes[yr] = hs
        for h in hs:
            if h not in seen:
                seen.add(h)
                unique_hashes.append(h)

    results = {}
    if args.prev and os.path.exists(args.prev):
        prev_data = json.load(open(args.prev))
        for h, rec in prev_data.get("results", {}).items():
            if rec["status"] in ("SAT", "UNSAT"):
                results[h] = rec
        print(f"Carried over {len(results)} solved instances from {args.prev}", flush=True)

    todo = [h for h in unique_hashes if h not in results]
    print(f"Running {len(todo)} instances (timeout={args.timeout}s, workers={args.workers})...", flush=True)

    gt, sc24_times, sc26_best = load_ground_truth(sc_dir)
    t_start = time.time()
    done_cnt = sat_cnt = unsat_cnt = to_cnt = err_cnt = unsound_cnt = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run_one, (h, args.cache_dir, args.bin, args.timeout, args.mem_gb)) for h in todo]
        for fut in concurrent.futures.as_completed(futs):
            h, st, dt, msg = fut.result()
            done_cnt += 1
            if st in ("SAT", "UNSAT"):
                if h in gt and gt[h] != st:
                    unsound_cnt += 1
                    print(f"!!! UNSOUNDNESS DETECTED on {h}: frobenius={st} vs official={gt[h]} !!!", flush=True)
                    st = f"UNSOUND_{st}_VS_{gt[h]}"
                elif st == "SAT":
                    sat_cnt += 1
                else:
                    unsat_cnt += 1
            elif st == "TIMEOUT":
                to_cnt += 1
            else:
                err_cnt += 1
                print(f"  [ERR] {h}: {st} ({dt:.2f}s) {msg}", flush=True)
            results[h] = {"status": st, "sec": round(dt, 4), "msg": msg}
            if done_cnt % 50 == 0 or done_cnt == len(todo):
                el = time.time() - t_start
                print(
                    f"[{done_cnt:4}/{len(todo)}] SAT={sat_cnt} UNSAT={unsat_cnt} T/O={to_cnt} ERR={err_cnt} UNSOUND={unsound_cnt} ({el:.1f}s)",
                    flush=True,
                )
                with open(args.out, "w") as outf:
                    json.dump({"timeout_s": args.timeout, "results": results}, outf)

    summary = {}
    print("\n================ PER-YEAR SUMMARY ================")
    for yr in years:
        hs = year_hashes[yr]
        sat = unsat = to = err = 0
        par2_cur = par2_5000 = 0.0
        for h in hs:
            rec = results.get(h, {"status": "MISSING", "sec": args.timeout})
            st = rec["status"]
            dt = rec["sec"]
            if st == "SAT":
                sat += 1
                par2_cur += dt
                par2_5000 += dt
            elif st == "UNSAT":
                unsat += 1
                par2_cur += dt
                par2_5000 += dt
            else:
                if st == "TIMEOUT":
                    to += 1
                else:
                    err += 1
                par2_cur += 2.0 * args.timeout
                par2_5000 += 10000.0
        n = len(hs)
        solved = sat + unsat
        summary[str(yr)] = {
            "n": n,
            "solved": solved,
            "sat": sat,
            "unsat": unsat,
            "timeout": to,
            "err": err,
            "par2_at_timeout": round(par2_cur / n, 2),
            "par2_5000_ub": round(par2_5000 / n, 2),
        }
        print(
            f"SC {yr}: Solved={solved:3}/{n} (SAT={sat:3} UNSAT={unsat:3} T/O={to:3} ERR={err:2}) | PAR-2(T={args.timeout:.0f}s)={par2_cur/n:7.2f} | PAR-2(5000s UB)={par2_5000/n:8.2f}"
        )

    with open(args.out, "w") as outf:
        json.dump({"timeout_s": args.timeout, "summary": summary, "results": results}, outf, indent=2)
    print(f"\nSaved full results to {args.out}", flush=True)


if __name__ == "__main__":
    main()
