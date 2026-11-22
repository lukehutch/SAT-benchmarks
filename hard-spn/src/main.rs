mod aig;

use aig::Aig;
use std::fs;
use std::path::Path;

fn build_spn(n_in: usize, rank_eqs: usize, n_nl: usize, flip_last_unsat: bool, seed: u64) -> Aig {
    let mut rng = seed;
    let mut secret = vec![false; n_in];
    for b in &mut secret {
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
        *b = (rng >> 63) != 0;
    }
    let mut aig = Aig::new();
    let xs = aig.new_inputs(n_in);
    {
        let mut lin = aig.begin_linear_region("HardSPN::LinearLayer");
        for _ in 0..rank_eqs {
            let mut cols = Vec::with_capacity(5);
            let mut lits = Vec::with_capacity(5);
            let mut rhs = false;
            for _ in 0..5 {
                rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                let idx = (rng >> 32) as usize % n_in;
                if !cols.contains(&idx) {
                    cols.push(idx);
                    lits.push(xs[idx]);
                    rhs ^= secret[idx];
                }
            }
            lin.assert_xor_parity(&lits, rhs);
        }
        lin.finish();
    }
    for g in 0..n_nl {
        let mut mk_lin = || {
            rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
            let a = (rng >> 32) as usize % n_in;
            rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
            let b = (rng >> 32) as usize % n_in;
            rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
            let c = (rng >> 32) as usize % n_in;
            (aig.xor3(xs[a], xs[b], xs[c]), secret[a] ^ secret[b] ^ secret[c])
        };
        let (la, va) = mk_lin();
        let (lb, vb) = mk_lin();
        let (lc, vc) = mk_lin();
        let (lit, mut val) = match g % 3 {
            0 => (aig.and(la, lb), va & vb),
            1 => (aig.maj3(la, lb, lc), (va & vb) | (va & vc) | (vb & vc)),
            _ => (aig.mux(la, lb, lc), if va { vb } else { vc }),
        };
        if flip_last_unsat && g + 1 == n_nl {
            val = !val;
        }
        aig.assert_true(if val { lit } else { lit.neg() });
    }
    aig
}

fn main() {
    let suite = Path::new("..");
    let cnf_dir = suite.join("cnf-version");
    fs::create_dir_all(&cnf_dir).expect("create cnf-version");
    let items = vec![
        ("spn_unsat_n48_d24", "UNSAT", build_spn(48, 24, 38, true, 0x7777_8888_9999_AAAA)),
        ("spn_sat_n64_d32", "SAT", build_spn(64, 32, 55, false, 0x1357_2468_ABCD_0064)),
        ("spn_sat_n96_d48", "SAT", build_spn(96, 48, 85, false, 0x1357_2468_ABCD_0096)),
        ("spn_sat_n128_d64", "SAT", build_spn(128, 64, 150, false, 0x1357_2468_ABCD_EF01 ^ 128 ^ (150 << 8))),
    ];
    for (name, ans, aig) in items {
        aig.write_aiger_binary(&suite.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={ans}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated {name}.aig + cnf-version/{name}.{{cnf,xcnf}}");
    }
}
