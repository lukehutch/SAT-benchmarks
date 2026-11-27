//! Exact O(n log n) Fermat-Prime Number Theoretic Transform (NTT) Integer Multiplier
//! Boolean Circuit over F_{65537} (P = F_4 = 2^16 + 1, primitive root g = 3),
//! plus exact Wallace-tree O(n^2) multiplier for empirical gate-count crossover measurement.
#![allow(dead_code)]

use crate::aig::{Aig, Lit};
use crate::bigint::BigUint;

pub const MOD_P: u32 = 65_537; // F_4 = 2^16 + 1
pub const PRIM_ROOT: u32 = 3;

/// Canonical 17-bit representation of an element of F_{65537} = {0, ..., 65536} (LSB first).
/// Invariant: if `bits[16] == 1`, then `bits[0..16] == 0` (value == 65536 == -1 mod P).
pub type F4Word = [Lit; 17];

pub fn f4_zero() -> F4Word {
    [Lit::FALSE; 17]
}

pub fn f4_is_const_zero(w: &F4Word) -> bool {
    w.iter().all(|&b| b == Lit::FALSE)
}

pub fn f4_const(val: u32) -> F4Word {
    assert!(val < MOD_P);
    let mut out = [Lit::FALSE; 17];
    for i in 0..17 {
        if ((val >> i) & 1) != 0 {
            out[i] = Lit::TRUE;
        }
    }
    out
}

pub fn f4_from_small(bits: &[Lit]) -> F4Word {
    assert!(bits.len() <= 16);
    let mut out = [Lit::FALSE; 17];
    for (i, &b) in bits.iter().enumerate() {
        out[i] = b;
    }
    out
}

pub fn pow_mod_p(mut base: u64, mut exp: u64) -> u32 {
    let mut acc = 1u64;
    base %= MOD_P as u64;
    while exp > 0 {
        if (exp & 1) != 0 {
            acc = (acc * base) % (MOD_P as u64);
        }
        base = (base * base) % (MOD_P as u64);
        exp >>= 1;
    }
    acc as u32
}

/// Exact `(a + b) mod 65537` for canonical `a, b in [0, 65536]`.
/// Uses zero-mux conditional decrementer: `ge = s[17] | (s[16] & any_nz(s[0..16]))`,
/// then `res[0..16] = s[0..16] - ge`, `res[16] = !ge & s[16]`.
/// When inputs have `bit[15..17] == FALSE` (small early-stage limbs), `s[16]=s[17]=FALSE`,
/// so hash-consing folds the entire reduction to 0 gates automatically.
pub fn add_mod_f4(aig: &mut Aig, a: &F4Word, b: &F4Word) -> F4Word {
    if f4_is_const_zero(a) { return *b; }
    if f4_is_const_zero(b) { return *a; }

    let mut s = [Lit::FALSE; 18];
    let mut carry = Lit::FALSE;
    for i in 0..17 {
        let (sum_i, c_i) = aig.full_adder(a[i], b[i], carry);
        s[i] = sum_i;
        carry = c_i;
    }
    s[17] = carry;

    // If s[16] and s[17] are both statically FALSE, s < 65536 < P: zero reduction gates!
    if s[16] == Lit::FALSE && s[17] == Lit::FALSE {
        let mut out = [Lit::FALSE; 17];
        out[..16].copy_from_slice(&s[..16]);
        return out;
    }

    // any_nz = OR(s[0..16]) via balanced tree
    let any_nz = or_tree(aig, &s[..16]);
    let s16_and_nz = aig.and(s[16], any_nz);
    let ge = aig.or(s[17], s16_and_nz);

    let mut out = [Lit::FALSE; 17];
    let mut borrow = ge;
    for i in 0..16 {
        out[i] = aig.xor(s[i], borrow);
        if i + 1 < 16 {
            borrow = aig.and(s[i].neg(), borrow);
        }
    }
    out[16] = aig.and(ge.neg(), s[16]);
    out
}

/// Exact `(a - b) mod 65537` for canonical `a, b in [0, 65536]`.
/// Uses zero-mux conditional `+ 65537`: `d = a + (~b) + 1`, `borrow = !cout`,
/// then `res = d + borrow * (2^16 + 1) mod 2^17`.
pub fn sub_mod_f4(aig: &mut Aig, a: &F4Word, b: &F4Word) -> F4Word {
    if f4_is_const_zero(b) { return *a; }

    let mut d = [Lit::FALSE; 17];
    let mut carry = Lit::TRUE;
    for i in 0..17 {
        let (sum_i, c_i) = aig.full_adder(a[i], b[i].neg(), carry);
        d[i] = sum_i;
        carry = c_i;
    }
    let borrow = carry.neg();

    let mut out = [Lit::FALSE; 17];
    let mut inc_c = borrow;
    for i in 0..16 {
        let (s_i, c_i) = aig.half_adder(d[i], inc_c);
        out[i] = s_i;
        inc_c = c_i;
    }
    out[16] = aig.xor3(d[16], borrow, inc_c);
    out
}

fn or_tree(aig: &mut Aig, lits: &[Lit]) -> Lit {
    let mut cur: Vec<Lit> = lits.iter().copied().filter(|&l| l != Lit::FALSE).collect();
    if cur.is_empty() { return Lit::FALSE; }
    if cur.contains(&Lit::TRUE) { return Lit::TRUE; }
    while cur.len() > 1 {
        let mut nxt = Vec::with_capacity((cur.len() + 1) / 2);
        let mut i = 0;
        while i + 1 < cur.len() {
            nxt.push(aig.or(cur[i], cur[i + 1]));
            i += 2;
        }
        if i < cur.len() {
            nxt.push(cur[i]);
        }
        cur = nxt;
    }
    cur[0]
}

/// Exact `(x * 2^k) mod 65537` for `k in 0..32` using single negacyclic shift-sub!
/// Since `2^16 == -1 mod 65537`:
/// - `k == 0`: identity (0 gates)
/// - `1 <= k <= 15`: `(lo << k) - hi mod P`, where `lo = x[0..16-k]`, `hi = x[16-k..17]`
/// - `k == 16`: `0 - x mod P`
/// - `17 <= k <= 31`: let `j = k - 16`, `hi - (lo << j) mod P`
pub fn mul_pow2_mod_f4(aig: &mut Aig, x: &F4Word, k: usize) -> F4Word {
    let k = k & 31;
    if k == 0 || f4_is_const_zero(x) {
        return *x;
    }
    if k == 16 {
        let z = f4_zero();
        return sub_mod_f4(aig, &z, x);
    }
    let j = if k < 16 { k } else { k - 16 };
    let mut lo_shifted = f4_zero();
    for i in 0..(16 - j) {
        lo_shifted[i + j] = x[i];
    }
    let mut hi = f4_zero();
    for i in (16 - j)..17 {
        hi[i - (16 - j)] = x[i];
    }
    if k < 16 {
        sub_mod_f4(aig, &lo_shifted, &hi)
    } else {
        sub_mod_f4(aig, &hi, &lo_shifted)
    }
}

/// Find minimal negacyclic signed power-of-2 decomposition `R subset {0..31}`
/// such that `sum_{r in R} 2^r == c (mod 65537)` (where `r < 16` means `+2^r`, `r >= 16` means `-2^(r-16)`).
fn min_negacyclic_rep(c: u32) -> Vec<usize> {
    let c = (c % MOD_P) as i64;
    if c == 0 {
        return Vec::new();
    }
    let p = MOD_P as i64;
    let mut best: Option<Vec<usize>> = None;
    for cand in [c, c - p, c + p, c - 2 * p] {
        let mut x = cand;
        let mut cnt = [0i32; 32];
        let mut pos = 0usize;
        while x != 0 {
            if (x & 1) != 0 {
                let d: i64 = if (x & 3) == 3 { -1 } else { 1 };
                x -= d;
                let r = (pos + if d < 0 { 16 } else { 0 }) & 31;
                cnt[r] += 1;
            }
            x >>= 1;
            pos += 1;
        }
        // Simplify opposite cancellations (r vs r^16) and carries (2 * 2^r = 2^(r+1)).
        loop {
            let mut changed = false;
            for r in 0..32 {
                let o = r ^ 16;
                let m = cnt[r].min(cnt[o]);
                if m > 0 {
                    cnt[r] -= m;
                    cnt[o] -= m;
                    changed = true;
                }
                if cnt[r] >= 2 {
                    let pairs = cnt[r] / 2;
                    cnt[r] -= 2 * pairs;
                    cnt[(r + 1) & 31] += pairs;
                    changed = true;
                }
            }
            if !changed { break; }
        }
        let mut rep = Vec::new();
        for r in 0..32 {
            for _ in 0..cnt[r] {
                rep.push(r);
            }
        }
        if best.as_ref().map_or(true, |b| rep.len() < b.len()) {
            best = Some(rep);
        }
    }
    best.unwrap()
}

/// Wallace 3:2 bit-column reduction + final CPA on arbitrary column heights.
fn reduce_columns_to_sum(aig: &mut Aig, mut cols: Vec<Vec<Lit>>) -> Vec<Lit> {
    // Strip FALSE bits and allow carries to grow top columns dynamically.
    for col in &mut cols {
        col.retain(|&b| b != Lit::FALSE);
    }
    loop {
        let max_h = cols.iter().map(|c| c.len()).max().unwrap_or(0);
        if max_h <= 2 {
            break;
        }
        let mut next_cols: Vec<Vec<Lit>> = vec![Vec::new(); cols.len() + 1];
        for col_idx in 0..cols.len() {
            let bits = &cols[col_idx];
            let mut i = 0;
            while i + 3 <= bits.len() {
                let (s, c) = aig.full_adder(bits[i], bits[i + 1], bits[i + 2]);
                if s != Lit::FALSE { next_cols[col_idx].push(s); }
                if c != Lit::FALSE { next_cols[col_idx + 1].push(c); }
                i += 3;
            }
            if i + 2 == bits.len() && bits.len() > 2 {
                let (s, c) = aig.half_adder(bits[i], bits[i + 1]);
                if s != Lit::FALSE { next_cols[col_idx].push(s); }
                if c != Lit::FALSE { next_cols[col_idx + 1].push(c); }
            } else {
                while i < bits.len() {
                    next_cols[col_idx].push(bits[i]);
                    i += 1;
                }
            }
        }
        while next_cols.last().map_or(false, |c| c.is_empty()) {
            next_cols.pop();
        }
        cols = next_cols;
    }

    let mut out = Vec::with_capacity(cols.len() + 1);
    let mut carry = Lit::FALSE;
    for col in &cols {
        let a = col.first().copied().unwrap_or(Lit::FALSE);
        let b = col.get(1).copied().unwrap_or(Lit::FALSE);
        let (s, c) = aig.full_adder(a, b, carry);
        out.push(s);
        carry = c;
    }
    if carry != Lit::FALSE {
        out.push(carry);
    }
    out
}

/// Exact `(x * c) mod 65537` for compile-time constant `c in [0, 65536]`.
/// - Power-of-2 constants (`|R| == 1`, including ALL twiddles for L <= 32 and L^{-1}) use `mul_pow2_mod_f4`.
/// - General constants use minimal negacyclic CSD-Wallace bit-folding with single final `sub_mod_f4(S_lo, S_hi)`.
/// - Statically zero bits of `x` (e.g., upper 13 bits of 4-bit limbs in DIF Stage 0!) drop out completely!
pub fn mul_const_mod_f4(aig: &mut Aig, x: &F4Word, c: u32) -> F4Word {
    let c = c % MOD_P;
    if c == 0 || f4_is_const_zero(x) {
        return f4_zero();
    }
    if c == 1 {
        return *x;
    }
    let rep = min_negacyclic_rep(c);
    if rep.len() == 1 {
        return mul_pow2_mod_f4(aig, x, rep[0]);
    }

    // Negacyclic bit folding:
    //   for each r in rep and each non-FALSE bit x[i]:
    //     q = (i + r) & 31
    //     if q < 16: +x[i] * 2^q
    //     else (k = q - 16): -x[i] * 2^k = (!x[i]) * 2^k - 2^k
    let mut cols: Vec<Vec<Lit>> = vec![Vec::new(); 17];
    let mut bias: i64 = 0;
    for &r in &rep {
        for i in 0..17 {
            let xi = x[i];
            if xi == Lit::FALSE {
                continue;
            }
            let q = (i + r) & 31;
            if xi == Lit::TRUE {
                if q < 16 {
                    bias += 1i64 << q;
                } else {
                    bias -= 1i64 << (q - 16);
                }
            } else if q < 16 {
                cols[q].push(xi);
            } else {
                let k = q - 16;
                cols[k].push(xi.neg());
                bias -= 1i64 << k;
            }
        }
    }
    let bias_mod = bias.rem_euclid(MOD_P as i64) as u32;
    for k in 0..17 {
        if ((bias_mod >> k) & 1) != 0 {
            cols[k].push(Lit::TRUE);
        }
    }

    let sum = reduce_columns_to_sum(aig, cols);
    let mut s_lo = f4_zero();
    let mut s_hi = f4_zero();
    for i in 0..16.min(sum.len()) {
        s_lo[i] = sum[i];
    }
    for i in 16..sum.len() {
        assert!(i - 16 < 16, "S_hi overflow in mul_const_mod_f4");
        s_hi[i - 16] = sum[i];
    }
    sub_mod_f4(aig, &s_lo, &s_hi)
}

/// Exact `(a * b) mod 65537` for canonical 17-bit `a, b in [0, 65536]`.
/// Exploits canonical invariant (`a[16]=1 => a[0..16]=0`, `b[16]=1 => b[0..16]=0`):
/// computes ONLY a 16x16 Wallace product `Z = a_lo * b_lo`, merges the mutually-exclusive
/// top-bit corrections (`a[16]&b[16]` into `Z_lo[0]`, `a[16]&b_lo` / `b[16]&a_lo` into `Z_hi`),
/// and finishes with one 16-bit `sub_mod_f4(u, v)`!
pub fn mul_mod_f4(aig: &mut Aig, a: &F4Word, b: &F4Word) -> F4Word {
    if f4_is_const_zero(a) || f4_is_const_zero(b) {
        return f4_zero();
    }
    let mut cols: Vec<Vec<Lit>> = vec![Vec::new(); 32];
    for i in 0..16 {
        if a[i] == Lit::FALSE { continue; }
        for j in 0..16 {
            if b[j] == Lit::FALSE { continue; }
            let prod = aig.and(a[i], b[j]);
            if prod != Lit::FALSE {
                cols[i + j].push(prod);
            }
        }
    }
    let z = reduce_columns_to_sum(aig, cols);
    let mut u = f4_zero();
    let mut v = f4_zero();
    for i in 0..16 {
        u[i] = z.get(i).copied().unwrap_or(Lit::FALSE);
    }
    let top_both = aig.and(a[16], b[16]);
    u[0] = aig.or(u[0], top_both);

    for i in 0..16 {
        let mut bi = z.get(16 + i).copied().unwrap_or(Lit::FALSE);
        let ab_i = aig.and(a[16], b[i]);
        let ba_i = aig.and(b[16], a[i]);
        bi = aig.or(bi, ab_i);
        bi = aig.or(bi, ba_i);
        v[i] = bi;
    }
    sub_mod_f4(aig, &u, &v)
}

/// Forward Decimation-In-Frequency (DIF / Gentleman-Sande) NTT over F_{65537}.
/// Takes natural-order input `a[0..L]` and outputs bit-reversed-order spectrum `A[0..L]`.
/// Because upper half of `a` is zero-padded (`m_p <= L/2`), Stage 0 multiplies ONLY 4-bit
/// input limbs against the heavy non-power-of-2 twiddles, and Stages >= 3 use 100% power-of-2 twiddles!
pub fn ntt_dif_forward(aig: &mut Aig, a: &mut [F4Word]) {
    let l = a.len();
    assert!(l.is_power_of_two() && l >= 2 && (MOD_P - 1) as usize % l == 0);
    let mut len = l;
    while len >= 2 {
        let half = len / 2;
        let w_len = pow_mod_p(PRIM_ROOT as u64, ((MOD_P - 1) as usize / len) as u64);
        let mut w_pows = Vec::with_capacity(half);
        let mut w = 1u64;
        for _ in 0..half {
            w_pows.push(w as u32);
            w = (w * (w_len as u64)) % (MOD_P as u64);
        }
        let mut start = 0;
        while start < l {
            for j in 0..half {
                let u = a[start + j];
                let v = a[start + j + half];
                let sum = add_mod_f4(aig, &u, &v);
                let diff = sub_mod_f4(aig, &u, &v);
                a[start + j] = sum;
                a[start + j + half] = mul_const_mod_f4(aig, &diff, w_pows[j]);
            }
            start += len;
        }
        len = half;
    }
}

/// Inverse Decimation-In-Time (DIT / Cooley-Tukey) NTT over F_{65537}.
/// Takes bit-reversed-order spectrum `C[0..L]` (exact dual of `ntt_dif_forward`, so ZERO
/// bit-reversal permutation is needed!), outputs natural-order convolution `c[0..L]`,
/// and folds the exact `L^{-1} = 2^{32 - log2(L)} mod 65537` power-of-2 scaling into the live outputs!
pub fn ntt_dit_inverse(aig: &mut Aig, a: &mut [F4Word], live_outputs: usize) {
    let l = a.len();
    assert!(l.is_power_of_two() && l >= 2 && (MOD_P - 1) as usize % l == 0);
    let log_l = l.trailing_zeros() as usize;
    let mut len = 2;
    while len <= l {
        let half = len / 2;
        // Inverse primitive len-th root: g^{(P-1) - (P-1)/len} mod P
        let w_inv = pow_mod_p(
            PRIM_ROOT as u64,
            ((MOD_P - 1) as usize - (MOD_P - 1) as usize / len) as u64,
        );
        let mut w_pows = Vec::with_capacity(half);
        let mut w = 1u64;
        for _ in 0..half {
            w_pows.push(w as u32);
            w = (w * (w_inv as u64)) % (MOD_P as u64);
        }
        let mut start = 0;
        while start < l {
            for j in 0..half {
                let u = a[start + j];
                let v = mul_const_mod_f4(aig, &a[start + j + half], w_pows[j]);
                if len == l {
                    // Final stage: skip dead outputs beyond `live_outputs`!
                    if start + j < live_outputs {
                        a[start + j] = add_mod_f4(aig, &u, &v);
                    } else {
                        a[start + j] = f4_zero();
                    }
                    if start + j + half < live_outputs {
                        a[start + j + half] = sub_mod_f4(aig, &u, &v);
                    } else {
                        a[start + j + half] = f4_zero();
                    }
                } else {
                    a[start + j] = add_mod_f4(aig, &u, &v);
                    a[start + j + half] = sub_mod_f4(aig, &u, &v);
                }
            }
            start += len;
        }
        len *= 2;
    }
    // Scale live outputs by L^{-1} = 2^{32 - log2(L)} mod 65537 (exact single shift-sub!).
    let inv_shift = 32 - log_l;
    for k in 0..live_outputs.min(l) {
        a[k] = mul_pow2_mod_f4(aig, &a[k], inv_shift);
    }
}

/// Exact O(n log n) Fermat-Prime F_{65537} NTT integer multiplier on bit-vectors `p` and `q` (LSB first).
/// Splits `p` and `q` into 4-bit base-16 limbs, computes exact non-wrapping convolution over F_{65537},
/// and propagates base-16 carries to return `p.len() + q.len()` exact product bits!
pub fn mul_ntt_f4(aig: &mut Aig, p: &[Lit], q: &[Lit]) -> (Vec<Lit>, usize, usize, usize) {
    let mp = (p.len() + 3) / 4;
    let mq = (q.len() + 3) / 4;
    let conv_len = mp + mq - 1;
    let l = conv_len.next_power_of_two().max(8);
    assert!(
        mp.min(mq) * 225 < MOD_P as usize,
        "NTT overflow: min(mp,mq)*225 = {} >= 65537",
        mp.min(mq) * 225
    );
    assert!(l <= 256 || (MOD_P as usize - 1) % l == 0);

    let mut pa = vec![f4_zero(); l];
    for limb in 0..mp {
        let mut w = f4_zero();
        for b in 0..4 {
            let idx = 4 * limb + b;
            if idx < p.len() {
                w[b] = p[idx];
            }
        }
        pa[limb] = w;
    }
    let mut qa = vec![f4_zero(); l];
    for limb in 0..mq {
        let mut w = f4_zero();
        for b in 0..4 {
            let idx = 4 * limb + b;
            if idx < q.len() {
                w[b] = q[idx];
            }
        }
        qa[limb] = w;
    }

    ntt_dif_forward(aig, &mut pa);
    ntt_dif_forward(aig, &mut qa);

    let mut prod_spec = vec![f4_zero(); l];
    for k in 0..l {
        prod_spec[k] = mul_mod_f4(aig, &pa[k], &qa[k]);
    }

    ntt_dit_inverse(aig, &mut prod_spec, conv_len);

    // Base-2^4 carry propagation from exact convolution coefficients `c_k <= min(mp, mq, k+1, conv_len-k) * 225`.
    // Guaranteed `c_k <= 28,800 < 2^15 < 65,537`, so zero modular wraparound for ALL inputs!
    let total_bits = p.len() + q.len();
    let mut out_bits = Vec::with_capacity(total_bits);
    let mut carry: Vec<Lit> = Vec::new();
    let mut max_carry_val: u64 = 0;

    for k in 0..conv_len {
        let terms = (k + 1).min(conv_len - k).min(mp).min(mq) as u64;
        let max_ck = terms * 225;
        let ck_bits = (64 - max_ck.leading_zeros() as usize).max(1).min(16);
        let ck_slice = &prod_spec[k][..ck_bits];

        // Add ck_slice + carry
        let add_len = ck_slice.len().max(carry.len());
        let mut acc = Vec::with_capacity(add_len + 1);
        let mut c = Lit::FALSE;
        for i in 0..add_len {
            let ba = ck_slice.get(i).copied().unwrap_or(Lit::FALSE);
            let bb = carry.get(i).copied().unwrap_or(Lit::FALSE);
            let (s, nc) = aig.full_adder(ba, bb, c);
            acc.push(s);
            c = nc;
        }
        let max_acc = max_ck + max_carry_val;
        let acc_bits = (64 - max_acc.leading_zeros() as usize).max(4);
        if c != Lit::FALSE && acc.len() < acc_bits {
            acc.push(c);
        }

        // Emit low 4 bits as product bits [4k .. 4k+4]
        for b in 0..4 {
            if out_bits.len() < total_bits {
                out_bits.push(acc.get(b).copied().unwrap_or(Lit::FALSE));
            }
        }
        // Carry = acc >> 4
        max_carry_val = max_acc >> 4;
        let carry_bits = if max_carry_val == 0 { 0 } else { 64 - max_carry_val.leading_zeros() as usize };
        carry = (4..(4 + carry_bits))
            .map(|i| acc.get(i).copied().unwrap_or(Lit::FALSE))
            .collect();
    }
    for &cb in &carry {
        if out_bits.len() < total_bits {
            out_bits.push(cb);
        }
    }
    while out_bits.len() < total_bits {
        out_bits.push(Lit::FALSE);
    }
    (out_bits, mp, mq, l)
}

/// Exact Wallace-tree O(n^2) multiplier on the exact same `Aig` (for crossover comparison).
pub fn mul_wallace(aig: &mut Aig, p: &[Lit], q: &[Lit]) -> Vec<Lit> {
    let out_bits = p.len() + q.len();
    let mut cols: Vec<Vec<Lit>> = vec![Vec::new(); out_bits];
    for (i, &pi) in p.iter().enumerate() {
        if pi == Lit::FALSE { continue; }
        for (j, &qj) in q.iter().enumerate() {
            if qj == Lit::FALSE { continue; }
            let prod = aig.and(pi, qj);
            if prod != Lit::FALSE {
                cols[i + j].push(prod);
            }
        }
    }
    let mut out = reduce_columns_to_sum(aig, cols);
    out.truncate(out_bits);
    while out.len() < out_bits {
        out.push(Lit::FALSE);
    }
    out
}

/// Assert `a <= b` for unsigned bit-vectors (LSB first).
fn assert_le(aig: &mut Aig, a: &[Lit], b: &[Lit]) {
    let n = a.len().max(b.len());
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

/// Assert that at least one bit in `bits[1..]` is 1 (i.e., odd number >= 3).
fn assert_gt_one(aig: &mut Aig, bits: &[Lit]) {
    let any = or_tree(aig, &bits[1..]);
    aig.assert_true(any);
}

pub struct NttFactoringCircuit {
    pub bit_width: usize,
    pub bp: usize,
    pub bq: usize,
    pub mp: usize,
    pub mq: usize,
    pub l: usize,
    pub aig: Aig,
    pub p_input_indices: Vec<usize>,
    pub q_input_indices: Vec<usize>,
}

impl NttFactoringCircuit {
    /// Build exact F_{65537} NTT factoring AIG for odd target `n_target`.
    /// Factor widths: `bp = ceil(B/2)`, `bq = min(ceil(B/2) + 4, 516)` (so RSA-1024 has `mp=128, mq=129, L=256`).
    /// Constraints: `p_0 = q_0 = 1` (odd), `p >= 3`, `q >= 3`, `p <= q`, and exact `p * q == N`.
    pub fn build(n_target: &BigUint, use_wallace: bool) -> Self {
        assert!(!n_target.is_even(), "target N must be odd");
        let bit_width = n_target.bit_len();
        let bp = (bit_width + 1) / 2;
        let bq = (bp + 4).min(516);
        assert!(bq >= bp);

        let mut aig = Aig::new();
        let mut p_vec = vec![Lit::TRUE];
        let mut q_vec = vec![Lit::TRUE];
        let mut p_input_indices = Vec::with_capacity(bp - 1);
        let mut q_input_indices = Vec::with_capacity(bq - 1);

        for _ in 1..bp {
            let idx = aig.num_inputs;
            p_vec.push(aig.new_input());
            p_input_indices.push(idx);
        }
        for _ in 1..bq {
            let idx = aig.num_inputs;
            q_vec.push(aig.new_input());
            q_input_indices.push(idx);
        }

        assert_gt_one(&mut aig, &p_vec);
        assert_gt_one(&mut aig, &q_vec);
        assert_le(&mut aig, &p_vec, &q_vec);

        let (prod, mp, mq, l) = if use_wallace {
            let mp = (bp + 3) / 4;
            let mq = (bq + 3) / 4;
            let l = (mp + mq - 1).next_power_of_two().max(8);
            (mul_wallace(&mut aig, &p_vec, &q_vec), mp, mq, l)
        } else {
            mul_ntt_f4(&mut aig, &p_vec, &q_vec)
        };

        for (i, &bit_lit) in prod.iter().enumerate() {
            let target_bit = n_target.bit(i);
            aig.assert_true(if target_bit { bit_lit } else { bit_lit.neg() });
        }

        Self {
            bit_width,
            bp,
            bq,
            mp,
            mq,
            l,
            aig,
            p_input_indices,
            q_input_indices,
        }
    }

    pub fn encode_witness(&self, p: &BigUint, q: &BigUint) -> Vec<bool> {
        assert!(p.bit(0) && q.bit(0), "factors must be odd");
        assert!(p.bit_len() <= self.bp, "p ({}b) exceeds bp ({})", p.bit_len(), self.bp);
        assert!(q.bit_len() <= self.bq, "q ({}b) exceeds bq ({})", q.bit_len(), self.bq);
        let mut inputs = vec![false; self.aig.num_inputs];
        for (k, &idx) in self.p_input_indices.iter().enumerate() {
            inputs[idx] = p.bit(k + 1);
        }
        for (k, &idx) in self.q_input_indices.iter().enumerate() {
            inputs[idx] = q.bit(k + 1);
        }
        inputs
    }
}
