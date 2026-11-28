# OEIS SAT instances

This repository collects SAT encodings of open terms of sequences in the
[On-Line Encyclopedia of Integer Sequences](https://oeis.org). Each instance decides one unknown term, or one
bound on it. A fast enough solver turns an answer into a new OEIS term.

Every sequence ships:

* a **generator** that rebuilds every instance from scratch (so the encoding can be audited and the large CNFs
  need not be trusted as opaque files);
* a **verifier** that turns a SAT model back into the combinatorial object and checks it independently;
* **calibration instances** whose answers are already known, so solver speed can be measured on the same
  encoding before any claim about the open one;
* the **open instance(s)**, with what SAT and UNSAT would each mean.

## Sequences

| sequence | question | open instance | status |
|---|---|---|---|
| [A067782](sequences/A067782) | least depth of an n-input sorting network | does an 18-input network of depth 10 exist? | open: a(18) ∈ {10, 11} |
| [A171081](sequences/A171081) (= A007783) | van der Waerden numbers w(2;3,t) | is w(2;3,20) = 389? | open: conjectured 389 |
| [A250000](sequences/A250000) | peaceable queens | 65 + 65 queens on 21 × 21? | open: a(21) ≥ 64 |
| [A350304](sequences/A350304) (+ A001198, A347473, A350237) | Zarankiewicz z(n;3) | z(17;3)? | open: 135 ≤ z ≤ 150 |
| [point-patterns](sequences/point-patterns) (A227133/A152125, A240443, A157795/A319158, A227308/A227116, A240114/A319159) | pattern-free point sets on square and triangular grids | the next term of each | open, one instance per pattern |

## Why these make good solver tests

A SAT answer is a certificate. The verifier rebuilds the object (a sorting network, a coloring, a matrix…) and
checks it directly, usually in seconds, without trusting the solver or the CNF. Each ladder has both
known-SAT and known-UNSAT rungs. A solver can show its speed on instances whose models anyone can check
instantly, and a wrong SAT claim on a known-UNSAT rung is caught at once. UNSAT answers are the exception: they
need a DRAT/LRAT proof to be checkable (see below).

## Getting the instances

Instances are in each sequence's `cnf/` folder, compressed with xz, with a `SHA256SUMS` of the uncompressed
files. Any instance can also be regenerated locally with the sequence's generator (see its `make_set.sh`); the
output is deterministic and matches the checksums. Future instances over GitHub's 100 MB file limit (compressed)
will be attached to a release tagged `A######-v1` instead.

```bash
xz -dk sortnet_n18_d10.cnf.xz      # -> DIMACS CNF
```

## Claiming a result

* **SAT:** run the sequence's verifier on the solver's model. It extracts the object and checks it without
  trusting the CNF. A verified model is a complete certificate.
* **UNSAT:** an UNSAT answer by itself cannot be checked. Produce a DRAT or LRAT proof and check it with an
  independent checker (`drat-trim`, `cake_lpr`, `lrat-check`). Then please open an issue with the solver,
  version, runtime and the proof's size and checksum.

## Layout and adding a sequence

```
common/              shared CNF helpers (cardinality encodings), validation harness, lower-bound search
sequences/
  A067782/
    README.md          question, encoding, what SAT/UNSAT mean, calibration table, references
    gen_*.py           generator: parameters -> DIMACS CNF (+ a .map.json for decoding)
    verify.py          model -> object -> independent check (decode_verify.py for A067782)
    validate.py        regenerates small cases and checks them against known OEIS terms
    make_set.sh        exact commands that produced the published instances
    cnf/               *.cnf.xz, *.map.json, SHA256SUMS
    certificates/      verified solutions behind lower bounds found here (optional)
```

To add a sequence, create `sequences/A######/` with the same pieces and add a row to the table above (instances
over 100 MB compressed go to a release tagged `A######-v1`). Instance files are named
`<problem>_<parameters>.cnf`, and their header comment lines (`c ...`) say what the instance asks.

## License

Code: MIT (see `LICENSE`). The generated CNF instances are released into the public domain (CC0).

Maintained by James Guillochon.
