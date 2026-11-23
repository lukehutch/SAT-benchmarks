mod aig;
mod sha256;

use sha256::{pad_single_block, sha256_compress_rounds, Sha256PreimageInstance};
use std::fs;
use std::path::Path;

fn main() {
    let suite = Path::new("..");
    let aig_dir = suite.join("aig-orig");
    let cnf_dir = suite.join("cnf-converted");
    let xcnf_dir = suite.join("xcnf-converted");
    fs::create_dir_all(&aig_dir).expect("create aig-orig");
    fs::create_dir_all(&cnf_dir).expect("create cnf-converted");
    fs::create_dir_all(&xcnf_dir).expect("create xcnf-converted");
    let blk_abc = pad_single_block(b"abc");
    let d16 = sha256_compress_rounds(&blk_abc, 16, false);
    let free32: Vec<usize> = (0..32).collect();
    let d17 = sha256_compress_rounds(&blk_abc, 17, false);
    let free16: Vec<usize> = (0..16).collect();
    let d64 = sha256_compress_rounds(&blk_abc, 64, true);
    let mut d64_bad = d64;
    d64_bad[0] ^= 1;
    let free20: Vec<usize> = (0..20).collect();

    let items = vec![
        ("sha256_16r_k32", "SAT", Sha256PreimageInstance::build(16, false, blk_abc, &free32, d16).aig),
        ("sha256_17r_k16", "SAT", Sha256PreimageInstance::build(17, false, blk_abc, &free16, d17).aig),
        ("sha256_64r_k16_sat", "SAT", Sha256PreimageInstance::build(64, true, blk_abc, &free16, d64).aig),
        ("sha256_64r_k16_unsat", "UNSAT", Sha256PreimageInstance::build(64, true, blk_abc, &free16, d64_bad).aig),
        ("sha256_64r_k20_sat", "SAT", Sha256PreimageInstance::build(64, true, blk_abc, &free20, d64).aig),
    ];
    for (name, ans, aig) in items {
        aig.write_aiger_binary(&aig_dir.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={ans}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated aig-orig/{name}.aig + cnf-converted/{name}.cnf + xcnf-converted/{name}.xcnf");
    }
}
