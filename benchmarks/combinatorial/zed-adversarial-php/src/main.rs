mod aig;

use aig::{Aig, Lit};
use std::fs;
use std::path::Path;

fn build_php_direct(pigeons: usize, holes: usize) -> Aig {
    let mut aig = Aig::new();
    let vars: Vec<Vec<Lit>> = (0..pigeons).map(|_| aig.new_inputs(holes)).collect();
    for i in 0..pigeons {
        let mut or_l = Lit::FALSE;
        for j in 0..holes {
            or_l = aig.or(or_l, vars[i][j]);
        }
        aig.assert_true(or_l);
    }
    for j in 0..holes {
        for i1 in 0..pigeons {
            for i2 in (i1 + 1)..pigeons {
                let both = aig.and(vars[i1][j], vars[i2][j]);
                aig.assert_true(both.neg());
            }
        }
    }
    aig
}
fn build_zed_php(pigeons: usize, holes: usize) -> Aig {
    let mut g = Aig::new();
    let x = g.new_inputs(pigeons * holes);
    for p in 0..pigeons {
        let mut o = Lit::FALSE;
        for h in 0..holes {
            o = g.or(o, x[p * holes + h]);
        }
        g.assert_true(o);
    }
    for h in 0..holes {
        for p in 0..pigeons {
            for q in p + 1..pigeons {
                let o = g.or(Lit::FALSE, x[p * holes + h].neg());
                let o = g.or(o, x[q * holes + h].neg());
                g.assert_true(o);
            }
        }
    }
    g
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
        ("php_9_8_unsat", "UNSAT", build_php_direct(9, 8)),
        ("php_13_12_unsat", "UNSAT", build_zed_php(13, 12)),
        ("php_14_13_unsat", "UNSAT", build_zed_php(14, 13)),
        ("php_15_14_unsat", "UNSAT", build_zed_php(15, 14)),
        ("php_16_15_unsat", "UNSAT", build_zed_php(16, 15)),
        ("php_17_16_unsat", "UNSAT", build_zed_php(17, 16)),
        ("php_19_18_unsat", "UNSAT", build_zed_php(19, 18)),
        ("php_20_19_unsat", "UNSAT", build_zed_php(20, 19)),
        ("php_31_30_unsat", "UNSAT", build_zed_php(31, 30)),
        ("php_50_49_unsat", "UNSAT", build_zed_php(50, 49)),
        ("php_20_20_sat", "SAT", build_zed_php(20, 20)),
        ("php_30_30_sat", "SAT", build_zed_php(30, 30)),
    ];
    for (name, ans, aig) in items {
        aig.write_aiger_binary(&aig_dir.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={ans}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated aig-orig/{name}.aig + cnf-converted/{name}.cnf + xcnf-converted/{name}.xcnf");
    }
}
