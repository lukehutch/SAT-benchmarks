mod aig;
mod bigint;
mod ntt;

use aig::{Aig, Lit, ParsedAiger};
use bigint::BigUint;
use ntt::{
    add_mod_f4, mul_const_mod_f4, mul_mod_f4, mul_ntt_f4, mul_pow2_mod_f4, sub_mod_f4,
    F4Word, NttFactoringCircuit, MOD_P, PRIM_ROOT, pow_mod_p,
};
use std::env;
use std::fs;
use std::path::Path;
use std::time::Instant;

struct BenchSpec {
    name: &'static str,
    expected: &'static str,
    n_dec: &'static str,
    p_dec: Option<&'static str>,
    q_dec: Option<&'static str>,
}

const SPECS: &[BenchSpec] = &[
    // 1. UNSAT 24-bit prime (2^24 - 3)
    BenchSpec {
        name: "ntt_prime_24b_unsat",
        expected: "UNSAT",
        n_dec: "16777213",
        p_dec: None,
        q_dec: None,
    },
    // 2-8. Synthetic balanced semiprimes (24b..256b)
    BenchSpec {
        name: "ntt_semiprime_24b",
        expected: "SAT",
        n_dec: "16744463",
        p_dec: Some("4091"),
        q_dec: Some("4093"),
    },
    BenchSpec {
        name: "ntt_semiprime_32b",
        expected: "SAT",
        n_dec: "4292870399",
        p_dec: Some("65519"),
        q_dec: Some("65521"),
    },
    BenchSpec {
        name: "ntt_semiprime_40b",
        expected: "SAT",
        n_dec: "1099503239183",
        p_dec: Some("1048571"),
        q_dec: Some("1048573"),
    },
    BenchSpec {
        name: "ntt_semiprime_48b",
        expected: "SAT",
        n_dec: "281474641166387",
        p_dec: Some("16777199"),
        q_dec: Some("16777213"),
    },
    BenchSpec {
        name: "ntt_semiprime_64b",
        expected: "SAT",
        n_dec: "18446743979220271189",
        p_dec: Some("4294967279"),
        q_dec: Some("4294967291"),
    },
    BenchSpec {
        name: "ntt_semiprime_128b",
        expected: "SAT",
        n_dec: "340282366920938460843936948965011886881",
        p_dec: Some("18446744073709551533"),
        q_dec: Some("18446744073709551557"),
    },
    BenchSpec {
        name: "ntt_semiprime_256b",
        expected: "SAT",
        n_dec: "115792089237316195423570985008687907740296238847888994169617214340566083464051",
        p_dec: Some("340282366920938463463374607431768211283"),
        q_dec: Some("340282366920938463463374607431768211297"),
    },
    // 9-17. Official RSA Challenge Moduli leading up to & beyond the 896-bit 2026 world record!
    BenchSpec {
        name: "rsa100_330b_ntt",
        expected: "SAT",
        n_dec: "1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139",
        p_dec: Some("37975227936943673922808872755445627854565536638199"),
        q_dec: Some("40094690950920881030683735292761468389214899724061"),
    },
    BenchSpec {
        name: "rsa155_512b_ntt",
        expected: "SAT",
        n_dec: "10941738641570527421809707322040357612003732945449205990913842131476349984288934784717997257891267332497625752899781833797076537244027146743531593354333897",
        p_dec: Some("102639592829741105772054196573991675900716567808038066803341933521790711307779"),
        q_dec: Some("106603488380168454820927220360012878679207958575989291522270608237193062808643"),
    },
    BenchSpec {
        name: "rsa200_663b_ntt",
        expected: "SAT",
        n_dec: "27997833911221327870829467638722601621070446786955428537560009929326128400107609345671052955360856061822351910951365788637105954482006576775098580557613579098734950144178863178946295187237869221823983",
        p_dec: Some("3532461934402770121272604978198464368671197400197625023649303468776121253679423200058547956528088349"),
        q_dec: Some("7925869954478333033347085841480059687737975857364219960734330341455767872818152135381409304740185467"),
    },
    BenchSpec {
        name: "rsa250_829b_ntt",
        expected: "SAT",
        n_dec: "2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589325976697471681738069364894699871578494975937497937",
        p_dec: Some("33372027594978156556226010605355114227940760344767554666784520987023841729210037080257448673296881877565718986258036932062711"),
        q_dec: Some("64135289477071580278790190170577389084825014742943447208116859632024532344630238623598752668347708737661925585694639798853367"),
    },
    BenchSpec {
        name: "rsa260_862b_ntt",
        expected: "SAT",
        n_dec: "22112825529529666435281085255026230927612089502470015394413748319128822941402001986512729726569746599085900330031400051170742204560859276357953757185954298838958709229238491006703034124620545784566413664540684214361293017694020846391065875914794251435144458199",
        p_dec: Some("4397328654844826923795068102505872571721883526553349659561256924505973939597593482272505698004801207988043088656411102133523080581"),
        q_dec: Some("5028695206842569864686141618253083416610081090075366674776775706538324961364412200138116378509733307971876652984898985905923678379"),
    },
    BenchSpec {
        name: "rsa270_895b_ntt",
        expected: "SAT",
        n_dec: "233108530344407544527637656910680524145619812480305449042948611968495918245135782867888369318577116418213919268572658314913060672626911354027609793166341626693946596196427744273886601876896313468704059066746903123910748277606548649151920812699309766587514735456594993207",
        p_dec: Some("359353359560835771039202980394651186700927320732604439802133630990767075387516847337701049401067297464438120309866365659527898117552867"),
        q_dec: Some("648688885584062714205875898360241359422565268898405718778199675963737815765312999868204516506259289963694375931123641015125668887749021"),
    },
    BenchSpec {
        name: "rsa896_896b_ntt",
        expected: "SAT",
        n_dec: "412023436986659543855531365332575948179811699844327982845455626433876445565248426198098870423161841879261420247188869492560931776375033421130982397485150944909106910269861031862704114880866970564902903653658867433731720813104105190864254793282601391257624033946373269391",
        p_dec: Some("636606729769440499166579950236036751749912014371509557713570027508971809534551913252252094954941974952859310861988904737359709200557919"),
        q_dec: Some("647218161102195448058768698177623951380616936266986989243011933572862870905830904361851542450154852431416136790787107595965374752513489"),
    },
    BenchSpec {
        name: "rsa280_928b_ntt",
        expected: "SAT",
        n_dec: "1790707753365795418841729699379193276395981524363782327873718589639655966058578374254964039644910359346857311359948708984278578450069871685344678652553655035251602806563637363071753327728754995053415389279785107516999221971781597724733184279534477239566789173532366357270583106789",
        p_dec: None,
        q_dec: None,
    },
    BenchSpec {
        name: "rsa1024_1024b_ntt",
        expected: "SAT",
        n_dec: "135066410865995223349603216278805969938881475605667027524485143851526510604859533833940287150571909441798207282164471551373680419703964191743046496589274256239341020864383202110372958725762358509643110564073501508187510676594629205563685529475213500852879416377328533906109750544334999811150056977236890927563",
        p_dec: None,
        q_dec: None,
    },
];

fn eval_word(vals: &[bool], w: &F4Word) -> u32 {
    let mut acc = 0u32;
    for i in 0..17 {
        let b = vals[w[i].var() as usize] ^ w[i].is_neg();
        if b {
            acc |= 1u32 << i;
        }
    }
    acc
}

fn self_test_f4_primitives() {
    let mut aig = Aig::new();
    let mut a = [Lit::FALSE; 17];
    let mut b = [Lit::FALSE; 17];
    for i in 0..17 { a[i] = aig.new_input(); }
    for i in 0..17 { b[i] = aig.new_input(); }

    let sum = add_mod_f4(&mut aig, &a, &b);
    let diff = sub_mod_f4(&mut aig, &a, &b);
    let prod = mul_mod_f4(&mut aig, &a, &b);
    let p2_7 = mul_pow2_mod_f4(&mut aig, &a, 7);
    let p2_16 = mul_pow2_mod_f4(&mut aig, &a, 16);
    let p2_24 = mul_pow2_mod_f4(&mut aig, &a, 24);
    let w256 = pow_mod_p(PRIM_ROOT as u64, ((MOD_P - 1) / 256) as u64);
    let c1 = pow_mod_p(w256 as u64, 1);
    let c2 = pow_mod_p(w256 as u64, 37);
    let c3 = pow_mod_p(w256 as u64, 127);
    let mc1 = mul_const_mod_f4(&mut aig, &a, c1);
    let mc2 = mul_const_mod_f4(&mut aig, &a, c2);
    let mc3 = mul_const_mod_f4(&mut aig, &a, c3);

    let edges: &[u32] = &[0, 1, 2, 15, 16, 255, 256, 32767, 32768, 65535, 65536];
    let mut rng = 0x1234_5678_9ABC_DEF0_u64;
    let mut pairs = Vec::new();
    for &x in edges {
        for &y in edges {
            pairs.push((x, y));
        }
    }
    for _ in 0..200 {
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        let x = ((rng >> 16) as u32) % MOD_P;
        rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        let y = ((rng >> 16) as u32) % MOD_P;
        pairs.push((x, y));
    }

    for (x, y) in pairs {
        let mut ins = vec![false; 34];
        for i in 0..17 {
            ins[i] = ((x >> i) & 1) != 0;
            ins[17 + i] = ((y >> i) & 1) != 0;
        }
        let vals = aig.eval_all(&ins);
        assert_eq!(eval_word(&vals, &sum), (x + y) % MOD_P, "add_mod_f4({x}, {y})");
        assert_eq!(eval_word(&vals, &diff), (x + MOD_P - y) % MOD_P, "sub_mod_f4({x}, {y})");
        assert_eq!(eval_word(&vals, &prod), (((x as u64) * (y as u64)) % (MOD_P as u64)) as u32, "mul_mod_f4({x}, {y})");
        assert_eq!(eval_word(&vals, &p2_7), (((x as u64) * (1u64 << 7)) % (MOD_P as u64)) as u32, "mul_pow2(7)({x})");
        assert_eq!(eval_word(&vals, &p2_16), (((x as u64) * 65536) % (MOD_P as u64)) as u32, "mul_pow2(16)({x})");
        assert_eq!(eval_word(&vals, &p2_24), (((x as u64) * (pow_mod_p(2, 24) as u64)) % (MOD_P as u64)) as u32, "mul_pow2(24)({x})");
        assert_eq!(eval_word(&vals, &mc1), (((x as u64) * (c1 as u64)) % (MOD_P as u64)) as u32, "mul_const({c1})({x})");
        assert_eq!(eval_word(&vals, &mc2), (((x as u64) * (c2 as u64)) % (MOD_P as u64)) as u32, "mul_const({c2})({x})");
        assert_eq!(eval_word(&vals, &mc3), (((x as u64) * (c3 as u64)) % (MOD_P as u64)) as u32, "mul_const({c3})({x})");
    }

    // End-to-end 36-bit x 40-bit NTT multiplier check
    let mut maig = Aig::new();
    let pbits = maig.new_inputs(36);
    let qbits = maig.new_inputs(40);
    let (pout, _, _, _) = mul_ntt_f4(&mut maig, &pbits, &qbits);
    for (pv, qv) in [(0u64, 0u64), (1, 1), ((1u64 << 36) - 1, (1u64 << 40) - 1), (0xBC_DEF0_123, 0x9876_5432_1F)] {
        let mut ins = vec![false; 76];
        for i in 0..36 { ins[i] = ((pv >> i) & 1) != 0; }
        for i in 0..40 { ins[36 + i] = ((qv >> i) & 1) != 0; }
        let vals = maig.eval_all(&ins);
        let mut got = 0u128;
        for (i, &l) in pout.iter().enumerate() {
            if vals[l.var() as usize] ^ l.is_neg() {
                got |= 1u128 << i;
            }
        }
        assert_eq!(got, (pv as u128) * (qv as u128), "mul_ntt_f4({pv}, {qv})");
    }
    println!("[SELF-TEST OK] F_65537 primitives (add/sub/pow2/const/mul) + full NTT convolution verified 100% exact.");
}

fn run_wallace_compare() {
    println!("=== EXACT EMPIRICAL GATE SCALING: O(n log n) F_65537 NTT vs. O(n^2) WALLACE ===");
    println!("{:<22} {:>5} {:>4} {:>4} {:>4} {:>10} {:>10} {:>8}", "Instance/Width", "Bits", "bp", "bq", "L", "NTT_ANDs", "Wal_ANDs", "Ratio");
    for spec in SPECS {
        let n = BigUint::from_dec(spec.n_dec);
        let c_ntt = NttFactoringCircuit::build(&n, false);
        let c_wal = NttFactoringCircuit::build(&n, true);
        let n_ands = c_ntt.aig.aiger_and_count();
        let w_ands = c_wal.aig.aiger_and_count();
        let ratio = (n_ands as f64) / (w_ands as f64);
        println!(
            "{:<22} {:>5} {:>4} {:>4} {:>4} {:>10} {:>10} {:>7.3}x",
            spec.name, c_ntt.bit_width, c_ntt.bp, c_ntt.bq, c_ntt.l, n_ands, w_ands, ratio
        );
    }
    // Also probe additional bit widths around crossover (e.g. 768, 960, 1024, 1152, 1280, 1536, 2048)
    println!("\n--- Extended Crossover Sweep (synthetic odd targets, bp=B/2, bq=min(bp+4,516)) ---");
    for &bits in &[700usize, 768, 896, 928, 932, 934, 936, 940, 960, 1000, 1024] {
        let mut n = BigUint::from_u64(1);
        n.set_bit(bits - 1, true);
        n.set_bit(0, true);
        let c_ntt = NttFactoringCircuit::build(&n, false);
        let c_wal = NttFactoringCircuit::build(&n, true);
        let n_ands = c_ntt.aig.aiger_and_count();
        let w_ands = c_wal.aig.aiger_and_count();
        println!(
            "width_{:<16} {:>5} {:>4} {:>4} {:>4} {:>10} {:>10} {:>7.3}x",
            bits, bits, c_ntt.bp, c_ntt.bq, c_ntt.l, n_ands, w_ands, (n_ands as f64) / (w_ands as f64)
        );
    }
}

fn dump_wallace_small(out_dir: &Path) {
    fs::create_dir_all(out_dir).expect("create wallace tmp dir");
    for spec in SPECS.iter().take(5) {
        let n = BigUint::from_dec(spec.n_dec);
        let c_wal = NttFactoringCircuit::build(&n, true);
        let p = out_dir.join(format!("{}_wallace.cnf", spec.name));
        let (nv, nc) = c_wal.aig.write_dimacs(&p, false).expect("write wallace cnf");
        println!("Wrote {} (vars={}, clauses={}, ANDs={})", p.display(), nv, nc, c_wal.aig.aiger_and_count());
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    self_test_f4_primitives();

    if args.iter().any(|a| a == "--wallace-compare") {
        run_wallace_compare();
        return;
    }
    if let Some(pos) = args.iter().position(|a| a == "--dump-wallace") {
        let dir = Path::new(&args[pos + 1]);
        dump_wallace_small(dir);
        return;
    }

    let suite = Path::new("..");
    let aig_dir = suite.join("aig-orig");
    let cnf_dir = suite.join("cnf-converted");
    let xcnf_dir = suite.join("xcnf-converted");
    fs::create_dir_all(&aig_dir).expect("create aig-orig");
    fs::create_dir_all(&cnf_dir).expect("create cnf-converted");
    fs::create_dir_all(&xcnf_dir).expect("create xcnf-converted");

    println!(
        "{:<22} {:>4} {:>4} {:>4} {:>4} {:>10} {:>9} {:>10} {:>10} {:>6} {:>6}",
        "Instance", "B", "bp", "bq", "L", "AIG_ANDs", "CNF_Vars", "CNF_Cls", "XCNF_Cls", "Ans", "Sim"
    );

    for spec in SPECS {
        let t0 = Instant::now();
        let n = BigUint::from_dec(spec.n_dec);

        // Step 1: Mathematical number-theoretic verification of every modulus & factor pair
        match (spec.p_dec, spec.q_dec) {
            (Some(ps), Some(qs)) => {
                let p = BigUint::from_dec(ps);
                let q = BigUint::from_dec(qs);
                assert_eq!(p.mul(&q), n, "MATH FAIL: p * q != N for {}", spec.name);
                assert!(p < q, "MATH FAIL: p >= q for {}", spec.name);
                assert!(p.is_probable_prime(), "MATH FAIL: p not prime for {}", spec.name);
                assert!(q.is_probable_prime(), "MATH FAIL: q not prime for {}", spec.name);
            }
            (None, None) => {
                if spec.expected == "UNSAT" {
                    assert!(n.is_probable_prime(), "MATH FAIL: UNSAT target {} not prime", spec.name);
                } else {
                    assert!(!n.is_probable_prime(), "MATH FAIL: unfactored RSA {} is prime?!", spec.name);
                }
            }
            _ => unreachable!(),
        }

        // Step 2: Build exact F_65537 NTT factoring circuit & export AIGER + CNF + XCNF
        let circ = NttFactoringCircuit::build(&n, false);
        let aig_path = aig_dir.join(format!("{}.aig", spec.name));
        let cnf_path = cnf_dir.join(format!("{}.cnf", spec.name));
        let xcnf_path = xcnf_dir.join(format!("{}.xcnf", spec.name));

        let comment = format!(
            "benchmark={}\nexpected={}\norigin=AIG\nmultiplier=F_65537_NTT\nbits={}\nbp={}\nbq={}\nL={}",
            spec.name, spec.expected, circ.bit_width, circ.bp, circ.bq, circ.l
        );
        let (ni, n_ands) = circ.aig.write_aiger_binary(&aig_path, &comment).expect("write aig");
        let (cnf_v, cnf_c) = circ.aig.write_dimacs(&cnf_path, false).expect("write cnf");
        let (_xcnf_v, xcnf_c) = circ.aig.write_dimacs(&xcnf_path, true).expect("write xcnf");

        // Step 3: Zero-Trust on-disk Binary AIGER 1.9 simulation!
        let parsed = ParsedAiger::read_file(&aig_path).expect("parse written aig");
        assert_eq!(parsed.num_inputs, ni);
        assert_eq!(parsed.ands.len(), n_ands);
        let sim_status = if let (Some(ps), Some(qs)) = (spec.p_dec, spec.q_dec) {
            let p = BigUint::from_dec(ps);
            let q = BigUint::from_dec(qs);
            let w_true = circ.encode_witness(&p, &q);
            assert!(parsed.eval(&w_true), "AIG SIM FAIL: true witness (p,q) evaluated to 0 on {}!", spec.name);

            // Perturb p (flip bit 1, i.e., p ^ 2) -> MUST evaluate to 0
            let mut p_bad = p.clone();
            p_bad.set_bit(1, !p.bit(1));
            let w_pbad = circ.encode_witness(&p_bad, &q);
            assert!(!parsed.eval(&w_pbad), "AIG SIM FAIL: perturbed (p^2, q) evaluated to 1 on {}!", spec.name);

            // Perturb q (flip bit 1, i.e., q ^ 2) -> MUST evaluate to 0
            let mut q_bad = q.clone();
            q_bad.set_bit(1, !q.bit(1));
            let w_qbad = circ.encode_witness(&p, &q_bad);
            assert!(!parsed.eval(&w_qbad), "AIG SIM FAIL: perturbed (p, q^2) evaluated to 1 on {}!", spec.name);
            "1/0/0"
        } else {
            // Sanity check on UNSAT / unfactored RSA: trivial (3, 5) must evaluate to 0
            let w_neg = circ.encode_witness(&BigUint::from_u64(3), &BigUint::from_u64(5));
            assert!(!parsed.eval(&w_neg), "AIG SIM FAIL: (3,5) evaluated to 1 on {}!", spec.name);
            "neg=0"
        };

        println!(
            "{:<22} {:>4} {:>4} {:>4} {:>4} {:>10} {:>9} {:>10} {:>10} {:>6} {:>6} ({:.2}s)",
            spec.name,
            circ.bit_width,
            circ.bp,
            circ.bq,
            circ.l,
            n_ands,
            cnf_v,
            cnf_c,
            xcnf_c,
            spec.expected,
            sim_status,
            t0.elapsed().as_secs_f64()
        );
    }
}
