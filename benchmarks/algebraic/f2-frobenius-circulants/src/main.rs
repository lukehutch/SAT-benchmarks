mod aig;
mod counterexamples;

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
    for &(k, name) in &[
        (6usize, "f2_frobenius_n64"),
        (8, "f2_frobenius_n256"),
        (10, "f2_frobenius_n1024"),
        (12, "f2_frobenius_n4096"),
    ] {
        let (aig, _) = counterexamples::build_frobenius_circulant(k, 12345 + k as u64);
        aig.write_aiger_binary(&aig_dir.join(format!("{name}.aig")), &format!("benchmark={name}\nk={k}\nexpected=SAT\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated aig-orig/{name}.aig + cnf-converted/{name}.cnf + xcnf-converted/{name}.xcnf");
    }
    for &(k, name) in &[
        (8usize, "f2_frobenius_n256_unsat"),
        (10, "f2_frobenius_n1024_unsat"),
    ] {
        let aig = counterexamples::build_frobenius_circulant_unsat(k, 22345 + k as u64);
        aig.write_aiger_binary(&aig_dir.join(format!("{name}.aig")), &format!("benchmark={name}\nk={k}\nexpected=UNSAT\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated aig-orig/{name}.aig + cnf-converted/{name}.cnf + xcnf-converted/{name}.xcnf");
    }
}
