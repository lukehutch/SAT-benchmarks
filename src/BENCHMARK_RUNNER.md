# Reproducible Offline Multi-Solver Benchmark Runner (`src/run_benchmarks.py`)

[`run_benchmarks.py`](run_benchmarks.py) is a zero-dependency Python 3 script for cloning, compiling, and running **Frobenius** alongside all four standard SAT competitors (**CaDiCaL 3.1.0**, **CryptoMiniSat 5.18.0**, **dense-solver 0.0.4**, and **Kissat 4.0.4**) across all **93** collections in `SAT-benchmarks` — designed to run completely offline without overloading the host machine.

## Key Features

- **Two-Stage Generic Workflow:**
  1. `build-solvers --solvers-dir <DIR>` creates `<DIR>` if missing, clones and compiles all competitor solvers from their pinned upstream GitHub releases into `<DIR>/bin/`, optionally builds Frobenius (`--frobenius-dir`, `--pgo`), and records exact git SHAs & versions in `<DIR>/solver_versions.json`.
  2. `run --solvers-dir <DIR> --frobenius-dir <DIR> --output <FILE.jsonl>` executes all benchmarks in a parallel work queue pinned **strictly 1 job per dedicated physical CPU core** (zero SMT sibling sharing, up to `--max-cores` or explicit `--cores`), decompressing `.xz` files into RAM (`/dev/shm`) **before** starting timing for exact apples-to-apples fairness.
- **Incremental, Monitorable, Resumable Output (JSONL):**
  - Every completed run is immediately appended, flushed, and `fsync`ed as one JSON line in `--output <FILE.jsonl>`, capturing `timestamp_utc`, `collection`, `instance`, `format`, `solver`, `solver_version`, `core_id`, `host_load_1m`, `timeout_s`, `verdict`, `expected`, `verdict_ok`, `model_verified` (raw-CNF SAT clause verification), `timed_out`, `wall_ms`, `user_ms`, `sys_ms`, `peak_rss_kb`, `par2_ms`, `internal_ms`, `conflicts`, `decisions`, `propagations`, and `exit_code`.
  - Refreshable live summaries (`<output>.summary.md` and `<output>.summary.json`) track per-collection PAR-2, verdict disagreements, `BADSAT` alerts, and every collection/instance where Frobenius is not `#1` fastest.
  - Safe `--resume` skips every `(collection, format, instance, solver)` already present in `--output`.
  - Optional `--load-guard <MAX_LOAD>` waits before launching until the machine is quiet.

## Usage

### 1. Clone and Compile All Competitor Solvers

```bash
python3 src/run_benchmarks.py build-solvers \
    --solvers-dir ~/sat-solvers \
    --jobs 8
```

To also build Frobenius (standard release or LLVM PGO):

```bash
python3 src/run_benchmarks.py build-solvers \
    --solvers-dir ~/sat-solvers \
    --frobenius-dir /path/to/papers/new/P_NE_NP/solver \
    --pgo \
    --jobs 8
```

### 2. Run All Benchmarks Across All Solvers (Parallel Work Queue, 1 Core per Job)

```bash
# Preview queue without executing:
python3 src/run_benchmarks.py run \
    --solvers-dir ~/sat-solvers \
    --frobenius-dir /path/to/papers/new/P_NE_NP/solver \
    --max-cores 8 \
    --output ~/sat_bench_results.jsonl \
    --dry-run

# Full quiet-host offline run (e.g. wait until load <= 2.0, reserve cores 14-15):
python3 src/run_benchmarks.py run \
    --solvers-dir ~/sat-solvers \
    --frobenius-dir /path/to/papers/new/P_NE_NP/solver \
    --cores 0,1,2,3,4,5,6,7,8,9,10,11 \
    --load-guard 2.0 \
    --output ~/sat_bench_results.jsonl
```

Resuming after an interruption (zero lost work):

```bash
python3 src/run_benchmarks.py run \
    --solvers-dir ~/sat-solvers \
    --frobenius-dir /path/to/papers/new/P_NE_NP/solver \
    --cores 0,1,2,3,4,5,6,7 \
    --resume \
    --output ~/sat_bench_results.jsonl
```

### 3. Live Monitoring (In Another Terminal While Running or Afterward)

```bash
# Stream raw per-run JSON records live:
tail -f ~/sat_bench_results.jsonl

# Print live per-collection PAR-2 and Frobenius deficit report:
python3 src/run_benchmarks.py summarize --input ~/sat_bench_results.jsonl
```

## Common CLI Switches (`run`)

| Switch | Default | Purpose |
|---|---|---|
| `--solvers-dir <DIR>` | *(optional)* | Directory containing competitor `bin/{cadical,cryptominisat5,dense-solver,kissat}` |
| `--frobenius-dir <DIR>` | *(optional)* | Path to Frobenius `solver/` directory (auto-discovers `target/release/frobenius`) |
| `--frobenius-bin <PATH>` | *(optional)* | Direct path to a specific `frobenius` executable |
| `--output <FILE.jsonl>` | *(required)* | Incremental JSONL output file (`flush` + `fsync` per run) |
| `--max-cores <N>` | `phys_cores - 1` | Max parallel jobs (strictly 1 job per physical core, no SMT sharing) |
| `--cores <list>` | auto physical | Explicit CPU core IDs (e.g. `0,1,2,3,4,5,6,7`) |
| `--solvers <list>` | all 5 CNF solvers | Subset of `frobenius,cadical,cryptominisat5-cnf,cryptominisat5-xcnf,dense-solver,kissat` |
| `--formats <list>` | `cnf` | Any subset of `cnf,xcnf,aig,anf,mata` |
| `--collections <list>` | all 93 | Run only named collections (e.g. `integer-factoring,mod-circuit-sat`) |
| `--exclude-collections <list>` | none | Skip specific collections |
| `--timeout <sec>` | README `T_max` | Override per-collection timeout globally |
| `--load-guard <float>` | `0` (off) | Wait before starting until 1-min host load average $\le$ value |
| `--resume` | off | Skip `(collection, format, instance, solver)` records already in `--output` |
| `--include-oeis-unknown` | off | By default skips `UNKNOWN` rows in `guillochon-oeis-*` |
| `--no-verify-models` | verify ON | Skip raw-CNF SAT model verification |
| `--dry-run` | off | Print resolved solvers and queue without running |
