#!/usr/bin/env python3
"""
Modular matrix inversion via SAT (Python port of the task from vzhn/z3-inv-matrix).

Given an integer n x n matrix A and a modulus m >= 2, find B with entries in [0, m)
such that  A * B = I (mod m).  The encoding is exact:

    SAT    <=>  A is invertible mod m  (gcd(det A, m) = 1); the decoded B is the inverse
    UNSAT  <=>  A is not invertible mod m

Encoding (shares the adder machinery of invmatrix.py):
  * A is reduced mod m; every B[k][j] is an unsigned bit-vector of ceil(log2 m) bits
    with a constant comparator B[k][j] <= m-1 (omitted when m is a power of two);
  * every entry is the exact integer equation
        sum_k A[i][k] * B[k][j]  -  m * Q[i][j]  =  delta_ij
    with a fresh unsigned quotient Q[i][j] wide enough for the largest possible sum;
  * the equation is compressed with full/half adders, exactly as in invmatrix.py.

Subcommands:
  gen    -m A.txt --mod M -o out.cnf            DIMACS + out.cnf.map.json
  decode out.cnf.map.json SOLVER_OUTPUT         model -> B (checked: A*B = I mod M)
  solve  -m A.txt --mod M [--solver S ...]      gen + run solver(s) + decode
  random -n N --mod M [--seed S]                random matrix invertible mod M
"""
import argparse
import json
import math
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invmatrix import (CNF, SOLVERS, fmt_matrix, linear_eq, parse_matrix,  # noqa: E402
                       parse_model, run_solver)


# ---------------- arithmetic helpers ----------------
def det(a):
    """Exact integer determinant (Bareiss)."""
    m = [row[:] for row in a]
    n, sign, prev = len(m), 1, 1
    for k in range(n - 1):
        if m[k][k] == 0:
            for r in range(k + 1, n):
                if m[r][k]:
                    m[k], m[r] = m[r], m[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) // prev
        prev = m[k][k]
    return sign * m[n - 1][n - 1]


def inverse_mod_reference(a, mod):
    """Reference inverse mod m via adjugate = det * A^-1 (exact rationals). None if singular mod m."""
    n = len(a)
    d = det(a)
    if math.gcd(d, mod) != 1:
        return None
    # Gauss-Jordan over Q to get A^-1, then adj = d * A^-1 (integer)
    aug = [[Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(a)]
    for c in range(n):
        p = next(r for r in range(c, n) if aug[r][c] != 0)
        aug[c], aug[p] = aug[p], aug[c]
        pv = aug[c][c]
        aug[c] = [x / pv for x in aug[c]]
        for r in range(n):
            if r != c and aug[r][c] != 0:
                f = aug[r][c]
                aug[r] = [x - f * y for x, y in zip(aug[r], aug[c])]
    adj = [[int(aug[i][n + j] * d) for j in range(n)] for i in range(n)]
    dinv = pow(d, -1, mod)
    return [[(dinv * x) % mod for x in row] for row in adj]


def matmul_mod(a, b, mod):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % mod for j in range(n)] for i in range(n)]


def is_identity_mod(a, b, mod):
    n = len(a)
    return all(v == (1 % mod if i == j else 0) for i, row in enumerate(matmul_mod(a, b, mod)) for j, v in enumerate(row))


def random_invertible(n, mod, seed):
    rnd = random.Random(seed)
    while True:
        a = [[rnd.randrange(mod) for _ in range(n)] for _ in range(n)]
        if math.gcd(det(a), mod) == 1:
            return a


def prime_powers(m):
    out, p = [], 2
    while p * p <= m:
        if m % p == 0:
            q = 1
            while m % p == 0:
                m //= p
                q *= p
            out.append(q)
        p += 1
    if m > 1:
        out.append(m)
    return out


def crt(residues, moduli):
    x, mm = 0, 1
    for r, q in zip(residues, moduli):
        t = ((r - x) * pow(mm, -1, q)) % q
        x, mm = x + mm * t, mm * q
    return x % mm


# ---------------- encoding ----------------
def at_most_const(cnf, bits, c):
    """Unsigned bit-vector (LSB first) <= constant c."""
    w = len(bits)
    if c >= (1 << w) - 1:
        return
    for p in range(w):
        if not (c >> p) & 1:
            higher_ones = [q for q in range(p + 1, w) if (c >> q) & 1]
            cnf.add(-bits[p], *[-bits[q] for q in higher_ones])


def encode(a, mod):
    n = len(a)
    a = [[x % mod for x in row] for row in a]
    w = max(1, (mod - 1).bit_length())
    cnf = CNF()
    bv = [[[cnf.var() for _ in range(w)] for _ in range(n)] for _ in range(n)]
    for row in bv:
        for bits in row:
            at_most_const(cnf, bits, mod - 1)
    qbits_map = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            delta = 1 % mod if i == j else 0
            max_sum = sum(a[i][k] for k in range(n)) * (mod - 1)
            qmax = max(0, (max_sum - delta) // mod)
            qw = max(1, qmax.bit_length())
            q = [cnf.var() for _ in range(qw)]
            at_most_const(cnf, q, qmax)
            qbits_map[i][j] = q
            terms = [(a[i][k] << t, bv[k][j][t]) for k in range(n) if a[i][k] for t in range(w)]
            terms += [(-(mod << t), q[t]) for t in range(qw)]
            linear_eq(cnf, terms, delta)
    vmap = {'n': n, 'mod': mod, 'encoding': 'binary', 'width': w, 'A': a, 'B_bits': bv, 'Q_bits': qbits_map}
    return cnf, vmap


def exactly_one(cnf, lits):
    cnf.add(*lits)
    if len(lits) <= 32:
        for x in range(len(lits)):
            for y in range(x + 1, len(lits)):
                cnf.add(-lits[x], -lits[y])
    else:                                   # sequential counter
        r = [cnf.var() for _ in range(len(lits) - 1)]
        cnf.add(-lits[0], r[0])
        for i in range(1, len(lits) - 1):
            cnf.add(-lits[i], r[i]); cnf.add(-r[i - 1], r[i]); cnf.add(-lits[i], -r[i - 1])
        cnf.add(-lits[-1], -r[-1])


def encode_onehot(a, mod, columns=None):
    """Every value mod m is a one-hot vector. Row i of A times column j of B is a running
    sum s_k = s_{k-1} + A[i][k] * B[k][j] (mod m); one clause per (s_{k-1}, B) value pair.
    columns: encode only these columns of B (the columns of A*B = I are independent)."""
    n = len(a)
    a = [[x % mod for x in row] for row in a]
    columns = list(range(n)) if columns is None else list(columns)
    cnf = CNF()
    bv = [[[cnf.var() for _ in range(mod)] for _ in columns] for _ in range(n)]
    for row in bv:
        for vec in row:
            exactly_one(cnf, vec)
    for i in range(n):
        for jj, j in enumerate(columns):
            delta = 1 % mod if i == j else 0
            ks = [k for k in range(n) if a[i][k]]
            if not ks:
                if delta:
                    cnf.false()
                continue
            prev = None                      # None = constant 0
            for idx, k in enumerate(ks):
                c, bvec = a[i][k], bv[k][jj]
                last = idx == len(ks) - 1
                cur = None if last else [cnf.var() for _ in range(mod)]
                if cur is not None:
                    exactly_one(cnf, cur)
                for w in ([0] if prev is None else range(mod)):
                    pre = [] if prev is None else [-prev[w]]
                    for u in range(mod):
                        v = (w + c * u) % mod
                        if last:
                            if v != delta:
                                cnf.add(*pre, -bvec[u])
                        else:
                            cnf.add(*pre, -bvec[u], cur[v])
                prev = cur
    vmap = {'n': n, 'mod': mod, 'encoding': 'onehot', 'columns': columns, 'A': a, 'B_bits': bv}
    return cnf, vmap


def decode(vmap, true_vars):
    if vmap.get('encoding') == 'onehot':
        return [[next(u for u, v in enumerate(vec) if v in true_vars) for vec in row]
                for row in vmap['B_bits']]
    return [[sum(1 << t for t, v in enumerate(bits) if v in true_vars) for bits in row]
            for row in vmap['B_bits']]


# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    def common(p):
        p.add_argument('-m', '--matrix', required=True, help='text file, one row per line')
        p.add_argument('--mod', type=int, required=True, help='modulus m >= 2')
        p.add_argument('--encoding', choices=['onehot', 'binary'], default='onehot',
                       help='onehot: values mod m as one-hot vectors (default, much faster); '
                            'binary: bit-vectors with explicit quotient')

    g = sub.add_parser('gen'); common(g)
    g.add_argument('-o', '--out', required=True)
    g.add_argument('--column', type=int, nargs='+', default=None,
                   help='encode only these columns of B (0-based; onehot only)')
    s = sub.add_parser('solve'); common(s)
    s.add_argument('-o', '--out', default=None)
    s.add_argument('--solver', nargs='+', default=['cadical'],
                   help=f'one or more of {", ".join(SOLVERS)} or a full command')
    s.add_argument('--split', action='store_true',
                   help='solve one small formula per (prime power of m, column of B) and combine by CRT')
    s.add_argument('--check', action='store_true',
                   help='also compare with an inverse computed by exact linear algebra')
    d = sub.add_parser('decode'); d.add_argument('map'); d.add_argument('model')
    r = sub.add_parser('random')
    r.add_argument('-n', type=int, required=True)
    r.add_argument('--mod', type=int, required=True)
    r.add_argument('--seed', type=int, default=None)
    args = ap.parse_args()

    if args.cmd == 'random':
        print(fmt_matrix(random_invertible(args.n, args.mod, args.seed)))
        return
    if args.cmd == 'decode':
        vmap = json.load(open(args.map))
        status, tv = parse_model(open(args.model).read())
        if status != 'SATISFIABLE':
            print(status or 'no result found in solver output')
            sys.exit(1)
        b = decode(vmap, tv)
        assert is_identity_mod(vmap['A'], b, vmap['mod']), 'decoded matrix is not an inverse'
        print(fmt_matrix(b))
        return

    if args.mod < 2:
        sys.exit('--mod must be >= 2')
    a = parse_matrix(open(args.matrix).read())
    if args.cmd == 'solve' and args.split:
        return solve_split(a, args)
    if args.encoding == 'onehot':
        cnf, vmap = encode_onehot(a, args.mod, getattr(args, 'column', None))
    else:
        if getattr(args, 'column', None):
            sys.exit('--column needs --encoding onehot')
        cnf, vmap = encode(a, args.mod)
    out = args.out or (args.matrix + f'.mod{args.mod}.cnf')
    with open(out, 'w') as fh:
        fh.write(cnf.dimacs([f'modular matrix inversion A*B = I mod {args.mod}, n={len(a)}, encoding={args.encoding}']))
    with open(out + '.map.json', 'w') as fh:
        json.dump(vmap, fh)
    print(f'== cnf ==\nn={len(a)}, mod={args.mod}, encoding={args.encoding}, {cnf.nvars} vars, {len(cnf.clauses)} clauses -> {out}')
    if args.cmd == 'gen':
        return

    print('\n== input ==\n' + fmt_matrix(a))
    ref = inverse_mod_reference(a, args.mod) if args.check else None
    if args.check:
        d = det(a)
        print(f'\n== check ==\ndet = {d}, gcd(det, {args.mod}) = {math.gcd(d, args.mod)} -> '
              + ('invertible' if ref else 'NOT invertible, expect UNSAT'))
    result = None
    for name in args.solver:
        try:
            (status, tv), dt = run_solver(name, out)
        except FileNotFoundError as e:
            print(f'\n{name}: skipped ({e})')
            continue
        print(f'\n{name}: {status}  {dt * 1000:.0f} ms')
        if args.check:
            assert (status == 'SATISFIABLE') == (ref is not None), f'{name}: answer contradicts det check'
        if status == 'SATISFIABLE':
            b = decode(vmap, tv)
            assert is_identity_mod(vmap['A'], b, args.mod), f'{name}: decoded matrix is not an inverse'
            if ref is not None:
                assert b == ref, f'{name}: differs from reference inverse'
            if result is None:
                result = b
                print('== output ==\n' + fmt_matrix(b))
                print('\n== input * output mod m ==\n' + fmt_matrix(matmul_mod(a, b, args.mod)))
            else:
                assert b == result, 'solvers disagree (inverse mod m is unique)'


def solve_split(a, args):
    if args.encoding != 'onehot':
        sys.exit('--split needs --encoding onehot')
    n, m = len(a), args.mod
    qs = prime_powers(m)
    base = args.out or (args.matrix + f'.mod{m}')
    print(f'== split ==\nmod {m} = ' + ' * '.join(map(str, qs)) + f', {len(qs) * n} formulas')
    print('\n== input ==\n' + fmt_matrix(a))
    ref = inverse_mod_reference(a, m) if args.check else None
    if args.check:
        d = det(a)
        print(f'\n== check ==\ndet = {d}, gcd(det, {m}) = {math.gcd(d, m)} -> '
              + ('invertible' if ref else 'NOT invertible, expect UNSAT'))
    paths = {}
    for q in qs:
        for j in range(n):
            cnf, vmap = encode_onehot(a, q, [j])
            path = f'{base}.q{q}.col{j}.cnf'
            with open(path, 'w') as fh:
                fh.write(cnf.dimacs([f'A * b = e_{j} mod {q}, n={n}']))
            with open(path + '.map.json', 'w') as fh:
                json.dump(vmap, fh)
            paths[q, j] = (path, vmap, cnf.nvars, len(cnf.clauses))
    biggest = max(paths.values(), key=lambda t: t[3])
    print(f'\nlargest formula: {biggest[2]} vars, {biggest[3]} clauses')
    result = None
    for name in args.solver:
        total, unsat, parts = 0.0, False, {}
        for (q, j), (path, vmap, _, _) in paths.items():
            try:
                (status, tv), dt = run_solver(name, path)
            except FileNotFoundError as e:
                print(f'\n{name}: skipped ({e})')
                break
            total += dt
            if status != 'SATISFIABLE':
                unsat = True
                break
            parts[q, j] = [row[0] for row in decode(vmap, tv)]
        else:
            if unsat:
                print(f'\n{name}: UNSATISFIABLE  {total * 1000:.0f} ms  (not invertible mod {m})')
                if args.check:
                    assert ref is None, f'{name}: UNSAT but matrix is invertible'
                continue
            b = [[crt([parts[q, j][k] for q in qs], qs) for j in range(n)] for k in range(n)]
            assert is_identity_mod(a, b, m), f'{name}: combined matrix is not an inverse'
            if ref is not None:
                assert b == ref, f'{name}: differs from reference inverse'
            print(f'\n{name}: SATISFIABLE  {total * 1000:.0f} ms total')
            if result is None:
                result = b
                print('== output ==\n' + fmt_matrix(b))
                print('\n== input * output mod m ==\n' + fmt_matrix(matmul_mod(a, b, m)))
            else:
                assert b == result, 'solvers disagree (inverse mod m is unique)'
            continue
        if unsat:
            print(f'\n{name}: UNSATISFIABLE  {total * 1000:.0f} ms  (not invertible mod {m})')


if __name__ == '__main__':
    main()
