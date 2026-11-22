#![allow(dead_code)]
//! Exact FIPS 180-4 SHA-256 Reference Implementation & Carry-Save Adder (CSA) AIG Compiler.
//!
//! Supports:
//! - Configurable number of rounds `R` in `1..=64` (exact FIPS 180-4 round function & message schedule)
//! - Optional feed-forward addition (`H0 + state`, standard for full SHA-256)
//! - Arbitrary mask of unknown vs. fixed message bits (e.g., 32-bit Bitcoin nonce, partial preimages,
//!   or full 512-bit free message preimages on step-reduced rounds)
//! - Carry-Save Adder (CSA) multi-operand 32-bit addition + first-class `Xor3`, `Maj3`, `Mux` (Ch)

use crate::aig::{Aig, F2LinearBuilder, Lit};

pub const H0: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];

pub const K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

/// Exact FIPS 180-4 SHA-256 compression function for `rounds` in `1..=64`.
pub fn sha256_compress_rounds(block: &[u32; 16], rounds: usize, add_iv: bool) -> [u32; 8] {
    assert!((1..=64).contains(&rounds));
    let mut w = [0u32; 64];
    w[..16].copy_from_slice(block);
    for i in 16..rounds {
        let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
        let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
    }

    let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut h] = H0;
    for i in 0..rounds {
        let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
        let ch = (e & f) ^ ((!e) & g);
        let t1 = h.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
        let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
        let maj = (a & b) ^ (a & c) ^ (b & c);
        let t2 = s0.wrapping_add(maj);

        h = g;
        g = f;
        f = e;
        e = d.wrapping_add(t1);
        d = c;
        c = b;
        b = a;
        a = t1.wrapping_add(t2);
    }

    if add_iv {
        [
            H0[0].wrapping_add(a),
            H0[1].wrapping_add(b),
            H0[2].wrapping_add(c),
            H0[3].wrapping_add(d),
            H0[4].wrapping_add(e),
            H0[5].wrapping_add(f),
            H0[6].wrapping_add(g),
            H0[7].wrapping_add(h),
        ]
    } else {
        [a, b, c, d, e, f, g, h]
    }
}

/// Pad a short message (`len <= 55` bytes) into a single 512-bit SHA-256 block.
pub fn pad_single_block(msg: &[u8]) -> [u32; 16] {
    assert!(msg.len() <= 55);
    let mut buf = [0u8; 64];
    buf[..msg.len()].copy_from_slice(msg);
    buf[msg.len()] = 0x80;
    let bit_len = (msg.len() as u64) * 8;
    buf[56..64].copy_from_slice(&bit_len.to_be_bytes());
    let mut block = [0u32; 16];
    for i in 0..16 {
        block[i] = u32::from_be_bytes([buf[4 * i], buf[4 * i + 1], buf[4 * i + 2], buf[4 * i + 3]]);
    }
    block
}

/// 32-bit word of AIG literals (index 0 = LSB, index 31 = MSB).
pub type Word = [Lit; 32];

fn const_word(val: u32) -> Word {
    let mut w = [Lit::FALSE; 32];
    for i in 0..32 {
        w[i] = Aig::const_lit(((val >> i) & 1) != 0);
    }
    w
}

/// Build one of SHA-256's four invertible 32x32 F2-linear diffusion subgraphs
/// (Sigma0, Sigma1, sigma0, sigma1) inside a type-safe `F2LinearBuilder`.
/// The builder statically guarantees degree <= 1 and flags the subgraph for F2 linearization
/// (including automatic joining with any adjoining linear gates!).
fn build_sha256_linear_map(
    aig: &mut Aig,
    name: &str,
    w: &Word,
    r1: usize,
    r2: usize,
    r3: usize,
    third_is_shift: bool,
) -> Word {
    let mut lin = aig.begin_linear_region(name);
    let a = F2LinearBuilder::rotr(w, r1);
    let b = F2LinearBuilder::rotr(w, r2);
    let c = if third_is_shift {
        F2LinearBuilder::shr(w, r3)
    } else {
        F2LinearBuilder::rotr(w, r3)
    };
    let out = lin.xor3_word(&a, &b, &c);
    lin.finish();
    out
}

fn ch_word(aig: &mut Aig, e: &Word, f: &Word, g: &Word) -> Word {
    let mut out = [Lit::FALSE; 32];
    for i in 0..32 {
        out[i] = aig.mux(e[i], f[i], g[i]);
    }
    out
}

fn maj_word(aig: &mut Aig, a: &Word, b: &Word, c: &Word) -> Word {
    let mut out = [Lit::FALSE; 32];
    for i in 0..32 {
        out[i] = aig.maj3(a[i], b[i], c[i]);
    }
    out
}

/// Multi-operand 32-bit modular addition via Carry-Save Adder (CSA) 3:2 tree + final CPA.
/// Automatically folds all constant operands into a single constant first!
fn add_multi_mod32(aig: &mut Aig, operands: &[Word]) -> Word {
    let mut const_sum = 0u32;
    let mut non_const: Vec<Word> = Vec::with_capacity(operands.len());
    for op in operands {
        if op.iter().all(|l| l.is_const()) {
            let mut val = 0u32;
            for i in 0..32 {
                if op[i] == Lit::TRUE {
                    val |= 1u32 << i;
                }
            }
            const_sum = const_sum.wrapping_add(val);
        } else {
            non_const.push(*op);
        }
    }
    if const_sum != 0 || non_const.is_empty() {
        non_const.push(const_word(const_sum));
    }
    if non_const.len() == 1 {
        return non_const[0];
    }

    // Repeated 3:2 Carry-Save Reduction until only 2 words remain.
    while non_const.len() > 2 {
        let mut next = Vec::with_capacity((non_const.len() * 2 + 2) / 3);
        let mut i = 0;
        while i + 3 <= non_const.len() {
            let a = non_const[i];
            let b = non_const[i + 1];
            let c = non_const[i + 2];
            let mut sum = [Lit::FALSE; 32];
            let mut carry = [Lit::FALSE; 32];
            for bit in 0..32 {
                let (s, co) = aig.full_adder(a[bit], b[bit], c[bit]);
                sum[bit] = s;
                if bit + 1 < 32 {
                    carry[bit + 1] = co;
                }
            }
            next.push(sum);
            next.push(carry);
            i += 3;
        }
        while i < non_const.len() {
            next.push(non_const[i]);
            i += 1;
        }
        non_const = next;
    }

    // Final 2-word 32-bit carry-propagate addition.
    let a = non_const[0];
    let b = non_const[1];
    let mut out = [Lit::FALSE; 32];
    let mut carry = Lit::FALSE;
    for bit in 0..32 {
        if bit == 31 {
            out[bit] = aig.xor3(a[bit], b[bit], carry);
        } else {
            let (s, c) = aig.full_adder(a[bit], b[bit], carry);
            out[bit] = s;
            carry = c;
        }
    }
    out
}

pub struct Sha256PreimageInstance {
    pub rounds: usize,
    pub add_iv: bool,
    pub base_block: [u32; 16],
    /// `(word_idx, bit_idx, aig_input_idx)` for every free (unknown) message bit.
    pub free_bits: Vec<(usize, usize, usize)>,
    pub target_digest: [u32; 8],
    pub aig: Aig,
}

impl Sha256PreimageInstance {
    /// Build an AIG for inverting `rounds`-round SHA-256 on `target_digest`, where
    /// all message bits in `free_bit_positions` (indexed `0..512`, word `pos/32`, bit `pos%32`)
    /// are free primary inputs and all other bits are fixed to `base_block`.
    pub fn build(
        rounds: usize,
        add_iv: bool,
        base_block: [u32; 16],
        free_bit_positions: &[usize],
        target_digest: [u32; 8],
    ) -> Self {
        assert!((1..=64).contains(&rounds));
        let mut aig = Aig::new();

        let mut is_free = [false; 512];
        for &pos in free_bit_positions {
            assert!(pos < 512);
            is_free[pos] = true;
        }

        let mut w_words: Vec<Word> = Vec::with_capacity(rounds.max(16));
        let mut free_bits = Vec::new();
        for wi in 0..16 {
            let mut word = [Lit::FALSE; 32];
            for bi in 0..32 {
                let pos = wi * 32 + bi;
                if is_free[pos] {
                    let inp_idx = aig.num_inputs;
                    word[bi] = aig.new_input();
                    free_bits.push((wi, bi, inp_idx));
                } else {
                    word[bi] = Aig::const_lit(((base_block[wi] >> bi) & 1) != 0);
                }
            }
            w_words.push(word);
        }

        // Message schedule expansion for rounds >= 16.
        for i in 16..rounds {
            let w15 = w_words[i - 15];
            let s0 = build_sha256_linear_map(&mut aig, "SHA256::sigma0", &w15, 7, 18, 3, true);
            let w2 = w_words[i - 2];
            let s1 = build_sha256_linear_map(&mut aig, "SHA256::sigma1", &w2, 17, 19, 10, true);
            let wi = add_multi_mod32(&mut aig, &[w_words[i - 16], s0, w_words[i - 7], s1]);
            w_words.push(wi);
        }

        let mut a = const_word(H0[0]);
        let mut b = const_word(H0[1]);
        let mut c = const_word(H0[2]);
        let mut d = const_word(H0[3]);
        let mut e = const_word(H0[4]);
        let mut f = const_word(H0[5]);
        let mut g = const_word(H0[6]);
        let mut h = const_word(H0[7]);

        for i in 0..rounds {
            let s1 = build_sha256_linear_map(&mut aig, "SHA256::Sigma1", &e, 6, 11, 25, false);
            let ch = ch_word(&mut aig, &e, &f, &g);
            let t1 = add_multi_mod32(&mut aig, &[h, s1, ch, const_word(K[i]), w_words[i]]);

            let s0 = build_sha256_linear_map(&mut aig, "SHA256::Sigma0", &a, 2, 13, 22, false);
            let maj = maj_word(&mut aig, &a, &b, &c);
            let t2 = add_multi_mod32(&mut aig, &[s0, maj]);

            let new_e = add_multi_mod32(&mut aig, &[d, t1]);
            let new_a = add_multi_mod32(&mut aig, &[t1, t2]);

            h = g;
            g = f;
            f = e;
            e = new_e;
            d = c;
            c = b;
            b = a;
            a = new_a;
        }

        let final_state = if add_iv {
            [
                add_multi_mod32(&mut aig, &[const_word(H0[0]), a]),
                add_multi_mod32(&mut aig, &[const_word(H0[1]), b]),
                add_multi_mod32(&mut aig, &[const_word(H0[2]), c]),
                add_multi_mod32(&mut aig, &[const_word(H0[3]), d]),
                add_multi_mod32(&mut aig, &[const_word(H0[4]), e]),
                add_multi_mod32(&mut aig, &[const_word(H0[5]), f]),
                add_multi_mod32(&mut aig, &[const_word(H0[6]), g]),
                add_multi_mod32(&mut aig, &[const_word(H0[7]), h]),
            ]
        } else {
            [a, b, c, d, e, f, g, h]
        };

        // Constrain all 256 digest bits to match `target_digest`.
        for wi in 0..8 {
            for bi in 0..32 {
                let target_bit = ((target_digest[wi] >> bi) & 1) != 0;
                let lit = final_state[wi][bi];
                aig.assert_true(if target_bit { lit } else { lit.neg() });
            }
        }

        Self {
            rounds,
            add_iv,
            base_block,
            free_bits,
            target_digest,
            aig,
        }
    }

    pub fn decode_block(&self, inputs: &[bool]) -> [u32; 16] {
        let mut blk = self.base_block;
        for &(wi, bi, inp_idx) in &self.free_bits {
            if inputs[inp_idx] {
                blk[wi] |= 1u32 << bi;
            } else {
                blk[wi] &= !(1u32 << bi);
            }
        }
        blk
    }
}
