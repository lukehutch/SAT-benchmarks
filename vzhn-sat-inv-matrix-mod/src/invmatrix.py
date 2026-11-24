#!/usr/bin/env python3
"""
Integer matrix inversion via SAT.

Given an integer n x n matrix A, find an integer matrix B with  A * B = I.
Every entry of B is a w-bit two's complement bit-vector of fresh variables.
The equations are encoded EXACTLY over the integers (no wrap-around), so

    SAT    <=>  an integer inverse with all entries in [-2^(w-1), 2^(w-1)) exists
    UNSAT  <=>  no such inverse (det A != +-1, or w too small).

Encoding: since A is a constant, each equation  sum_k A[i][k] * B[k][j] = delta_ij
is a linear combination of bits with constant integer weights. Every weight is
split into powers of two (negative weights become  |c| * (not x) - |c|), the bits
are dropped into columns by weight and compressed with full/half adders
(Dadda/Wallace style), and the remaining bit of every column is fixed to the
corresponding bit of the right-hand side. Adders are Tseitin-encoded.

Subcommands:
  gen    -m A.txt [-w W] -o out.cnf         DIMACS + out.cnf.map.json
  decode out.cnf.map.json SOLVER_OUTPUT     model -> B (verified: A*B = I)
  solve  -m A.txt [-w W] [--solver NAME]    gen + run solver + decode
  random -n N [--steps K] [--seed S]        print a random unimodular matrix (det = +-1)

Width: -w W, or "-w auto" (default): the smallest width that is guaranteed to hold
the inverse if it exists (Hadamard bound on the cofactors), so UNSAT is a proof
that A has no integer inverse.
"""
import argparse
import json
import math
import os
import random
import shlex
import shutil
import subprocess
import sys
import time

SOLVERS = {
    'cadical': 'cadical -q',
    'kissat': 'kissat -q',
    'cryptominisat5': 'cryptominisat5 --verb 0',
    'minisat': 'minisat -verb=0',   # writes model to a file, handled specially
    'z3': 'z3 -dimacs',
}


# ---------------- matrix helpers ----------------
def parse_matrix(text):
    rows = [list(map(int, line.split())) for line in text.splitlines() if line.strip()]
    n = len(rows)
    if any(len(r) != n for r in rows):
        raise ValueError('matrix must be square')
    return rows


def fmt_matrix(m):
    width = max(len(str(x)) for r in m for x in r)
    return '\n'.join(' '.join(str(x).rjust(width) for x in r) for r in m)


def matmul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def is_identity(m):
    return all(m[i][j] == (1 if i == j else 0) for i in range(len(m)) for j in range(len(m)))


def auto_width(a):
    """Width that surely holds A^-1 if it is integer: |A^-1_ij| = |adj_ij| <= product of the
    n-1 largest row norms of A (Hadamard bound on the cofactor)."""
    n = len(a)
    norms = sorted((math.sqrt(sum(x * x for x in r)) for r in a), reverse=True)
    bound = int(math.prod(norms[:n - 1]) + 1e-6) if n > 1 else 1
    return max(2, bound.bit_length() + 1)


def random_unimodular(n, steps, seed, maxmul=2):
    rnd = random.Random(seed)
    m = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for _ in range(steps):
        i, j = rnd.sample(range(n), 2)
        c = rnd.choice([x for x in range(-maxmul, maxmul + 1) if x])
        m[i] = [x + c * y for x, y in zip(m[i], m[j])]
    rnd.shuffle(m)
    for r in range(n):
        if rnd.random() < 0.5:
            m[r] = [-x for x in m[r]]
    return m


# ---------------- CNF builder ----------------
class CNF:
    def __init__(self):
        self.nvars = 0
        self.clauses = []

    def var(self):
        self.nvars += 1
        return self.nvars

    def add(self, *c):
        self.clauses.append(list(c))

    def false(self):
        v = self.var()
        self.add(v)
        self.add(-v)

    def xor3(self, a, b, c):
        s = self.var()
        # s <-> a ^ b ^ c : one clause per assignment of (a, b, c)
        for ta in (0, 1):
            for tb in (0, 1):
                for tc in (0, 1):
                    blocking = [-a if ta else a, -b if tb else b, -c if tc else c]
                    self.add(*blocking, s if (ta ^ tb ^ tc) else -s)
        return s

    def maj(self, a, b, c):
        m = self.var()
        self.add(-a, -b, m); self.add(-a, -c, m); self.add(-b, -c, m)
        self.add(a, b, -m); self.add(a, c, -m); self.add(b, c, -m)
        return m

    def xor2(self, a, b):
        s = self.var()
        self.add(-a, -b, -s); self.add(a, b, -s); self.add(a, -b, s); self.add(-a, b, s)
        return s

    def and2(self, a, b):
        c = self.var()
        self.add(-c, a); self.add(-c, b); self.add(-a, -b, c)
        return c

    def dimacs(self, comments=()):
        out = [f'c {x}' for x in comments]
        out.append(f'p cnf {self.nvars} {len(self.clauses)}')
        out += [' '.join(map(str, c)) + ' 0' for c in self.clauses]
        return '\n'.join(out) + '\n'


def linear_eq(cnf, terms, rhs):
    """Constrain  sum(c * x for c, x in terms) == rhs  exactly; x are literals (bits)."""
    cols = {}
    const = 0
    for c, x in terms:
        if c == 0:
            continue
        if c < 0:
            const += c          # c*x = |c|*(1-x) + c  = |c|*(~x) - |c|
            c, x = -c, -x
        p = 0
        while c:
            if c & 1:
                cols.setdefault(p, []).append(x)
            c >>= 1
            p += 1
    t = rhs - const
    if t < 0:
        cnf.false()
        return
    p = 0
    while cols or t:
        col = cols.pop(p, [])
        while len(col) >= 3:
            a, b, c = col.pop(), col.pop(), col.pop()
            col.insert(0, cnf.xor3(a, b, c))
            cols.setdefault(p + 1, []).append(cnf.maj(a, b, c))
        if len(col) == 2:
            a, b = col
            col = [cnf.xor2(a, b)]
            cols.setdefault(p + 1, []).append(cnf.and2(a, b))
        bit = t & 1
        if col:
            cnf.add(col[0] if bit else -col[0])
        elif bit:
            cnf.false()
            return
        t >>= 1
        p += 1


def encode(a, w):
    n = len(a)
    cnf = CNF()
    # B[k][j] bits, LSB first; bit w-1 has weight -2^(w-1)
    bv = [[[cnf.var() for _ in range(w)] for _ in range(n)] for _ in range(n)]
    weights = [1 << t for t in range(w - 1)] + [-(1 << (w - 1))]
    for i in range(n):
        for j in range(n):
            terms = [(a[i][k] * weights[t], bv[k][j][t]) for k in range(n) if a[i][k] for t in range(w)]
            linear_eq(cnf, terms, 1 if i == j else 0)
    vmap = {'n': n, 'width': w, 'A': a, 'B_bits': bv}
    return cnf, vmap


# ---------------- decoding ----------------
def parse_model(text):
    status, true_vars = None, set()
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('s '):
            status = line[2:].strip()
        elif line in ('sat', 'unsat', 'SAT', 'UNSAT', 'SATISFIABLE', 'UNSATISFIABLE'):  # z3 / minisat
            status = 'SATISFIABLE' if line.lower().startswith('sat') else 'UNSATISFIABLE'
        elif line.startswith('v '):
            true_vars.update(int(x) for x in line[2:].split() if int(x) > 0)
        elif status == 'SATISFIABLE' and line and line.lstrip('-').split()[0].isdigit():
            true_vars.update(int(x) for x in line.split() if int(x) > 0)   # minisat/z3 bare model
    return status, true_vars


def decode(vmap, true_vars):
    w = vmap['width']
    b = []
    for row in vmap['B_bits']:
        out = []
        for bits in row:
            v = sum(1 << t for t in range(w - 1) if bits[t] in true_vars)
            if bits[w - 1] in true_vars:
                v -= 1 << (w - 1)
            out.append(v)
        b.append(out)
    return b


def run_solver(name_or_cmd, cnf_path):
    cmd = SOLVERS.get(name_or_cmd, name_or_cmd)
    exe = shlex.split(cmd)[0]
    if not shutil.which(exe):
        raise FileNotFoundError(f'solver "{exe}" not found in PATH')
    t0 = time.time()
    if exe == 'minisat':
        res = cnf_path + '.res'
        p = subprocess.run(shlex.split(cmd) + [cnf_path, res], capture_output=True, text=True)
        text = open(res).read() if os.path.exists(res) else p.stdout
    else:
        p = subprocess.run(shlex.split(cmd) + [cnf_path], capture_output=True, text=True)
        text = p.stdout
    return parse_model(text), time.time() - t0


# ---------------- CLI ----------------
def build(args):
    a = parse_matrix(open(args.matrix).read())
    w = auto_width(a) if args.width == 'auto' else int(args.width)
    cnf, vmap = encode(a, w)
    comments = [f'integer matrix inversion A*B = I, n={len(a)}, width={w} (exact, no overflow)']
    return a, w, cnf, vmap, comments


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    def common(p):
        p.add_argument('-m', '--matrix', required=True, help='text file, one row per line')
        p.add_argument('-w', '--width', default='auto', help='bit width of B entries, or "auto"')

    g = sub.add_parser('gen', help='write DIMACS + variable map'); common(g)
    g.add_argument('-o', '--out', required=True)
    s = sub.add_parser('solve', help='gen + run solver(s) + decode'); common(s)
    s.add_argument('-o', '--out', default=None, help='CNF path (default: temp next to matrix)')
    s.add_argument('--solver', nargs='+', default=['cadical'],
                   help=f'one or more of {", ".join(SOLVERS)} or a full command')
    d = sub.add_parser('decode', help='solver output -> B'); d.add_argument('map'); d.add_argument('model')
    r = sub.add_parser('random', help='random unimodular matrix')
    r.add_argument('-n', type=int, required=True)
    r.add_argument('--steps', type=int, default=None, help='elementary row operations (default 3n)')
    r.add_argument('--seed', type=int, default=None)
    args = ap.parse_args()

    if args.cmd == 'random':
        print(fmt_matrix(random_unimodular(args.n, args.steps or 3 * args.n, args.seed)))
        return

    if args.cmd == 'decode':
        vmap = json.load(open(args.map))
        status, tv = parse_model(open(args.model).read())
        if status != 'SATISFIABLE':
            print(status or 'no result found in solver output')
            sys.exit(1)
        b = decode(vmap, tv)
        assert is_identity(matmul(vmap['A'], b)), 'decoded matrix is not an inverse'
        print(fmt_matrix(b))
        return

    a, w, cnf, vmap, comments = build(args)
    out = args.out or (args.matrix + f'.w{w}.cnf')
    with open(out, 'w') as fh:
        fh.write(cnf.dimacs(comments))
    with open(out + '.map.json', 'w') as fh:
        json.dump(vmap, fh)
    print(f'== cnf ==\nn={len(a)}, width={w}, {cnf.nvars} vars, {len(cnf.clauses)} clauses -> {out}')
    if args.cmd == 'gen':
        return

    print('\n== input ==\n' + fmt_matrix(a))
    result = None
    for name in args.solver:
        try:
            (status, tv), dt = run_solver(name, out)
        except FileNotFoundError as e:
            print(f'\n{name}: skipped ({e})')
            continue
        print(f'\n{name}: {status}  {dt * 1000:.0f} ms')
        if status == 'SATISFIABLE':
            b = decode(vmap, tv)
            assert is_identity(matmul(a, b)), f'{name}: decoded matrix is not an inverse'
            if result is None:
                result = b
                print('== output ==\n' + fmt_matrix(b))
            else:
                assert b == result, 'solvers disagree (inverse is unique)'


if __name__ == '__main__':
    main()
