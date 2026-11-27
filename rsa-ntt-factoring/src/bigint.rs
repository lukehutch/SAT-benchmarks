//! Minimal zero-dependency arbitrary-precision unsigned integer (`BigUint`)
//! with decimal parsing, multiplication, modular exponentiation, and Miller-Rabin primality check.
#![allow(dead_code)]

use std::cmp::Ordering;
use std::fmt;

#[derive(Clone, Eq, PartialEq, Debug)]
pub struct BigUint {
    /// Little-endian 64-bit limbs, normalized (no trailing zero limbs).
    pub limbs: Vec<u64>,
}

impl BigUint {
    pub fn zero() -> Self {
        Self { limbs: Vec::new() }
    }

    pub fn from_u64(x: u64) -> Self {
        if x == 0 { Self::zero() } else { Self { limbs: vec![x] } }
    }

    pub fn from_dec(s: &str) -> Self {
        let mut acc = Self::zero();
        for ch in s.bytes() {
            if ch == b'_' || ch == b' ' { continue; }
            assert!(ch.is_ascii_digit(), "invalid decimal char in {s}");
            acc.mul_add_u64(10, (ch - b'0') as u64);
        }
        acc
    }

    fn normalize(&mut self) {
        while self.limbs.last() == Some(&0) {
            self.limbs.pop();
        }
    }

    pub fn is_zero(&self) -> bool {
        self.limbs.is_empty()
    }

    pub fn is_even(&self) -> bool {
        self.limbs.first().copied().unwrap_or(0) & 1 == 0
    }

    pub fn bit_len(&self) -> usize {
        if let Some(&top) = self.limbs.last() {
            (self.limbs.len() - 1) * 64 + (64 - top.leading_zeros() as usize)
        } else {
            0
        }
    }

    pub fn bit(&self, idx: usize) -> bool {
        let w = idx / 64;
        let b = idx % 64;
        if w >= self.limbs.len() { false } else { ((self.limbs[w] >> b) & 1) != 0 }
    }

    pub fn set_bit(&mut self, idx: usize, val: bool) {
        let w = idx / 64;
        let b = idx % 64;
        if w >= self.limbs.len() {
            if !val { return; }
            self.limbs.resize(w + 1, 0);
        }
        if val {
            self.limbs[w] |= 1u64 << b;
        } else {
            self.limbs[w] &= !(1u64 << b);
            self.normalize();
        }
    }

    pub fn mul_add_u64(&mut self, mul: u64, add: u64) {
        let mut carry = add as u128;
        for limb in &mut self.limbs {
            let v = (*limb as u128) * (mul as u128) + carry;
            *limb = v as u64;
            carry = v >> 64;
        }
        if carry > 0 {
            self.limbs.push(carry as u64);
        }
        self.normalize();
    }

    pub fn add(&self, other: &Self) -> Self {
        let n = self.limbs.len().max(other.limbs.len());
        let mut out = Vec::with_capacity(n + 1);
        let mut carry = 0u128;
        for i in 0..n {
            let a = self.limbs.get(i).copied().unwrap_or(0) as u128;
            let b = other.limbs.get(i).copied().unwrap_or(0) as u128;
            let s = a + b + carry;
            out.push(s as u64);
            carry = s >> 64;
        }
        if carry > 0 {
            out.push(carry as u64);
        }
        let mut r = Self { limbs: out };
        r.normalize();
        r
    }

    pub fn sub(&self, other: &Self) -> Self {
        assert!(self >= other, "BigUint underflow");
        let mut out = Vec::with_capacity(self.limbs.len());
        let mut borrow = 0i128;
        for i in 0..self.limbs.len() {
            let a = self.limbs[i] as i128;
            let b = other.limbs.get(i).copied().unwrap_or(0) as i128;
            let mut d = a - b - borrow;
            if d < 0 {
                d += 1i128 << 64;
                borrow = 1;
            } else {
                borrow = 0;
            }
            out.push(d as u64);
        }
        let mut r = Self { limbs: out };
        r.normalize();
        r
    }

    pub fn mul(&self, other: &Self) -> Self {
        if self.is_zero() || other.is_zero() {
            return Self::zero();
        }
        let mut out = vec![0u64; self.limbs.len() + other.limbs.len()];
        for (i, &a) in self.limbs.iter().enumerate() {
            let mut carry = 0u128;
            for (j, &b) in other.limbs.iter().enumerate() {
                let prod = (a as u128) * (b as u128) + (out[i + j] as u128) + carry;
                out[i + j] = prod as u64;
                carry = prod >> 64;
            }
            out[i + other.limbs.len()] = carry as u64;
        }
        let mut r = Self { limbs: out };
        r.normalize();
        r
    }

    pub fn shr1(&mut self) {
        let mut carry = 0u64;
        for limb in self.limbs.iter_mut().rev() {
            let next_carry = *limb & 1;
            *limb = (*limb >> 1) | (carry << 63);
            carry = next_carry;
        }
        self.normalize();
    }

    pub fn rem(&self, modulus: &Self) -> Self {
        assert!(!modulus.is_zero());
        if self < modulus {
            return self.clone();
        }
        let mut r = Self::zero();
        for bit_idx in (0..self.bit_len()).rev() {
            // r <<= 1
            let mut carry = if self.bit(bit_idx) { 1u64 } else { 0u64 };
            for limb in &mut r.limbs {
                let next_c = *limb >> 63;
                *limb = (*limb << 1) | carry;
                carry = next_c;
            }
            if carry != 0 {
                r.limbs.push(carry);
            }
            if &r >= modulus {
                r = r.sub(modulus);
            }
        }
        r
    }

    pub fn pow_mod(&self, exp: &Self, modulus: &Self) -> Self {
        let mut res = Self::from_u64(1);
        let mut base = self.rem(modulus);
        for bit_idx in 0..exp.bit_len() {
            if exp.bit(bit_idx) {
                res = res.mul(&base).rem(modulus);
            }
            base = base.mul(&base).rem(modulus);
        }
        res
    }

    pub fn rem_u64(&self, m: u64) -> u64 {
        let mut r = 0u128;
        let m128 = m as u128;
        for &limb in self.limbs.iter().rev() {
            r = ((r << 64) | (limb as u128)) % m128;
        }
        r as u64
    }

    pub fn is_probable_prime(&self) -> bool {
        let one = Self::from_u64(1);
        let two = Self::from_u64(2);
        if self < &two { return false; }
        let small: [u64; 16] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53];
        for &p in &small {
            if *self == Self::from_u64(p) { return true; }
            if self.rem_u64(p) == 0 { return false; }
        }
        let n_minus_1 = self.sub(&one);
        let mut d = n_minus_1.clone();
        let mut s = 0usize;
        while d.is_even() {
            d.shr1();
            s += 1;
        }
        for &a in &[2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
            let base = Self::from_u64(a);
            if &base >= self { continue; }
            let mut x = base.pow_mod(&d, self);
            if x == one || x == n_minus_1 { continue; }
            let mut composite = true;
            for _ in 1..s {
                x = x.mul(&x).rem(self);
                if x == n_minus_1 {
                    composite = false;
                    break;
                }
            }
            if composite { return false; }
        }
        true
    }
}

impl Ord for BigUint {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.limbs.len().cmp(&other.limbs.len()) {
            Ordering::Equal => {
                for i in (0..self.limbs.len()).rev() {
                    match self.limbs[i].cmp(&other.limbs[i]) {
                        Ordering::Equal => continue,
                        ord => return ord,
                    }
                }
                Ordering::Equal
            }
            ord => ord,
        }
    }
}

impl PartialOrd for BigUint {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl fmt::Display for BigUint {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.is_zero() {
            return write!(f, "0");
        }
        let mut tmp = self.clone();
        let mut chunks: Vec<u64> = Vec::new();
        while !tmp.is_zero() {
            let mut rem = 0u128;
            for limb in tmp.limbs.iter_mut().rev() {
                let cur = (rem << 64) | (*limb as u128);
                *limb = (cur / 1_000_000_000) as u64;
                rem = cur % 1_000_000_000;
            }
            tmp.normalize();
            chunks.push(rem as u64);
        }
        write!(f, "{}", chunks.last().unwrap())?;
        for &c in chunks.iter().rev().skip(1) {
            write!(f, "{:09}", c)?;
        }
        Ok(())
    }
}
