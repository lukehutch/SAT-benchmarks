#![allow(dead_code)]
//! Algebraic & Parity Counterexample Circuit Benchmarks:
//! 1. F2-Frobenius Circulant Psi_{k,b}:
//!    - Balanced invertible 3-XOR and minimally unsatisfiable 4-XOR circulants over F_2
//!    - Forces >= 2^{sqrt(n)/(3*sqrt(2))} in every merge-tree DNF solver
//! 2. MOD2-Tseitin on 3-Regular Prisms and Expanders:
//!    - Forces 2^{Omega(n)} in general Resolution/CDCL without parity reasoning

use crate::aig::Aig;

/// Build the uniquely satisfiable, strictly balanced F2-Frobenius circulant Psi_{k,b}
/// (`n = 2^k`, `s = 2^{floor(k/2)}`) with planted unique witness `x_true`.
pub fn build_frobenius_circulant(k: usize, seed: u64) -> (Aig, Vec<bool>) {
    assert!(k >= 4);
    let n = 1usize << k;
    let s = 1usize << (k / 2);

    // Generate deterministic planted witness x_true.
    let mut state = seed ^ 0x9e3779b97f4a7c15;
    let mut x_true = vec![false; n];
    for b in &mut x_true {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        *b = (state >> 63) != 0;
    }

    let mut aig = Aig::new();
    let xs = aig.new_inputs(n);
    {
        let mut lin = aig.begin_linear_region("F2-Frobenius");
        for i in 0..n {
            let rhs = x_true[i] ^ x_true[(i + 1) % n] ^ x_true[(i + s) % n];
            let eq = lin.xor3(xs[i], xs[(i + 1) % n], xs[(i + s) % n]);
            lin.assert_true(if rhs { eq } else { eq.neg() });
        }
        lin.finish();
    }
    (aig, x_true)
}

/// Build a provably unsatisfiable, strictly balanced 4-XOR F2-Frobenius circulant on `n = 2^k`
/// variables (`s = 2^{floor(k/2)}`):
///     x_i ^ x_{(i+1) mod n} ^ x_{(i+s) mod n} ^ x_{(i+s+1) mod n} = b_i  (0 <= i < n),
/// where `b_i` matches a planted assignment for all `i > 0` and is flipped at `i = 0`.
/// Every variable occurs in exactly 4 equations, so the F2 sum of all `n` LHS rows is identically 0
/// while `sum b_i = 1 (mod 2)` -> minimally unsatisfiable global parity contradiction!
pub fn build_frobenius_circulant_unsat(k: usize, seed: u64) -> Aig {
    assert!(k >= 4);
    let n = 1usize << k;
    let s = 1usize << (k / 2);

    let mut state = seed ^ 0x517C_C1B7_2722_0A95;
    let mut x_ref = vec![false; n];
    for b in &mut x_ref {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        *b = (state >> 63) != 0;
    }

    let mut aig = Aig::new();
    let xs = aig.new_inputs(n);
    {
        let mut lin = aig.begin_linear_region("F2-Frobenius-UNSAT");
        for i in 0..n {
            let mut rhs = x_ref[i]
                ^ x_ref[(i + 1) % n]
                ^ x_ref[(i + s) % n]
                ^ x_ref[(i + s + 1) % n];
            if i == 0 {
                rhs = !rhs;
            }
            lin.assert_xor_parity(
                &[xs[i], xs[(i + 1) % n], xs[(i + s) % n], xs[(i + s + 1) % n]],
                rhs,
            );
        }
        lin.finish();
    }
    aig
}

/// Build an unsatisfiable MOD2-Tseitin AIG on the 3-regular prism graph C_m x K_2 (n = 2m vertices).
pub fn build_tseitin_prism(m: usize) -> Aig {
    assert!(m >= 4);
    let mut aig = Aig::new();
    // 3m edges: top cycle t[0..m], bottom cycle b[0..m], spokes s[0..m]
    let t = aig.new_inputs(m);
    let b = aig.new_inputs(m);
    let s = aig.new_inputs(m);

    {
        let mut lin = aig.begin_linear_region("Tseitin-Prism");
        for i in 0..m {
            let prev = (i + m - 1) % m;
            // Top vertex i: charge 1 at i==0, 0 elsewhere => odd total charge => UNSAT!
            let top_xor = lin.xor3(t[prev], t[i], s[i]);
            lin.assert_true(if i == 0 { top_xor } else { top_xor.neg() });
            // Bottom vertex i: charge 0
            let bot_xor = lin.xor3(b[prev], b[i], s[i]);
            lin.assert_true(bot_xor.neg());
        }
        lin.finish();
    }
    aig
}

/// Build an unsatisfiable MOD2-Tseitin AIG on a deterministic 3-regular expander-like graph
/// on `n` vertices (even `n >= 8`): union of a Hamiltonian cycle plus a pseudorandom perfect matching.
pub fn build_tseitin_expander(n: usize, seed: u64) -> Aig {
    assert!(n >= 8 && n % 2 == 0);
    // Construct 3-regular multigraph-free graph: cycle i-(i+1) plus shuffled matching.
    let mut perm: Vec<usize> = (0..n).collect();
    let mut state = seed ^ 0xA5A5_5A5A_1234_5678;
    for i in (1..n).rev() {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
        let j = (state as usize) % (i + 1);
        perm.swap(i, j);
    }

    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    let mut edges: Vec<(usize, usize)> = Vec::with_capacity((3 * n) / 2);

    for i in 0..n {
        let u = i;
        let v = (i + 1) % n;
        let eid = edges.len();
        edges.push((u, v));
        adj[u].push(eid);
        adj[v].push(eid);
    }
    for k in 0..(n / 2) {
        let u = perm[2 * k];
        let v = perm[2 * k + 1];
        let eid = edges.len();
        edges.push((u, v));
        adj[u].push(eid);
        adj[v].push(eid);
    }

    let mut aig = Aig::new();
    let x_e = aig.new_inputs(edges.len());
    {
        let mut lin = aig.begin_linear_region("Tseitin-Expander");
        for v in 0..n {
            debug_assert_eq!(adj[v].len(), 3);
            let eq = lin.xor3(x_e[adj[v][0]], x_e[adj[v][1]], x_e[adj[v][2]]);
            // Odd total charge: vertex 0 has charge 1, all others 0.
            lin.assert_true(if v == 0 { eq } else { eq.neg() });
        }
        lin.finish();
    }
    aig
}
