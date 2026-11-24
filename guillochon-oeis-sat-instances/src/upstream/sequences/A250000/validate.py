"""Check gen_queens.py + verify.py on known A250000(n), n = 3..8 (SAT at a(n), UNSAT at a(n)+1)."""
import os, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..", "..", "common"))
from harness import run
A = [0, 0, 1, 2, 4, 5, 7, 9, 12, 14, 17, 21, 24, 28, 32, 37, 42, 47, 52, 58]   # a(1..20)
cases = [c for n in range(3, 9) for c in (([str(n), str(A[n-1])], True, f"n={n} m={A[n-1]}"), ([str(n), str(A[n-1] + 1)], False, f"n={n} m={A[n-1]+1}"))]
sys.exit(run(cases, os.path.join(here, "gen_queens.py"), os.path.join(here, "verify.py"), sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()))
