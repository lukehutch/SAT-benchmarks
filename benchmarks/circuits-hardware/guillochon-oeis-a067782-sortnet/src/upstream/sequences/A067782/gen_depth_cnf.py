#!/usr/bin/env python3
"""DIMACS CNF for "is there an n-channel sorting network of depth d?" (A067782).

    python gen_depth_cnf.py N D [-o out.cnf] [--prefix layers.json] [--no-last-adjacent]

SAT  <=> some n-channel sorting network of depth d extends the fixed prefix.
UNSAT    with the default prefix  =>  no depth-d sorting network exists, so a(n) > d.

Encoding (Bundala & Zavodny 2014 style, one-sided "upper bound" form):

* Fixed prefix.  By Parberry (1991) the first layer of a depth-optimal network can be taken to be
  the maximal layer (0,1),(2,3),...; that is the default prefix.  A longer prefix (one CNF per
  prefix, e.g. a symmetry-reduced set of 2-layer prefixes) can be given with --prefix.
* Comparator variables g[l][i,j] (i<j) for every free layer l; a channel is in at most one
  comparator per layer; used[l][i] <-> OR of the comparators touching i.
* Inputs: the 0/1 principle.  Only the distinct outputs of the fixed prefix on all 2^n 0/1 inputs
  matter, minus those already sorted.
* Values: for every input x and every free layer, a variable v per channel that is an UPPER BOUND
  of the true 0/1 value (clauses only force v up: g & a & b -> min, g & a -> max, g & b -> max,
  ~used & a -> out).  For an input with k ones, the outputs on channels 0..n-k-1 must be 0.
  Sound and complete: a real sorting network satisfies the clauses with v = true values; and in
  any model v >= true value by induction, so channels 0..n-k-1 are truly 0, and since comparators
  preserve the number of ones the k ones sit on channels n-k..n-1, i.e. the output is sorted.
* Simplifications (all equivalence-preserving): constant values are folded in; a value nothing
  can force to 1 is the constant 0; last-layer outputs on channels n-k..n-1 never constrain
  anything and are dropped.
* Last layer only has comparators (i,i+1): true for every non-redundant sorting network
  (Codish, Cruz-Filipe, Schneider-Kamp, "Sorting networks: the end game", 2015), and deleting
  redundant comparators never increases depth.  --no-last-adjacent turns this off.

A <out>.map.json sidecar records which variables are which comparators, for decode_verify.py.
"""
import argparse
import json
import os
import sys
import tempfile
from itertools import combinations


def apply_layer(x, layer):
    x = list(x)
    for i, j in layer:
        if x[i] > x[j]:
            x[i], x[j] = x[j], x[i]
    return tuple(x)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("n", type=int)
    ap.add_argument("depth", type=int)
    ap.add_argument("-o", "--out")
    ap.add_argument("--prefix", help="JSON list of layers, each a list of [i,j] pairs (0-based, i<j)")
    ap.add_argument("--no-last-adjacent", action="store_true")
    args = ap.parse_args()
    n, d = args.n, args.depth
    out = args.out or f"sortnet_n{n}_d{d}.cnf"

    if args.prefix:
        with open(args.prefix) as f:
            prefix = [[tuple(p) for p in layer] for layer in json.load(f)]
    else:
        prefix = [[(i, i + 1) for i in range(0, n - 1, 2)]]
    for layer in prefix:
        used = [c for p in layer for c in p]
        assert len(used) == len(set(used)) and all(0 <= i < j < n for i, j in layer), layer
    free = d - len(prefix)
    assert free >= 1, "prefix is as deep as the network"

    # Distinct, unsorted outputs of the prefix over all 0/1 inputs.
    inputs = set()
    for m in range(1 << n):
        x = tuple((m >> (n - 1 - c)) & 1 for c in range(n))
        for layer in prefix:
            x = apply_layer(x, layer)
        if any(x[c] > x[c + 1] for c in range(n - 1)):
            inputs.add(x)
    inputs = sorted(inputs)

    nv = 0

    def new():
        nonlocal nv
        nv += 1
        return nv

    ncl = 0
    body = tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(os.path.abspath(out)),
                                       suffix=".body", newline="\n")
    buf = []

    def emit(lits):
        nonlocal ncl
        ncl += 1
        buf.append(" ".join(map(str, lits)) + " 0\n")
        if len(buf) >= 200000:
            body.writelines(buf)
            buf.clear()

    # Comparator structure.
    layers = []  # per free layer: (pairs, gvar dict, used list)
    for l in range(free):
        last = (l == free - 1) and not args.no_last_adjacent
        pairs = [(i, i + 1) for i in range(n - 1)] if last else list(combinations(range(n), 2))
        g = {p: new() for p in pairs}
        used = [new() for _ in range(n)]
        touch = [[g[p] for p in pairs if c in p] for c in range(n)]
        for c in range(n):
            for a, b in combinations(touch[c], 2):      # at most one comparator per channel
                emit([-a, -b])
            emit([-used[c]] + touch[c])                  # used -> some comparator
            for a in touch[c]:
                emit([-a, used[c]])                      # comparator -> used
        layers.append((pairs, g, used))

    # Values.  A value is 0, 1 (constants) or a positive variable id.
    def clause(gs, ants, concl):
        """(gs and ants) -> concl, with constant folding.  Returns False if concl is forced."""
        lits = [-v for v in gs]
        for a in ants:
            if a == 0:
                return None          # antecedent false: clause satisfied
            if a != 1:
                lits.append(-a)
        return lits

    for x in inputs:
        k = sum(x)
        cur = list(x)
        for l, (pairs, g, used) in enumerate(layers):
            is_last = (l == free - 1)
            # Collect, per output channel, the clauses that would force it to 1.
            force = [[] for _ in range(n)]
            for (i, j) in pairs:
                gi = g[(i, j)]
                c = clause([gi], [cur[i], cur[j]], None)
                if c is not None:
                    force[i].append(c)
                for src in (i, j):
                    c = clause([gi], [cur[src]], None)
                    if c is not None:
                        force[j].append(c)
            for c in range(n):
                if cur[c] == 0:
                    continue
                lits = [used[c]] + ([-cur[c]] if cur[c] != 1 else [])
                force[c].append(lits)
            nxt = [0] * n
            for c in range(n):
                if not force[c]:
                    nxt[c] = 0
                    continue
                if is_last:
                    if c >= n - k:
                        continue     # unconstrained output: drop
                    for lits in force[c]:
                        emit(lits)   # output must be 0: the forcing conditions must fail
                    continue
                v = new()
                nxt[c] = v
                for lits in force[c]:
                    emit(lits + [v])
            cur = nxt

    body.writelines(buf)
    body.close()
    with open(out, "w", newline="\n") as f:
        f.write(f"c sorting network existence: n={n} channels, depth {d}\n")
        f.write(f"c fixed prefix ({len(prefix)} layer(s)): {json.dumps(prefix)}\n")
        f.write(f"c last layer adjacent-only: {not args.no_last_adjacent}\n")
        f.write(f"c {len(inputs)} distinct unsorted prefix outputs encoded\n")
        f.write("c SAT <=> a depth-d sorting network extends the prefix; decode with decode_verify.py\n")
        f.write(f"p cnf {nv} {ncl}\n")
        with open(body.name) as b:
            while True:
                chunk = b.read(1 << 24)
                if not chunk:
                    break
                f.write(chunk)
    os.remove(body.name)
    meta = {"n": n, "depth": d, "prefix": prefix,
            "free_layers": [[[i, j, g[(i, j)]] for (i, j) in pairs] for pairs, g, _ in layers]}
    with open(out + ".map.json", "w") as f:
        json.dump(meta, f)
    print(f"{out}: {nv} vars, {ncl} clauses, {len(inputs)} inputs", file=sys.stderr)


if __name__ == "__main__":
    main()
