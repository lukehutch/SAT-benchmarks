"""Validation harness: generate small instances with known answers, solve them with CaDiCaL (PySAT), and run
the sequence's verifier on every SAT model.  Needs `pip install python-sat`.

    run(cases, gen_script, verify_script, tmpdir)
    cases: list of (generator_args: list[str], expected_sat: bool, label: str)
"""
import os
import subprocess
import sys
import time


def run(cases, gen, verify, tmp):
    from pysat.formula import CNF
    from pysat.solvers import Cadical153
    os.makedirs(tmp, exist_ok=True)
    bad = 0
    for args, want, label in cases:
        f = os.path.join(tmp, "_".join(args) + ".cnf")
        subprocess.run([sys.executable, gen] + args + ["-o", f], check=True, capture_output=True)
        t = time.time()
        with Cadical153(bootstrap_with=CNF(from_file=f).clauses) as s:
            sat = s.solve()
            model = s.get_model() if sat else None
        msg = ""
        if sat:
            m = f + ".model"
            open(m, "w").write("v " + " ".join(map(str, model)) + " 0\n")
            r = subprocess.run([sys.executable, verify, f + ".map.json", m], capture_output=True, text=True)
            msg = r.stdout.strip().splitlines()[-1]
            bad += r.returncode != 0
        ok = sat == want
        bad += not ok
        print(f"{label:28s} {'SAT' if sat else 'UNSAT':5s} {'ok' if ok else 'WRONG'} {time.time() - t:6.1f}s  {msg}",
              flush=True)
    print("ALL OK" if not bad else f"{bad} FAILURES")
    return bad
