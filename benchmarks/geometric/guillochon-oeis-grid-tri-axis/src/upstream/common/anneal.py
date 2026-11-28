#!/usr/bin/env python3
"""Simulated annealing for "paint as many primary variables as possible with no forbidden set fully painted",
reading the forbidden sets straight from a generator's CNF (its all-negative clauses over variables 1..P).

    python anneal.py instance.cnf P SECONDS [seed]  > model.txt

Prints the best verified-feasible set as a model ("v ..." line; aux variables omitted) and its size on stderr.
Check the result with the sequence's verify.py, as always.  Needs numpy.
"""
import sys
import time

import numpy as np


def main():
    path, P, secs = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 1)
    confs = []
    for line in open(path):
        if line[0] in "cp":
            continue
        lits = list(map(int, line.split()))[:-1]
        if lits and all(-P <= l < 0 for l in lits) and len(lits) > 1:
            confs.append([-l - 1 for l in lits])
    C = len(confs)
    size = np.array([len(c) for c in confs], dtype=np.int32)
    inc = [[] for _ in range(P)]
    for k, c in enumerate(confs):
        for p in c:
            inc[p].append(k)
    inc = [np.array(i, dtype=np.int64) for i in inc]
    cnt = np.zeros(C, dtype=np.int32)
    x = np.zeros(P, dtype=bool)
    viol = 0
    n_on = 0
    best, best_x = 0, x.copy()
    lam = 1.5
    T0, T1 = 1.0, 0.05
    t_start = time.time()
    it = 0
    while True:
        it += 1
        if it % 2000 == 0:
            el = time.time() - t_start
            if el > secs:
                break
        frac = min(1.0, (time.time() - t_start) / secs) if it % 2000 == 0 or it == 1 else frac
        T = T0 * (T1 / T0) ** frac
        p = rng.integers(P)
        ks = inc[p]
        if x[p]:
            dv = -int(np.count_nonzero(cnt[ks] == size[ks]))
            d = -1 - lam * dv
        else:
            dv = int(np.count_nonzero(cnt[ks] == size[ks] - 1))
            d = 1 - lam * dv
        if d >= 0 or rng.random() < np.exp(d / T):
            if x[p]:
                cnt[ks] -= 1
                n_on -= 1
            else:
                cnt[ks] += 1
                n_on += 1
            x[p] = not x[p]
            viol += dv
            if viol == 0 and n_on > best:
                best, best_x = n_on, x.copy()
    print(f"best feasible: {best} ({it} moves, {C} forbidden sets)", file=sys.stderr)
    print("v " + " ".join(str(i + 1 if best_x[i] else -(i + 1)) for i in range(P)) + " 0")


if __name__ == "__main__":
    main()
