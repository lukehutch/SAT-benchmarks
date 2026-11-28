#!/usr/bin/env python3
"""Find a lower bound by solving "max >= m" for increasing m with CaDiCaL (PySAT), each under a time cap.

    python find_lb.py GEN VERIFY OUTDIR M0 CAP_SECONDS -- gen args before m ...

Runs GEN <args> m, solves, verifies the model with VERIFY, and keeps the best verified model in OUTDIR
(best.cnf.map.json + best.model). Stops at the first UNSAT or timeout.
"""
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import time


def solve(path, q):
    from pysat.formula import CNF
    from pysat.solvers import Cadical153
    with Cadical153(bootstrap_with=CNF(from_file=path).clauses) as s:
        r = s.solve()
        q.put((r, s.get_model() if r else None))


def main():
    gen, verify, outdir, m, cap = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5])
    args = sys.argv[sys.argv.index("--") + 1:]
    os.makedirs(outdir, exist_ok=True)
    best = None
    while True:
        f = os.path.join(outdir, f"try_m{m}.cnf")
        subprocess.run([sys.executable, gen] + args + [str(m), "-o", f], check=True, capture_output=True)
        q = mp.Queue()
        p = mp.Process(target=solve, args=(f, q))
        t = time.time()
        p.start()
        p.join(cap)
        if p.is_alive():
            p.terminate()
            print(f"m={m}: timeout after {cap:.0f}s", flush=True)
            break
        r, model = q.get()
        if not r:
            print(f"m={m}: UNSAT in {time.time() - t:.0f}s", flush=True)
            break
        mf = f + ".model"
        open(mf, "w").write("v " + " ".join(map(str, model)) + " 0\n")
        v = subprocess.run([sys.executable, verify, f + ".map.json", mf], capture_output=True, text=True)
        print(f"m={m}: SAT in {time.time() - t:.0f}s; {v.stdout.strip().splitlines()[-1]}", flush=True)
        if v.returncode != 0:
            break
        shutil.copy(f + ".map.json", os.path.join(outdir, "best.cnf.map.json"))
        shutil.copy(mf, os.path.join(outdir, "best.model"))
        best = m
        os.remove(f)
        m += 1
    print(f"BEST verified: {best}")


if __name__ == "__main__":
    main()
