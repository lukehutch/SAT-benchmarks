#!/usr/bin/env python3
"""
SAT encodings for exact synthesis of MOD_n^{m,r} circuits over B2 (or AIG/XAIG).

    MOD_n^{m,R}(x_1..x_n) = [ x_1 + ... + x_n mod m  in  R ]

Question encoded: "is there a circuit with exactly s binary gates computing f?"
The encoding follows Kojevnikov–Kulikov–Yaroslavtsev / Knuth (TAOCP 7.1.2) as used
in circuit_improvement (core/circuit_search.py), plus some extra reductions:

  * normal gates: every gate g has g(0,0)=0. Any B2 circuit can be normalised so
    (complements are pushed into successors). If f(0^n)=1 we synthesise ~f instead,
    which has the same B2-complexity. Consequently row t=0 of every truth table is 0
    and is dropped.
  * inputs and the output gate are constants in the formula (substituted, not variables).
  * non-degenerate gates (gate depends on both predecessors).
  * every gate except the output gate is used; every essential input is used.
  * optional symmetry breaking (see --sb):
      lex   : consecutive independent gates have lexicographically increasing fan-in pairs
      noreuse: forbid  g = op(j,k), g' = op(j,g) or op(k,g)   (g' could read j,k directly)
      inputs : input x_{i+1} is first used no earlier than x_i (valid since f is symmetric)
    --le gives a sound "is there a circuit of size <= s" formula (normalisation only),
    so a single UNSAT is a lower bound size(f) > s.
    "all used", "noreuse" are only valid for *minimum* circuits, so an UNSAT answer at
    size s means "no irredundant circuit of size exactly s". Find the optimum by
    increasing s from a lower bound: the first SAT size is the circuit complexity.

Usage:
  modsat.py gen    -n 5 -m 3 -r 1 -s 9  -o mod3_5_1_s9.cnf     # write DIMACS (+ .map.json)
  modsat.py decode mod3_5_1_s9.cnf.map.json  solver_output.txt  # model -> circuit
  modsat.py solve  -n 5 -m 3 -r 1 -s 9                         # gen + run solver + decode
  modsat.py search -n 5 -m 3 -r 1 --from 1 --to 12             # first SAT size = optimum

Solver: any DIMACS solver printing 'v' lines (cadical, kissat, ...). --solver "cadical -q".
"""
import argparse
import itertools
import json
import os
import shlex
import subprocess
import sys
import time
from itertools import combinations

# normal gate types (f(0,0)=0): bits (f01, f10, f11) -> name
GATE_NAMES = {
    (0, 0, 1): 'AND',      # a & b
    (0, 1, 0): 'GT',       # a & ~b
    (1, 0, 0): 'LT',       # ~a & b
    (1, 1, 1): 'OR',       # a | b
    (1, 1, 0): 'XOR',      # a ^ b
}
DEGENERATE = [(0, 0, 0), (0, 1, 1), (1, 0, 1)]   # const 0, a, b


def mod_function(n, m, residues):
    return [1 if (bin(t).count('1') % m) in residues else 0 for t in range(1 << n)]


def input_bit(t, i, n):
    # x_1 is the most significant bit, as in circuit_improvement
    return (t >> (n - 1 - i)) & 1


class Encoder:
    def __init__(self, n, s, truth_table, basis='b2', sb=('lex', 'noreuse', 'inputs'),
                 symmetric=True, allow_unused=False):
        assert len(truth_table) == 1 << n
        self.n, self.s = n, s
        self.negated_output = bool(truth_table[0])
        self.target = [b ^ self.negated_output for b in truth_table]
        self.basis = basis
        self.sb = set(sb)
        self.symmetric = symmetric
        self.allow_unused = allow_unused
        if allow_unused:
            assert not self.sb, '--le mode must be used without symmetry breaking'
        self.rows = list(range(1, 1 << n))         # row 0 is always 0 (normal gates)
        self.nvars = 0
        self.clauses = []
        self.gates = list(range(n, n + s))         # internal gate ids; inputs are 0..n-1
        self.out = n + s - 1
        self._build()

    # ---------- variable helpers ----------
    def new_var(self):
        self.nvars += 1
        return self.nvars

    def add(self, lits):
        """Add a clause; literals may be ints or Python bools (constants)."""
        out = []
        for l in lits:
            if l is True:
                return
            if l is False:
                continue
            out.append(l)
        if not out:
            raise ValueError('empty clause produced: instance trivially UNSAT')
        self.clauses.append(out)

    @staticmethod
    def neg(l):
        return (not l) if isinstance(l, bool) else -l

    def val(self, g, t):
        """Literal (or constant) for the value of node g on row t."""
        if g < self.n:
            return bool(input_bit(t, g, self.n))
        if g == self.out:
            return bool(self.target[t])
        return self.x[g][t]

    def exactly_one(self, lits):
        self.add(lits)
        self.at_most_one(lits)

    def at_most_one(self, lits):
        # sequential counter (Sinz)
        k = len(lits)
        if k <= 1:
            return
        if k <= 5:
            for a, b in combinations(lits, 2):
                self.add([-a, -b])
            return
        r = [self.new_var() for _ in range(k - 1)]
        self.add([-lits[0], r[0]])
        for i in range(1, k - 1):
            self.add([-lits[i], r[i]])
            self.add([-r[i - 1], r[i]])
            self.add([-lits[i], -r[i - 1]])
        self.add([-lits[k - 1], -r[k - 2]])

    # ---------- encoding ----------
    def _build(self):
        n, s = self.n, self.s
        if s == 0:
            raise ValueError('size 0 not supported')
        # selector: gate i reads pair (j,k), j<k<i
        self.sel = {i: {(j, k): self.new_var() for j, k in combinations(range(i), 2)} for i in self.gates}
        # gate type bits f01, f10, f11
        self.f = {i: [self.new_var() for _ in range(3)] for i in self.gates}
        # values on rows
        self.x = {i: {t: self.new_var() for t in self.rows} for i in self.gates if i != self.out}

        for i in self.gates:
            self.exactly_one(list(self.sel[i].values()))
            f01, f10, f11 = self.f[i]
            for d in DEGENERATE:                         # forbid degenerate types
                self.add([f01 if d[0] == 0 else -f01, f10 if d[1] == 0 else -f10, f11 if d[2] == 0 else -f11])
            if self.basis == 'aig':                     # no XOR
                self.add([-f01, -f10, f11])

        # semantics: sel(i,j,k) & x_j=b & x_k=c  ->  (x_i <-> f_i(b,c))
        for i in self.gates:
            fb = {(0, 1): self.f[i][0], (1, 0): self.f[i][1], (1, 1): self.f[i][2]}
            for (j, k), sv in self.sel[i].items():
                for t in self.rows:
                    xi, xj, xk = self.val(i, t), self.val(j, t), self.val(k, t)
                    for b in (0, 1):
                        lj = self.neg(xj) if b else xj        # "x_j != b" literal
                        if lj is True:
                            continue
                        for c in (0, 1):
                            lk = self.neg(xk) if c else xk
                            if lk is True:
                                continue
                            if (b, c) == (0, 0):
                                self.add([-sv, lj, lk, self.neg(xi)])
                            else:
                                ft = fb[(b, c)]
                                self.add([-sv, lj, lk, self.neg(xi), ft])
                                self.add([-sv, lj, lk, xi, -ft])

        # every internal non-output gate is used
        for g in self.gates:
            if g == self.out or self.allow_unused:
                continue
            self.add([sv for i in self.gates if i > g for (j, k), sv in self.sel[i].items() if g in (j, k)])
        # every essential input is used
        for v in range(n):
            bit = 1 << (n - 1 - v)
            if any(self.target[t] != self.target[t ^ bit] for t in range(1 << n)):
                self.add([sv for i in self.gates for (j, k), sv in self.sel[i].items() if v in (j, k)])

        if 'lex' in self.sb:
            # if gate i+1 does not read gate i, then pair(i) <= pair(i+1) (lex on (k, j)? use (j,k))
            for i in self.gates[:-1]:
                i2 = i + 1
                for (j, k), sv in self.sel[i].items():
                    for (j2, k2), sv2 in self.sel[i2].items():
                        if k2 == i:
                            continue
                        if (j2, k2) < (j, k):
                            self.add([-sv, -sv2])
        if 'noreuse' in self.sb:
            for g, g2 in combinations(self.gates, 2):
                for (j, k), sv in self.sel[g].items():
                    for p in ((j, g), (k, g)):
                        self.add([-sv, -self.sel[g2][p]])
        if 'inputs' in self.sb and self.symmetric:
            # used[v][i]: input v read by some gate <= i.  used[v+1][i] -> used[v][i]
            used = {}
            for v in range(n):
                prev = None
                for i in self.gates:
                    u = self.new_var()
                    direct = [sv for (j, k), sv in self.sel[i].items() if v in (j, k)]
                    # u <-> prev | OR(direct)
                    for d in direct:
                        self.add([-d, u])
                    if prev is not None:
                        self.add([-prev, u])
                    self.add([-u] + direct + ([prev] if prev is not None else []))
                    used[v, i] = u
                    prev = u
            for v in range(n - 1):
                for i in self.gates:
                    self.add([-used[v + 1, i], used[v, i]])

    # ---------- output ----------
    def var_map(self):
        return {
            'n': self.n, 's': self.s, 'negated_output': self.negated_output,
            'target': self.target, 'basis': self.basis,
            'sel': {str(i): [[j, k, v] for (j, k), v in d.items()] for i, d in self.sel.items()},
            'f': {str(i): v for i, v in self.f.items()},
        }

    def dimacs(self):
        mode = 'size<=s (unused gates allowed)' if self.allow_unused else 'size==s, irredundant'
        lines = [f'c exact synthesis: n={self.n} s={self.s} basis={self.basis} sb={sorted(self.sb)} mode={mode}',
                 f'c target (row t, x1=MSB; complemented if negated): {"".join(map(str, self.target))} negated_output={int(self.negated_output)}',
                 f'p cnf {self.nvars} {len(self.clauses)}']
        lines += [' '.join(map(str, c)) + ' 0' for c in self.clauses]
        return '\n'.join(lines) + '\n'


# ---------- decoding / verification ----------
def decode(vmap, true_vars):
    n, s = vmap['n'], vmap['s']
    gates = []
    for i in range(n, n + s):
        pair = [(j, k) for j, k, v in vmap['sel'][str(i)] if v in true_vars]
        assert len(pair) == 1, f'gate {i}: {pair}'
        bits = tuple(int(v in true_vars) for v in vmap['f'][str(i)])
        gates.append((i, pair[0][0], pair[0][1], bits))
    return gates


def simulate(n, gates, negated_output):
    res = []
    for t in range(1 << n):
        val = {v: input_bit(t, v, n) for v in range(n)}
        for i, j, k, (f01, f10, f11) in gates:
            a, b = val[j], val[k]
            val[i] = [[0, f01], [f10, f11]][a][b]
        res.append(val[gates[-1][0]] ^ negated_output)
    return res


def fmt_circuit(n, gates, negated_output):
    name = lambda g: f'x{g + 1}' if g < n else f'g{g - n + 1}'
    lines = []
    for i, j, k, bits in gates:
        op = GATE_NAMES.get(bits, str(bits))
        sym = {'AND': f'{name(j)} & {name(k)}', 'GT': f'{name(j)} & ~{name(k)}', 'LT': f'~{name(j)} & {name(k)}',
               'OR': f'{name(j)} | {name(k)}', 'XOR': f'{name(j)} ^ {name(k)}'}[op]
        lines.append(f'{name(i)} = {sym}')
    out = name(gates[-1][0])
    lines.append(f'out = {"~" if negated_output else ""}{out}')
    return '\n'.join(lines)


def parse_model(text):
    status, true_vars = None, set()
    for line in text.splitlines():
        if line.startswith('s '):
            status = line[2:].strip()
        elif line.startswith('v '):
            true_vars.update(int(x) for x in line[2:].split() if int(x) > 0)
    return status, true_vars


# ---------- CLI ----------
def build_encoder(a, s):
    residues = set(int(x) for x in str(a.r).split(','))
    tt = mod_function(a.n, a.m, residues)
    sb = [] if (a.sb == 'none' or a.le) else a.sb.split(',')
    return Encoder(a.n, s, tt, basis=a.basis, sb=sb, allow_unused=a.le), tt


def run_solver(a, enc, tt, path):
    with open(path, 'w') as fh:
        fh.write(enc.dimacs())
    t0 = time.time()
    p = subprocess.run(shlex.split(a.solver) + [path], capture_output=True, text=True)
    dt = time.time() - t0
    status, tv = parse_model(p.stdout)
    if status == 'SATISFIABLE':
        gates = decode(enc.var_map(), tv)
        assert simulate(a.n, gates, enc.negated_output) == tt, 'decoded circuit is WRONG'
        return status, dt, gates
    return status, dt, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    def common(p, size=True):
        p.add_argument('-n', type=int, required=True, help='number of inputs')
        p.add_argument('-m', type=int, default=3, help='modulus')
        p.add_argument('-r', default='0', help='residue(s), comma separated')
        if size:
            p.add_argument('-s', type=int, required=True, help='number of gates')
        p.add_argument('--basis', choices=['b2', 'aig'], default='b2')
        p.add_argument('--sb', default='lex,noreuse,inputs',
                       help='symmetry breaking: comma list of lex,noreuse,inputs or "none"')
        p.add_argument('--le', action='store_true',
                       help='sound "size <= s" formula: no symmetry breaking, unused gates allowed')

    g = sub.add_parser('gen'); common(g)
    g.add_argument('-o', required=True)
    so = sub.add_parser('solve'); common(so)
    so.add_argument('--solver', default='cadical -q')
    se = sub.add_parser('search'); common(se, size=False)
    se.add_argument('--from', dest='lo', type=int, default=1)
    se.add_argument('--to', dest='hi', type=int, default=30)
    se.add_argument('--solver', default='cadical -q')
    d = sub.add_parser('decode')
    d.add_argument('map'); d.add_argument('model')
    a = ap.parse_args()

    if a.cmd == 'gen':
        enc, _ = build_encoder(a, a.s)
        with open(a.o, 'w') as fh:
            fh.write(enc.dimacs())
        with open(a.o + '.map.json', 'w') as fh:
            json.dump(enc.var_map(), fh)
        print(f'{a.o}: {enc.nvars} vars, {len(enc.clauses)} clauses (map: {a.o}.map.json)')
    elif a.cmd == 'decode':
        vmap = json.load(open(a.map))
        status, tv = parse_model(open(a.model).read())
        if status != 'SATISFIABLE':
            print(status); return
        gates = decode(vmap, tv)
        assert simulate(vmap['n'], gates, vmap['negated_output']) == [b ^ vmap['negated_output'] for b in vmap['target']]
        print(fmt_circuit(vmap['n'], gates, vmap['negated_output']))
    elif a.cmd in ('solve', 'search'):
        sizes = [a.s] if a.cmd == 'solve' else range(a.lo, a.hi + 1)
        os.makedirs('cnf', exist_ok=True)
        for s in sizes:
            try:
                enc, tt = build_encoder(a, s)
            except ValueError as e:
                print(f's={s}: UNSATISFIABLE ({e})'); continue
            path = f'cnf/mod{a.m}_{a.n}_{a.r.replace(",", "-")}_s{s}.cnf'
            status, dt, gates = run_solver(a, enc, tt, path)
            print(f's={s}: {status}  ({enc.nvars} vars, {len(enc.clauses)} clauses, {dt:.2f}s)', flush=True)
            if gates:
                print(fmt_circuit(a.n, gates, enc.negated_output))
                if a.cmd == 'search':
                    return


if __name__ == '__main__':
    main()
