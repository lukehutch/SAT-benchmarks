"""Check gen_depth_cnf.py against known values of A067782 (SAT at a(n), UNSAT at a(n)-1)."""
import subprocess, sys, time, os
from pysat.formula import CNF
from pysat.solvers import Cadical153
A = [0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10]   # a(1..17)
here = os.path.dirname(os.path.abspath(__file__))
tmp = sys.argv[1]
nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 10
bad = 0
for n in range(3, nmax + 1):
    for d, want in ((A[n-1], True), (A[n-1]-1, False)):
        for extra in ([], ["--no-last-adjacent"]):
            f = os.path.join(tmp, f"v_n{n}_d{d}.cnf")
            subprocess.run([sys.executable, os.path.join(here, "gen_depth_cnf.py"), str(n), str(d), "-o", f] + extra,
                           check=True, capture_output=True)
            t = time.time()
            with Cadical153(bootstrap_with=CNF(from_file=f).clauses) as s:
                sat = s.solve()
                model = s.get_model()
            msg = ""
            if sat:
                m = f + ".model"
                open(m, "w").write("v " + " ".join(map(str, model)) + " 0\n")
                r = subprocess.run([sys.executable, os.path.join(here, "decode_verify.py"), f + ".map.json", m],
                                   capture_output=True, text=True)
                msg = r.stdout.strip().splitlines()[-1]
                if r.returncode != 0: bad += 1
            ok = sat == want
            bad += not ok
            print(f"n={n:2d} d={d:2d} {' '.join(extra):18s} {'SAT' if sat else 'UNSAT':5s} "
                  f"{'ok' if ok else 'WRONG'} {time.time()-t:7.1f}s {msg}", flush=True)
print("ALL OK" if not bad else f"{bad} FAILURES")
