"""Small shared helpers for writing DIMACS CNF files (pure Python, no dependencies)."""


class CNF:
    def __init__(self):
        self.nv = 0
        self.clauses = []

    def var(self):
        self.nv += 1
        return self.nv

    def vars(self, k):
        return [self.var() for _ in range(k)]

    def add(self, lits):
        self.clauses.append(list(lits))

    # --- cardinality: Sinz sequential counter --------------------------------------------------
    def at_most(self, lits, k):
        """sum(lits) <= k (Sinz 2005 sequential counter, O(n k) clauses)."""
        n = len(lits)
        if k >= n:
            return
        if k == 0:
            for x in lits:
                self.add([-x])
            return
        # s[i][j]: at least j+1 of lits[0..i] are true
        s = [self.vars(k) for _ in range(n - 1)]
        self.add([-lits[0], s[0][0]])
        for j in range(1, k):
            self.add([-s[0][j]])
        for i in range(1, n - 1):
            self.add([-lits[i], s[i][0]])
            self.add([-s[i - 1][0], s[i][0]])
            for j in range(1, k):
                self.add([-lits[i], -s[i - 1][j - 1], s[i][j]])
                self.add([-s[i - 1][j], s[i][j]])
            self.add([-lits[i], -s[i - 1][k - 1]])
        self.add([-lits[n - 1], -s[n - 2][k - 1]])

    def at_least(self, lits, k):
        """sum(lits) >= k, as at most len-k of the negations."""
        if k <= 0:
            return
        if k > len(lits):
            self.add([])          # impossible: empty clause
            return
        self.at_most([-x for x in lits], len(lits) - k)

    def write(self, path, comments=()):
        with open(path, "w", newline="\n") as f:
            for c in comments:
                f.write(f"c {c}\n")
            f.write(f"p cnf {self.nv} {len(self.clauses)}\n")
            f.writelines(" ".join(map(str, cl)) + " 0\n" for cl in self.clauses)


def read_model(path):
    """Positive literals from solver output ('v ...' lines) or a bare literal list."""
    true = set()
    for line in open(path):
        t = line.split()
        if not t or t[0] == "c":
            continue
        if t[0] == "s":
            if "UNSAT" in line:
                raise SystemExit("solver says UNSATISFIABLE")
            continue
        if t[0] == "v":
            t = t[1:]
        true.update(int(v) for v in t if int(v) > 0)
    return true
