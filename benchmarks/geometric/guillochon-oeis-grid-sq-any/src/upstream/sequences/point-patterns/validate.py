"""Check gen_points.py + verify.py against known terms (SAT at the max, UNSAT at max+1) for every pattern."""
import os, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..", "..", "common"))
from harness import run
KNOWN = {  # pattern: (sequence, {grid size: max})
    "sq-axis":  ("A227133", dict(enumerate([1, 3, 7, 12, 17, 24, 32, 41, 51, 61, 73, 85, 98], 1))),
    "sq-any":   ("A240443", dict(enumerate([1, 3, 6, 10, 15, 21, 27, 34, 42, 50], 1))),
    "tri-up":   ("A157795", dict(enumerate([1, 2, 4, 6, 9, 12, 15, 18, 22, 26, 31, 35, 40], 1))),   # side = offset-0 index + 1
    "tri-axis": ("A227308", dict(enumerate([1, 2, 4, 6, 8, 12, 14, 18, 22, 26, 30, 34, 39, 44, 49], 1))),
    "tri-any":  ("A240114", dict(enumerate([1, 2, 4, 6, 8, 10, 12, 14, 17, 20, 22, 25, 28, 31, 34], 1))),
}
nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 7
cases = []
for pat, (seq, vals) in KNOWN.items():
    for n in range(2, nmax + 1):
        m = vals[n]
        cases += [([pat, str(n), str(m)], True, f"{seq} {pat} n={n} m={m}"),
                  ([pat, str(n), str(m + 1)], False, f"{seq} {pat} n={n} m={m+1}")]
sys.exit(run(cases, os.path.join(here, "gen_points.py"), os.path.join(here, "verify.py"), sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()))
