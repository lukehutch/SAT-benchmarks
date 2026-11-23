#!/usr/bin/env python3
"""
Generate DIMACS formulas for the open MOD_n^{3,r} circuit-size cases.

Knuth's conjecture (TAOCP 7.1.2, ex. 480):
    size(MOD_n^{3,r}) = 3n - 5 - [(n + r) = 0 mod 3]      for n >= 3.
The upper bound is known for every n (Kulikov-Pechenev-Slezkin 2021; circuits in
circuit_improvement/circuits/mod3). Exact values are known for n <= 5 and for
(n=6, r=0) = 12. Everything else is open: the open question for each case is
whether a circuit with UB-1 gates exists.

Two kinds of formula per case (choose with --mode):

  le : ONE formula "is there a circuit of size <= UB-1" (no symmetry breaking,
       unused gates allowed). UNSAT  ==>  size = UB, conjecture proved for that case.
       Sound but slow.

  sb : formulas "is there an irredundant circuit of size exactly s" with symmetry
       breaking, one file per s in [--min-size, UB-1]. Much faster per file, but
       you need UNSAT for EVERY s in that range (down to a size you know is
       impossible) to conclude size = UB. Any SAT gives a circuit beating the
       conjecture (decode with: modsat.py decode FILE.map.json SOLVER_OUTPUT).

Examples:
  gen_open_cases.py --out formulas                    # n=6,7,8, both modes
  gen_open_cases.py --n 6 --mode le --out formulas
  gen_open_cases.py --n 9 10 --r 1 --mode sb --min-size 20 --gzip --out big
  gen_open_cases.py --list                            # just print the cases
"""
import argparse
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modsat import Encoder, mod_function  # noqa: E402

KNOWN_EXACT = {(3, 0): 3, (3, 1): 4, (3, 2): 4,
               (4, 0): 7, (4, 1): 7, (4, 2): 6,
               (5, 0): 10, (5, 1): 9, (5, 2): 10,
               (6, 0): 12}


def upper_bound(n, r):
    return 3 * n - 5 - (1 if (n + r) % 3 == 0 else 0)


def open_cases(ns, rs):
    return [(n, r, upper_bound(n, r)) for n in ns for r in rs if (n, r) not in KNOWN_EXACT]


def write(enc, path, gz):
    path = path + ('.gz' if gz else '')
    opener = gzip.open if gz else open
    with opener(path, 'wt') as fh:
        fh.write(enc.dimacs())
    with open(path + '.map.json', 'w') as fh:
        json.dump(enc.var_map(), fh)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--n', type=int, nargs='+', default=[6, 7, 8])
    ap.add_argument('--r', type=int, nargs='+', default=[0, 1, 2])
    ap.add_argument('--mode', choices=['le', 'sb', 'both'], default='both')
    ap.add_argument('--min-size', type=int, default=None,
                    help='smallest s for sb mode (default: UB-3)')
    ap.add_argument('--basis', choices=['b2', 'aig'], default='b2')
    ap.add_argument('--gzip', action='store_true')
    ap.add_argument('--out', default='formulas')
    ap.add_argument('--list', action='store_true', help='only list the open cases')
    a = ap.parse_args()

    cases = open_cases(a.n, a.r)
    if a.list:
        for n, r, ub in cases:
            print(f'MOD_{n}^(3,{r}): best known {ub}, open: is there a circuit of size {ub - 1}?')
        return

    os.makedirs(a.out, exist_ok=True)
    manifest = []
    for n, r, ub in cases:
        tt = mod_function(n, 3, {r})
        target = ub - 1
        jobs = []
        if a.mode in ('le', 'both'):
            jobs.append(('le', target))
        if a.mode in ('sb', 'both'):
            lo = a.min_size if a.min_size is not None else ub - 3
            jobs += [('sb', s) for s in range(max(lo, n - 1), target + 1)]
        for mode, s in jobs:
            if mode == 'le':
                enc = Encoder(n, s, tt, basis=a.basis, sb=[], allow_unused=True)
                name = f'mod3_n{n}_r{r}_le{s}.cnf'
                meaning = f'UNSAT => size(MOD_{n}^(3,{r})) > {s}, i.e. = {ub}'
            else:
                enc = Encoder(n, s, tt, basis=a.basis, sb=['lex', 'noreuse', 'inputs'])
                name = f'mod3_n{n}_r{r}_eq{s}_sb.cnf'
                meaning = f'UNSAT => no irredundant circuit with exactly {s} gates'
            path = write(enc, os.path.join(a.out, name), a.gzip)
            manifest.append({'file': os.path.basename(path), 'n': n, 'm': 3, 'r': r, 'size': s,
                             'mode': mode, 'best_known': ub, 'vars': enc.nvars,
                             'clauses': len(enc.clauses), 'meaning': meaning})
            print(f'{path}: {enc.nvars} vars, {len(enc.clauses)} clauses', flush=True)

    mpath = os.path.join(a.out, 'manifest.json')
    old = json.load(open(mpath)) if os.path.exists(mpath) else []
    files = {m['file'] for m in manifest}
    json.dump([m for m in old if m['file'] not in files] + manifest, open(mpath, 'w'), indent=1)
    print(f'manifest: {mpath}')


if __name__ == '__main__':
    main()
