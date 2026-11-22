mod aig;
mod factoring;

use aig::{Aig, Lit};
use factoring::{mul_karatsuba, mul_wallace};
use std::fs;
use std::path::Path;

fn build_array_multiplier(aig: &mut Aig, p: &[Lit], q: &[Lit]) -> Vec<Lit> {
    let out_bits = p.len() + q.len();
    let mut acc = vec![Lit::FALSE; out_bits];
    for (j, &qj) in q.iter().enumerate() {
        let mut carry = Lit::FALSE;
        for i in 0..p.len() {
            let pp = aig.and(p[i], qj);
            let (s, c) = aig.full_adder(acc[i + j], pp, carry);
            acc[i + j] = s;
            carry = c;
        }
        let mut k = j + p.len();
        while k < out_bits && carry != Lit::FALSE {
            let (s, c) = aig.half_adder(acc[k], carry);
            acc[k] = s;
            carry = c;
            k += 1;
        }
    }
    acc
}

fn build_cec_adder_miter(width: usize) -> Aig {
    let mut aig = Aig::new();
    let a = aig.new_inputs(width);
    let b = aig.new_inputs(width);
    let mut rc = Vec::with_capacity(width + 1);
    let mut carry = Lit::FALSE;
    for i in 0..width {
        let (s, c) = aig.full_adder(a[i], b[i], carry);
        rc.push(s);
        carry = c;
    }
    rc.push(carry);

    let p0: Vec<Lit> = (0..width).map(|i| aig.xor(a[i], b[i])).collect();
    let mut p = p0.clone();
    let mut g: Vec<Lit> = (0..width).map(|i| aig.and(a[i], b[i])).collect();
    let mut step = 1usize;
    while step < width {
        let mut next_g = g.clone();
        let mut next_p = p.clone();
        for i in step..width {
            let pg = aig.and(p[i], g[i - step]);
            next_g[i] = aig.or(g[i], pg);
            next_p[i] = aig.and(p[i], p[i - step]);
        }
        g = next_g;
        p = next_p;
        step <<= 1;
    }
    let mut ks = Vec::with_capacity(width + 1);
    ks.push(p0[0]);
    for i in 1..width {
        ks.push(aig.xor(p0[i], g[i - 1]));
    }
    ks.push(g[width - 1]);

    let mut any_diff = Lit::FALSE;
    for k in 0..=width {
        let diff = aig.xor(rc[k], ks[k]);
        any_diff = aig.or(any_diff, diff);
    }
    aig.assert_true(any_diff);
    aig
}

fn build_cec_mult_miter(width: usize, use_karatsuba: bool) -> Aig {
    let mut aig = Aig::new();
    let x = aig.new_inputs(width);
    let y = aig.new_inputs(width);
    let prod_a = mul_wallace(&mut aig, &x, &y);
    let prod_b = if use_karatsuba {
        mul_karatsuba(&mut aig, &x, &y)
    } else {
        build_array_multiplier(&mut aig, &x, &y)
    };
    let mut any_diff = Lit::FALSE;
    for k in 0..(2 * width) {
        let diff = aig.xor(prod_a[k], prod_b[k]);
        any_diff = aig.or(any_diff, diff);
    }
    aig.assert_true(any_diff);
    aig
}

fn main() {
    let suite = Path::new("..");
    let cnf_dir = suite.join("cnf-version");
    fs::create_dir_all(&cnf_dir).expect("create cnf-version");
    let items = vec![
        ("cec_adder_32b_rc_vs_ks", build_cec_adder_miter(32)),
        ("cec_mult_6x6_arr_vs_wal", build_cec_mult_miter(6, false)),
        ("cec_mult_8x8_arr_vs_wal", build_cec_mult_miter(8, false)),
        ("cec_array_vs_wallace_10x10", build_cec_mult_miter(10, false)),
        ("cec_wallace_vs_karat_12x12", build_cec_mult_miter(12, true)),
    ];
    for (name, aig) in items {
        aig.write_aiger_binary(&suite.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected=UNSAT\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated {name}.aig + cnf-version/{name}.{{cnf,xcnf}}");
    }
}
