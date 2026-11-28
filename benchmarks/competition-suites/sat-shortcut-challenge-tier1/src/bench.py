"""Run the structure front end, plain CaDiCaL and Kissat on each instance. CPU seconds; timeout per run."""
import subprocess, sys, os, resource, time
import gen
V = sys.executable; TO = float(sys.argv[1]) if len(sys.argv) > 1 else 20
os.makedirs('cnf', exist_ok=True)
inst = [gen.tseitin(n, 1, False) for n in (20, 30, 40, 60, 100, 200)] + [gen.tseitin(n, 2, True) for n in (40, 100, 200)] \
     + [gen.php(h) for h in (7, 8, 9, 10, 12)] + [gen.random3(n, s) for n, s in ((150, 1), (200, 1), (200, 2), (250, 1))]
def run(cmd):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TO * 6)   # generous wall limit: the machine is loaded
        out = p.stdout
    except subprocess.TimeoutExpired: return None, None
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    return out, (r1.ru_utime - r0.ru_utime)
print(f"{'instance':24} {'vars':>5} {'clauses':>7} {'expect':>6} | {'ours':>22} | {'CaDiCaL':>16} | {'Kissat':>16}")
for name, exp, cl in inst:
    fn = f"cnf/{name}.cnf"; gen.write(cl, fn)
    nv = max(abs(l) for c in cl for l in c)
    o, _ = run([V, 'structsat.py', fn]); a = o.split() if o else None
    ours = f"{a[0]} {float(a[2])*1000:9.2f} ms {a[1][:8]}" if a else "timeout"
    o, _ = run(['perl', '-e', f'alarm {int(TO*6)}; exec @ARGV', V, 'run_cadical.py', fn]); c = o.split() if o else None
    cad = f"{c[0]} {float(c[1])*1000:9.1f} ms" if c and len(c) == 2 and float(c[1]) < TO else f"> {TO:.0f} s"
    o, cpu = run(['kissat', '-q', f'--time={int(TO)}', fn])
    ans = 'SAT' if o and 's SATISFIABLE' in o else 'UNSAT' if o and 's UNSATISFIABLE' in o else None
    kis = f"{ans} {cpu*1000:9.1f} ms" if ans else f"> {TO:.0f} s"
    answers = {x for x in (a[0] if a else None, c[0] if c and cad[0] != '>' else None, ans) if x}
    flag = "" if len(answers) <= 1 and (exp is None or not answers or answers == {'SAT' if exp else 'UNSAT'}) else "  << DISAGREE"
    print(f"{name:24} {nv:5d} {len(cl):7d} {('SAT' if exp else 'UNSAT') if exp is not None else '?':>6} | {ours:>22} | {cad:>16} | {kis:>16}{flag}", flush=True)
