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

    let mut blk = pad_single_block(b"SAT-Benchmarks-SHA256-64R-Nonce-Scaling-v1");
    blk[0] = 0x9E37_79B9u32;
    let digest = sha256_compress_rounds(&blk, 64, true);

    print!("Target digest (64R FIPS 180-4, W[0]=0x{:08x}): ", blk[0]);
    for w in &digest {
        print!("{:08x}", w);
    }
    println!();

    for k in 1..=32usize {
        let name = format!("sha256_64r_k{:02}", k);
        let free: Vec<usize> = (0..k).collect();
        let inst = Sha256PreimageInstance::build(64, true, blk, &free, digest);

        // Self-verify witness decoding against exact FIPS 180-4 compression.
        let expected_inputs: Vec<bool> = (0..k).map(|bi| ((blk[0] >> bi) & 1) != 0).collect();
        let decoded = inst.decode_block(&expected_inputs);
        assert_eq!(decoded, blk, "decoded block mismatch for {name}");
        assert_eq!(
            sha256_compress_rounds(&decoded, 64, true),
            digest,
            "FIPS 180-4 digest verification failed for {name}"
        );

        inst.aig
            .write_aiger_binary(
                &aig_dir.join(format!("{name}.aig")),
                &format!("benchmark={name}\nexpected=SAT\norigin=AIG\nnonce_w0=0x9e3779b9\nfree_bits={k}"),
            )
            .unwrap();
        inst.aig
            .write_dimacs(&cnf_dir.join(format!("{name}.cnf")), false)
            .unwrap();
        inst.aig
            .write_dimacs(&xcnf_dir.join(format!("{name}.xcnf")), true)
            .unwrap();
        println!(
            "Generated {name}: inputs={}, gates={}",
            inst.aig.num_inputs,
            inst.aig.gates.len()
        );
    }
}
