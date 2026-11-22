mod aig;
mod factoring;

use aig::{Aig, Lit};
use factoring::{FactoringInstance, MultTopology};
use std::fs;
use std::path::Path;

fn build_masked_mult_32b_xor16() -> Aig {
    let p32 = 65519u128;
    let q32 = 65521u128;
    let mut inst = FactoringInstance::build(p32 * q32, MultTopology::Wallace, true);
    let mut all_bits: Vec<(Lit, bool)> = Vec::new();
    for (k, &idx) in inst.p_input_indices.iter().enumerate() {
        all_bits.push((Lit::from_var(inst.aig.input_vars[idx], false), ((p32 >> (k + 1)) & 1) != 0));
    }
    for (k, &idx) in inst.q_input_indices.iter().enumerate() {
        all_bits.push((Lit::from_var(inst.aig.input_vars[idx], false), ((q32 >> (k + 1)) & 1) != 0));
    }
    let mut rng = 0x55AA_33CC_1122_3344_u64;
    {
        let mut lin = inst.aig.begin_linear_region("MaskedMult::XorLeaks");
        for _ in 0..16 {
            let mut lits = Vec::new();
            let mut par = false;
            for _ in 0..4 {
                rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                let idx = (rng >> 32) as usize % all_bits.len();
                lits.push(all_bits[idx].0);
                par ^= all_bits[idx].1;
            }
            lin.assert_xor_parity(&lits, par);
        }
        lin.finish();
    }
    inst.aig
}

fn main() {
    let suite = Path::new("..");
    let cnf_dir = suite.join("cnf-version");
    fs::create_dir_all(&cnf_dir).expect("create cnf-version");
    let items = vec![
        ("factor_prime_28b_unsat", "UNSAT", FactoringInstance::build(268_435_399u128, MultTopology::Wallace, true).aig),
        ("factor_wallace_32b", "SAT", FactoringInstance::build(65519u128 * 65521u128, MultTopology::Wallace, true).aig),
        ("factor_wallace_36b", "SAT", FactoringInstance::build(262133u128 * 262139u128, MultTopology::Wallace, true).aig),
        ("factor_karatsuba_36b", "SAT", FactoringInstance::build(262133u128 * 262139u128, MultTopology::Karatsuba, true).aig),
        ("factor_wallace_40b", "SAT", FactoringInstance::build(960017u128 * 1048573u128, MultTopology::Wallace, true).aig),
        ("masked_mult_32b_xor16", "SAT", build_masked_mult_32b_xor16()),
    ];
    for (name, ans, aig) in items {
        aig.write_aiger_binary(&suite.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={ans}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated {name}.aig + cnf-version/{name}.{{cnf,xcnf}}");
    }
}
