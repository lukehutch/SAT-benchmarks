"""Benchmark families. Each returns (name, expected answer or None, clauses)."""
import random, itertools
def xor_clauses(vs, b):
    """clauses for x1 ^ ... ^ xk = b"""
    out = []
    for signs in itertools.product((0, 1), repeat=len(vs)):
        if sum(signs) % 2 != b:                       # forbid assignments of the wrong parity
            out.append([-v if s else v for v, s in zip(vs, signs)])
    return out
def tseitin(n, seed, sat):
    """Tseitin formula on a random 3-regular graph with n vertices (n even). Odd total charge = UNSAT."""
    rng = random.Random(seed)
    while True:
        pts = [v for v in range(n) for _ in range(3)]; rng.shuffle(pts)
        edges = set(); ok = True
        for i in range(0, len(pts), 2):
            a, b = pts[i], pts[i + 1]
            if a == b or (min(a, b), max(a, b)) in edges: ok = False; break
            edges.add((min(a, b), max(a, b)))
        if ok: break
    edges = sorted(edges); var = {e: i + 1 for i, e in enumerate(edges)}
    charge = [rng.randrange(2) for _ in range(n)]
    if sum(charge) % 2 == (0 if sat else 1): pass
    else: charge[0] ^= 1
    cl = []
    for v in range(n):
        cl += xor_clauses([var[e] for e in edges if v in e], charge[v])
    return f"tseitin_n{n}_{'sat' if sat else 'unsat'}", sat, cl
def php(holes):
    """holes+1 pigeons into holes holes: UNSAT"""
    P = holes + 1; x = lambda p, h: p * holes + h + 1
    cl = [[x(p, h) for h in range(holes)] for p in range(P)]
    for h in range(holes):
        for p in range(P):
            for q in range(p + 1, P): cl.append([-x(p, h), -x(q, h)])
    return f"php_{P}_{holes}", False, cl
def random3(n, seed, ratio=4.26):
    rng = random.Random(seed); cl = []
    for _ in range(int(n * ratio)):
        vs = rng.sample(range(1, n + 1), 3); cl.append([v if rng.random() < .5 else -v for v in vs])
    return f"random3sat_n{n}_s{seed}", None, cl
def write(cl, fn):
    nv = max(abs(l) for c in cl for l in c)
    with open(fn, 'w') as f:
        f.write(f"p cnf {nv} {len(cl)}\n")
        for c in cl: f.write(' '.join(map(str, c)) + " 0\n")
