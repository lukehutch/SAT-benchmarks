mod aig;
mod counterexamples;

use std::fs;
use std::path::Path;

fn main() {
    let suite = Path::new("..");
    let cnf_dir = suite.join("cnf-version");
    fs::create_dir_all(&cnf_dir).expect("create cnf-version");
    let items = vec![
        ("tseitin_exp_n60", counterexamples::build_tseitin_expander(60, 777)),
        ("tseitin_exp_n120", counterexamples::build_tseitin_expander(120, 778)),
        ("tseitin_exp_n300", counterexamples::build_tseitin_expander(300, 779)),
        ("tseitin_prism_n400", counterexamples::build_tseitin_prism(200)),
    ];
    for (name, aig) in items {
        aig.write_aiger_binary(&suite.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected=UNSAT\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated {name}.aig + cnf-version/{name}.{{cnf,xcnf}}");
    }
}
