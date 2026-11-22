mod aig;

use aig::{Aig, Lit};
use std::fs;
use std::path::Path;

type W = Vec<Lit>;

fn konst(c: i64, w: usize) -> W {
    (0..w).map(|i| Aig::const_lit((c >> i.min(63)) & 1 == 1)).collect()
}
fn add(g: &mut Aig, a: &W, b: &W) -> W {
    let mut carry = Lit::FALSE;
    let mut out = Vec::with_capacity(a.len());
    for i in 0..a.len() {
        let (s, c) = g.full_adder(a[i], b[i], carry);
        out.push(s);
        carry = c;
    }
    out
}
fn neg(g: &mut Aig, a: &W) -> W {
    let n: W = a.iter().map(|l| l.neg()).collect();
    add(g, &n, &konst(1, a.len()))
}
fn mulc(g: &mut Aig, a: &W, c: i64) -> W {
    if c < 0 {
        let p = mulc(g, a, -c);
        return neg(g, &p);
    }
    let w = a.len();
    let mut r = konst(0, w);
    for k in 0..63 {
        if (c >> k) & 1 == 1 {
            let sh: W = (0..w).map(|i| if i >= k { a[i - k] } else { Lit::FALSE }).collect();
            r = add(g, &r, &sh);
        }
    }
    r
}
fn lin(g: &mut Aig, terms: &[(i64, &W)], k: i64, w: usize) -> W {
    let mut r = konst(k, w);
    for (c, v) in terms {
        let p = mulc(g, v, *c);
        r = add(g, &r, &p);
    }
    r
}
fn ge0(v: &W) -> Lit {
    v[v.len() - 1].neg()
}
fn var(g: &mut Aig, lo: i64, hi: i64, w: usize) -> W {
    let x = g.new_inputs(w);
    let a = lin(g, &[(1, &x)], -lo, w);
    let b = lin(g, &[(-1, &x)], hi, w);
    g.assert_true(ge0(&a));
    g.assert_true(ge0(&b));
    x
}
fn build_hub(n: usize, sat: bool) -> Aig {
    let mut g = Aig::new();
    let low = if sat { 25 } else { 31 };
    let wd = 10;
    let h = var(&mut g, low, 63, wd);
    for i in 0..n {
        let x = var(&mut g, 20, 63, wd);
        let y = var(&mut g, 0, 40, wd);
        let p = lin(&mut g, &[(-1, &x), (-2, &h)], 40 + (i % 7) as i64, wd);
        let r = lin(&mut g, &[(1, &y), (-1, &h)], -10 + (i % 5) as i64, wd);
        let o = g.or(ge0(&p), ge0(&r));
        g.assert_true(o);
    }
    g
}
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
    let cnf_dir = suite.join("cnf-version");
    fs::create_dir_all(&cnf_dir).expect("create cnf-version");
    let items = vec![
        ("hub_20_unsat", "UNSAT", build_hub(20, false)),
        ("hub_24_unsat", "UNSAT", build_hub(24, false)),
        ("hub_30_unsat", "UNSAT", build_hub(30, false)),
        ("hub_60_unsat", "UNSAT", build_hub(60, false)),
        ("hub_80_unsat", "UNSAT", build_hub(80, false)),
        ("hub_60_sat", "SAT", build_hub(60, true)),
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
        aig.write_aiger_binary(&suite.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={ans}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated {name}.aig + cnf-version/{name}.{{cnf,xcnf}}");
    }
}
