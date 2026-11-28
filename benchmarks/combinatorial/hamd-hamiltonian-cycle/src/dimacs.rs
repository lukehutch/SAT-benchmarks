//! Minimal DIMACS CNF container + Binary AIGER 1.9 CNF->AIG converter for HAMD generator.
#![allow(dead_code)]

use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufWriter, Write};
use std::path::Path;

#[derive(Clone, Debug)]
pub struct CnfFormula {
    pub num_vars: usize,
    pub clauses: Vec<Vec<i32>>,
    pub xor_clauses: Vec<(Vec<u32>, bool)>,
}

impl CnfFormula {
    pub fn write_dimacs<W: Write>(&self, mut w: W) -> io::Result<()> {
        writeln!(w, "p cnf {} {}", self.num_vars, self.clauses.len())?;
        for cl in &self.clauses {
            for &l in cl {
                write!(w, "{l} ")?;
            }
            writeln!(w, "0")?;
        }
        w.flush()
    }

    pub fn write_aiger_binary(&self, path: &Path, comment: &str) -> io::Result<()> {
        let ni = self.num_vars as u32;
        let mut ands: Vec<(u32, u32)> = Vec::new();
        let mut tbl: HashMap<(u32, u32), u32> = HashMap::new();
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
        let bal = |mut lits: Vec<u32>, ands: &mut Vec<(u32, u32)>, tbl: &mut HashMap<(u32, u32), u32>| -> u32 {
            if lits.is_empty() { return 1; }
            while lits.len() > 1 {
                let mut nxt = Vec::with_capacity((lits.len() + 1) / 2);
                let mut i = 0;
                while i + 1 < lits.len() {
                    let g = mk_and(lits[i], lits[i + 1], ands, tbl);
                    if g == 0 { return 0; }
                    nxt.push(g);
                    i += 2;
                }
                if i < lits.len() { nxt.push(lits[i]); }
                lits = nxt;
            }
            lits[0]
        };

        let mut cl_lits: Vec<u32> = Vec::with_capacity(self.clauses.len());
        let mut unsat = false;
        for cl in &self.clauses {
            if cl.is_empty() { unsat = true; break; }
            let mut a: Vec<u32> = cl.iter().map(|&dl| (dl.unsigned_abs() << 1) | ((dl < 0) as u32)).collect();
            a.sort_unstable();
            a.dedup();
            if a.windows(2).any(|w| (w[0] ^ w[1]) == 1) { continue; }
            let negs: Vec<u32> = a.into_iter().map(|l| l ^ 1).collect();
            cl_lits.push(bal(negs, &mut ands, &mut tbl) ^ 1);
        }
        let out_lit = if unsat { 0 } else { bal(cl_lits, &mut ands, &mut tbl) };
        let a = ands.len() as u32;
        let m = ni + a;
        let mut w = BufWriter::new(File::create(path)?);
        writeln!(w, "aig {m} {ni} 0 1 {a}")?;
        writeln!(w, "{out_lit}")?;
        let enc = |mut x: u32, out: &mut BufWriter<File>| -> io::Result<()> {
            while x >= 0x80 { out.write_all(&[((x & 0x7f) as u8) | 0x80])?; x >>= 7; }
            out.write_all(&[x as u8])
        };
        for (k, &(r0, r1)) in ands.iter().enumerate() {
            let lhs = (ni + 1 + k as u32) << 1;
            enc(lhs - r0, &mut w)?;
            enc(r0 - r1, &mut w)?;
        }
        if !comment.is_empty() {
            writeln!(w, "c")?;
            for line in comment.lines() { writeln!(w, "{line}")?; }
        }
        w.flush()
    }
}
