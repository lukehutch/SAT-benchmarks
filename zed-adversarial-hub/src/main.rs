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

fn main() {
    let suite = Path::new("..");
    let aig_dir = suite.join("aig-orig");
    let cnf_dir = suite.join("cnf-converted");
    let xcnf_dir = suite.join("xcnf-converted");
    fs::create_dir_all(&aig_dir).expect("create aig-orig");
    fs::create_dir_all(&cnf_dir).expect("create cnf-converted");
    fs::create_dir_all(&xcnf_dir).expect("create xcnf-converted");
    let items = vec![
        ("hub_20_unsat", "UNSAT", build_hub(20, false)),
        ("hub_24_unsat", "UNSAT", build_hub(24, false)),
        ("hub_30_unsat", "UNSAT", build_hub(30, false)),
        ("hub_60_unsat", "UNSAT", build_hub(60, false)),
        ("hub_80_unsat", "UNSAT", build_hub(80, false)),
        ("hub_60_sat", "SAT", build_hub(60, true)),
    ];
    for (name, ans, aig) in items {
        aig.write_aiger_binary(&aig_dir.join(format!("{name}.aig")), &format!("benchmark={name}\nexpected={ans}\norigin=AIG")).unwrap();
        aig.write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false).unwrap();
        aig.write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true).unwrap();
        println!("Generated aig-orig/{name}.aig + cnf-converted/{name}.cnf + xcnf-converted/{name}.xcnf");
    }
}
