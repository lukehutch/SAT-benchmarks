#![allow(dead_code)]
//! Pure-Logic Integer Factorization Circuit Benchmarks (Zero Number Theory).
//!
//! Provides two multiplier AIG topologies from Section 10.2 of `p_vs_np_gemini.tex`:
//! 1. **Wallace-Tree Multiplier**: Carry-save 3:2 reduction tree using first-class
//!    `Xor3` + `Maj3` full adders (O(log n) carry depth, exposes XOR sums to Gauss).
//! 2. **Karatsuba Multiplier**: Recursive sub-quadratic O(n^{1.585}) AIG for wider bit-widths.

use crate::aig::{Aig, Lit};

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum MultTopology {
    Wallace,
    Karatsuba,
}

/// Add two unsigned bit-vectors (LSB first), returning `max(a.len(), b.len()) + 1` bits.
pub fn add_vecs(aig: &mut Aig, a: &[Lit], b: &[Lit]) -> Vec<Lit> {
    let n = a.len().max(b.len());
    let mut out = Vec::with_capacity(n + 1);
    let mut carry = Lit::FALSE;
    for i in 0..n {
        let ba = a.get(i).copied().unwrap_or(Lit::FALSE);
        let bb = b.get(i).copied().unwrap_or(Lit::FALSE);
        let (s, c) = aig.full_adder(ba, bb, carry);
        out.push(s);
        carry = c;
    }
    if carry != Lit::FALSE {
        out.push(carry);
    }
    out
}

/// Subtract `b` from `a` assuming `a >= b` (returns `a.len()` bits, LSB first).
/// Uses two's complement: `a + (~b) + 1`, dropping the final carry.
pub fn sub_vecs_unchecked(aig: &mut Aig, a: &[Lit], b: &[Lit]) -> Vec<Lit> {
    let n = a.len().max(b.len());
    let mut out = Vec::with_capacity(n);
    let mut carry = Lit::TRUE;
    for i in 0..n {
        let ba = a.get(i).copied().unwrap_or(Lit::FALSE);
        let bb = b.get(i).copied().unwrap_or(Lit::FALSE).neg();
        let (s, c) = aig.full_adder(ba, bb, carry);
        out.push(s);
        carry = c;
    }
    out
}

/// Wallace-tree carry-save multiplier of `p` (len `wp`) and `q` (len `wq`),
/// producing `wp + wq` product bits (LSB first).
pub fn mul_wallace(aig: &mut Aig, p: &[Lit], q: &[Lit]) -> Vec<Lit> {
    let out_bits = p.len() + q.len();
    let mut cols: Vec<Vec<Lit>> = vec![Vec::new(); out_bits];
    for (i, &pi) in p.iter().enumerate() {
        if pi == Lit::FALSE {
            continue;
        }
        for (j, &qj) in q.iter().enumerate() {
            if qj == Lit::FALSE {
                continue;
            }
            let prod = aig.and(pi, qj);
            if prod != Lit::FALSE {
                cols[i + j].push(prod);
            }
        }
    }

    // Repeated Wallace 3:2 reduction layers until every column has height <= 2.
    loop {
        let max_h = cols.iter().map(|c| c.len()).max().unwrap_or(0);
        if max_h <= 2 {
            break;
        }
        let mut next_cols: Vec<Vec<Lit>> = vec![Vec::new(); out_bits];
        for col in 0..out_bits {
            let bits = &cols[col];
            let mut idx = 0;
            while idx + 3 <= bits.len() {
                let (s, c) = aig.full_adder(bits[idx], bits[idx + 1], bits[idx + 2]);
                if s != Lit::FALSE {
                    next_cols[col].push(s);
                }
                if col + 1 < out_bits && c != Lit::FALSE {
                    next_cols[col + 1].push(c);
                }
                idx += 3;
            }
            if idx + 2 == bits.len() && bits.len() > 2 {
                let (s, c) = aig.half_adder(bits[idx], bits[idx + 1]);
                if s != Lit::FALSE {
                    next_cols[col].push(s);
                }
                if col + 1 < out_bits && c != Lit::FALSE {
                    next_cols[col + 1].push(c);
                }
            } else {
                while idx < bits.len() {
                    next_cols[col].push(bits[idx]);
                    idx += 1;
                }
            }
        }
        cols = next_cols;
    }

    // Final 2-row carry-propagate addition.
    let mut out = Vec::with_capacity(out_bits);
    let mut carry = Lit::FALSE;
    for col in 0..out_bits {
        let a = cols[col].first().copied().unwrap_or(Lit::FALSE);
        let b = cols[col].get(1).copied().unwrap_or(Lit::FALSE);
        let (s, c) = aig.full_adder(a, b, carry);
        out.push(s);
        carry = c;
    }
    out
}

/// Karatsuba recursive multiplier (falls back to Wallace below threshold `k <= 8`).
pub fn mul_karatsuba(aig: &mut Aig, p: &[Lit], q: &[Lit]) -> Vec<Lit> {
    let n = p.len().max(q.len());
    if p.len().min(q.len()) <= 8 || n <= 10 {
        return mul_wallace(aig, p, q);
    }

    let m = n / 2;
    let p_lo = &p[..m.min(p.len())];
    let p_hi = if p.len() > m { &p[m..] } else { &[] };
    let q_lo = &q[..m.min(q.len())];
    let q_hi = if q.len() > m { &q[m..] } else { &[] };

    if p_hi.is_empty() {
        return mul_karatsuba(aig, p_lo, q);
    }
    if q_hi.is_empty() {
        return mul_karatsuba(aig, p, q_lo);
    }

    // z0 = p_lo * q_lo, z2 = p_hi * q_hi
    let z0 = mul_karatsuba(aig, p_lo, q_lo);
    let z2 = mul_karatsuba(aig, p_hi, q_hi);

    // z1 = (p_lo + p_hi) * (q_lo + q_hi) - z0 - z2
    let p_sum = add_vecs(aig, p_lo, p_hi);
    let q_sum = add_vecs(aig, q_lo, q_hi);
    let z_mid_raw = mul_karatsuba(aig, &p_sum, &q_sum);
    let z0_plus_z2 = add_vecs(aig, &z0, &z2);
    let z1 = sub_vecs_unchecked(aig, &z_mid_raw, &z0_plus_z2);

    // Combine z0 + (z1 << m) + (z2 << 2m) via a 3-operand Wallace reduction!
    let out_bits = p.len() + q.len();
    let mut cols: Vec<Vec<Lit>> = vec![Vec::new(); out_bits];
    for (i, &b) in z0.iter().enumerate() {
        if i < out_bits && b != Lit::FALSE {
            cols[i].push(b);
        }
    }
    for (i, &b) in z1.iter().enumerate() {
        if i + m < out_bits && b != Lit::FALSE {
            cols[i + m].push(b);
        }
    }
    for (i, &b) in z2.iter().enumerate() {
        if i + 2 * m < out_bits && b != Lit::FALSE {
            cols[i + 2 * m].push(b);
        }
    }

    // Compress height-3 columns to height-2, then final CPA.
    let mut row0 = vec![Lit::FALSE; out_bits];
    let mut row1 = vec![Lit::FALSE; out_bits];
    let mut carries = vec![Lit::FALSE; out_bits];
    for col in 0..out_bits {
        match cols[col].len() {
            0 => {}
            1 => row0[col] = cols[col][0],
            2 => {
                row0[col] = cols[col][0];
                row1[col] = cols[col][1];
            }
            _ => {
                let (s, c) = aig.full_adder(cols[col][0], cols[col][1], cols[col][2]);
                row0[col] = s;
                if col + 1 < out_bits {
                    carries[col + 1] = c;
                }
            }
        }
    }
    // Second pass if any col has both row1 and carry.
    let mut out = Vec::with_capacity(out_bits);
    let mut c_prop = Lit::FALSE;
    for col in 0..out_bits {
        let mut active_bits = Vec::new();
        for b in [row0[col], row1[col], carries[col]] {
            if b != Lit::FALSE {
                active_bits.push(b);
            }
        }
        match active_bits.len() {
            0 => {
                out.push(c_prop);
                c_prop = Lit::FALSE;
            }
            1 => {
                let (s, c) = aig.half_adder(active_bits[0], c_prop);
                out.push(s);
                c_prop = c;
            }
            2 => {
                let (s, c) = aig.full_adder(active_bits[0], active_bits[1], c_prop);
                out.push(s);
                c_prop = c;
            }
            _ => {
                // At most 3 bits + c_prop: rare, fold cleanly.
                let (s1, c1) = aig.full_adder(active_bits[0], active_bits[1], active_bits[2]);
                let (s2, c2) = aig.half_adder(s1, c_prop);
                out.push(s2);
                c_prop = aig.or(c1, c2);
            }
        }
    }
    out
}

/// Assert `a <= b` for unsigned bit-vectors (LSB first).
fn assert_le(aig: &mut Aig, a: &[Lit], b: &[Lit]) {
    let n = a.len().max(b.len());
    // Compute `le = (a <= b)` from LSB to MSB:
    // At bit i: le_new = (!a_i & b_i) | ((a_i == b_i) & le_prev)
    let mut le = Lit::TRUE;
    for i in 0..n {
        let ai = a.get(i).copied().unwrap_or(Lit::FALSE);
        let bi = b.get(i).copied().unwrap_or(Lit::FALSE);
        let lt_i = aig.and(ai.neg(), bi);
        let eq_i = aig.xor(ai, bi).neg();
        let eq_and_le = aig.and(eq_i, le);
        le = aig.or(lt_i, eq_and_le);
    }
    aig.assert_true(le);
}

/// Assert that at least one bit in `bits[1..]` is 1 (i.e., odd number > 1).
fn assert_gt_one(aig: &mut Aig, bits: &[Lit]) {
    let mut any = Lit::FALSE;
    for &b in bits.iter().skip(1) {
        any = aig.or(any, b);
    }
    aig.assert_true(any);
}

pub struct FactoringInstance {
    pub n_target: u128,
    pub bit_width: usize,
    pub p_bits: usize,
    pub q_bits: usize,
    pub aig: Aig,
    /// Input indices corresponding to `p[1..p_bits]` and `q[1..q_bits]` (bit 0 fixed to 1).
    pub p_input_indices: Vec<usize>,
    pub q_input_indices: Vec<usize>,
}

impl FactoringInstance {
    /// Build a pure-logic factoring AIG for odd integer `n_target > 1`.
    ///
    /// - If `balanced_semiprime == false` (general odd factoring):
    ///   `p` has `ceil(bit_width / 2)` bits (exact because `min(p,q) <= sqrt(N) < 2^{ceil(n/2)}`),
    ///   `q` has `bit_width - 1` bits (exact because `max(p,q) <= N/3 < 2^{n-1}`),
    ///   with `p > 1`, `q > 1`, `p <= q`, and `p * q == N`.
    /// - If `balanced_semiprime == true` (RSA-style balanced factor widths):
    ///   both `p` and `q` have `ceil(bit_width / 2)` bits (with top bits optionally free),
    ///   with `p > 1`, `q > 1`, `p <= q`, and `p * q == N`.
    pub fn build(n_target: u128, topology: MultTopology, balanced_semiprime: bool) -> Self {
        assert!(n_target >= 9 && (n_target & 1) == 1, "n_target must be odd >= 9");
        let bit_width = (128 - n_target.leading_zeros()) as usize;
        let p_bits = (bit_width + 1) / 2;
        let q_bits = if balanced_semiprime { p_bits } else { bit_width - 1 };

        let mut aig = Aig::new();
        let mut p_vec = vec![Lit::TRUE]; // odd LSB fixed to 1
        let mut q_vec = vec![Lit::TRUE]; // odd LSB fixed to 1
        let mut p_input_indices = Vec::new();
        let mut q_input_indices = Vec::new();

        for _ in 1..p_bits {
            let idx = aig.num_inputs;
            p_vec.push(aig.new_input());
            p_input_indices.push(idx);
        }
        for _ in 1..q_bits {
            let idx = aig.num_inputs;
            q_vec.push(aig.new_input());
            q_input_indices.push(idx);
        }

        // Enforce non-triviality and symmetry breaking: 1 < p <= q.
        assert_gt_one(&mut aig, &p_vec);
        assert_gt_one(&mut aig, &q_vec);
        assert_le(&mut aig, &p_vec, &q_vec);

        let prod = match topology {
            MultTopology::Wallace => mul_wallace(&mut aig, &p_vec, &q_vec),
            MultTopology::Karatsuba => mul_karatsuba(&mut aig, &p_vec, &q_vec),
        };

        // Constrain every product bit to match `n_target` (Proposition 2.4).
        for (i, &bit_lit) in prod.iter().enumerate() {
            let target_bit = if i < 128 { ((n_target >> i) & 1) != 0 } else { false };
            aig.assert_true(if target_bit { bit_lit } else { bit_lit.neg() });
        }

        Self {
            n_target,
            bit_width,
            p_bits,
            q_bits,
            aig,
            p_input_indices,
            q_input_indices,
        }
    }

    pub fn decode(&self, inputs: &[bool]) -> (u128, u128) {
        let mut p = 1u128;
        for (k, &idx) in self.p_input_indices.iter().enumerate() {
            if inputs[idx] {
                p |= 1u128 << (k + 1);
            }
        }
        let mut q = 1u128;
        for (k, &idx) in self.q_input_indices.iter().enumerate() {
            if inputs[idx] {
                q |= 1u128 << (k + 1);
            }
        }
        (p, q)
    }
}
