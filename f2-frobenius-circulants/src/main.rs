mod aig;
mod counterexamples;

use std::fs;
use std::path::Path;

fn main() {
    let suite = Path::new("..");
    let cnf_dir = suite.join("cnf-version");
    fs::create_dir_all(&cnf_dir).expect("create cnf-version");
    for &(k, name) in &[
        (6usize, "f2_frobenius_n64"),
        (8, "f2_frobenius_n256"),
        (10, "f2_frobenius_n1024"),
        (12, "f2_frobenius_n4096"),
    ] {
        let (aig, _) = counterexamples::build_frobenius_circulant(k, 12345 + k as u64);
        aig.write_aiger_binary(&suite.join(format!("{name}.aig")), &format!("benchmark={name}\nk={k}\nexpected=SAT\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated {name}.aig + cnf-version/{name}.{{cnf,xcnf}}");
    }
}
