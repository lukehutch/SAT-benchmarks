#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate one deterministic, ordinary DIMACS CNF per invocation.

    uv run sat_challenges.py matmul 2 2 2 7 --mod 2 > strassen.cnf
    uv run sat_challenges.py dot 3 2 --mod 4 > dot.cnf
    uv run sat_challenges.py cross 5 --mod 3 > cross.cnf
    uv run sat_challenges.py sort 4 5 > sort.cnf
    uv run sat_challenges.py select 5 3 6 --adaptive > median.cnf
    uv run sat_challenges.py golomb 5 11 > ruler.cnf
    uv run sat_challenges.py sha256 2 --bytes 4 > equiv.cnf
    uv run sat_challenges.py sha256 64 --message-hex 616263 > abc.cnf

K is an upper bound. Sweep K (or ruler length L) to bracket an optimum.
SAT at K and UNSAT at K-1 establish the minimum under the specified model.
Each 'c var ID NAME' describes a primary choice. Lines 'c lit L NAME'
give Boolean observables. A signed literal L is true exactly when NAME holds.
Comparator slots, tensor terms, wires and matrix entries are indexed from 0.
The requested order statistic is indexed from 1, starting with the smallest.

For tensor synthesis, term t multiplies the linear forms U[t] and V[t].
W[t,o] is the coefficient of that product in output o. Linear operations
and constant scalings are free. Entries are flattened in row-major order.
At modulus 2 the single =1 bit names the coefficient. For larger moduli
exactly one of the labeled =r variables is true for each coefficient.
A zero term permits fewer than K products. The coefficient equations hold
on all pairs of basis vectors and hence on every input over Z/mod.
See https://arxiv.org/abs/1903.11391

Sort/select networks put the smaller value on the lower-numbered wire.
They use a fixed sequence of compare-exchanges. Thresholding commutes with
min and max, so checking Boolean inputs suffices even when keys repeat.
Adaptive selection instead counts worst-case comparisons in a decision tree.
Tree node 1 is the root. Test [h,i,j] compares items i and j (ties by
original index). Visit 2*h if i comes first, or 2*h+1 otherwise.
The encoding uses N! permutations and 2^K leaves. Start small.
For a network the answer is on wire rank-1. All cmp bits false in a
slot means that slot is idle. For a ruler, true mark[i] bits are its ticks.

Small UNSAT/SAT pairs to reproduce by changing only the last bound:
    cross 4 / 5                 (modulus 2)
    sort 4 4 / 5
    select 5 3 6 / 7            (fixed median of five)
    select 5 3 5 / 6 --adaptive
    golomb 5 10 / 11

SHA uses standard one-block padding, the standard IV, the first R rounds
and feed-forward, including when R < 64. At 64 rounds this gives SHA-256
for byte messages of length 0..55. In equivalence mode the proposition is
'there exists a message on which ripple and prefix addition yield different
outputs'. In trace mode the message is fixed and output bits are labeled.
See https://doi.org/10.6028/NIST.FIPS.180-4
"""

import argparse
from itertools import combinations, permutations, product
import operator
import shutil
import sys
import tempfile


class CNF:
    """Signed literals. Variable 1 is pinned true. Spool clauses until header is known."""

    true = 1
    false = -1

    def __init__(self, body):
        self.body = body
        self.nvars = 1
        self.nclauses = 1
        self.notes = ["lit 1 constant_true"]
        self.body.write("1 0\n")

    def var(self, name=None):
        self.nvars += 1
        if name is not None:
            self.notes.append(f"var {self.nvars} {name}")
        return self.nvars

    def clause(self, *lits):
        unique = {}
        for lit in lits:
            if lit == self.true or -lit in unique:
                return
            if lit != self.false:
                unique[lit] = None
        self.body.write(" ".join(map(str, (*unique, 0))) + "\n")
        self.nclauses += 1

    def at_most_one(self, lits):
        # Pairwise for short lists, linear sequential encoding for longer ones.
        if len(lits) <= 4:
            for a, b in combinations(lits, 2):
                self.clause(-a, -b)
            return
        seen = self.false
        for x in lits[:-1]:
            nxt = self.var()
            self.clause(-seen, -x)
            self.clause(-seen, nxt)
            self.clause(-x, nxt)
            seen = nxt
        self.clause(-seen, -lits[-1])

    def exactly_one(self, lits):
        self.clause(*lits)
        self.at_most_one(lits)

    def and2(self, a, b):
        if a == self.false or b == self.false or a == -b:
            return self.false
        if a == self.true or a == b:
            return b
        if b == self.true:
            return a
        x = self.var()
        self.clause(-x, a)
        self.clause(-x, b)
        self.clause(x, -a, -b)
        return x

    def or2(self, a, b):
        return -self.and2(-a, -b)

    def xor2(self, a, b):
        if a == self.false:
            return b
        if b == self.false:
            return a
        if a == self.true:
            return -b
        if b == self.true:
            return -a
        if a == b:
            return self.false
        if a == -b:
            return self.true
        x = self.var()
        self.clause(-a, -b, -x)
        self.clause(a, b, -x)
        self.clause(a, -b, x)
        self.clause(-a, b, x)
        return x

    def dump(self, output):
        for note in self.notes:
            print("c", note, file=output)
        print("p cnf", self.nvars, self.nclauses, file=output)
        self.body.seek(0)
        shutil.copyfileobj(self.body, output)


class Ring:
    """Residue represented by a tuple of literals, one per possible value."""

    def __init__(self, cnf, modulus):
        self.f = cnf
        self.m = modulus

    def residue(self, name=None):
        if self.m == 2:
            bit = self.f.var(None if name is None else name + "=1")
            return (-bit, bit)
        values = tuple(self.f.var(None if name is None else f"{name}={r}")
                       for r in range(self.m))
        self.f.exactly_one(values)
        return values

    def table(self, left, right, op):
        out = self.residue()
        for a, x in enumerate(left):
            for b, y in enumerate(right):
                self.f.clause(-x, -y, out[op(a, b) % self.m])
        return out

    def mul(self, left, right):
        if self.m == 2:
            bit = self.f.and2(left[1], right[1])
            return (-bit, bit)
        return self.table(left, right, operator.mul)

    def add(self, left, right):
        if self.m == 2:
            bit = self.f.xor2(left[1], right[1])
            return (-bit, bit)
        return self.table(left, right, operator.add)


def tensor(f, args):
    """Impose the Brent coefficient equations, including every zero coefficient."""
    if args.family == "matmul":
        a, b, c = args.a, args.b, args.c
        nu, nv, nw = a*b, b*c, a*c
        target = {(i*b+j, j*c+k, i*c+k): 1
                  for i, j, k in product(range(a), range(b), range(c))}
    elif args.family == "dot":
        nu, nv, nw = args.n, args.n, 1
        target = {(i, i, 0): 1 for i in range(nu)}
    else:
        nu = nv = nw = 3
        target = {}
        for o in range(3):
            i, j = (o+1) % 3, (o+2) % 3
            target[i, j, o], target[j, i, o] = 1, -1

    ring = Ring(f, args.mod)

    def factors(label, size):
        return [[ring.residue(f"{label}[{t},{i}]") for i in range(size)]
                for t in range(args.k)]

    u, v, w = factors("U", nu), factors("V", nv), factors("W", nw)
    for i, j in product(range(nu), range(nv)):
        uv = [ring.mul(u[t][i], v[t][j]) for t in range(args.k)]
        for o in range(nw):
            wanted = target.get((i, j, o), 0) % args.mod
            total = None
            for t, term in enumerate(uv):
                summand = ring.mul(term, w[t][o])
                total = summand if total is None else ring.add(total, summand)
            if total is not None:
                f.clause(total[wanted])
            elif wanted != 0:
                f.clause()


def comparator_network(f, args):
    n, k = args.n, args.k
    rank = getattr(args, "rank", None)
    pairs = list(combinations(range(n), 2))
    stages = []
    for t in range(k):
        selectors = [f.var(f"cmp[{t},{i},{j}]") for i, j in pairs]
        # At most one, so all false encodes an idle slot.
        f.at_most_one(selectors)
        incident = [[] for _ in range(n)]
        for sel, (i, j) in zip(selectors, pairs):
            incident[i].append(sel)
            incident[j].append(sel)
        stages.append((selectors, incident))

    if rank is None:
        zero_counts = range(n + 1)
    else:
        # The answer is 1 at <= rank-1 zeros and 0 at >= rank zeros.
        # Monotonicity extends these two boundary layers to the entire cube.
        zero_counts = (rank - 1, rank)
    for count in zero_counts:
        expected = [f.false] * count + [f.true] * (n - count)
        for zeros in combinations(range(n), count):
            state = [f.true] * n
            for i in zeros:
                state[i] = f.false
            if state == expected:
                continue  # Every permitted comparator fixes this input.
            for selectors, incident in stages:
                nxt = [f.var() for _ in range(n)]
                for sel, (i, j) in zip(selectors, pairs):
                    a, b = state[i], state[j]
                    lo, hi = nxt[i], nxt[j]
                    f.clause(-sel, -lo, a)
                    f.clause(-sel, -lo, b)
                    f.clause(-sel, lo, -a, -b)
                    f.clause(-sel, hi, -a)
                    f.clause(-sel, hi, -b)
                    f.clause(-sel, -hi, a, b)
                for i, touched in enumerate(incident):
                    f.clause(*touched, -state[i], nxt[i])
                    f.clause(*touched, state[i], -nxt[i])
                state = nxt
            outputs = range(n) if rank is None else (rank - 1,)
            for i in outputs:
                f.clause(state[i] if expected[i] == f.true else -state[i])


def adaptive_selection(f, args):
    """Tree nodes compare original positions. True takes child 2*h and false takes 2*h+1."""
    n, k, r = args.n, args.k, args.rank
    if n == 1:
        f.notes.append("the sole input is the answer at cost zero")
        return
    pairs = list(combinations(range(n), 2))
    first_leaf = 1 << k
    tests, answers = {}, {}
    for h in range(1, first_leaf):
        tests[h] = [f.var(f"test[{h},{i},{j}]") for i, j in pairs]
        f.exactly_one(tests[h])
    for h in range(first_leaf, 2 * first_leaf):
        answers[h] = [f.var(f"return[{h},{i}]") for i in range(n)]
        f.exactly_one(answers[h])

    # Each permutation lists positions in increasing key order. Ties can be
    # resolved by original index, so these cases cover the stable order as well.
    for order in permutations(range(n)):
        value = {i: pos for pos, i in enumerate(order)}
        correct = order[r - 1]
        route = [f.false, f.true] + [f.var() for _ in range(2, 2 * first_leaf)]
        for h, choices in tests.items():
            yes, no = [], []
            for choice, (i, j) in zip(choices, pairs):
                (yes if value[i] < value[j] else no).append(choice)
            # Exactly one choice is active. Propagate reach to its one child.
            f.clause(-route[h], *no, route[2*h])
            f.clause(-route[h], *yes, route[2*h+1])
        for h, outputs in answers.items():
            f.clause(-route[h], outputs[correct])


def golomb(f, args):
    """Bounded span, with translation removed by requiring tick zero."""
    m, length = args.marks, args.length
    if m > length + 1 or m * (m - 1) // 2 > length:
        f.notes.append("infeasible by number of ticks or distinct positive distances")
        f.clause()
        return
    marks = [f.var(f"mark[{i}]") for i in range(length + 1)]
    f.clause(marks[0])
    # ge[j] <=> the processed prefix contains at least j marks.
    ge = [f.true] + [f.false] * (m + 1)
    for i, x in enumerate(marks):
        for j in range(min(i + 1, m + 1), 0, -1):
            ge[j] = f.or2(ge[j], f.and2(x, ge[j-1]))
    f.clause(ge[m])
    f.clause(-ge[m+1])
    for distance in range(1, length + 1):
        pairs = [f.and2(marks[i], marks[i + distance])
                 for i in range(length + 1 - distance)]
        f.at_most_one(pairs)


IV = (
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
)
ROUND_CONSTANTS = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
)


def const_bits(value, width):
    return [CNF.true if (value >> i) & 1 else CNF.false for i in range(width)]


def add_word(f, x, y, prefix):
    """Modulo 2^32. Words are lists with least significant bit first."""
    prop = [f.xor2(a, b) for a, b in zip(x, y)]
    generate = [f.and2(a, b) for a, b in zip(x[:-1], y[:-1])]
    if prefix:
        # Combine adjacent carry-generate/propagate groups in five levels.
        group_prop = prop[:-1]
        for stride in (1, 2, 4, 8, 16):
            for i in range(30, stride - 1, -1):
                generate[i] = f.or2(generate[i], f.and2(group_prop[i], generate[i-stride]))
                group_prop[i] = f.and2(group_prop[i], group_prop[i-stride])
        carries = [f.false, *generate]
    else:
        carries = [f.false]
        for p, g in zip(prop, generate):
            carries.append(f.or2(g, f.and2(p, carries[-1])))
    return [f.xor2(p, c) for p, c in zip(prop, carries)]


def sha_circuit(gates, block, rounds, prefix):
    def add(*words):
        total = words[0]
        for word in words[1:]:
            total = add_word(gates, total, word, prefix)
        return total

    def sigma(x, r1, r2, r3, shift=False):
        def rotate(k):
            return x[k:] + x[:k]
        last = x[r3:] + [gates.false]*r3 if shift else rotate(r3)
        return [gates.xor2(gates.xor2(a, b), c) for a, b, c in zip(rotate(r1), rotate(r2), last)]

    schedule = block[:]
    for t in range(16, rounds):
        schedule.append(add(sigma(schedule[t-2], 17, 19, 10, shift=True),
                            schedule[t-7], sigma(schedule[t-15], 7, 18, 3, shift=True),
                            schedule[t-16]))
    initial = [const_bits(v, 32) for v in IV]
    a, b, c, d, e, f, g, h = initial
    for t in range(rounds):
        choose = [gates.or2(gates.and2(x, y), gates.and2(-x, z)) for x, y, z in zip(e, f, g)]
        majority = [gates.or2(gates.and2(x, y), gates.and2(gates.or2(x, y), z)) for x, y, z in zip(a, b, c)]
        t1 = add(h, sigma(e, 6, 11, 25), choose, const_bits(ROUND_CONSTANTS[t], 32), schedule[t])
        t2 = add(sigma(a, 2, 13, 22), majority)
        a, b, c, d, e, f, g, h = add(t1, t2), a, b, c, add(d, t1), e, f, g
    return [add(x, y) for x, y in zip(initial, (a, b, c, d, e, f, g, h))]


def sha256(f, args):
    fixed = args.message_hex
    size = len(fixed) if fixed is not None else args.bytes
    byte_bits = []
    for i in range(size):
        bits = [f.var(f"message[{i}].bit{j}") for j in range(8)]
        if fixed is not None:
            for bit, sign in zip(bits, const_bits(fixed[i], 8)):
                f.clause(bit * sign)
        byte_bits.append(bits)
    padding = b"\x80" + bytes(55 - size) + (8 * size).to_bytes(8, "big")
    byte_bits.extend(const_bits(v, 8) for v in padding)
    # SHA parses four consecutive bytes as a big-endian word.
    block = [[bit for byte in reversed(byte_bits[i:i+4]) for bit in byte]
             for i in range(0, 64, 4)]
    out = sha_circuit(f, block, args.rounds, prefix=False)
    if fixed is None:
        other = sha_circuit(f, block, args.rounds, prefix=True)
        mismatch = [f.xor2(a, b) for x, y in zip(out, other) for a, b in zip(x, y)]
        f.clause(*mismatch)
        return
    for i, word in enumerate(out):
        expected = None
        if args.expect is not None:
            expected = int.from_bytes(args.expect[4*i:4*i+4], "big")
        for j, bit in enumerate(word):
            f.notes.append(f"lit {bit} digest[{i}].bit{j}")
            if expected is not None:
                f.clause(bit if (expected >> j) & 1 else -bit)


def at_least(minimum):
    def parse(s):
        value = int(s)
        if value < minimum:
            raise argparse.ArgumentTypeError(f"expected an integer >= {minimum}")
        return value
    return parse


def hex_bytes(s):
    try:
        return bytes.fromhex(s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected pairs of hexadecimal digits") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="family", required=True)

    def family(name, description):
        return sub.add_parser(name, help=description, description=description)

    def arg(p, name, minimum, help_text):
        p.add_argument(name, type=at_least(minimum), help=help_text)

    p = family("matmul", "Bilinear rank of an A x B by B x C matrix product over Z/mod.")
    for axis, desc in zip("abc", ("left rows", "inner dimension", "right columns")):
        arg(p, axis, 1, desc)
    d = family("dot", "Bilinear rank of the length-N scalar dot product over Z/mod.")
    arg(d, "n", 1, "vector dimension")
    x = family("cross", "Bilinear rank of the ordinary three-dimensional vector cross product over Z/mod.")
    for cmd in (p, d, x):
        arg(cmd, "k", 0, "maximum number of products of linear forms")
        cmd.add_argument("--mod", type=at_least(2), default=2, help="coefficient modulus (default 2)")
        cmd.set_defaults(encode=tensor)

    for name in ("sort", "select"):
        desc = ("Sort all N wires with at most K comparators." if name == "sort" else
                "Return the rank-th smallest using at most K comparators.")
        p = family(name, desc)
        arg(p, "n", 1, "number of inputs")
        if name == "select":
            arg(p, "rank", 1, "order statistic from 1 (min) to N (max)")
            p.add_argument("--adaptive", action="store_true",
                           help="use a decision tree of worst-case depth K (default is a fixed network)")
        arg(p, "k", 0, "comparator budget")
        p.set_defaults(encode=comparator_network)

    p = family("golomb", "Place M marks on integer ticks 0..L with all positive pairwise distances distinct.")
    arg(p, "marks", 1, "exact number of marks")
    arg(p, "length", 0, "maximum span")
    p.set_defaults(encode=golomb)

    p = family("sha256", "Compare two reduced-round SHA-256 circuits, or emit a fixed-message trace.")
    arg(p, "rounds", 0, "number of rounds, 0..64 (includes final feed-forward)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--bytes", type=at_least(0), default=4, metavar="B",
                      help="equivalence challenge on all B-byte messages (0..55, default 4)")
    mode.add_argument("--message-hex", type=hex_bytes, metavar="HEX",
                      help="trace a fixed message of 0..55 bytes, e.g. 616263")
    p.add_argument("--expect", type=hex_bytes, metavar="HEX",
                   help="require a particular 32-byte digest in fixed-message mode")
    p.set_defaults(encode=sha256)

    args = parser.parse_args()
    if args.family == "select":
        if args.rank > args.n:
            parser.error("rank must be <= n")
        if args.adaptive:
            args.encode = adaptive_selection
    if args.family == "sha256":
        if args.rounds > 64 or args.bytes > 55 or (args.message_hex is not None and len(args.message_hex) > 55):
            parser.error("SHA-256 requires 0..64 rounds and a one-block message of 0..55 bytes")
        if args.expect is not None and (len(args.expect) != 32 or args.message_hex is None):
            parser.error("--expect requires 32 digest bytes and a fixed --message-hex")

    with tempfile.TemporaryFile(mode="w+t", encoding="ascii", newline="\n") as body:
        f = CNF(body)
        # Canonical parameter comment also covers default values and empty messages.
        fields = []
        for key, value in vars(args).items():
            if key == "encode" or value is None or (key == "bytes" and args.message_hex is not None):
                continue
            fields.append(f"{key}={value.hex() if isinstance(value, bytes) else value}")
        f.notes.insert(0, " ".join(fields))
        args.encode(f, args)
        f.dump(sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
