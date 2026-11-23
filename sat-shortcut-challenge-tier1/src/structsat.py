"""A structure-recognising front end for SAT. It reads plain CNF (it is NOT told the family) and looks for
two kinds of structure before falling back to CaDiCaL:
  1. XOR constraints written out as clauses  -> Gaussian elimination over GF(2);
  2. at-most-one groups against positive clauses (pigeonhole shape) -> a bipartite matching bound.
Returns (answer, model or None, method)."""
import sys, time
from collections import defaultdict
from pysat.solvers import Cadical153

def find_xors(clauses, kmax=6):
    groups = defaultdict(list)
    for i, c in enumerate(clauses):
        if len(c) <= kmax and len({abs(l) for l in c}) == len(c):
            groups[frozenset(abs(l) for l in c)].append(i)
    xors = []; used = set()
    for vs, idx in groups.items():
        k = len(vs)
        par = {sum(1 for l in clauses[i] if l < 0) % 2 for i in idx}
        distinct = {tuple(sorted(clauses[i])) for i in idx}
        if len(par) == 1 and len(distinct) == 1 << (k - 1):
            xors.append((sorted(vs), 1 - par.pop())); used.update(idx)
    return xors, used

def gauss(xors, nv):
    """rows as ints: bit v = variable v, bit 0 = right-hand side. Returns (consistent, pivots dict var->row)."""
    piv = {}
    for vs, b in xors:
        r = b
        for v in vs: r ^= 1 << v
        while True:
            hi = r.bit_length() - 1
            if hi <= 0: break
            if hi in piv: r ^= piv[hi]
            else: piv[hi] = r; break
        if r == 1: return False, None                 # 0 = 1
    return True, piv

def xor_model(piv, nv):
    val = [0] * (nv + 1)
    for hi in sorted(piv):                            # rows only involve variables below their pivot
        r = piv[hi]; s = r & 1
        for v in range(1, hi):
            if (r >> v) & 1: s ^= val[v]
        val[hi] = s
    return val

def matching_bound(clauses):
    """Sound UNSAT test: positive clauses whose variables each lie in at most one of them, against groups of
    variables that are pairwise exclusive. If the clauses cannot be matched to distinct groups, UNSAT."""
    neg = defaultdict(set); pos = []
    for c in clauses:
        if len(c) == 2 and c[0] < 0 and c[1] < 0:
            a, b = -c[0], -c[1]; neg[a].add(b); neg[b].add(a)
        elif all(l > 0 for l in c): pos.append(c)
    if not pos or not neg: return False
    seen = defaultdict(int)
    for c in pos:
        for v in c: seen[v] += 1
    pos = [c for c in pos if all(seen[v] == 1 for v in c)]
    if not pos: return False
    comp = {}; ncomp = 0                               # connected components that are cliques
    for v in list(neg):
        if v in comp: continue
        stack = [v]; mem = []
        comp[v] = ncomp
        while stack:
            u = stack.pop(); mem.append(u)
            for x in neg[u]:
                if x not in comp: comp[x] = ncomp; stack.append(x)
        if any(len(neg[u]) != len(mem) - 1 for u in mem):
            for u in mem: comp[u] = None               # not a clique: unusable
        ncomp += 1
    adj = []
    for c in pos:
        if any(comp.get(v) is None for v in c): return False   # a variable outside every exclusive group could serve freely
        adj.append(sorted({comp[v] for v in c}))
    match = {}
    def aug(i, vis):
        for g in adj[i]:
            if g in vis: continue
            vis.add(g)
            if g not in match or aug(match[g], vis): match[g] = i; return True
        return False
    sys.setrecursionlimit(100000)
    return sum(1 for i in range(len(adj)) if aug(i, set())) < len(adj)

def solve(clauses):
    nv = max(abs(l) for c in clauses for l in c)
    xors, used = find_xors(clauses)
    if xors:
        ok, piv = gauss(xors, nv)
        if not ok: return False, None, "xor-gauss"
        if len(used) == len(clauses):
            val = xor_model(piv, nv)
            return True, [v if val[v] else -v for v in range(1, nv + 1)], "xor-gauss"
    if matching_bound(clauses): return False, None, "matching"
    s = Cadical153(bootstrap_with=clauses)
    r = s.solve(); m = s.get_model() if r else None; s.delete()
    return r, m, "cadical-fallback"

def read(fn):
    cl = []
    for line in open(fn):
        if line[0] in 'pc': continue
        c = [int(x) for x in line.split()[:-1]]
        if c: cl.append(c)
    return cl

if __name__ == "__main__":
    cl = read(sys.argv[1]); t = time.process_time()
    r, m, how = solve(cl); dt = time.process_time() - t
    if r: assert all(any((l > 0) == (m[abs(l) - 1] > 0) for l in c) for c in cl), "model check failed"
    print(("SAT" if r else "UNSAT"), how, f"{dt:.4f}")
