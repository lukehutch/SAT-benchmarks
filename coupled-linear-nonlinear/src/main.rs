mod aig;

use aig::Aig;
use std::fs;
use std::path::Path;

fn build_coupled(n_in: usize, rank_eqs: usize, n_nl: usize, seed: u64, flip_last_nl: bool) -> Aig {
    let mut rng = seed;
    let mut secret = vec![false; n_in];
    for b in &mut secret {
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
        *b = (rng >> 63) != 0;
    }
    let mut aig = Aig::new();
    let xs = aig.new_inputs(n_in);
    {
        let mut lin = aig.begin_linear_region("Coupled::LinearLayer");
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
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
        let a = (rng >> 32) as usize % n_in;
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
        let b = (rng >> 32) as usize % n_in;
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
        let c = (rng >> 32) as usize % n_in;
        let (lit, mut val) = match g % 3 {
            0 => (aig.maj3(xs[a], xs[b], xs[c]), (secret[a] & secret[b]) | (secret[a] & secret[c]) | (secret[b] & secret[c])),
            1 => (aig.and(xs[a], xs[b]), secret[a] & secret[b]),
            _ => (aig.mux(xs[a], xs[b], xs[c]), if secret[a] { secret[b] } else { secret[c] }),
        };
        if flip_last_nl && g + 1 == n_nl {
            val = !val;
        }
        aig.assert_true(if val { lit } else { lit.neg() });
    }
    aig
}

fn main() {
    let suite = Path::new("..");
    let aig_dir = suite.join("aig-orig");
    let cnf_dir = suite.join("cnf-converted");
    let xcnf_dir = suite.join("xcnf-converted");
    fs::create_dir_all(&aig_dir).expect("create aig-orig");
    fs::create_dir_all(&cnf_dir).expect("create cnf-converted");
    fs::create_dir_all(&xcnf_dir).expect("create xcnf-converted");
    let items = vec![
        ("coupled_n128_d64", "SAT", build_coupled(128, 64, 96, 0xFEED_FACE_1111_2222 ^ 128 ^ (64 << 16), false)),
        ("coupled_n128_d32_unsat", "UNSAT", build_coupled(128, 96, 84, 0xCAFE_BABE_0003, true)),
        ("coupled_n256_d128", "SAT", build_coupled(256, 128, 180, 0xFEED_FACE_1111_2222 ^ 256 ^ (128 << 16), false)),
        ("coupled_n512_d128", "SAT", build_coupled(512, 384, 420, 0xFEED_FACE_1111_2222 ^ 512 ^ (384 << 16), false)),
    ];
    for (name, expected, aig) in items {
        aig.write_aiger_binary(&aig_dir.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={expected}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated aig-orig/{name}.aig + cnf-converted/{name}.cnf + xcnf-converted/{name}.xcnf ({expected})");
    }
}
