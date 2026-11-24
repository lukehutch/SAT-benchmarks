"""Check gen_vdw.py + verify.py on known w(2;3,t), t = 3..9 (SAT at N = w-1, UNSAT at N = w)."""
import os, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..", "..", "common"))
from harness import run
W = {3: 9, 4: 18, 5: 22, 6: 32, 7: 46, 8: 58, 9: 77}          # A171081
cases = [c for t, w in W.items() for c in (([str(t), str(w - 1)], True, f"t={t} N={w-1}"), ([str(t), str(w)], False, f"t={t} N={w}"))]
sys.exit(run(cases, os.path.join(here, "gen_vdw.py"), os.path.join(here, "verify.py"), sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()))
