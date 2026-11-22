mod dimacs;
mod hamd;

use std::fs::{self, File};
use std::io::BufWriter;
use std::path::Path;

fn main() {
    let suite_dir = Path::new("..");
    let aig_dir = suite_dir.join("aig-version");
    fs::create_dir_all(&aig_dir).expect("create aig-version");
    for g in hamd::standard_hamd_benchmark_suite() {
        let enc = g.encode_cnf();
        let cnf_path = suite_dir.join(format!("{}.cnf", g.name));
        let aig_path = aig_dir.join(format!("{}.aig", g.name));
        let f = File::create(&cnf_path).expect("create cnf");
        enc.formula.write_dimacs(BufWriter::new(f)).expect("write cnf");
        let ans = if g.expect_sat { "SAT" } else { "UNSAT" };
        let comment = format!("benchmark={}\nfamily={}\nN={}\nexpected={ans}\norigin=CNF", g.name, g.family, g.num_vertices);
        enc.formula.write_aiger_binary(&aig_path, &comment).expect("write aig");
        println!("Generated {}.cnf & aig-version/{}.aig", g.name, g.name);
    }
}
