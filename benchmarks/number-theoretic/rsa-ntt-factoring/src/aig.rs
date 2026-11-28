//! Minimal zero-dependency hash-consed AIG + Binary AIGER 1.9 + DIMACS CNF/XCNF exporter
//! plus direct on-disk Binary AIGER 1.9 parser & forward simulator for zero-trust verification.
#![allow(dead_code)]

use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, BufWriter, Write};
use std::path::Path;

#[derive(Copy, Clone, Eq, PartialEq, Hash, Ord, PartialOrd, Debug)]
pub struct Lit(pub u32);

impl Lit {
    pub const FALSE: Lit = Lit(0);
    pub const TRUE: Lit = Lit(1);

    #[inline]
    pub fn from_var(var: u32, neg: bool) -> Self {
        Lit((var << 1) | (neg as u32))
    }
    #[inline]
    pub fn var(self) -> u32 {
        self.0 >> 1
    }
    #[inline]
    pub fn is_neg(self) -> bool {
        (self.0 & 1) != 0
    }
    #[inline]
    pub fn neg(self) -> Self {
        Lit(self.0 ^ 1)
    }
    #[inline]
    pub fn xor_sign(self, flip: bool) -> Self {
        Lit(self.0 ^ (flip as u32))
    }
    #[inline]
    pub fn is_const(self) -> bool {
        self.var() == 0
    }
}

#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)]
pub enum Gate {
    ConstFalse,
    Input(usize),
    And(Lit, Lit),
    Xor(Lit, Lit),
    Xor3(Lit, Lit, Lit),
    Maj3(Lit, Lit, Lit),
    Mux(Lit, Lit, Lit),
}

#[derive(Clone)]
pub struct Aig {
    pub gates: Vec<Gate>,
    pub num_inputs: usize,
    pub input_vars: Vec<u32>,
    pub assertions: Vec<Lit>,
    and_table: HashMap<(Lit, Lit), u32>,
    xor_table: HashMap<(Lit, Lit), u32>,
    xor3_table: HashMap<(Lit, Lit, Lit), u32>,
    maj3_table: HashMap<(Lit, Lit, Lit), u32>,
    mux_table: HashMap<(Lit, Lit, Lit), u32>,
}

impl Aig {
    pub fn new() -> Self {
        Self {
            gates: vec![Gate::ConstFalse],
            num_inputs: 0,
            input_vars: Vec::new(),
            assertions: Vec::new(),
            and_table: HashMap::new(),
            xor_table: HashMap::new(),
            xor3_table: HashMap::new(),
            maj3_table: HashMap::new(),
            mux_table: HashMap::new(),
        }
    }

    #[inline]
    pub fn const_lit(val: bool) -> Lit {
        if val { Lit::TRUE } else { Lit::FALSE }
    }

    pub fn new_input(&mut self) -> Lit {
        let idx = self.num_inputs;
        self.num_inputs += 1;
        let var = self.gates.len() as u32;
        self.gates.push(Gate::Input(idx));
        self.input_vars.push(var);
        Lit::from_var(var, false)
    }

    pub fn new_inputs(&mut self, n: usize) -> Vec<Lit> {
        (0..n).map(|_| self.new_input()).collect()
    }

    pub fn assert_true(&mut self, lit: Lit) {
        self.assertions.push(lit);
    }

    pub fn and(&mut self, mut a: Lit, mut b: Lit) -> Lit {
        if a == Lit::FALSE || b == Lit::FALSE || a == b.neg() {
            return Lit::FALSE;
        }
        if a == Lit::TRUE {
            return b;
        }
        if b == Lit::TRUE || a == b {
            return a;
        }
        if a > b {
            std::mem::swap(&mut a, &mut b);
        }
        if let Some(&v) = self.and_table.get(&(a, b)) {
            return Lit::from_var(v, false);
        }
        let v = self.gates.len() as u32;
        self.gates.push(Gate::And(a, b));
        self.and_table.insert((a, b), v);
        Lit::from_var(v, false)
    }

    pub fn or(&mut self, a: Lit, b: Lit) -> Lit {
        self.and(a.neg(), b.neg()).neg()
    }

    pub fn xor(&mut self, a: Lit, b: Lit) -> Lit {
        if a == Lit::FALSE { return b; }
        if b == Lit::FALSE { return a; }
        if a == Lit::TRUE { return b.neg(); }
        if b == Lit::TRUE { return a.neg(); }
        if a == b { return Lit::FALSE; }
        if a == b.neg() { return Lit::TRUE; }
        let flip = a.is_neg() ^ b.is_neg();
        let mut x = Lit::from_var(a.var(), false);
        let mut y = Lit::from_var(b.var(), false);
        if x > y { std::mem::swap(&mut x, &mut y); }
        if let Some(&v) = self.xor_table.get(&(x, y)) {
            return Lit::from_var(v, flip);
        }
        let v = self.gates.len() as u32;
        self.gates.push(Gate::Xor(x, y));
        self.xor_table.insert((x, y), v);
        Lit::from_var(v, flip)
    }

    pub fn xor3(&mut self, a: Lit, b: Lit, c: Lit) -> Lit {
        if a.is_const() { return self.xor(b, c).xor_sign(a == Lit::TRUE); }
        if b.is_const() { return self.xor(a, c).xor_sign(b == Lit::TRUE); }
        if c.is_const() { return self.xor(a, b).xor_sign(c == Lit::TRUE); }
        if a.var() == b.var() { return c.xor_sign(a != b); }
        if a.var() == c.var() { return b.xor_sign(a != c); }
        if b.var() == c.var() { return a.xor_sign(b != c); }
        let flip = a.is_neg() ^ b.is_neg() ^ c.is_neg();
        let mut arr = [
            Lit::from_var(a.var(), false),
            Lit::from_var(b.var(), false),
            Lit::from_var(c.var(), false),
        ];
        arr.sort_unstable();
        let key = (arr[0], arr[1], arr[2]);
        if let Some(&v) = self.xor3_table.get(&key) {
            return Lit::from_var(v, flip);
        }
        let v = self.gates.len() as u32;
        self.gates.push(Gate::Xor3(arr[0], arr[1], arr[2]));
        self.xor3_table.insert(key, v);
        Lit::from_var(v, flip)
    }

    pub fn maj3(&mut self, a: Lit, b: Lit, c: Lit) -> Lit {
        if a == Lit::FALSE { return self.and(b, c); }
        if a == Lit::TRUE { return self.or(b, c); }
        if b == Lit::FALSE { return self.and(a, c); }
        if b == Lit::TRUE { return self.or(a, c); }
        if c == Lit::FALSE { return self.and(a, b); }
        if c == Lit::TRUE { return self.or(a, b); }
        if a == b { return a; }
        if a == c { return a; }
        if b == c { return b; }
        if a == b.neg() { return c; }
        if a == c.neg() { return b; }
        if b == c.neg() { return a; }
        let mut arr = [a, b, c];
        arr.sort_unstable();
        let key = (arr[0], arr[1], arr[2]);
        if let Some(&v) = self.maj3_table.get(&key) {
            return Lit::from_var(v, false);
        }
        let v = self.gates.len() as u32;
        self.gates.push(Gate::Maj3(arr[0], arr[1], arr[2]));
        self.maj3_table.insert(key, v);
        Lit::from_var(v, false)
    }

    pub fn mux(&mut self, sel: Lit, on_t: Lit, on_f: Lit) -> Lit {
        if sel == Lit::TRUE { return on_t; }
        if sel == Lit::FALSE { return on_f; }
        if on_t == on_f { return on_t; }
        if on_t == Lit::TRUE { return self.or(sel, on_f); }
        if on_t == Lit::FALSE { return self.and(sel.neg(), on_f); }
        if on_f == Lit::TRUE { return self.or(sel.neg(), on_t); }
        if on_f == Lit::FALSE { return self.and(sel, on_t); }
        if on_t == on_f.neg() { return self.xor(sel, on_f); }
        let (s, t, f) = if sel.is_neg() { (sel.neg(), on_f, on_t) } else { (sel, on_t, on_f) };
        if let Some(&v) = self.mux_table.get(&(s, t, f)) {
            return Lit::from_var(v, false);
        }
        let v = self.gates.len() as u32;
        self.gates.push(Gate::Mux(s, t, f));
        self.mux_table.insert((s, t, f), v);
        Lit::from_var(v, false)
    }

    pub fn full_adder(&mut self, a: Lit, b: Lit, c: Lit) -> (Lit, Lit) {
        (self.xor3(a, b, c), self.maj3(a, b, c))
    }

    pub fn half_adder(&mut self, a: Lit, b: Lit) -> (Lit, Lit) {
        (self.xor(a, b), self.and(a, b))
    }

    pub fn active_coi(&self) -> Vec<bool> {
        let mut active = vec![false; self.gates.len()];
        let mut stack: Vec<usize> = self.assertions.iter().map(|l| l.var() as usize).collect();
        while let Some(v) = stack.pop() {
            if v == 0 || active[v] {
                continue;
            }
            active[v] = true;
            match self.gates[v] {
                Gate::ConstFalse | Gate::Input(_) => {}
                Gate::And(a, b) | Gate::Xor(a, b) => {
                    stack.push(a.var() as usize);
                    stack.push(b.var() as usize);
                }
                Gate::Xor3(a, b, c) | Gate::Maj3(a, b, c) | Gate::Mux(a, b, c) => {
                    stack.push(a.var() as usize);
                    stack.push(b.var() as usize);
                    stack.push(c.var() as usize);
                }
            }
        }
        active
    }

    /// Lower to pure 2-input AND-Inverter Graph (combinational miter: PO_0 = AND of assertions).
    /// Uses polarity-normalized `mk_xor` so `Xor3` and `Maj3` in every full adder share `x ^ y`
    /// (9 ANDs per full adder instead of 10, while preserving 3-AND XOR patterns for `to_anf.py`).
    pub fn lower_to_aiger(&self) -> (u32, u32, Vec<(u32, u32)>) {
        let mut ands: Vec<(u32, u32)> = Vec::new();
        let mut table: HashMap<(u32, u32), u32> = HashMap::new();
        let ni = self.num_inputs as u32;

        let mk_and = |mut a: u32, mut b: u32, ands: &mut Vec<(u32, u32)>, tbl: &mut HashMap<(u32, u32), u32>| -> u32 {
            if a == 0 || b == 0 || (a ^ b) == 1 { return 0; }
            if a == 1 { return b; }
            if b == 1 || a == b { return a; }
            if a < b { std::mem::swap(&mut a, &mut b); }
            if let Some(&e) = tbl.get(&(a, b)) { return e; }
            let lhs = (ni + 1 + ands.len() as u32) << 1;
            ands.push((a, b));
            tbl.insert((a, b), lhs);
            lhs
        };
        let mk_or = |a: u32, b: u32, ands: &mut Vec<(u32, u32)>, tbl: &mut HashMap<(u32, u32), u32>| -> u32 {
            mk_and(a ^ 1, b ^ 1, ands, tbl) ^ 1
        };
        let mk_xor = |a: u32, b: u32, ands: &mut Vec<(u32, u32)>, tbl: &mut HashMap<(u32, u32), u32>| -> u32 {
            if a == 0 { return b; }
            if b == 0 { return a; }
            if a == 1 { return b ^ 1; }
            if b == 1 { return a ^ 1; }
            if a == b { return 0; }
            if (a ^ b) == 1 { return 1; }
            let flip = (a ^ b) & 1;
            let mut x0 = a & !1;
            let mut y0 = b & !1;
            if x0 < y0 { std::mem::swap(&mut x0, &mut y0); }
            let p = mk_and(x0, y0 ^ 1, ands, tbl);
            let q = mk_and(x0 ^ 1, y0, ands, tbl);
            mk_or(p, q, ands, tbl) ^ flip
        };

        let mut memo: Vec<Option<u32>> = vec![None; self.gates.len()];
        memo[0] = Some(0);
        let mut stack: Vec<(usize, bool)> = Vec::new();
        for &al in &self.assertions {
            if memo[al.var() as usize].is_none() {
                stack.push((al.var() as usize, false));
            }
        }
        while let Some((v, done)) = stack.pop() {
            if memo[v].is_some() { continue; }
            if !done {
                stack.push((v, true));
                match self.gates[v] {
                    Gate::ConstFalse | Gate::Input(_) => {}
                    Gate::And(x, y) | Gate::Xor(x, y) => {
                        for l in [x, y] { if memo[l.var() as usize].is_none() { stack.push((l.var() as usize, false)); } }
                    }
                    Gate::Xor3(x, y, z) | Gate::Maj3(x, y, z) | Gate::Mux(x, y, z) => {
                        for l in [x, y, z] { if memo[l.var() as usize].is_none() { stack.push((l.var() as usize, false)); } }
                    }
                }
            } else {
                let ml = |l: Lit, m: &[Option<u32>]| m[l.var() as usize].unwrap() ^ (l.is_neg() as u32);
                let out = match self.gates[v] {
                    Gate::ConstFalse => 0,
                    Gate::Input(idx) => (idx as u32 + 1) << 1,
                    Gate::And(x, y) => mk_and(ml(x, &memo), ml(y, &memo), &mut ands, &mut table),
                    Gate::Xor(x, y) => mk_xor(ml(x, &memo), ml(y, &memo), &mut ands, &mut table),
                    Gate::Xor3(x, y, z) => {
                        let xy = mk_xor(ml(x, &memo), ml(y, &memo), &mut ands, &mut table);
                        mk_xor(xy, ml(z, &memo), &mut ands, &mut table)
                    }
                    Gate::Maj3(x, y, z) => {
                        let (ax, ay, az) = (ml(x, &memo), ml(y, &memo), ml(z, &memo));
                        let xy = mk_xor(ax, ay, &mut ands, &mut table);
                        let ab = mk_and(ax, ay, &mut ands, &mut table);
                        let cab = mk_and(az, xy, &mut ands, &mut table);
                        mk_or(ab, cab, &mut ands, &mut table)
                    }
                    Gate::Mux(s, t, f) => {
                        let (as_, at, af) = (ml(s, &memo), ml(t, &memo), ml(f, &memo));
                        let p = mk_and(as_, at, &mut ands, &mut table);
                        let q = mk_and(as_ ^ 1, af, &mut ands, &mut table);
                        mk_or(p, q, &mut ands, &mut table)
                    }
                };
                memo[v] = Some(out);
            }
        }
        let mut lits: Vec<u32> = self.assertions.iter().map(|&al| memo[al.var() as usize].unwrap() ^ (al.is_neg() as u32)).collect();
        let out_lit = if lits.is_empty() {
            1
        } else {
            while lits.len() > 1 {
                let mut nxt = Vec::with_capacity((lits.len() + 1) / 2);
                let mut i = 0;
                while i + 1 < lits.len() {
                    let g = mk_and(lits[i], lits[i + 1], &mut ands, &mut table);
                    if g == 0 { lits = vec![0]; break; }
                    nxt.push(g);
                    i += 2;
                }
                if lits.len() == 1 && lits[0] == 0 { break; }
                if i < lits.len() { nxt.push(lits[i]); }
                lits = nxt;
            }
            lits[0]
        };
        (ni, out_lit, ands)
    }

    pub fn aiger_and_count(&self) -> usize {
        self.lower_to_aiger().2.len()
    }

    /// Export exact Binary AIGER 1.9 (combinational miter: PO_0 = AND of all assertions).
    /// Returns `(num_inputs, num_ands)`.
    pub fn write_aiger_binary(&self, path: &Path, comment: &str) -> io::Result<(usize, usize)> {
        let (ni, out_lit, ands) = self.lower_to_aiger();
        let a = ands.len() as u32;
        let m = ni + a;
        let mut w = BufWriter::new(File::create(path)?);
        writeln!(w, "aig {m} {ni} 0 1 {a}")?;
        writeln!(w, "{out_lit}")?;
        let enc = |mut x: u32, out: &mut BufWriter<File>| -> io::Result<()> {
            while x >= 0x80 {
                out.write_all(&[((x & 0x7f) as u8) | 0x80])?;
                x >>= 7;
            }
            out.write_all(&[x as u8])
        };
        for (k, &(rhs0, rhs1)) in ands.iter().enumerate() {
            let lhs = (ni + 1 + k as u32) << 1;
            enc(lhs - rhs0, &mut w)?;
            enc(rhs0 - rhs1, &mut w)?;
        }
        if !comment.is_empty() {
            writeln!(w, "c")?;
            for line in comment.lines() {
                writeln!(w, "{line}")?;
            }
        }
        w.flush()?;
        Ok((ni as usize, a as usize))
    }

    /// Export Tseitin DIMACS CNF (`native_xors=false`) or CryptoMiniSat XCNF (`native_xors=true`).
    /// Returns `(num_vars, num_clauses_plus_xors)`.
    pub fn write_dimacs(&self, path: &Path, native_xors: bool) -> io::Result<(usize, usize)> {
        let active = self.active_coi();
        let mut v2d = vec![0i32; self.gates.len()];
        let mut next_id = 1i32;
        // Preserve primary inputs as DIMACS vars 1..=num_inputs in exact PI order!
        for &iv in &self.input_vars {
            v2d[iv as usize] = next_id;
            next_id += 1;
        }
        for v in 1..self.gates.len() {
            if active[v] && v2d[v] == 0 {
                v2d[v] = next_id;
                next_id += 1;
            }
        }
        let mut cnf: Vec<Vec<i32>> = Vec::new();
        let mut xors: Vec<Vec<i32>> = Vec::new();
        let push_cl = |out: &mut Vec<Vec<i32>>, lits: &[Lit]| {
            let mut cl = Vec::with_capacity(lits.len());
            for &l in lits {
                let v = l.var() as usize;
                if v == 0 {
                    if l.is_neg() { return; }
                    continue;
                }
                let dl = if l.is_neg() { -v2d[v] } else { v2d[v] };
                if cl.contains(&(-dl)) { return; }
                if !cl.contains(&dl) { cl.push(dl); }
            }
            out.push(cl);
        };
        let push_xor = |cnf_out: &mut Vec<Vec<i32>>, xor_out: &mut Vec<Vec<i32>>, z: Lit, ins: &[Lit]| {
            if native_xors {
                let mut rhs = false;
                let mut vars = Vec::with_capacity(ins.len() + 1);
                let mut add = |l: Lit| {
                    let v = l.var() as usize;
                    rhs ^= l.is_neg();
                    if v != 0 {
                        let id = v2d[v];
                        if let Some(p) = vars.iter().position(|&x| x == id) { vars.swap_remove(p); } else { vars.push(id); }
                    }
                };
                add(z);
                for &l in ins { add(l); }
                if vars.is_empty() {
                    if rhs { cnf_out.push(Vec::new()); }
                } else {
                    if !rhs { vars[0] = -vars[0]; }
                    xor_out.push(vars);
                }
            } else if ins.len() == 2 {
                let (a, b) = (ins[0], ins[1]);
                push_cl(cnf_out, &[z.neg(), a.neg(), b.neg()]);
                push_cl(cnf_out, &[z.neg(), a, b]);
                push_cl(cnf_out, &[z, a.neg(), b]);
                push_cl(cnf_out, &[z, a, b.neg()]);
            } else {
                let (a, b, c) = (ins[0], ins[1], ins[2]);
                for mask in 0u8..8 {
                    let na = (mask & 1) != 0;
                    let nb = (mask & 2) != 0;
                    let nc = (mask & 4) != 0;
                    let nz = na ^ nb ^ nc;
                    push_cl(cnf_out, &[z.xor_sign(!nz), a.xor_sign(na), b.xor_sign(nb), c.xor_sign(nc)]);
                }
            }
        };
        for v in 1..self.gates.len() {
            if !active[v] { continue; }
            let z = Lit::from_var(v as u32, false);
            match self.gates[v] {
                Gate::ConstFalse | Gate::Input(_) => {}
                Gate::And(a, b) => {
                    push_cl(&mut cnf, &[z.neg(), a]);
                    push_cl(&mut cnf, &[z.neg(), b]);
                    push_cl(&mut cnf, &[z, a.neg(), b.neg()]);
                }
                Gate::Xor(a, b) => push_xor(&mut cnf, &mut xors, z, &[a, b]),
                Gate::Xor3(a, b, c) => push_xor(&mut cnf, &mut xors, z, &[a, b, c]),
                Gate::Maj3(a, b, c) => {
                    push_cl(&mut cnf, &[z.neg(), a, b]);
                    push_cl(&mut cnf, &[z.neg(), a, c]);
                    push_cl(&mut cnf, &[z.neg(), b, c]);
                    push_cl(&mut cnf, &[z, a.neg(), b.neg()]);
                    push_cl(&mut cnf, &[z, a.neg(), c.neg()]);
                    push_cl(&mut cnf, &[z, b.neg(), c.neg()]);
                }
                Gate::Mux(s, t, f) => {
                    push_cl(&mut cnf, &[s.neg(), t.neg(), z]);
                    push_cl(&mut cnf, &[s.neg(), t, z.neg()]);
                    push_cl(&mut cnf, &[s, f.neg(), z]);
                    push_cl(&mut cnf, &[s, f, z.neg()]);
                }
            }
        }
        for &al in &self.assertions {
            if al == Lit::FALSE {
                cnf.push(Vec::new());
            } else if al != Lit::TRUE {
                push_cl(&mut cnf, &[al]);
            }
        }
        let mut w = BufWriter::new(File::create(path)?);
        let nvars = (next_id - 1) as usize;
        let ncls = cnf.len() + xors.len();
        writeln!(w, "p cnf {nvars} {ncls}")?;
        for cl in &cnf {
            for &l in cl { write!(w, "{l} ")?; }
            writeln!(w, "0")?;
        }
        for xl in &xors {
            write!(w, "x ")?;
            for &l in xl { write!(w, "{l} ")?; }
            writeln!(w, "0")?;
        }
        w.flush()?;
        Ok((nvars, ncls))
    }

    /// Evaluate all gates in memory given primary input bits (0-based by PI index).
    pub fn eval_all(&self, inputs: &[bool]) -> Vec<bool> {
        assert_eq!(inputs.len(), self.num_inputs);
        let mut vals = vec![false; self.gates.len()];
        let get = |l: Lit, v: &[bool]| v[l.var() as usize] ^ l.is_neg();
        for i in 1..self.gates.len() {
            vals[i] = match self.gates[i] {
                Gate::ConstFalse => false,
                Gate::Input(idx) => inputs[idx],
                Gate::And(a, b) => get(a, &vals) & get(b, &vals),
                Gate::Xor(a, b) => get(a, &vals) ^ get(b, &vals),
                Gate::Xor3(a, b, c) => get(a, &vals) ^ get(b, &vals) ^ get(c, &vals),
                Gate::Maj3(a, b, c) => {
                    let s = (get(a, &vals) as u8) + (get(b, &vals) as u8) + (get(c, &vals) as u8);
                    s >= 2
                }
                Gate::Mux(s, t, f) => if get(s, &vals) { get(t, &vals) } else { get(f, &vals) },
            };
        }
        vals
    }
}

/// Independent Binary AIGER 1.9 parser & combinational forward simulator for zero-trust checks.
pub struct ParsedAiger {
    pub num_inputs: usize,
    pub output_lit: u32,
    pub ands: Vec<(u32, u32)>,
}

impl ParsedAiger {
    pub fn read_file(path: &Path) -> io::Result<Self> {
        let data = fs::read(path)?;
        let nl = data.iter().position(|&b| b == b'\n').expect("AIGER header newline");
        let hdr = std::str::from_utf8(&data[..nl]).expect("ASCII header");
        let parts: Vec<&str> = hdr.split_whitespace().collect();
        assert!(parts.len() >= 6 && parts[0] == "aig", "bad AIGER header: {hdr}");
        let m: usize = parts[1].parse().unwrap();
        let i: usize = parts[2].parse().unwrap();
        let l: usize = parts[3].parse().unwrap();
        let o: usize = parts[4].parse().unwrap();
        let a: usize = parts[5].parse().unwrap();
        assert_eq!(l, 0, "expected combinational AIGER (L=0)");
        assert_eq!(o, 1, "expected single-output miter (O=1)");
        assert_eq!(i + a, m, "binary AIGER requires I+A==M");

        let mut pos = nl + 1;
        let nl2 = data[pos..].iter().position(|&b| b == b'\n').expect("output line") + pos;
        let output_lit: u32 = std::str::from_utf8(&data[pos..nl2]).unwrap().trim().parse().unwrap();
        pos = nl2 + 1;

        let mut ands = Vec::with_capacity(a);
        for k in 0..a {
            let lhs = ((i + 1 + k) as u32) << 1;
            let mut d0 = 0u32;
            let mut sh = 0u32;
            loop {
                let b = data[pos];
                pos += 1;
                d0 |= ((b & 0x7f) as u32) << sh;
                if (b & 0x80) == 0 { break; }
                sh += 7;
            }
            let mut d1 = 0u32;
            let mut sh = 0u32;
            loop {
                let b = data[pos];
                pos += 1;
                d1 |= ((b & 0x7f) as u32) << sh;
                if (b & 0x80) == 0 { break; }
                sh += 7;
            }
            assert!(d0 <= lhs, "AIGER delta0 out of range at gate {k}");
            let r0 = lhs - d0;
            assert!(d1 <= r0, "AIGER delta1 out of range at gate {k}");
            let r1 = r0 - d1;
            ands.push((r0, r1));
        }
        Ok(Self { num_inputs: i, output_lit, ands })
    }

    pub fn eval(&self, inputs: &[bool]) -> bool {
        assert_eq!(inputs.len(), self.num_inputs);
        let mut vals = vec![false; self.num_inputs + self.ands.len() + 1];
        for (idx, &b) in inputs.iter().enumerate() {
            vals[idx + 1] = b;
        }
        for (k, &(r0, r1)) in self.ands.iter().enumerate() {
            let b0 = vals[(r0 >> 1) as usize] ^ ((r0 & 1) != 0);
            let b1 = vals[(r1 >> 1) as usize] ^ ((r1 & 1) != 0);
            vals[self.num_inputs + 1 + k] = b0 & b1;
        }
        vals[(self.output_lit >> 1) as usize] ^ ((self.output_lit & 1) != 0)
    }
}
