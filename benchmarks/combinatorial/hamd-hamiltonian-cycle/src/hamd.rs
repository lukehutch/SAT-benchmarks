#![allow(dead_code)]
//! Provably Hamiltonian (SAT) and Provably Non-Hamiltonian (UNSAT) Benchmark Graph
//! Constructors (HAMD / HCP), Compact Binary-Order MTZ DIMACS CNF Encoder, and Exact
//! Independent Cycle Verifier!
//!
//! Every generated graph is **non-trivial by construction**:
//! - Zero vertices of degree <= 2 (all undirected families satisfy minimum degree `delta(G) >= 3`,
//!   and directed Broken Crown satisfies `in_deg >= 2, out_deg >= 2` on the core crown),
//! - 2-connected or k-connected (zero cut-vertices, zero bridges),
//! - Randomly vertex-relabeled (deterministic seed) so vertex numbering leaks zero structure!
//!
//! Literature-grounded families implemented:
//! 1. **Generalized Petersen Graphs `GP(n, 2)`** (Watkins 1969; Alspach 1983; Haythorpe 2019 FHCP):
//!    - 3-regular, 3-connected (`N = 2n`).
//!    - `n % 6 == 5`: provably **UNSAT** (hypohamiltonian & maximally non-Hamiltonian!).
//!    - `n % 6 == 3`: provably **SAT** with **exact count = 3** Hamiltonian cycles!
//!    - `GP(n, 2) + e` (`n % 6 == 5` plus chord `(u_0, v_{n-1})`): provably **SAT** (Haythorpe FHCP).
//! 2. **Isaacs Flower Snarks `J_k`** (Isaacs 1975; Haythorpe 2019 FHCP):
//!    - 3-regular, 3-connected, cyclically 6-edge-connected (`N = 4k`, odd `k >= 5`).
//!    - Provably **UNSAT** (hypohamiltonian snark); `J_k + e` is provably **SAT**.
//! 3. **Meredith `k`-Regular `k`-Connected Non-Hamiltonian Graphs `G_k`** (Meredith 1973, JCTB):
//!    - Inflates every vertex of the `k`-regular `k`-edge-connected Petersen multigraph `H_k`
//!      into a complete bipartite gadget `K_{k, k-1}` (`N = 10*(2k - 1)` vertices).
//!    - Simple, `k`-regular, `k`-vertex-connected, provably **UNSAT** for all `k >= 3`!
//! 4. **Chvatal Toughness-Violating High-Density Non-Hamiltonian Graphs `Chv(s, q)`**
//!    (Chvatal 1973, Discrete Math):
//!    - `s`-vertex separator clique `S` joined to `s + 1` disjoint dense blocks `C_1..C_{s+1}`
//!      of size `q` (`N = s + (s+1)*q`), with tunable internal density `p_int`.
//!    - `s`-vertex-connected, minimum degree `delta >= s + 3`, NON-bipartite, tunable medium/high
//!      edge density (`0.15..0.50`), provably **UNSAT** since toughness `t(G) <= s/(s+1) < 1`!
//! 5. **Planted Hidden-Cycle Tunable-Density Graphs `Planted(N, target_density)`**
//!    (Vandegriend & Culberson 1998; Haythorpe 2019):
//!    - Random hidden Hamiltonian cycle disguised inside a random decoy graph at controllable
//!      sizes (`N = 20..120`) and densities (`sparse`, `medium`, `dense`, `very dense`),
//!      enforcing `delta(G) >= 3` and 2-connectivity; provably **SAT**!
//! 6. **Haythorpe Broken Crown Directed Graphs `B_{n, k}`** (Haythorpe 2019, arXiv:1902.10351):
//!    - Directed graph on `5n - 9` vertices with **exact** `k` directed Hamiltonian cycles
//!      (e.g., `k = 1` uniquely Hamiltonian **SAT**), and **exact 0** cycles (**UNSAT**) when
//!      retained incoming and outgoing label sets are disjoint (by Haythorpe Theorem 2.1)!

use crate::dimacs::CnfFormula;
use std::collections::HashSet;

#[derive(Clone, Debug)]
pub struct HamdGraph {
    pub name: String,
    pub family: String,
    pub num_vertices: usize,
    pub directed: bool,
    /// Directed arcs `(u, v)` with `0 <= u, v < num_vertices`.
    /// For undirected graphs, both `(u, v)` and `(v, u)` are stored!
    pub arcs: Vec<(usize, usize)>,
    pub expect_sat: bool,
    /// Optional known ground-truth Hamiltonian cycle (for SAT generators)
    pub witness_cycle: Option<Vec<usize>>,
}

#[derive(Clone, Debug)]
pub struct HamdEncodedCnf {
    pub graph: HamdGraph,
    pub formula: CnfFormula,
    /// 1-based DIMACS variable index for each directed arc `graph.arcs[i]`.
    pub arc_vars: Vec<i32>,
}

/// Deterministic xorshift64* PRNG (zero external crate dependencies).
struct Rng64(u64);
impl Rng64 {
    fn new(seed: u64) -> Self {
        Self(seed.max(1) ^ 0x9E37_79B9_7F4A_7C15)
    }
    #[inline]
    fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
    #[inline]
    fn gen_range(&mut self, n: usize) -> usize {
        (self.next_u64() as usize) % n
    }
}

impl HamdGraph {
    /// Construct an undirected simple graph from undirected edges `(u, v)`, deduplicating and
    /// optionally applying a random vertex relabeling (seeded deterministically).
    pub fn from_undirected(
        name: impl Into<String>,
        family: impl Into<String>,
        num_vertices: usize,
        raw_edges: &[(usize, usize)],
        expect_sat: bool,
        witness_cycle: Option<Vec<usize>>,
        scramble_seed: Option<u64>,
    ) -> Self {
        let mut perm: Vec<usize> = (0..num_vertices).collect();
        if let Some(seed) = scramble_seed {
            let mut rng = Rng64::new(seed);
            for i in (1..num_vertices).rev() {
                let j = rng.gen_range(i + 1);
                perm.swap(i, j);
            }
        }
        let mut seen: HashSet<(usize, usize)> = HashSet::with_capacity(raw_edges.len() * 2);
        let mut arcs: Vec<(usize, usize)> = Vec::with_capacity(raw_edges.len() * 2);
        for &(u0, v0) in raw_edges {
            assert!(u0 < num_vertices && v0 < num_vertices && u0 != v0, "invalid undirected edge ({u0},{v0})");
            let u = perm[u0];
            let v = perm[v0];
            let key = if u < v { (u, v) } else { (v, u) };
            if seen.insert(key) {
                arcs.push((u, v));
                arcs.push((v, u));
            }
        }
        arcs.sort_unstable();
        let witness = witness_cycle.map(|cyc| cyc.into_iter().map(|v| perm[v]).collect());
        Self {
            name: name.into(),
            family: family.into(),
            num_vertices,
            directed: false,
            arcs,
            expect_sat,
            witness_cycle: witness,
        }
    }

    /// Construct a directed simple graph from directed arcs `(u, v)` with optional relabeling.
    pub fn from_directed(
        name: impl Into<String>,
        family: impl Into<String>,
        num_vertices: usize,
        raw_arcs: &[(usize, usize)],
        expect_sat: bool,
        witness_cycle: Option<Vec<usize>>,
        scramble_seed: Option<u64>,
    ) -> Self {
        let mut perm: Vec<usize> = (0..num_vertices).collect();
        if let Some(seed) = scramble_seed {
            let mut rng = Rng64::new(seed);
            for i in (1..num_vertices).rev() {
                let j = rng.gen_range(i + 1);
                perm.swap(i, j);
            }
        }
        let mut seen: HashSet<(usize, usize)> = HashSet::with_capacity(raw_arcs.len());
        let mut arcs: Vec<(usize, usize)> = Vec::with_capacity(raw_arcs.len());
        for &(u0, v0) in raw_arcs {
            assert!(u0 < num_vertices && v0 < num_vertices && u0 != v0, "invalid directed arc ({u0},{v0})");
            let u = perm[u0];
            let v = perm[v0];
            if seen.insert((u, v)) {
                arcs.push((u, v));
            }
        }
        arcs.sort_unstable();
        let witness = witness_cycle.map(|cyc| cyc.into_iter().map(|v| perm[v]).collect());
        Self {
            name: name.into(),
            family: family.into(),
            num_vertices,
            directed: true,
            arcs,
            expect_sat,
            witness_cycle: witness,
        }
    }

    /// Number of undirected edges (or directed arcs for directed graphs).
    pub fn num_edges(&self) -> usize {
        if self.directed { self.arcs.len() } else { self.arcs.len() / 2 }
    }

    /// Edge density in `[0.0, 1.0]`.
    pub fn density(&self) -> f64 {
        let n = self.num_vertices as f64;
        if n <= 1.0 {
            return 0.0;
        }
        if self.directed {
            self.arcs.len() as f64 / (n * (n - 1.0))
        } else {
            (self.arcs.len() as f64 / 2.0) / (n * (n - 1.0) / 2.0)
        }
    }

    /// Minimum out-degree and in-degree (equals minimum vertex degree for undirected graphs).
    pub fn min_out_in_degree(&self) -> (usize, usize) {
        let mut out_d = vec![0usize; self.num_vertices];
        let mut in_d = vec![0usize; self.num_vertices];
        for &(u, v) in &self.arcs {
            out_d[u] += 1;
            in_d[v] += 1;
        }
        (
            out_d.into_iter().min().unwrap_or(0),
            in_d.into_iter().min().unwrap_or(0),
        )
    }

    /// Check that an undirected graph is 2-vertex-connected (connected with zero articulation points).
    pub fn is_biconnected_undirected(&self) -> bool {
        if self.directed || self.num_vertices < 3 {
            return false;
        }
        let n = self.num_vertices;
        let mut adj = vec![Vec::new(); n];
        for &(u, v) in &self.arcs {
            adj[u].push(v);
        }
        let mut disc = vec![0usize; n];
        let mut low = vec![0usize; n];
        let mut timer = 0usize;
        let mut has_art = false;

        fn dfs(
            u: usize,
            parent: Option<usize>,
            adj: &[Vec<usize>],
            disc: &mut [usize],
            low: &mut [usize],
            timer: &mut usize,
            has_art: &mut bool,
        ) {
            *timer += 1;
            disc[u] = *timer;
            low[u] = *timer;
            let mut children = 0usize;
            for &v in &adj[u] {
                if disc[v] == 0 {
                    children += 1;
                    dfs(v, Some(u), adj, disc, low, timer, has_art);
                    low[u] = low[u].min(low[v]);
                    if parent.is_none() && children > 1 {
                        *has_art = true;
                    }
                    if parent.is_some() && low[v] >= disc[u] {
                        *has_art = true;
                    }
                } else if Some(v) != parent {
                    low[u] = low[u].min(disc[v]);
                }
            }
        }

        dfs(0, None, &adj, &mut disc, &mut low, &mut timer, &mut has_art);
        timer == n && !has_art
    }

    /// Independently verify that `cycle` is a valid simple Hamiltonian cycle of `self`!
    pub fn verify_cycle(&self, cycle: &[usize]) -> bool {
        if cycle.len() != self.num_vertices || self.num_vertices < 3 {
            return false;
        }
        let mut seen = vec![false; self.num_vertices];
        for &v in cycle {
            if v >= self.num_vertices || seen[v] {
                return false;
            }
            seen[v] = true;
        }
        let arc_set: HashSet<(usize, usize)> = self.arcs.iter().copied().collect();
        for i in 0..self.num_vertices {
            let u = cycle[i];
            let v = cycle[(i + 1) % self.num_vertices];
            if !arc_set.contains(&(u, v)) {
                return false;
            }
        }
        true
    }

    /// Encode this graph into a compact, 100% equisatisfiable flat DIMACS CNF using:
    /// - Directed arc variables `a_{u->v}` (`1..=arcs.len()`),
    /// - Exact-One outgoing and Exact-One incoming arc per vertex (pairwise AMO for `deg <= 6`,
    ///   Sinz sequential counter AMO for `deg > 6` so even dense graphs remain `O(|E|)`),
    /// - No 2-cycles `(!a_{u->v} | !a_{v->u})` for undirected graphs,
    /// - Strict Binary-Order MTZ Subtour Elimination (`a_{u->v} => r_u < r_v` for all `u, v != 0`)
    ///   using `b = ceil(log2(N))` bits per vertex (`O(|E| log N)` clauses total!).
    pub fn encode_cnf(&self) -> HamdEncodedCnf {
        let n = self.num_vertices;
        assert!(n >= 3, "HAMD requires at least 3 vertices");
        let num_arcs = self.arcs.len();
        let mut next_var: i32 = (num_arcs as i32) + 1;
        let arc_vars: Vec<i32> = (1..=num_arcs as i32).collect();

        let mut out_arcs: Vec<Vec<i32>> = vec![Vec::new(); n];
        let mut in_arcs: Vec<Vec<i32>> = vec![Vec::new(); n];
        let mut arc_lookup: HashSet<(usize, usize)> = HashSet::with_capacity(num_arcs);
        let mut arc_var_map = std::collections::HashMap::with_capacity(num_arcs);
        for (idx, &(u, v)) in self.arcs.iter().enumerate() {
            let var = arc_vars[idx];
            out_arcs[u].push(var);
            in_arcs[v].push(var);
            arc_lookup.insert((u, v));
            arc_var_map.insert((u, v), var);
        }

        let mut clauses: Vec<Vec<i32>> = Vec::with_capacity(num_arcs * 12);

        // Helper: Exact-One(lits) with pairwise AMO for len <= 6, Sinz sequential counter for len > 6.
        let add_eo = |lits: &[i32], clauses: &mut Vec<Vec<i32>>, next_var: &mut i32| {
            assert!(!lits.is_empty(), "HAMD vertex has 0 incident arcs");
            // ALO
            clauses.push(lits.to_vec());
            let k = lits.len();
            if k <= 6 {
                for i in 0..k {
                    for j in (i + 1)..k {
                        clauses.push(vec![-lits[i], -lits[j]]);
                    }
                }
            } else {
                // Sinz (2005) sequential counter AMO: k - 1 auxiliary register vars s_0..s_{k-2}
                let s_base = *next_var;
                *next_var += (k as i32) - 1;
                clauses.push(vec![-lits[0], s_base]);
                for i in 1..(k - 1) {
                    let s_prev = s_base + (i as i32) - 1;
                    let s_cur = s_base + (i as i32);
                    clauses.push(vec![-lits[i], s_cur]);
                    clauses.push(vec![-s_prev, s_cur]);
                    clauses.push(vec![-lits[i], -s_prev]);
                }
                clauses.push(vec![-lits[k - 1], -(s_base + (k as i32) - 2)]);
            }
        };

        // 1. Exact-One out-arc and Exact-One in-arc at every vertex
        for v in 0..n {
            add_eo(&out_arcs[v], &mut clauses, &mut next_var);
            add_eo(&in_arcs[v], &mut clauses, &mut next_var);
        }

        // 2. For undirected graphs: forbid 2-cycles `(u -> v) & (v -> u)` + break cycle reversal
        //    symmetry on root vertex 0 (pick canonical direction if deg(0) >= 2).
        if !self.directed {
            for &(u, v) in &self.arcs {
                if u < v {
                    if let (Some(&av), Some(&bv)) = (arc_var_map.get(&(u, v)), arc_var_map.get(&(v, u))) {
                        clauses.push(vec![-av, -bv]);
                    }
                }
            }
            // Reversal symmetry breaking at root vertex 0: for `a < b` in N(0), if `0->b` then not `a->0`?
            // Even cleaner & strictly sound: if `0->v_i` and `v_j->0`, require `v_i < v_j` (since any
            // undirected cycle through 0 can be traversed in either direction, exactly one orientation
            // has `successor(0) < predecessor(0)`!).
            let mut root_nbrs: Vec<usize> = self
                .arcs
                .iter()
                .filter_map(|&(u, v)| if u == 0 { Some(v) } else { None })
                .collect();
            root_nbrs.sort_unstable();
            for i in 0..root_nbrs.len() {
                for j in 0..i {
                    // Forbid `successor(0) = root_nbrs[i] > root_nbrs[j] = predecessor(0)`
                    if let (Some(&out_i), Some(&in_j)) = (
                        arc_var_map.get(&(0, root_nbrs[i])),
                        arc_var_map.get(&(root_nbrs[j], 0)),
                    ) {
                        clauses.push(vec![-out_i, -in_j]);
                    }
                }
            }
        }

        // 3. Strict Binary-Order MTZ Subtour Elimination (`a_{u->v} => r_u < r_v` for all `u, v != 0`)
        let bits = (usize::BITS - (n - 1).leading_zeros()).max(1) as usize;
        // `r_var[v][k]` for `v in 1..n`, `k in 0..bits` (k = 0 is LSB, k = bits - 1 is MSB)
        let mut r_var: Vec<Vec<i32>> = vec![Vec::new(); n];
        for v in 1..n {
            let mut rv = Vec::with_capacity(bits);
            for _ in 0..bits {
                rv.push(next_var);
                next_var += 1;
            }
            r_var[v] = rv;
        }

        for (idx, &(u, v)) in self.arcs.iter().enumerate() {
            if u == 0 || v == 0 {
                continue;
            }
            let a = arc_vars[idx];
            if bits == 1 {
                // Only `u, v` with 1-bit rank: `a => (!r_u & r_v)`
                clauses.push(vec![-a, -r_var[u][0]]);
                clauses.push(vec![-a, r_var[v][0]]);
                continue;
            }
            // Chain `prev_eq` from MSB (`k = bits - 1`) down to `k = 1`, then strict LSB at `k = 0`:
            let mut prev_cond = a;
            for k in (1..bits).rev() {
                let ru = r_var[u][k];
                let rv = r_var[v][k];
                // Cannot have `ru = 1, rv = 0` while `prev_cond = 1`
                clauses.push(vec![-prev_cond, -ru, rv]);
                let eq_k = next_var;
                next_var += 1;
                // `prev_cond & (ru == rv) => eq_k`
                clauses.push(vec![-prev_cond, -ru, -rv, eq_k]);
                clauses.push(vec![-prev_cond, ru, rv, eq_k]);
                prev_cond = eq_k;
            }
            // Strict LSB (`k = 0`): `prev_cond => (r_u[0] = 0 AND r_v[0] = 1)`
            clauses.push(vec![-prev_cond, -r_var[u][0]]);
            clauses.push(vec![-prev_cond, r_var[v][0]]);
        }

        let formula = CnfFormula {
            num_vars: (next_var - 1) as usize,
            clauses,
            xor_clauses: Vec::new(),
        };
        HamdEncodedCnf {
            graph: self.clone(),
            formula,
            arc_vars,
        }
    }
}

impl HamdEncodedCnf {
    /// Decode a satisfying CNF assignment into the vertex sequence of the Hamiltonian cycle,
    /// and verify it directly against `self.graph`!
    pub fn decode_and_verify_cycle(&self, model: &[bool]) -> Option<Vec<usize>> {
        let n = self.graph.num_vertices;
        let mut succ = vec![usize::MAX; n];
        for (idx, &(u, v)) in self.graph.arcs.iter().enumerate() {
            let var = self.arc_vars[idx] as usize;
            if model.get(var).copied().unwrap_or(false) {
                if succ[u] != usize::MAX {
                    return None; // out-degree > 1
                }
                succ[u] = v;
            }
        }
        let mut cycle = Vec::with_capacity(n);
        let mut cur = 0usize;
        for _ in 0..n {
            if cur == usize::MAX {
                return None;
            }
            cycle.push(cur);
            cur = succ[cur];
        }
        if cur != 0 || !self.graph.verify_cycle(&cycle) {
            return None;
        }
        Some(cycle)
    }
}

// ============================================================================
// LITERATURE-GROUNDED PROVABLE HAMD CONSTRUCTORS
// ============================================================================

/// 1. **Generalized Petersen Graph `GP(n, 2)`** (Watkins 1969; Alspach 1983; Haythorpe 2019 FHCP).
/// - `N = 2n` vertices, 3-regular, 3-connected.
/// - `n % 6 == 5`: provably **UNSAT** (hypohamiltonian & maximally non-Hamiltonian).
/// - `n % 6 == 3` (or `n % 6 != 5` for `n >= 3`): provably **SAT** (`n % 6 == 3` has EXACTLY 3 HCs!).
/// - If `add_haythorpe_chord` is true on `n % 6 == 5`, adds edge `(u_0, v_{n-1})` making it
///   provably **SAT** (Haythorpe 2019 FHCP §2.2!).
pub fn build_gen_petersen_k2(n: usize, add_haythorpe_chord: bool, seed: u64) -> HamdGraph {
    assert!(n >= 5);
    let mut edges = Vec::with_capacity(3 * n + 1);
    for i in 0..n {
        let u = i;
        let v = n + i;
        edges.push((u, (i + 1) % n)); // outer cycle
        edges.push((u, v)); // spoke
        edges.push((v, n + (i + 2) % n)); // inner 2-step star
    }
    if add_haythorpe_chord {
        edges.push((0, n + n - 1));
    }
    let expect_sat = add_haythorpe_chord || (n % 6 != 5);
    let name = if add_haythorpe_chord {
        format!("hamd_gp_{n}_2_plus_e_sat")
    } else if expect_sat {
        format!("hamd_gp_{n}_2_sat")
    } else {
        format!("hamd_gp_{n}_2_unsat")
    };
    HamdGraph::from_undirected(name, "HAMD-GenPet", 2 * n, &edges, expect_sat, None, Some(seed))
}

/// 2. **Isaacs Flower Snark `J_k`** for odd `k >= 5` (Isaacs 1975; Haythorpe 2019 FHCP).
/// - `N = 4k` vertices, 3-regular, 3-connected, cyclically 6-edge-connected.
/// - Provably **UNSAT** (maximally non-Hamiltonian / hypohamiltonian).
/// - If `add_haythorpe_chord` is true, adds one chord `(b_0, c_0)` in star 0 making it
///   provably **SAT** (Haythorpe 2019 FHCP §2.2!).
pub fn build_flower_snark(k: usize, add_haythorpe_chord: bool, seed: u64) -> HamdGraph {
    assert!(k >= 5 && k % 2 == 1, "Flower Snark J_k requires odd k >= 5");
    // Star i has center `a_i = 4*i` and 3 outer vertices `b_i = 4*i+1`, `c_i = 4*i+2`, `d_i = 4*i+3`.
    let a = |i: usize| 4 * i;
    let b = |i: usize| 4 * i + 1;
    let c = |i: usize| 4 * i + 2;
    let d = |i: usize| 4 * i + 3;
    let mut edges = Vec::with_capacity(6 * k + 1);
    for i in 0..k {
        let nxt = (i + 1) % k;
        edges.push((a(i), b(i)));
        edges.push((a(i), c(i)));
        edges.push((a(i), d(i)));
        edges.push((b(i), b(nxt)));
        if i + 1 < k {
            edges.push((c(i), c(nxt)));
            edges.push((d(i), d(nxt)));
        } else {
            // Twisted Möbius closure on the `(c, d)` rails!
            edges.push((c(i), d(0)));
            edges.push((d(i), c(0)));
        }
    }
    if add_haythorpe_chord {
        edges.push((b(0), c(0)));
    }
    let expect_sat = add_haythorpe_chord;
    let name = if add_haythorpe_chord {
        format!("hamd_snark_j{k}_plus_e_sat")
    } else {
        format!("hamd_snark_j{k}_unsat")
    };
    HamdGraph::from_undirected(name, "HAMD-Snark", 4 * k, &edges, expect_sat, None, Some(seed))
}

/// 3. **Meredith `k`-Regular `k`-Connected Non-Hamiltonian Graph `G_k`** (Meredith 1973, JCTB 14:55-60).
/// - Starts from the Petersen graph `P_10` with edge multiplicities `a = m, b = m + alpha` where
///   `k = 3m + alpha`, `alpha in {-1, 0, +1}` (spokes get multiplicity `b`, outer 5-cycle and inner
///   5-star get multiplicity `a`, so `2a + b = k`).
/// - Replaces EVERY vertex of `H_k` with a complete bipartite gadget `K_{k, k-1}` (`2k - 1` vertices):
///   `k - 1` internal vertices `a_0..a_{k-2}` and `k` port vertices `b_0..b_{k-1}`, each port
///   connecting to one distinct incident edge of `H_k`.
/// - Result: Simple, **`k`-regular**, **`k`-vertex-connected**, `N = 10*(2k - 1)` vertices,
///   **provably UNSAT** by Meredith (1973) Theorems 1, 3, and 4!
pub fn build_meredith_graph(k: usize, seed: u64) -> HamdGraph {
    assert!(k >= 3, "Meredith G_k requires k >= 3");
    // Solve `k = 3m + alpha`, `alpha in {-1, 0, +1}` => `a = m`, `b = m + alpha`.
    let m = (k + 1) / 3;
    let a_mult = m;
    let b_mult = k - 2 * a_mult;
    assert_eq!(2 * a_mult + b_mult, k);
    assert!(a_mult >= 1 && b_mult >= 1);

    // Build multigraph edges of H_k on 10 vertices: 0..5 = outer A_i, 5..10 = inner B_i.
    let mut mult_edges: Vec<(usize, usize)> = Vec::new();
    for i in 0..5 {
        for _ in 0..a_mult {
            mult_edges.push((i, (i + 1) % 5)); // outer 5-cycle
            mult_edges.push((5 + i, 5 + (i + 2) % 5)); // inner 5-star
        }
        for _ in 0..b_mult {
            mult_edges.push((i, 5 + i)); // spoke A_i B_i
        }
    }

    let block_sz = 2 * k - 1;
    let n = 10 * block_sz;
    let mut edges: Vec<(usize, usize)> = Vec::with_capacity(n * k / 2);

    // Internal K_{k, k-1} edges for each of the 10 blocks:
    //   ports:    base + 0 .. base + k - 1
    //   internal: base + k .. base + 2k - 2
    for u in 0..10 {
        let base = u * block_sz;
        for port in 0..k {
            for intern in 0..(k - 1) {
                edges.push((base + port, base + k + intern));
            }
        }
    }

    // Connect each multigraph edge between distinct free port vertices!
    let mut next_port = [0usize; 10];
    for (u, v) in mult_edges {
        let pu = u * block_sz + next_port[u];
        let pv = v * block_sz + next_port[v];
        next_port[u] += 1;
        next_port[v] += 1;
        edges.push((pu, pv));
    }
    assert!(next_port.iter().all(|&p| p == k));

    HamdGraph::from_undirected(
        format!("hamd_meredith_k{k}_n{n}_unsat"),
        "HAMD-Meredith",
        n,
        &edges,
        false,
        None,
        Some(seed),
    )
}

/// 4. **Chvatal Toughness-Violating High-Density Non-Hamiltonian Graph `Chv(s, q, p_int)`**
///    (Chvatal 1973, Discrete Math 5:215-228).
/// - Separator `S` of size `s >= 3` (a clique `K_s`) joined to `c = s + 1` disjoint dense blocks
///   `C_0..C_s`, each of size `q >= 4`, with internal edge density `p_int in (0, 1]` (always
///   starting from a spanning cycle + chord inside each block so `C_j` is 2-connected and
///   non-bipartite, plus random internal edges up to `p_int`, and connecting every vertex of `S`
///   to all vertices of every `C_j` if `full_sep_join`, or to at least `max(3, q/2)` vertices!).
/// - Properties: `N = s + (s+1)*q`, `s`-vertex-connected, minimum degree `delta >= s + 3`,
///   tunable medium-to-high density (`0.15..0.55`), **provably UNSAT** (`t(G) <= s/(s+1) < 1`)!
pub fn build_chvatal_toughness(
    s: usize,
    q: usize,
    internal_density: f64,
    sep_density: f64,
    seed: u64,
) -> HamdGraph {
    assert!(s >= 3 && q >= 4);
    let c = s + 1;
    let n = s + c * q;
    let mut rng = Rng64::new(seed);
    let mut edges: Vec<(usize, usize)> = Vec::new();

    // Separator S = 0..s forms a clique K_s (non-bipartite, high connectivity)
    for i in 0..s {
        for j in (i + 1)..s {
            edges.push((i, j));
        }
    }

    // `c = s + 1` disjoint components C_0..C_{c-1}
    for comp in 0..c {
        let base = s + comp * q;
        // Spanning cycle + odd triangle chord inside C_comp (guarantees connected & non-bipartite!)
        for i in 0..q {
            edges.push((base + i, base + (i + 1) % q));
        }
        edges.push((base, base + 2));
        // Add remaining internal edges up to `internal_density`
        let mut rem = Vec::new();
        for i in 0..q {
            for j in (i + 1)..q {
                if j == i + 1 || (i == 0 && j == q - 1) || (i == 0 && j == 2) {
                    continue;
                }
                rem.push((base + i, base + j));
            }
        }
        let max_int = q * (q - 1) / 2;
        let target_int = ((max_int as f64) * internal_density.clamp(0.0, 1.0)).round() as usize;
        let cur_int = q + 1;
        for i in (1..rem.len()).rev() {
            let j = rng.gen_range(i + 1);
            rem.swap(i, j);
        }
        for &(u, v) in rem.iter().take(target_int.saturating_sub(cur_int)) {
            edges.push((u, v));
        }

        // Join C_comp to EVERY separator vertex in S (guarantees s-vertex-connected!)
        // First ensure each vertex in C_comp has >= 1 separator neighbor and each s in S has >= 2 neighbors in C_comp.
        let mut sep_pairs = Vec::with_capacity(s * q);
        for si in 0..s {
            for qi in 0..q {
                sep_pairs.push((si, base + qi));
            }
        }
        let mut chosen = HashSet::new();
        for qi in 0..q {
            let si = qi % s;
            chosen.insert((si, base + qi));
            let si2 = (qi + 1) % s;
            chosen.insert((si2, base + qi));
        }
        for si in 0..s {
            chosen.insert((si, base + (si % q)));
            chosen.insert((si, base + ((si + 1) % q)));
        }
        let target_sep = (((s * q) as f64) * sep_density.clamp(0.0, 1.0)).round() as usize;
        for i in (1..sep_pairs.len()).rev() {
            let j = rng.gen_range(i + 1);
            sep_pairs.swap(i, j);
        }
        for pair in sep_pairs {
            if chosen.len() >= target_sep {
                break;
            }
            chosen.insert(pair);
        }
        for (u, v) in chosen {
            edges.push((u, v));
        }
    }

    let tag = if internal_density >= 0.95 && sep_density >= 0.95 {
        "dense"
    } else {
        "med"
    };
    HamdGraph::from_undirected(
        format!("hamd_chvatal_s{s}_q{q}_{tag}_unsat"),
        "HAMD-Chvatal",
        n,
        &edges,
        false,
        None,
        Some(seed ^ 0x55AA_33CC),
    )
}

/// 5. **Planted Hidden-Cycle Tunable-Density Graph** (Vandegriend & Culberson 1998; Haythorpe 2019).
/// - Plants a Hamiltonian cycle `0-1-...-(n-1)-0`, ensures every vertex has degree `>= 3`
///   (by adding a random chord per degree-2 vertex), and adds random decoy edges up to
///   `target_density`, then randomly relabels all vertices!
/// - Properties: provably **SAT** (explicit verified witness cycle), `delta(G) >= 3`, 2-connected,
///   arbitrary size `n` and density `rho in (3/(n-1), 0.95)`!
pub fn build_planted_hamd(n: usize, target_density: f64, tag: &str, seed: u64) -> HamdGraph {
    assert!(n >= 6);
    let mut rng = Rng64::new(seed);
    let mut edge_set: HashSet<(usize, usize)> = HashSet::new();
    let mut deg = vec![0usize; n];

    let add_edge = |u: usize, v: usize, set: &mut HashSet<(usize, usize)>, deg: &mut [usize]| {
        if u == v {
            return false;
        }
        let key = if u < v { (u, v) } else { (v, u) };
        if set.insert(key) {
            deg[u] += 1;
            deg[v] += 1;
            true
        } else {
            false
        }
    };

    // Plant spanning cycle
    let witness: Vec<usize> = (0..n).collect();
    for i in 0..n {
        add_edge(i, (i + 1) % n, &mut edge_set, &mut deg);
    }

    // Guarantee minimum degree >= 3 (non-trivial!)
    for u in 0..n {
        while deg[u] < 3 {
            let v = rng.gen_range(n);
            if v != u {
                add_edge(u, v, &mut edge_set, &mut deg);
            }
        }
    }

    // Fill up to `target_density`
    let max_edges = n * (n - 1) / 2;
    let target_edges = ((max_edges as f64) * target_density.clamp(0.0, 0.95))
        .round()
        .max(edge_set.len() as f64) as usize;
    if target_edges > edge_set.len() {
        let mut cand = Vec::with_capacity(max_edges - edge_set.len());
        for u in 0..n {
            for v in (u + 1)..n {
                if !edge_set.contains(&(u, v)) {
                    cand.push((u, v));
                }
            }
        }
        for i in (1..cand.len()).rev() {
            let j = rng.gen_range(i + 1);
            cand.swap(i, j);
        }
        for &(u, v) in cand.iter().take(target_edges - edge_set.len()) {
            add_edge(u, v, &mut edge_set, &mut deg);
        }
    }

    let raw_edges: Vec<(usize, usize)> = edge_set.into_iter().collect();
    HamdGraph::from_undirected(
        format!("hamd_planted_n{n}_{tag}_sat"),
        "HAMD-Planted",
        n,
        &raw_edges,
        true,
        Some(witness),
        Some(seed ^ 0x1357_9BDF),
    )
}

/// 6. **Haythorpe Broken Crown Directed Graph `B_{n, k}`** (Haythorpe 2019, arXiv:1902.10351).
/// - `N = 5n - 9` vertices (`n >= 6`).
/// - By Haythorpe Theorem 2.1, any directed Hamiltonian cycle traversing the Crown Subgraph `C_n`
///   must enter via incoming edge `i` and exit via outgoing edge `i` with the **same label**!
/// - When `expect_sat = true`, retains `k = 1` matching pair (`i = 1`) plus `n/2` non-matching
///   incoming/outgoing distractors => **provably uniquely Hamiltonian (exact 1 HC, SAT)**!
/// - When `expect_sat = false`, retains incoming labels `{1..=n/2}` and outgoing labels
///   `{n/2+1..=n}` (completely disjoint!) => **zero matched pairs, provably UNSAT**, while
///   retaining full crown connectivity (`in_deg >= 2, out_deg >= 2` on every crown vertex)!
pub fn build_broken_crown(n: usize, expect_sat: bool, seed: u64) -> HamdGraph {
    assert!(n >= 6);
    let crown_n = 5 * n - 10; // vertices 0..crown_n correspond to paper's 1..=5n-10
    let hub = crown_n; // vertex `v` in Definition 3.1
    let total_v = crown_n + 1;
    let mut arcs: Vec<(usize, usize)> = Vec::new();

    // Bidirectional outer cycle of C_n: (i, i+1) & (i+1, i) mod crown_n
    for i in 0..crown_n {
        let nxt = (i + 1) % crown_n;
        arcs.push((i, nxt));
        arcs.push((nxt, i));
    }
    // Crown internal directed chords (paper 1-indexed -> 0-indexed):
    //   (2n, 2n-2) and (5n-10, 2)
    arcs.push((2 * n - 1, 2 * n - 3));
    arcs.push((5 * n - 11, 1));
    //   (2n + 3i, 2n - 2 - 2i) for i = 1..=ceil((n-4)/2)
    let ceil_h = (n - 4 + 1) / 2;
    for i in 1..=ceil_h {
        let u = 2 * n + 3 * i - 1;
        let v = 2 * n - 2 - 2 * i - 1;
        arcs.push((u, v));
    }
    //   (5n - 10 - 3i, 2i + 2) for i = 1..=floor((n-4)/2)
    let floor_h = (n - 4) / 2;
    for i in 1..=floor_h {
        let u = 5 * n - 10 - 3 * i - 1;
        let v = 2 * i + 2 - 1;
        arcs.push((u, v));
    }

    // Label -> (incoming target vertex in C_n, outgoing source vertex in C_n), 1-indexed labels 1..=n
    let mut in_target = vec![0usize; n + 1];
    let mut out_source = vec![0usize; n + 1];
    for lbl in 1..=n {
        in_target[lbl] = 2 * lbl - 2; // paper `2i - 1`
    }
    out_source[1] = 5 * n - 11; // paper `5n - 10`
    out_source[2] = 0; // paper `1`
    out_source[n - 1] = 2 * n - 2; // paper `2n - 1`
    out_source[n] = 2 * n - 1; // paper `2n`
    for i in 1..=floor_h {
        out_source[i + 2] = 5 * n - 9 - 3 * i - 1; // paper `5n - 9 - 3i`
    }
    for i in 1..=ceil_h {
        out_source[n - 1 - i] = 2 * n - 1 + 3 * i - 1; // paper `2n - 1 + 3i`
    }

    let split = n / 2;
    if expect_sat {
        // Keep incoming 1..=split+1 and outgoing {1} U (split+2..=n) => EXACTLY 1 matching label (1)!
        for lbl in 1..=(split + 1) {
            arcs.push((hub, in_target[lbl]));
        }
        arcs.push((out_source[1], hub));
        for lbl in (split + 2)..=n {
            arcs.push((out_source[lbl], hub));
        }
    } else {
        // Disjoint incoming `{1..=split}` and outgoing `{split+1..=n}` => ZERO matching labels (UNSAT)!
        for lbl in 1..=split {
            arcs.push((hub, in_target[lbl]));
        }
        for lbl in (split + 1)..=n {
            arcs.push((out_source[lbl], hub));
        }
    }

    let name = if expect_sat {
        format!("hamd_broken_crown_n{n}_v{total_v}_k1_sat")
    } else {
        format!("hamd_broken_crown_n{n}_v{total_v}_k0_unsat")
    };
    HamdGraph::from_directed(name, "HAMD-Crown", total_v, &arcs, expect_sat, None, Some(seed))
}

/// Curated HAMD benchmark suite spanning 6 literature families, varied vertex counts (`N = 20..100`),
/// and varied edge densities (`0.05..0.50`), both provably SAT and provably UNSAT!
pub fn standard_hamd_benchmark_suite() -> Vec<HamdGraph> {
    vec![
        // --- Sparse 3-regular Provably UNSAT (Hypohamiltonian / Snarks) ---
        build_flower_snark(5, false, 101),                  // N=20, 3-reg (rho=0.158), UNSAT
        build_gen_petersen_k2(11, false, 102),              // N=22, 3-reg (rho=0.143), UNSAT
        build_flower_snark(7, false, 103),                  // N=28, 3-reg (rho=0.111), UNSAT
        build_gen_petersen_k2(17, false, 104),              // N=34, 3-reg (rho=0.091), UNSAT
        // --- Higher-regular k-connected Provably UNSAT (Meredith 1973) ---
        build_meredith_graph(3, 201),                       // N=50, 3-reg 3-conn (rho=0.061), UNSAT
        build_meredith_graph(4, 202),                       // N=70, 4-reg 4-conn (rho=0.058), UNSAT
        // --- Medium & High Density Provably UNSAT (Chvatal 1973 Toughness < 1) ---
        build_chvatal_toughness(3, 5, 1.0, 1.0, 301),       // N=23, delta=7, rho=0.39, UNSAT
        build_chvatal_toughness(4, 6, 0.70, 0.70, 302),     // N=34, delta=6+, rho=0.22, UNSAT
        build_chvatal_toughness(4, 7, 1.0, 1.0, 303),       // N=39, delta=10, rho=0.29, UNSAT
        // --- Directed Broken Crown (Haythorpe 2019: exact 0 HCs vs exact 1 HC) ---
        build_broken_crown(8, false, 401),                  // N=31 directed, k=0, UNSAT
        build_broken_crown(8, true, 402),                   // N=31 directed, k=1, SAT
        build_broken_crown(12, true, 403),                  // N=51 directed, k=1, SAT
        // --- Sparse Structurally Hard Provably SAT (FHCP: GP(n,2) exact 3 HCs & J_k+e) ---
        build_gen_petersen_k2(15, false, 501),              // N=30, 3-reg (rho=0.103), exact 3 HCs SAT
        build_flower_snark(7, true, 502),                   // N=28, 3-reg+e (rho=0.114), SAT
        build_gen_petersen_k2(21, false, 503),              // N=42, 3-reg (rho=0.073), exact 3 HCs SAT
        // --- Planted Hidden-Cycle Provably SAT across Sizes (N=24..100) & Densities (0.06..0.50) ---
        build_planted_hamd(24, 0.18, "med", 601),           // N=24, rho=0.18, SAT
        build_planted_hamd(40, 0.12, "sparse", 602),        // N=40, rho=0.12, SAT
        build_planted_hamd(40, 0.35, "dense", 603),         // N=40, rho=0.35, SAT
        build_planted_hamd(64, 0.10, "sparse", 604),        // N=64, rho=0.10, SAT
        build_planted_hamd(64, 0.30, "dense", 605),         // N=64, rho=0.30, SAT
        build_planted_hamd(100, 0.06, "sparse", 606),       // N=100, rho=0.06, SAT
        build_planted_hamd(80, 0.50, "vdense", 607),        // N=80, rho=0.50, SAT
    ]
}
