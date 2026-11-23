"""More families. For each: a specialised method (a known shortcut), against CaDiCaL and Kissat on the CNF.
Where the shortcut needs the original object (the circuit or the graph) and not just the CNF, the table says so.
Usage: more.py [timeout seconds]"""
import sys, os, time, random, subprocess, resource, itertools
from collections import defaultdict
from pysat.solvers import Cadical153
import gen, structsat
V = sys.executable; TO = float(sys.argv[1]) if len(sys.argv) > 1 else 10
os.makedirs('cnf', exist_ok=True)

# ---------------------------------------------------------------- circuits
class Circ:
    def __init__(s): s.nv = 0; s.cl = []; s.gates = []; s.inputs = []
    def var(s): s.nv += 1; return s.nv
    def inp(s): v = s.var(); s.inputs.append(v); return v
    def const0(s):
        v = s.var(); s.cl.append([-v]); s.gates.append((v, 'c', 0, 0)); return v
    def AND(s, a, b):
        o = s.var(); s.cl += [[-o, a], [-o, b], [o, -a, -b]]; s.gates.append((o, '&', a, b)); return o
    def XOR(s, a, b):
        o = s.var(); s.cl += [[-o, a, b], [-o, -a, -b], [o, -a, b], [o, a, -b]]; s.gates.append((o, '^', a, b)); return o
    def OR(s, a, b): return -s.AND(-a, -b)
    def fa(s, a, b, c):
        t = s.XOR(a, b); return s.XOR(t, c), s.OR(s.AND(a, b), s.AND(c, t))
    def ha(s, a, b): return s.XOR(a, b), s.AND(a, b)
    def ripple(s, A, B):
        out = []; c = None
        for a, b in zip(A, B):
            if c is None: x, c = s.ha(a, b)
            else: x, c = s.fa(a, b, c)
            out.append(x)
        return out + [c]
    def kogge(s, A, B):
        n = len(A); G = [s.AND(a, b) for a, b in zip(A, B)]; P = [s.XOR(a, b) for a, b in zip(A, B)]; p0 = P[:]
        d = 1
        while d < n:
            G2, P2 = G[:], P[:]
            for i in range(d, n):
                G2[i] = s.OR(G[i], s.AND(P[i], G[i - d])); P2[i] = s.AND(P[i], P[i - d])
            G, P = G2, P2; d *= 2
        return [p0[0]] + [s.XOR(p0[i], G[i - 1]) for i in range(1, n)] + [G[n - 1]]
    def mul_array(s, A, B):
        n = len(A); z = s.const0()
        acc = [s.AND(a, B[0]) for a in A] + [z] * n
        for j in range(1, n):
            row = [z] * j + [s.AND(a, B[j]) for a in A] + [z] * (n - j)
            acc = s.ripple(acc, row)[:2 * n]
        return acc
    def mul_wallace(s, A, B):
        n = len(A); cols = [[] for _ in range(2 * n + 1)]
        for i, a in enumerate(A):
            for j, b in enumerate(B): cols[i + j].append(s.AND(a, b))
        while any(len(c) > 2 for c in cols):
            new = [[] for _ in cols]
            for k, c in enumerate(cols):
                i = 0
                while len(c) - i >= 3:
                    x, cy = s.fa(c[i], c[i + 1], c[i + 2]); new[k].append(x); new[k + 1].append(cy); i += 3
                if len(c) - i == 2 and len(c) > 2:
                    x, cy = s.ha(c[i], c[i + 1]); new[k].append(x); new[k + 1].append(cy); i += 2
                new[k] += c[i:]
            cols = new
        z = s.const0()
        X = [c[0] if len(c) > 0 else z for c in cols[:2 * n]]; Y = [c[1] if len(c) > 1 else z for c in cols[:2 * n]]
        return s.ripple(X, Y)[:2 * n]
    def miter(s, O1, O2):
        d = None
        for a, b in zip(O1, O2):
            x = s.XOR(a, b); d = x if d is None else s.OR(d, x)
        s.out = d; return s.cl + [[d]]

def simulate(c):
    """exhaustive bit-parallel simulation over all inputs: one big integer per wire"""
    k = len(c.inputs); L = 1 << k; MASK = (1 << L) - 1; val = {}
    for j, v in enumerate(c.inputs):
        b = 1 << j; val[v] = (MASK // ((1 << (2 * b)) - 1)) * (((1 << b) - 1) << b)
    g = lambda l: val[l] if l > 0 else val[-l] ^ MASK
    for o, op, a, b in c.gates:
        val[o] = 0 if op == 'c' else (g(a) & g(b)) if op == '&' else (g(a) ^ g(b))
    return g(c.out) != 0

def sweep(c):
    """SAT sweeping: random simulation proposes equal internal wires, small SAT calls prove them in order."""
    rng = random.Random(1); W = 2048; MASK = (1 << W) - 1; val = {v: rng.getrandbits(W) for v in c.inputs}
    g = lambda l: val[l] if l > 0 else val[-l] ^ MASK
    for o, op, a, b in c.gates:
        val[o] = 0 if op == 'c' else (g(a) & g(b)) if op == '&' else (g(a) ^ g(b))
    s = Cadical153(bootstrap_with=c.cl); rep = {}
    for v in sorted(val):
        sig = val[v]; ph = 1
        if sig & 1: sig ^= MASK; ph = -1
        if sig in rep:
            r = rep[sig] * ph
            if not s.solve(assumptions=[v, -r]) and not s.solve(assumptions=[-v, r]):
                s.add_clause([-v, r]); s.add_clause([v, -r])
        else: rep[sig] = v * ph
    r = s.solve(assumptions=[c.out]); s.delete(); return r

def cec(kind, n):
    c = Circ(); A = [c.inp() for _ in range(n)]; B = [c.inp() for _ in range(n)]
    if kind == 'adder': cl = c.miter(c.ripple(A, B), c.kogge(A, B))
    else: cl = c.miter(c.mul_array(A, B), c.mul_wallace(A, B))
    return c, cl

def mult_target(n, N):
    c = Circ(); A = [c.inp() for _ in range(n)]; B = [c.inp() for _ in range(n)]
    O = c.mul_array(A, B); cl = c.cl[:]
    for i, o in enumerate(O): cl.append([o] if (N >> i) & 1 else [-o])
    cl.append(A[1:]); cl.append(B[1:])                 # both factors at least 2
    return cl

# ---------------------------------------------------------------- perfect matching (mutilated chessboard)
def chessboard(n, sat):
    gone = {(0, 0), (0, n - 1)} if sat else {(0, 0), (n - 1, n - 1)}
    cells = [(r, q) for r in range(n) for q in range(n) if (r, q) not in gone]; inc = defaultdict(list); nv = 0
    for (r, q) in cells:
        for (r2, q2) in ((r, q + 1), (r + 1, q)):
            if (r2, q2) in inc or (r2, q2) in set(cells):
                nv += 1; inc[(r, q)].append(nv); inc[(r2, q2)].append(nv)
    cl = []
    for cell in cells:
        vs = inc[cell]; cl.append(vs[:])
        for a, b in itertools.combinations(vs, 2): cl.append([-a, -b])
    return cl

def matching_solver(clauses):
    """Recognise 'every positive clause needs exactly one of its variables, each variable sits in two clauses':
    a perfect matching problem. Solved by augmenting paths when the graph is bipartite. Returns True/False/None."""
    pos = [c for c in clauses if all(l > 0 for l in c)]; rest = [c for c in clauses if not all(l > 0 for l in c)]
    if not pos or any(len(c) != 2 or c[0] > 0 or c[1] > 0 for c in rest): return None
    where = defaultdict(list)
    for i, c in enumerate(pos):
        for v in c: where[v].append(i)
    if any(len(w) != 2 for w in where.values()): return None
    negs = {frozenset((-c[0], -c[1])) for c in rest}
    need = {frozenset(p) for c in pos for p in itertools.combinations(c, 2)}
    if negs != need: return None
    n = len(pos); adj = defaultdict(list)
    for v, (a, b) in where.items(): adj[a].append(b); adj[b].append(a)
    col = {}
    for s0 in range(n):
        if s0 in col: continue
        col[s0] = 0; st = [s0]
        while st:
            u = st.pop()
            for x in adj[u]:
                if x not in col: col[x] = 1 - col[u]; st.append(x)
                elif col[x] == col[u]: return None           # not bipartite: leave it to the general solver
    left = [u for u in range(n) if col[u] == 0]
    if 2 * len(left) != n: return False
    match = {}; sys.setrecursionlimit(100000)
    def aug(u, vis):
        for x in adj[u]:
            if x in vis: continue
            vis.add(x)
            if x not in match or aug(match[x], vis): match[x] = u; return True
        return False
    return all(aug(u, set()) for u in left)

# ---------------------------------------------------------------- Hamiltonian cycle
def ham_cnf(n, E):
    x = lambda v, i: v * n + i + 1; cl = []; adj = set(E) | {(b, a) for a, b in E}
    for v in range(n):
        cl.append([x(v, i) for i in range(n)])
        for i, j in itertools.combinations(range(n), 2): cl.append([-x(v, i), -x(v, j)])
    for i in range(n):
        cl.append([x(v, i) for v in range(n)])
        for u, v in itertools.combinations(range(n), 2): cl.append([-x(u, i), -x(v, i)])
    for u in range(n):
        for v in range(n):
            if u != v and (u, v) not in adj:
                for i in range(n): cl.append([-x(u, i), -x(v, (i + 1) % n)])
    cl.append([x(0, 0)]); return cl

def ham_solver(n, E, limit=5.0):
    """Quick impossibility tests (degree, cut vertex, unbalanced bipartite), then a depth-first search that always
    extends to the neighbour with the fewest free neighbours. Returns True/False/None (None = gave up)."""
    adj = defaultdict(set)
    for a, b in E: adj[a].add(b); adj[b].add(a)
    if any(len(adj[v]) < 2 for v in range(n)): return False
    def connected(skip):
        st = [next(v for v in range(n) if v != skip)]; seen = set(st)
        while st:
            for x in adj[st.pop()]:
                if x != skip and x not in seen: seen.add(x); st.append(x)
        return len(seen) == n - (skip is not None)
    if not connected(None) or any(not connected(v) for v in range(n)): return False
    col = {0: 0}; st = [0]; bip = True
    while st and bip:
        u = st.pop()
        for x in adj[u]:
            if x not in col: col[x] = 1 - col[u]; st.append(x)
            elif col[x] == col[u]: bip = False
    if bip and 2 * sum(col.values()) != n: return False
    t0 = time.process_time(); used = [False] * n; used[0] = True; sys.setrecursionlimit(100000)
    def dfs(u, k):
        if time.process_time() - t0 > limit: raise TimeoutError
        if k == n: return 0 in adj[u]
        for x in sorted((y for y in adj[u] if not used[y]), key=lambda y: sum(1 for z in adj[y] if not used[z])):
            used[x] = True
            if dfs(x, k + 1): return True
            used[x] = False
        return False
    try: return dfs(0, 1)
    except TimeoutError: return None

def ham_graphs():
    out = []; rng = random.Random(7)
    for n, extra in ((20, 20), (30, 45), (40, 80)):                       # planted cycle plus random edges: has a cycle
        p = list(range(n)); rng.shuffle(p); E = {(min(p[i], p[(i + 1) % n]), max(p[i], p[(i + 1) % n])) for i in range(n)}
        while len(E) < n + extra:
            a, b = rng.sample(range(n), 2); E.add((min(a, b), max(a, b)))
        out.append((f"ham_planted_n{n}", True, n, sorted(E)))
    for a, b in ((7, 8), (10, 11), (14, 15)):                             # complete bipartite, unequal sides: no cycle
        out.append((f"ham_bipartite_{a}_{b}", False, a + b, [(i, a + j) for i in range(a) for j in range(b)]))
    for m in (8, 12):                                                     # two cliques sharing one vertex: no cycle
        E = [(i, j) for i in range(m) for j in range(i + 1, m)] + [(i, j) for i in range(m - 1, 2 * m - 1) for j in range(i + 1, 2 * m - 1)]
        out.append((f"ham_cutvertex_{2*m-1}", False, 2 * m - 1, E))
    return out

# ---------------------------------------------------------------- XOR system with a few free dimensions plus clauses
def linfew(n, k, nclauses, seed):
    rng = random.Random(seed); cl = []
    for _ in range(n - k): cl += gen.xor_clauses(rng.sample(range(1, n + 1), 3), rng.randrange(2))
    for _ in range(nclauses):
        vs = rng.sample(range(1, n + 1), 3); cl.append([v if rng.random() < .5 else -v for v in vs])
    return cl
def linfew_solver(clauses, maxfree=22):
    nv = max(abs(l) for c in clauses for l in c); xors, used = structsat.find_xors(clauses)
    if not xors: return None
    ok, piv = structsat.gauss(xors, nv)
    if not ok: return False
    free = [v for v in range(1, nv + 1) if v not in piv]
    if len(free) > maxfree: return None
    k = len(free); L = 1 << k; MASK = (1 << L) - 1; tt = {}
    for j, v in enumerate(free):
        b = 1 << j; tt[v] = (MASK // ((1 << (2 * b)) - 1)) * (((1 << b) - 1) << b)
    for hi in sorted(piv):
        r = piv[hi]; t = MASK if r & 1 else 0
        for v in range(1, hi):
            if (r >> v) & 1: t ^= tt[v]
        tt[hi] = t
    alive = MASK
    for i, c in enumerate(clauses):
        if i in used: continue
        t = 0
        for l in c: t |= tt[l] if l > 0 else tt[-l] ^ MASK
        alive &= t
        if not alive: return False
    return True

# ---------------------------------------------------------------- harness
def run(cmd):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    try: out = subprocess.run(cmd, capture_output=True, text=True, timeout=TO * 8).stdout
    except subprocess.TimeoutExpired: return None, None
    return out, resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime - r0.ru_utime
def timed(f):
    t = time.process_time(); r = f(); return r, (time.process_time() - t) * 1000
S = lambda r: "SAT" if r else "UNSAT"
rows = []
def add(name, exp, cl, special, note): rows.append((name, exp, cl, special, note))

for n in (8, 16, 32, 64):
    c, cl = cec('adder', n); add(f"cec_adder_{n}b_rc_vs_ks", False, cl, (lambda c=c: sweep(c)), "sweeping (circuit)")
for n in (5, 6, 8, 10):
    c, cl = cec('mult', n); add(f"cec_mult_{n}x{n}_arr_vs_wal", False, cl, (lambda c=c: simulate(c)), "simulate all inputs (circuit)")
for n, N in ((14, 16127 * 16139), (14, 268435399), (16, 65521 * 65519), (18, 262139 * 262133)):
    add(f"mult_target_{2*n}b_{'sat' if N % 16127 == 0 or N % 65521 == 0 or N % 262139 == 0 else 'unsat'}", None, mult_target(n, N), None, "no generic shortcut tried")
for n in (6, 8, 10, 14):
    cl = chessboard(n, False); add(f"chessboard_{n}x{n}_unsat", False, cl, (lambda cl=cl: matching_solver(cl)), "perfect matching (from CNF)")
cl = chessboard(14, True); add("chessboard_14x14_sat", True, cl, (lambda cl=cl: matching_solver(cl)), "perfect matching (from CNF)")
for name, exp, n, E in ham_graphs():
    add(name, exp, ham_cnf(n, E), (lambda n=n, E=E: ham_solver(n, E)), "graph search (graph)")
for n, k, m, sd in ((100, 14, 60, 1), (160, 16, 90, 2), (240, 18, 120, 3), (240, 18, 160, 4)):
    cl = linfew(n, k, m, sd); add(f"xor_plus_clauses_n{n}_free{k}_s{sd}", None, cl, (lambda cl=cl: linfew_solver(cl)), "Gauss + enumerate (from CNF)")

print(f"{'instance':32} {'vars':>5} {'clauses':>7} | {'specialised':>20} | {'CaDiCaL':>16} | {'Kissat':>16} | method")
for name, exp, cl, special, note in rows:
    fn = f"cnf/{name}.cnf"; gen.write(cl, fn); nv = max(abs(l) for c in cl for l in c)
    if special:
        r, ms = timed(special); sp = f"{S(r) if r is not None else 'gave up'} {ms:9.2f} ms"; sa = S(r) if r is not None else None
    else: sp = "-"; sa = None
    o, _ = run(['perl', '-e', f'alarm {int(TO*8)}; exec @ARGV', V, 'run_cadical.py', fn]); c = o.split() if o else None
    cok = c and len(c) == 2 and float(c[1]) < TO; cad = f"{c[0]} {float(c[1])*1000:9.1f} ms" if cok else f"> {TO:.0f} s"
    o, cpu = run(['kissat', '-q', f'--time={int(TO)}', fn])
    ka = 'SAT' if o and 's SATISFIABLE' in o else 'UNSAT' if o and 's UNSATISFIABLE' in o else None
    kis = f"{ka} {cpu*1000:9.1f} ms" if ka else f"> {TO:.0f} s"
    ans = {a for a in (sa, c[0] if cok else None, ka) if a}
    bad = len(ans) > 1 or (exp is not None and ans and ans != {S(exp)})
    print(f"{name:32} {nv:5d} {len(cl):7d} | {sp:>20} | {cad:>16} | {kis:>16} | {note}{'   << DISAGREE' if bad else ''}", flush=True)
