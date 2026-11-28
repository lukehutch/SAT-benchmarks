import sys, time
from pysat.solvers import Cadical153
from structsat import read
cl = read(sys.argv[1]); t = time.process_time()
s = Cadical153(bootstrap_with=cl); r = s.solve()
print(("SAT" if r else "UNSAT"), f"{time.process_time() - t:.4f}")
