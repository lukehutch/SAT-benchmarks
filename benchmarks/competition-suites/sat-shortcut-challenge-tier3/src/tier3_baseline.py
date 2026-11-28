"""Kissat on the Tier 3 instances: answer and CPU seconds per instance. Usage: tier3_baseline.py [limit seconds] [parallel jobs]"""
import sys, os, subprocess, resource, glob
from concurrent.futures import ThreadPoolExecutor
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 300; JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
def run(fn):
    p = subprocess.Popen(['kissat', '-q', f'--time={LIM}', fn], stdout=subprocess.PIPE, text=True)
    out = p.stdout.read(); _, _, ru = os.wait4(p.pid, 0)
    ans = 'SAT' if 's SATISFIABLE' in out else 'UNSAT' if 's UNSATISFIABLE' in out else f'> {LIM} s'
    return os.path.basename(fn), ans, ru.ru_utime
key = lambda f: (int(f.split('_n')[1].split('_')[0]), f)
with ThreadPoolExecutor(JOBS) as ex:
    for name, ans, t in ex.map(run, sorted(glob.glob('cnf/tier3/*.cnf'), key=key)):
        print(f"{name}\t{ans}\t{t:.2f}", flush=True)
