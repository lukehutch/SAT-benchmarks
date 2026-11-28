# Sources and credits

Merlin Numa's counting implementation first appeared in the project on August 19, 2026. The public C solver derives from the November 8 Eclipse v0.0.61 source snapshot. The original solve order was parity elimination, counting and then conflict-driven clause learning. During release preparation, the identifiers and headers were renamed. In v0.0.1 the compiled instruction bytes in the counting, parity, dispatch and CDCL modules matched the benchmark build under GCC 14.2.0.

The dated changelog excerpts, earlier experiment and archive fingerprints are available in the [Eclipse project history](ECLIPSE-HISTORY.md).

## Research

- Armin Haken, *The Intractability of Resolution* (1985). The Eclipse changelog cites this result on resolution proofs for pigeonhole formulas. [Paper](https://doi.org/10.1016/0304-3975%2885%2990144-6)

- Armin Biere, *Two Pigeons per Hole Problem* (2013). Lingeling already used cardinality reasoning for pigeonhole formulas. Table II gives the standard 72-variable, 297-clause case. [Paper](https://cca.informatik.uni-freiburg.de/papers/Biere-SAT-Competition-2013-TPH-problem.pdf)
- Armin Biere, Daniel Le Berre, Emmanuel Lonca and Norbert Manthey, *Detecting Cardinality Constraints in CNF* (2014). The authors compared six pigeonhole encodings. [Paper](https://doi.org/10.1007/978-3-319-09284-3_22)
- Carsten Sinz, *Towards an Optimal CNF Encoding of Boolean Cardinality Constraints* (2005). Basis for the sequential-counter control. [Paper](https://doi.org/10.1007/11564751_73)
- Alexey Ignatiev, Antonio Morgado and Joao Marques-Silva, *PySAT: A Python Toolkit for Prototyping with SAT Oracles* (2018). PySAT supplied the sequential encoding and three comparison backends. [Paper](https://doi.org/10.1007/978-3-319-94144-8_26)
- Luke Hutchison's November 21, 2026 Frobenius benchmark prompted this comparison. His 9-by-8 row used 423 variables. The v0.0.1 comparison used four local DIMACS inputs. Version 0.0.2 measures six. [Original post](https://x.com/LH/status/2124247270824812710)

## Software

| Used for | Version | Upstream |
| --- | --- | --- |
| Lingeling, native C library | 1.0.0, tag `rel-1.0.0`, commit `89a167d0d2efe98d983c87b5b84175b40ea55842` | [Lingeling](https://github.com/arminbiere/lingeling/tree/rel-1.0.0) |
| Kissat, CaDiCaL and MiniSat | 4.0.4, 3.0.0 and 2.2 via python-sat 1.9.dev24 | [PySAT](https://github.com/pysathq/pysat), [Kissat](https://github.com/arminbiere/kissat), [CaDiCaL](https://github.com/arminbiere/cadical), [MiniSat](https://minisat.se/) |
| CryptoMiniSat | 5.18.0 via pycryptosat 5.18.0 | [CryptoMiniSat](https://github.com/msoos/cryptominisat) |
| AI-assisted development | OpenAI ChatGPT and Anthropic Claude, August to November 2026. The independent matching patch credits Claude Opus 5.5. Earlier sessions lack exact model identifiers. | [ChatGPT](https://chatgpt.com/), [Claude](https://claude.ai/) |

The comparison solvers are obtained separately under their upstream licenses. The reference used the following distribution archives.

| Artifact | SHA-256 |
| --- | --- |
| Lingeling 1.0.0 GitHub source tarball | `99f35f14091a495ca22e4bf7394f645bff7161ea4e0294f73cf4d5114ac33ac3` |
| python-sat 1.9.dev24, CPython 3.12 manylinux x86-64 wheel | `a0692ba7693bde440cf6bf4b4e58c11685e22df3516b13bf721f630dce6dac84` |
| pycryptosat 5.18.0, CPython 3.12 manylinux x86-64 wheel | `d5e215062e049528768c5a53980155a8921084c15531b64b78761c652da00b93` |

## Version 0.0.2

The supplied MIT-licensed TypeScript prototype contributed the sparse conflict graph, binary implication chains and bounded reachability pass, parity prefilter, binary and blocking watchers, activity heap, learned-clause minimization, native workbench workflows and expanded tests. The C implementation retains the original C APIs and exposes structural diagnostics through an optional trace stream. Input archive SHA-256: `b141e9bee3a1f136aec7cd530c60f939a8ae703b7b30cf916aed69b99aa0d932`.

- satsuma-iter+kissat came from the `anders.tar.xz` main-track submission archive. SHA-256: `1951097402831eaaa9cdd6b670a09b9e9cbe1714e16d48b17d420e3b40816623`. Extract the archive and use its `satsuma-iter-kissat/src` directory with the comparison runner. [SAT Competition 2026 downloads](https://satcompetition.github.io/2026/downloads.html)
- PySAT's bitwise and ladder at-most-one encodings supply the two extra 9/8 test fixtures. Generate them with the same row order as `bench/generate.py`, using `EncType.bitwise` or `EncType.ladder` for each column. [PySAT](https://github.com/pysathq/pysat)
- The optional browser workbench links against libevent 2 for local HTTP and form handling. [libevent](https://libevent.org/)

## Version 0.0.3

Merlin Numa directed an independent MIT-licensed implementation of the matching pass with Claude Opus 5.5 on November 22, 2026. Its source archive, independently numbered 0.0.2, has SHA-256 `1674508de71e59daa944e9afab4279d4816246239c955b666a9b2fa25131ac91`. The v0.0.3 integration used ChatGPT to adapt the matching pass, certificate checker, generators and tests to the prepared C release. That baseline is commit `dd3bfde8f06bc6ee5f5f23c237e53a77d626923d`. The integration retains the sparse counter, extends it to emit certificates, and bounds the conflict pairs stored by the matching pass.

- Philip Hall, *On Representatives of Subsets* (1935). The matching pass identifies a group of requirements with too few available places. [Paper](https://doi.org/10.1112/jlms/s1-10.37.26)
- John E. Hopcroft and Richard M. Karp, *An n^5/2 Algorithm for Maximum Matchings in Bipartite Graphs* (1973). The solver uses bipartite matching to find the shortage. [Paper](https://doi.org/10.1137/0202019)
- Marijn J. H. Heule, Benjamin Kiesl and Armin Biere, *Clausal Proofs of Mutilated Chessboards* (2019). Prior work on certifying this domino-tiling family. [Paper](https://doi.org/10.1007/978-3-030-20652-9_13)

## Version 0.0.4

The 22 classic formulas come from the SATLIB collection. The benchmark manifest credits the individual files and provides the archive member names and checksums. The DIMACS pigeonhole files are attributed to John Hooker, the flat graph-coloring files to Joseph Culberson, and the parity-learning files to James Crawford. The other sets are the SATLIB uniform random 3-SAT collection and SATPLAN Blocks World. [SATLIB index](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html) | [Input manifest](bench/public-inputs.csv)

The eight competition formulas came directly from the Global Benchmark Database. The selection used RocSAT's list of compact competition representatives. Each selected formula's main-track membership, original filename, attribution and verdict were checked against the competition database. The manifest records the database's author identifiers. [SAT Competition 2025](https://satcompetition.github.io/2025/downloads.html) | [GBD main-track list](https://benchmark-database.de/?context=cnf&track=main_2025) | [RocSAT selection manifest](https://github.com/mpizenberg/rocsat/blob/5c3ba48f22acc4ffbf1b35a12c15a8aec41523cb/bench/corpus.toml)

The comparison uses the upstream release executables for Kissat 4.0.4 and CaDiCaL 3.0.0. The SHA-256 digests of their GitHub source tarballs were `bfe93eaa6323b48011e4b1fcf74b3f2e20f9de544767e728009e5b2018296193` and `282b1c9422fde8631cb721b86450ae94df4e8de0545c17a69a301aaa4bf92fcf`, respectively. [Kissat rel-4.0.4](https://github.com/arminbiere/kissat/tree/rel-4.0.4) | [CaDiCaL rel-3.0.0](https://github.com/arminbiere/cadical/tree/rel-3.0.0)

The project MIT license covers dense-solver's code. The files in `bench/public-instances` are third-party benchmark data. Their source notices and attributions are preserved. Merlin Numa directed preparation of this comparison using ChatGPT.
