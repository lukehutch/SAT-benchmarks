#!/usr/bin/env python3
"""Comprehensive analysis of Frobenius vs official SC 2024 / 2025 / 2026 Main Track benchmarks."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_uris(path: Path):
    hashes = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        name = line.rsplit("/", 1)[-1]
        h = name.split("-")[0].split(".")[0]
        hashes.append(h)
    return hashes


def main():
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/sc-bench/frob_sc_pgo_60s.json")
    sc_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/sc-bench")
    data = json.loads(json_path.read_text())
    results = data.get("results", data)
    tmax = float(data.get("timeout_s", data.get("timeout", 60.0))) if isinstance(data, dict) else 60.0

    errs, unsounds = [], []
    for h, r in results.items():
        st = r.get("status", "")
        if st in ("ERR", "ERROR", "CRASH") or st.startswith("ERR_") or st == "BAD_MODEL":
            errs.append((h, r))
        if r.get("unsound") or st.startswith("UNSOUND"):
            unsounds.append((h, r))
    print(f"=== INTEGRITY AUDIT ({json_path}, T={tmax}s) ===")
    print(f"Total entries: {len(results)}, ERR={len(errs)}, UNSOUND={len(unsounds)}")
    if errs:
        print("ERRORS:", errs[:10])
    if unsounds:
        print("UNSOUNDS:", unsounds[:10])

    years = {yr: load_uris(sc_dir / f"main_{yr}.uri") for yr in (2024, 2025, 2026)}

    vresult = {}
    with open(sc_dir / "sc2024/detailed_main.csv") as f:
        for row in csv.DictReader(f):
            if row["vresult"] in ("sat", "unsat"):
                vresult[row["hash"]] = row["vresult"].upper()
    with open(sc_dir / "sc2026_scores.csv") as f:
        for row in csv.DictReader(f):
            if row["vresult"] in ("sat", "unsat"):
                vresult[row["instanceid"]] = row["vresult"].upper()

    disagreements = []
    for h, r in results.items():
        st = r.get("status", "")
        if st in ("SAT", "UNSAT") and h in vresult and vresult[h] != st:
            disagreements.append((h, st, vresult[h]))
    print(f"Cross-check vs official SC24/SC26 vresult: {len(disagreements)} disagreements")

    def eval_frob(hashes, cap):
        solved = sat = unsat = 0
        total_t = 0.0
        for h in hashes:
            r = results.get(h)
            t = float(r.get("sec", r.get("time", 1e9))) if r else 1e9
            if r and r.get("status") in ("SAT", "UNSAT") and t <= cap:
                solved += 1
                if r["status"] == "SAT":
                    sat += 1
                else:
                    unsat += 1
                total_t += t
            else:
                total_t += 2.0 * cap
        return solved, sat, unsat, total_t / len(hashes)

    print("\n=== FROBENIUS STANDINGS ===")
    for cap in sorted(set([15.0, tmax])):
        print(f"\n-- Cutoff T = {cap:.0f}s (PAR-2 penalty = {2*cap:.0f}s) --")
        for yr in (2024, 2025, 2026):
            s, sat, unsat, par2 = eval_frob(years[yr], cap)
            print(f"  SC {yr}: {s:3d}/400 (SAT={sat:3d}, UNSAT={unsat:3d})  PAR-2({cap:.0f}s) = {par2:7.2f}s")

    print("\n=== SC 2024 OFFICIAL HEAD-TO-HEAD (detailed_main.csv) ===")
    sc24_rows = list(csv.DictReader(open(sc_dir / "sc2024/detailed_main.csv")))
    sc24_solvers = [k for k in sc24_rows[0].keys() if k not in ("hash", "vresult")]
    for cap in (15.0, tmax):
        board = []
        s, sat, unsat, par2 = eval_frob(years[2024], cap)
        board.append(("Frobenius (ours)", s, sat, unsat, par2))
        for sv in sc24_solvers:
            s = sat = unsat = 0
            tot = 0.0
            for row in sc24_rows:
                t = float(row[sv])
                if t < 5000.0 and t <= cap:
                    s += 1
                    if row["vresult"] == "sat":
                        sat += 1
                    elif row["vresult"] == "unsat":
                        unsat += 1
                    tot += t
                else:
                    tot += 2.0 * cap
            board.append((sv, s, sat, unsat, tot / len(sc24_rows)))
        board.sort(key=lambda x: (-x[1], x[4]))
        print(f"\n-- SC 2024 at T={cap:.0f}s --")
        for rank, (sv, s, sat, unsat, p2) in enumerate(board[:12], 1):
            print(f"  #{rank:2d} {sv:22s}: {s:3d}/400 (SAT={sat:3d}, UNSAT={unsat:3d}) PAR-2 = {p2:8.2f}s")

    print("\n=== SC 2026 OFFICIAL HEAD-TO-HEAD (sc2026_scores.csv) ===")
    sc26_by_solver = defaultdict(list)
    with open(sc_dir / "sc2026_scores.csv") as f:
        for row in csv.DictReader(f):
            sc26_by_solver[row["solverid"]].append(row)
    for cap in (15.0, tmax):
        board = []
        s, sat, unsat, par2 = eval_frob(years[2026], cap)
        board.append(("Frobenius (ours)", s, sat, unsat, par2))
        for sv, rows in sc26_by_solver.items():
            if len(rows) < 390:
                continue
            s = sat = unsat = 0
            tot = 0.0
            for row in rows:
                st = row["status"]
                t = float(row["runtime"])
                if st in ("sat-verified", "unsat-verified") and t <= cap:
                    s += 1
                    if st == "sat-verified":
                        sat += 1
                    else:
                        unsat += 1
                    tot += t
                else:
                    tot += 2.0 * cap
            board.append((sv, s, sat, unsat, tot / 400.0))
        board.sort(key=lambda x: (-x[1], x[4]))
        print(f"\n-- SC 2026 at T={cap:.0f}s (top 15) --")
        for rank, (sv, s, sat, unsat, p2) in enumerate(board[:15], 1):
            print(f"  #{rank:2d} {sv:42s}: {s:3d}/400 (SAT={sat:3d}, UNSAT={unsat:3d}) PAR-2 = {p2:8.2f}s")


if __name__ == "__main__":
    main()
