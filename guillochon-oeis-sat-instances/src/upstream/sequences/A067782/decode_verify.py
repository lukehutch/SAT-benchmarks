#!/usr/bin/env python3
"""Decode a solver model for a gen_depth_cnf.py instance and check the network on all 2^n inputs.

    python decode_verify.py out.cnf.map.json solver_output.txt

solver_output.txt: standard competition output ("s SATISFIABLE" and "v ..." lines) or a bare list of
literals.  Prints the network layer by layer and exits 0 only if it really sorts all 2^n inputs.
"""
import json
import sys


def sorts(n, layers):
    """Bit-parallel 0/1-principle check over all 2^n inputs."""
    N = 1 << n
    full = (1 << N) - 1
    # channel c holds bit (n-1-c) of the input index, for every index at once
    ch = []
    for c in range(n):
        b = n - 1 - c
        block = ((1 << (1 << b)) - 1) << (1 << b)     # pattern 0^(2^b) 1^(2^b)
        period = 1 << (b + 1)
        pat, width = block, period
        while width < N:
            pat |= pat << width
            width *= 2
        ch.append(pat & full)
    for layer in layers:
        for i, j in layer:
            ch[i], ch[j] = ch[i] & ch[j], ch[i] | ch[j]
    # sorted iff channel c is 1 exactly when the input has >= n-c ones
    for c in range(n - 1):
        if ch[c] & ~ch[c + 1] & full:
            return False
    return True


def main():
    meta = json.load(open(sys.argv[1]))
    true = set()
    for line in open(sys.argv[2]):
        t = line.split()
        if not t or t[0] in ("c", "s"):
            if t and t[0] == "s" and "UNSAT" in line:
                print("solver says UNSATISFIABLE")
                sys.exit(2)
            continue
        if t[0] == "v":
            t = t[1:]
        true.update(int(v) for v in t if int(v) > 0)
    n = meta["n"]
    layers = [[tuple(p) for p in layer] for layer in meta["prefix"]]
    for layer in meta["free_layers"]:
        layers.append([(i, j) for i, j, v in layer if v in true])
    for l, layer in enumerate(layers, 1):
        print(f"layer {l}: " + " ".join(f"({i},{j})" for i, j in layer))
    ok = sorts(n, layers)
    print(f"n={n}, depth {len(layers)}, {sum(map(len, layers))} comparators: "
          + ("SORTS all 2^n inputs" if ok else "DOES NOT SORT"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
