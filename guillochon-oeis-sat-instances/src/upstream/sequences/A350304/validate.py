"""Check gen_zaran.py + verify.py on known z(n;3) = A350304(n), n = 3..NMAX (SAT at z, UNSAT at z+1)."""
import os, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..", "..", "common"))
from harness import run
Z = [1, 4, 8, 13, 20, 26, 33, 42, 49, 60, 69, 80, 92, 105, 120, 128]   # A350304(1..16)
cases = [c for n in range(3, int(sys.argv[2]) + 1 if len(sys.argv) > 2 else 9) for c in (([str(n), str(Z[n-1])], True, f"n={n} m={Z[n-1]}"), ([str(n), str(Z[n-1] + 1)], False, f"n={n} m={Z[n-1]+1}"))]
sys.exit(run(cases, os.path.join(here, "gen_zaran.py"), os.path.join(here, "verify.py"), sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()))
