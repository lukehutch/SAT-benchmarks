//! `sat-bench-tools`: zero-dependency compiled accelerator for
//! `SAT-benchmarks/src/to_anf.py` and `SAT-benchmarks/src/analyze_benchmarks.py`.
//!
//! Subcommands:
//!   sat-bench-tools aig-to-anf <in.aig[.xz|.gz|.bz2]> <out.anf[.xz|.gz|.bz2]> [--verify] [--preset N]
//!       Binary AIGER 1.9 -> DIMACS-ANF (degree <= 2), byte-for-byte identical to the
//!       pure-Python `convert_aiger_to_anf`, plus an independent re-read of the written
//!       file and a 64-lane bit-parallel (`u64`) forward-equivalence check.
//!   sat-bench-tools analyze-cnf <in.cnf[.xz|.gz|.bz2]>
//!       Single streaming byte pass over DIMACS CNF; prints the JSON structural /
//!       phase-transition metrics of `analyze_benchmarks.analyze_cnf` with the exact
//!       same floating-point operation order (Counter insertion order for rho/kappa,
//!       CPython >= 3.12 Neumaier `sum()` for the degree variance).
//!
//! Compressed I/O is delegated to the system `xz` / `gzip` / `bzip2` binaries via pipes.

use std::fs::{self, File};
use std::io::{self, BufWriter, Read, Write};
use std::path::Path;
use std::process::{Child, Command, Stdio};
use std::time::Instant;

type Res<T> = Result<T, String>;

const USAGE: &str = "usage:
  sat-bench-tools aig-to-anf <in.aig[.xz]> <out.anf[.xz]> [--verify] [--preset N]
  sat-bench-tools analyze-cnf <in.cnf[.xz]>";

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let r = match args.get(1).map(String::as_str) {
        Some("aig-to-anf") => cmd_aig_to_anf(&args[2..]),
        Some("analyze-cnf") => cmd_analyze_cnf(&args[2..]),
        Some("-h") | Some("--help") => {
            println!("{USAGE}");
            Ok(())
        }
        Some(other) => Err(format!("unknown subcommand `{other}`\n{USAGE}")),
        None => Err(USAGE.to_string()),
    };
    if let Err(e) = r {
        eprintln!("sat-bench-tools: error: {e}");
        std::process::exit(1);
    }
}

// ============================================================================
// Transparent compressed I/O (via system xz / gzip / bzip2 pipes)
// ============================================================================

fn sniff_compression(path: &str) -> Res<Option<&'static str>> {
    let mut f = File::open(path).map_err(|e| format!("{path}: {e}"))?;
    let mut head = [0u8; 6];
    let mut n = 0;
    while n < head.len() {
        match f.read(&mut head[n..]) {
            Ok(0) => break,
            Ok(k) => n += k,
            Err(e) => return Err(format!("{path}: {e}")),
        }
    }
    let h = &head[..n];
    Ok(if h.starts_with(b"\xfd7zXZ\x00") {
        Some("xz")
    } else if h.starts_with(b"\x1f\x8b") {
        Some("gzip")
    } else if h.starts_with(b"BZh") {
        Some("bzip2")
    } else {
        None
    })
}

struct Input {
    reader: Box<dyn Read>,
    child: Option<(Child, &'static str)>,
}

impl Input {
    fn open(path: &str) -> Res<Input> {
        match sniff_compression(path)? {
            Some(tool) => {
                let mut child = Command::new(tool)
                    .arg("-dc")
                    .arg(path)
                    .stdin(Stdio::null())
                    .stdout(Stdio::piped())
                    .spawn()
                    .map_err(|e| format!("failed to spawn `{tool} -dc {path}`: {e}"))?;
                let out = child
                    .stdout
                    .take()
                    .ok_or_else(|| format!("no stdout pipe from `{tool}`"))?;
                Ok(Input { reader: Box::new(out), child: Some((child, tool)) })
            }
            None => {
                let f = File::open(path).map_err(|e| format!("{path}: {e}"))?;
                Ok(Input { reader: Box::new(f), child: None })
            }
        }
    }

    fn finish(self) -> Res<()> {
        drop(self.reader);
        if let Some((mut child, tool)) = self.child {
            let st = child.wait().map_err(|e| format!("`{tool}` wait failed: {e}"))?;
            if !st.success() {
                return Err(format!("`{tool} -dc` exited with {st}"));
            }
        }
        Ok(())
    }
}

fn read_all(path: &str) -> Res<Vec<u8>> {
    let mut inp = Input::open(path)?;
    let mut buf = Vec::new();
    inp.reader.read_to_end(&mut buf).map_err(|e| format!("{path}: {e}"))?;
    inp.finish()?;
    Ok(buf)
}

fn write_output(path: &str, chunks: &[&[u8]], xz_preset: u32) -> Res<()> {
    if let Some(parent) = Path::new(path).parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent).map_err(|e| format!("{}: {e}", parent.display()))?;
        }
    }
    let low = path.to_ascii_lowercase();
    let comp: Option<(&str, Vec<String>)> = if low.ends_with(".xz") {
        Some(("xz", vec![format!("-{xz_preset}"), "-T1".into(), "-c".into()]))
    } else if low.ends_with(".gz") {
        Some(("gzip", vec!["-6".into(), "-c".into()]))
    } else if low.ends_with(".bz2") {
        Some(("bzip2", vec!["-6".into(), "-c".into()]))
    } else {
        None
    };
    let file = File::create(path).map_err(|e| format!("{path}: {e}"))?;
    match comp {
        None => {
            let mut w = BufWriter::with_capacity(1 << 20, file);
            for c in chunks {
                w.write_all(c).map_err(|e| format!("{path}: {e}"))?;
            }
            w.flush().map_err(|e| format!("{path}: {e}"))?;
        }
        Some((tool, args)) => {
            let mut child = Command::new(tool)
                .args(&args)
                .stdin(Stdio::piped())
                .stdout(Stdio::from(file))
                .spawn()
                .map_err(|e| format!("failed to spawn `{tool}`: {e}"))?;
            {
                let mut stdin = child
                    .stdin
                    .take()
                    .ok_or_else(|| format!("no stdin pipe to `{tool}`"))?;
                for c in chunks {
                    stdin.write_all(c).map_err(|e| format!("`{tool}` pipe: {e}"))?;
                }
            }
            let st = child.wait().map_err(|e| format!("`{tool}` wait failed: {e}"))?;
            if !st.success() {
                return Err(format!("`{tool}` exited with {st}"));
            }
        }
    }
    Ok(())
}

fn basename(path: &str) -> &str {
    Path::new(path).file_name().and_then(|s| s.to_str()).unwrap_or(path)
}

#[inline]
fn push_u32(buf: &mut Vec<u8>, mut n: u32) {
    let mut tmp = [0u8; 10];
    let mut i = tmp.len();
    loop {
        i -= 1;
        tmp[i] = b'0' + (n % 10) as u8;
        n /= 10;
        if n == 0 {
            break;
        }
    }
    buf.extend_from_slice(&tmp[i..]);
}

/// Python `str.isspace()` over latin-1 decoded bytes (what `str.strip()` / `str.split()` use).
#[inline]
fn is_py_ws(b: u8) -> bool {
    matches!(b, b' ' | b'\t' | b'\n' | b'\r' | 0x0b | 0x0c | 0x1c..=0x1f | 0x85 | 0xa0)
}

// ============================================================================
// aig-to-anf
// ============================================================================

struct Aig {
    ni: u32,
    na: u32,
    outputs: Vec<u32>,
    ands: Vec<(u32, u32)>,
}

fn read_varint(data: &[u8], pos: &mut usize) -> Res<u64> {
    let mut x = 0u64;
    let mut sh = 0u32;
    loop {
        let b = *data.get(*pos).ok_or("truncated AIGER binary AND section")?;
        *pos += 1;
        if sh > 56 {
            return Err("AIGER delta varint overflow".into());
        }
        x |= u64::from(b & 0x7f) << sh;
        if b & 0x80 == 0 {
            return Ok(x);
        }
        sh += 7;
    }
}

fn parse_aig(data: &[u8]) -> Res<Aig> {
    let nl = data.iter().position(|&b| b == b'\n').ok_or("missing AIGER header line")?;
    let hdr_s = std::str::from_utf8(&data[..nl]).map_err(|_| "non-ASCII AIGER header")?;
    let hdr: Vec<&str> = hdr_s.split_ascii_whitespace().collect();
    if hdr.len() < 6 || (hdr[0] != "aig" && hdr[0] != "aag") {
        return Err(format!("Unsupported AIGER header: {hdr:?}"));
    }
    if hdr[0] != "aig" {
        return Err("ASCII AIGER (aag) is handled by the pure-Python path only".into());
    }
    let p = |s: &str| s.parse::<u64>().map_err(|_| format!("bad AIGER header field `{s}`"));
    let (m, i, l, o, a) = (p(hdr[1])?, p(hdr[2])?, p(hdr[3])?, p(hdr[4])?, p(hdr[5])?);
    if l != 0 {
        return Err(format!("Sequential AIGER (L={l}) not supported"));
    }
    if o == 0 {
        return Err("AIGER file has O=0 outputs".into());
    }
    if i + a != m {
        return Err(format!("Binary AIGER requires I+A==M (got I={i}, A={a}, M={m})"));
    }
    if m >= (1u64 << 30) {
        return Err(format!("AIGER too large for u32 literals (M={m})"));
    }
    let max_lit = 2 * m + 1;
    let mut pos = nl + 1;
    let mut outputs = Vec::with_capacity(o as usize);
    for _ in 0..o {
        let end = data[pos..].iter().position(|&b| b == b'\n').map_or(data.len(), |k| pos + k);
        let line = std::str::from_utf8(&data[pos..end]).map_err(|_| "non-ASCII AIGER output line")?;
        let tok = line.split_ascii_whitespace().next().ok_or("empty AIGER output line")?;
        let lit: u64 = tok.parse().map_err(|_| format!("bad AIGER output literal `{tok}`"))?;
        if lit > max_lit {
            return Err(format!("AIGER output literal {lit} out of range"));
        }
        outputs.push(lit as u32);
        pos = (end + 1).min(data.len());
    }
    let mut ands = Vec::with_capacity(a as usize);
    for k in 0..a {
        let lhs = (i + 1 + k) << 1;
        let d0 = read_varint(data, &mut pos)?;
        let d1 = read_varint(data, &mut pos)?;
        let r0 = lhs.checked_sub(d0).ok_or("invalid AIGER delta d0")?;
        let r1 = r0.checked_sub(d1).ok_or("invalid AIGER delta d1")?;
        ands.push((r0 as u32, r1 as u32));
    }
    Ok(Aig { ni: i as u32, na: a as u32, outputs, ands })
}

/// Monomial `(a, b)` = x_a * x_b (b == 0 => linear monomial x_a). Tuple ordering
/// reproduces Python's lexicographic ordering of `(a,)` / `(a, b)` tuples.
type Mon = (u32, u32);

#[inline]
fn toggle_mon(mons: &mut Vec<Mon>, m: Mon) {
    if let Some(p) = mons.iter().position(|&x| x == m) {
        mons.swap_remove(p);
    } else {
        mons.push(m);
    }
}

/// Exact port of `_expand_and_lits`: `(x_{v0} ^ n0) * (x_{v1} ^ n1)` (var 0 = const 0).
fn expand_and_lits(v0: u32, n0: u32, v1: u32, n1: u32) -> (Vec<Mon>, u32) {
    if v0 == 0 {
        if n0 == 0 {
            return (vec![], 0);
        }
        if v1 == 0 {
            return (vec![], n1);
        }
        return (vec![(v1, 0)], n1);
    }
    if v1 == 0 {
        if n1 == 0 {
            return (vec![], 0);
        }
        return (vec![(v0, 0)], n0);
    }
    if v0 == v1 {
        if n0 != n1 {
            return (vec![], 0);
        }
        return (vec![(v0, 0)], n0);
    }
    let (a, na, b, nb) = if v0 < v1 { (v0, n0, v1, n1) } else { (v1, n1, v0, n0) };
    let mut mons = vec![(a, b)];
    if na != 0 {
        toggle_mon(&mut mons, (b, 0));
    }
    if nb != 0 {
        toggle_mon(&mut mons, (a, 0));
    }
    (mons, na & nb)
}

/// Sorted symmetric difference of two sorted, duplicate-free slices.
fn symdiff(a: &[u32], b: &[u32]) -> Vec<u32> {
    let mut out = Vec::with_capacity(a.len() + b.len());
    let (mut i, mut j) = (0, 0);
    while i < a.len() && j < b.len() {
        match a[i].cmp(&b[j]) {
            std::cmp::Ordering::Less => {
                out.push(a[i]);
                i += 1;
            }
            std::cmp::Ordering::Greater => {
                out.push(b[j]);
                j += 1;
            }
            std::cmp::Ordering::Equal => {
                i += 1;
                j += 1;
            }
        }
    }
    out.extend_from_slice(&a[i..]);
    out.extend_from_slice(&b[j..]);
    out
}

/// Appends one `format_anf_line` equation; returns its degree.
fn emit_eq(body: &mut Vec<u8>, mons: &[Mon], rhs: u32) -> usize {
    body.push(b'x');
    if rhs == 0 {
        body.extend_from_slice(b" T");
    }
    let mut deg = 0;
    for &(a, b) in mons {
        body.push(b' ');
        push_u32(body, a);
        if b != 0 {
            body.push(b'.');
            push_u32(body, b);
            deg = 2;
        } else if deg == 0 {
            deg = 1;
        }
    }
    body.extend_from_slice(b" 0\n");
    deg
}

struct Conversion {
    header: String,
    body: Vec<u8>,
    nv: u32,
    neq: u64,
    max_deg: usize,
    vmap: Vec<u32>,
}

/// Exact port of `to_anf.convert_aiger_to_anf` (same equation order, same text).
fn convert_aig(aig: &Aig, source_name: &str) -> Res<Conversion> {
    let ni = aig.ni;
    let max_var = ni + aig.na;
    let nvars = max_var as usize + 1;
    let ands = &aig.ands;
    let gi = |v: u32| (v - ni - 1) as usize;
    let is_gate = |v: u32| v > ni && v <= max_var;
    for &(r0, r1) in ands {
        if (r0 >> 1) > max_var || (r1 >> 1) > max_var {
            return Err("AIGER AND literal out of range".into());
        }
    }

    // Step 1: 3-AND XOR patterns.
    let mut is_xor = vec![false; ands.len()];
    let mut xch = vec![(0u32, 0u32); ands.len()];
    for (i, &(r0, r1)) in ands.iter().enumerate() {
        if r0 & 1 == 1 && r1 & 1 == 1 {
            let (v0, v1) = (r0 >> 1, r1 >> 1);
            if is_gate(v0) && is_gate(v1) {
                let (x1, y1) = ands[gi(v0)];
                let (x2, y2) = ands[gi(v1)];
                if (x1 == (x2 ^ 1) && y1 == (y2 ^ 1)) || (x1 == (y2 ^ 1) && y1 == (x2 ^ 1)) {
                    is_xor[i] = true;
                    xch[i] = (x1, y1);
                }
            }
        }
    }
    let children = |v: u32| if is_xor[gi(v)] { xch[gi(v)] } else { ands[gi(v)] };

    // Step 2: unpack top-level positive AND trees (stopping at XORs), dedup preserving order.
    let mut stack: Vec<u32> = aig.outputs.iter().rev().copied().collect();
    let mut raw_asserts = Vec::new();
    while let Some(lit) = stack.pop() {
        let v = lit >> 1;
        if lit & 1 == 0 && is_gate(v) && !is_xor[gi(v)] {
            let (r0, r1) = ands[gi(v)];
            stack.push(r1);
            stack.push(r0);
        } else {
            raw_asserts.push(lit);
        }
    }
    let mut seen_lit = vec![false; 2 * nvars];
    let mut asserts = Vec::new();
    for l in raw_asserts {
        if !seen_lit[l as usize] {
            seen_lit[l as usize] = true;
            asserts.push(l);
        }
    }
    drop(seen_lit);

    // Step 3: active cone of influence.
    let mut needed = vec![false; nvars];
    let mut work = Vec::new();
    for &lit in &asserts {
        let v = lit >> 1;
        if v > ni && !needed[v as usize] {
            needed[v as usize] = true;
            work.push(v);
        }
    }
    while let Some(v) = work.pop() {
        let (c0, c1) = children(v);
        for c in [c0 >> 1, c1 >> 1] {
            if c > ni && !needed[c as usize] {
                needed[c as usize] = true;
                work.push(c);
            }
        }
    }

    // Step 4: fanout counts.
    let mut fo = vec![0u32; nvars];
    let mut fo_and = vec![0u32; nvars];
    let mut fo_assert_neg = vec![0u32; nvars];
    for &lit in &asserts {
        let v = (lit >> 1) as usize;
        fo[v] += 1;
        if lit & 1 == 1 {
            fo_assert_neg[v] += 1;
        }
    }
    for v in (ni + 1)..=max_var {
        if !needed[v as usize] {
            continue;
        }
        let x = is_xor[gi(v)];
        let (c0, c1) = children(v);
        for c in [c0 >> 1, c1 >> 1] {
            fo[c as usize] += 1;
            if !x {
                fo_and[c as usize] += 1;
            }
        }
    }

    // Inline single-fanout XORs feeding only XORs/assertions (width <= 256).
    const NONE: u32 = u32::MAX;
    let mut exp_idx = vec![NONE; nvars];
    let mut exp_sets: Vec<Vec<u32>> = Vec::new();
    let mut exp_par: Vec<u32> = Vec::new();
    let mut not_kept = vec![false; nvars];
    for v in (ni + 1)..=max_var {
        let vu = v as usize;
        if !needed[vu] || !is_xor[gi(v)] || fo[vu] != 1 || fo_and[vu] != 0 {
            continue;
        }
        let (c0, c1) = xch[gi(v)];
        let (v0, n0, v1, n1) = (c0 >> 1, c0 & 1, c1 >> 1, c1 & 1);
        let (i0, i1) = (exp_idx[v0 as usize], exp_idx[v1 as usize]);
        let (sym, par) = {
            fn side<'a>(sets: &'a [Vec<u32>], pars: &[u32], vv: &'a u32, idx: u32, n: u32) -> (&'a [u32], u32) {
                if idx != u32::MAX {
                    (&sets[idx as usize][..], pars[idx as usize] ^ n)
                } else if *vv > 0 {
                    (std::slice::from_ref(vv), n)
                } else {
                    (&[][..], n)
                }
            }
            let (s0, p0) = side(&exp_sets, &exp_par, &v0, i0, n0);
            let (s1, p1) = side(&exp_sets, &exp_par, &v1, i1, n1);
            (symdiff(s0, s1), p0 ^ p1)
        };
        if sym.len() <= 256 {
            not_kept[vu] = true;
            exp_idx[vu] = exp_sets.len() as u32;
            exp_sets.push(sym);
            exp_par.push(par);
            // Children's sets have exactly one consumer (this inlined XOR): free them.
            for idx in [i0, i1] {
                if idx != NONE {
                    exp_sets[idx as usize] = Vec::new();
                }
            }
        }
    }

    // Inline single-fanout AND gates used only as one negated assertion.
    let mut inlined_neg_and = vec![false; nvars];
    for v in (ni + 1)..=max_var {
        let vu = v as usize;
        if needed[vu] && !is_xor[gi(v)] && fo[vu] == 1 && fo_assert_neg[vu] == 1 {
            inlined_neg_and[vu] = true;
            not_kept[vu] = true;
        }
    }

    // Step 5: compact 1-based ANF ids.
    let mut vmap = vec![0u32; nvars];
    for i in 1..=ni {
        vmap[i as usize] = i;
    }
    let mut kept: Vec<u32> = Vec::new();
    let mut next_id = ni + 1;
    for v in (ni + 1)..=max_var {
        if needed[v as usize] && !not_kept[v as usize] {
            vmap[v as usize] = next_id;
            next_id += 1;
            kept.push(v);
        }
    }
    let nv = next_id - 1;

    let map_var = |v: u32| -> Res<u32> {
        if v == 0 {
            return Ok(0);
        }
        match vmap[v as usize] {
            0 => Err(format!("internal: unmapped AIGER var {v}")),
            m => Ok(m),
        }
    };
    let expand_lit_linear = |lit: u32| -> Res<(Vec<u32>, u32)> {
        let v = lit >> 1;
        let neg = lit & 1;
        let idx = exp_idx[v as usize];
        if idx != NONE {
            let mut out = Vec::with_capacity(exp_sets[idx as usize].len());
            for &u in &exp_sets[idx as usize] {
                if u > 0 {
                    out.push(map_var(u)?);
                }
            }
            out.sort_unstable();
            return Ok((out, exp_par[idx as usize] ^ neg));
        }
        if v == 0 {
            return Ok((vec![], neg));
        }
        Ok((vec![map_var(v)?], neg))
    };
    let lin_mons = |vs: &[u32]| -> Vec<Mon> { vs.iter().map(|&u| (u, 0)).collect() };

    let mut body: Vec<u8> = Vec::with_capacity(kept.len() * 24 + asserts.len() * 16 + 64);
    let (mut neq, mut n_xor_eqs, mut n_and_eqs, mut max_deg) = (0u64, 0u64, 0u64, 0usize);

    for &v in &kept {
        let zv = vmap[v as usize];
        if is_xor[gi(v)] {
            let (c0, c1) = xch[gi(v)];
            let (s0, p0) = expand_lit_linear(c0)?;
            let (s1, p1) = expand_lit_linear(c1)?;
            let vs = symdiff(&symdiff(&s0, &s1), &[zv]);
            max_deg = max_deg.max(emit_eq(&mut body, &lin_mons(&vs), p0 ^ p1));
            n_xor_eqs += 1;
        } else {
            let (r0, r1) = ands[gi(v)];
            let (v0, v1) = (map_var(r0 >> 1)?, map_var(r1 >> 1)?);
            let (mut mons, c) = expand_and_lits(v0, r0 & 1, v1, r1 & 1);
            toggle_mon(&mut mons, (zv, 0));
            mons.sort_unstable();
            max_deg = max_deg.max(emit_eq(&mut body, &mons, c));
            n_and_eqs += 1;
        }
        neq += 1;
    }

    for &lit in &asserts {
        let v = lit >> 1;
        if lit & 1 == 1 && inlined_neg_and[v as usize] {
            let (r0, r1) = ands[gi(v)];
            let (v0, v1) = (map_var(r0 >> 1)?, map_var(r1 >> 1)?);
            let (mut mons, c) = expand_and_lits(v0, r0 & 1, v1, r1 & 1);
            if mons.is_empty() && c == 0 {
                continue;
            }
            mons.sort_unstable();
            max_deg = max_deg.max(emit_eq(&mut body, &mons, c));
            n_and_eqs += 1;
        } else {
            let (vs, p) = expand_lit_linear(lit)?;
            let rhs = 1 ^ p;
            if vs.is_empty() && rhs == 0 {
                continue;
            }
            max_deg = max_deg.max(emit_eq(&mut body, &lin_mons(&vs), rhs));
            n_xor_eqs += 1;
        }
        neq += 1;
    }

    if neq == 0 {
        emit_eq(&mut body, &[], 0);
        neq = 1;
    }

    let header = format!(
        "c Converted from AIGER ({source_name}) by to_anf.py\n\
         c orig_inputs={ni} orig_ands={} anf_vars={nv} linear_eqs={n_xor_eqs} quad_eqs={n_and_eqs}\n\
         p anf {nv} {neq}\n",
        aig.na
    );
    Ok(Conversion { header, body, nv, neq, max_deg, vmap })
}

struct SplitMix64(u64);
impl SplitMix64 {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }
}

fn trim_py(mut s: &[u8]) -> &[u8] {
    while let [f, rest @ ..] = s {
        if is_py_ws(*f) {
            s = rest;
        } else {
            break;
        }
    }
    while let [rest @ .., l] = s {
        if is_py_ws(*l) {
            s = rest;
        } else {
            break;
        }
    }
    s
}

fn parse_int_bytes(tok: &[u8]) -> Res<i64> {
    let (neg, digits) = match tok.first() {
        Some(b'-') => (true, &tok[1..]),
        Some(b'+') => (false, &tok[1..]),
        _ => (false, tok),
    };
    if digits.is_empty() || digits.len() > 18 || !digits.iter().all(u8::is_ascii_digit) {
        return Err(format!("invalid integer token `{}`", String::from_utf8_lossy(tok)));
    }
    let mut x = 0i64;
    for &d in digits {
        x = x * 10 + i64::from(d - b'0');
    }
    Ok(if neg { -x } else { x })
}

/// Independent re-read of the written DIMACS-ANF + 64-lane bit-parallel forward
/// equivalence check (port of `verify_conversion` for AIGER, `u64` lanes = vectors).
fn verify_aig(out_path: &str, aig: &Aig, conv: &Conversion) -> Res<(usize, u32)> {
    let text = read_all(out_path)?;
    let (mut hdr_nv, mut hdr_neq) = (0i64, 0i64);
    let (mut max_v, mut max_deg) = (0u32, 0usize);
    let mut eq_start: Vec<usize> = vec![0];
    let mut mons: Vec<Mon> = Vec::new();
    let mut rhs: Vec<u8> = Vec::new();
    for raw_line in text.split(|&b| b == b'\n') {
        let s = trim_py(raw_line);
        if s.is_empty() || s[0] == b'c' || s[0] == b'#' {
            continue;
        }
        if s.starts_with(b"p ") {
            let parts: Vec<&[u8]> = s.split(|&b| is_py_ws(b)).filter(|t| !t.is_empty()).collect();
            if parts.len() < 4 || parts[1] != b"anf" {
                return Err(format!("Bad p anf header: {}", String::from_utf8_lossy(s)));
            }
            hdr_nv = parse_int_bytes(parts[2])?;
            hdr_neq = parse_int_bytes(parts[3])?;
            continue;
        }
        let s = if s[0] == b'x' || s[0] == b'X' { trim_py(&s[1..]) } else { s };
        let mut r = 1u8;
        for tok in s.split(|&b| is_py_ws(b)).filter(|t| !t.is_empty()) {
            if tok == b"0" {
                break;
            }
            if tok == b"T" || tok.eq_ignore_ascii_case(b"true") {
                r ^= 1;
                continue;
            }
            let tok = if tok[0] == b'-' {
                r ^= 1;
                &tok[1..]
            } else {
                tok
            };
            let mut facs: Vec<u32> = Vec::with_capacity(2);
            for f in tok.split(|&b| b == b'.').filter(|f| !f.is_empty()) {
                let x = parse_int_bytes(f)?;
                if x <= 0 || x > i64::from(u32::MAX) {
                    return Err(format!("bad ANF variable {x}"));
                }
                facs.push(x as u32);
            }
            facs.sort_unstable();
            facs.dedup();
            if let Some(&last) = facs.last() {
                max_v = max_v.max(last);
                max_deg = max_deg.max(facs.len());
                if facs.len() > 2 {
                    return Err(format!("max degree {} exceeds bound 2", facs.len()));
                }
                mons.push((facs[0], facs.get(1).copied().unwrap_or(0)));
            }
        }
        rhs.push(r);
        eq_start.push(mons.len());
    }
    if hdr_nv != i64::from(conv.nv) {
        return Err(format!("header nv {hdr_nv} != {}", conv.nv));
    }
    if hdr_neq != rhs.len() as i64 {
        return Err(format!("header neq {hdr_neq} != {}", rhs.len()));
    }
    if rhs.len() as u64 != conv.neq {
        return Err(format!("parsed neq {} != emitted {}", rhs.len(), conv.neq));
    }
    if i64::from(max_v) > hdr_nv {
        return Err(format!("var {max_v} exceeds header nv {hdr_nv}"));
    }

    // 64 random input vectors, one per u64 bit lane.
    let ni = aig.ni as usize;
    let nvars = ni + aig.ands.len() + 1;
    let mask = |n: u32| if n & 1 == 1 { !0u64 } else { 0u64 };
    let mut rng = SplitMix64(20261123);
    let mut vals = vec![0u64; nvars];
    for v in vals.iter_mut().take(ni + 1).skip(1) {
        *v = rng.next();
    }
    for (k, &(r0, r1)) in aig.ands.iter().enumerate() {
        let b0 = vals[(r0 >> 1) as usize] ^ mask(r0);
        let b1 = vals[(r1 >> 1) as usize] ^ mask(r1);
        vals[ni + 1 + k] = b0 & b1;
    }
    let mut aig_ok = !0u64;
    for &po in &aig.outputs {
        aig_ok &= vals[(po >> 1) as usize] ^ mask(po);
    }
    let mut av = vec![0u64; hdr_nv as usize + 1];
    for (v, &m) in conv.vmap.iter().enumerate() {
        if m != 0 {
            av[m as usize] = vals[v];
        }
    }
    let mut anf_ok = !0u64;
    for e in 0..rhs.len() {
        let mut acc = 0u64;
        for &(a, b) in &mons[eq_start[e]..eq_start[e + 1]] {
            acc ^= if b == 0 { av[a as usize] } else { av[a as usize] & av[b as usize] };
        }
        anf_ok &= if rhs[e] == 1 { acc } else { !acc };
    }
    if anf_ok != aig_ok {
        return Err(format!(
            "Random vector mismatch on AIGER->ANF (aig lanes={aig_ok:#018x}, anf lanes={anf_ok:#018x})"
        ));
    }
    Ok((max_deg, aig_ok.count_ones()))
}

fn cmd_aig_to_anf(args: &[String]) -> Res<()> {
    let mut pos: Vec<&str> = Vec::new();
    let mut verify = false;
    let mut preset = 3u32;
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--verify" => verify = true,
            "--preset" => {
                let p = it.next().ok_or("--preset needs a value")?;
                preset = p.parse().map_err(|_| format!("bad --preset `{p}`"))?;
                if preset > 9 {
                    return Err("--preset must be 0..=9".into());
                }
            }
            s if s.starts_with("--") => return Err(format!("unknown option `{s}`")),
            s => pos.push(s),
        }
    }
    let [inp, out] = pos[..] else {
        return Err(format!("aig-to-anf needs <in> <out>\n{USAGE}"));
    };

    let t0 = Instant::now();
    let raw = read_all(inp)?;
    let aig = parse_aig(&raw)?;
    drop(raw);
    let src_name = basename(inp);
    let conv = convert_aig(&aig, src_name)?;
    write_output(out, &[conv.header.as_bytes(), &conv.body], preset)?;
    let conv_ms = t0.elapsed().as_secs_f64() * 1000.0;
    println!(
        "[ok] {src_name} (aiger) -> {}: nv={} neq={} max_deg={} ({conv_ms:.1}ms) [sat-bench-tools]",
        basename(out),
        conv.nv,
        conv.neq,
        conv.max_deg
    );
    if verify {
        let t1 = Instant::now();
        let (vdeg, sat_lanes) = verify_aig(out, &aig, &conv)?;
        println!(
            "  [verified] structural + 64-vector forward equivalence passed (max_deg={vdeg}) \
             [u64 bit-parallel, {sat_lanes}/64 lanes satisfy POs, {:.1}ms]",
            t1.elapsed().as_secs_f64() * 1000.0
        );
    }
    io::stdout().flush().map_err(|e| e.to_string())?;
    Ok(())
}

// ============================================================================
// analyze-cnf
// ============================================================================

struct CnfAcc {
    declared_vars: i64,
    num_clauses: u64,
    total_lits: u64,
    pos_lits: u64,
    horn_clauses: u64,
    len_counts: Vec<u64>,
    len_order: Vec<usize>,
    pos_deg: Vec<u32>,
    neg_deg: Vec<u32>,
    parent: Vec<u32>,
    unions: u64,
    cur_k: usize,
    cur_pos: usize,
    cur_first: u32,
}

impl CnfAcc {
    fn new() -> Self {
        CnfAcc {
            declared_vars: 0,
            num_clauses: 0,
            total_lits: 0,
            pos_lits: 0,
            horn_clauses: 0,
            len_counts: vec![0; 64],
            len_order: Vec::new(),
            pos_deg: vec![0; 1],
            neg_deg: vec![0; 1],
            parent: vec![0; 1],
            unions: 0,
            cur_k: 0,
            cur_pos: 0,
            cur_first: 0,
        }
    }

    #[inline]
    fn find(&mut self, mut x: u32) -> u32 {
        while self.parent[x as usize] != x {
            let gp = self.parent[self.parent[x as usize] as usize];
            self.parent[x as usize] = gp;
            x = gp;
        }
        x
    }

    #[inline]
    fn lit(&mut self, lit: i64) -> Res<()> {
        if lit == 0 {
            self.flush();
            return Ok(());
        }
        let va = lit.unsigned_abs();
        if va >= (1u64 << 31) {
            return Err(format!("variable {va} too large"));
        }
        let v = va as u32;
        let vu = v as usize;
        if vu >= self.pos_deg.len() {
            let new_len = (vu + 1).max(self.pos_deg.len() * 2);
            self.pos_deg.resize(new_len, 0);
            self.neg_deg.resize(new_len, 0);
            let old = self.parent.len();
            self.parent.extend((old as u32)..(new_len as u32));
        }
        if lit > 0 {
            self.pos_deg[vu] += 1;
            self.cur_pos += 1;
        } else {
            self.neg_deg[vu] += 1;
        }
        if self.cur_k == 0 {
            self.cur_first = v;
        } else {
            let ra = self.find(self.cur_first);
            let rb = self.find(v);
            if ra != rb {
                self.parent[rb as usize] = ra;
                self.unions += 1;
            }
        }
        self.cur_k += 1;
        Ok(())
    }

    #[inline]
    fn flush(&mut self) {
        let k = self.cur_k;
        if k == 0 {
            return;
        }
        self.num_clauses += 1;
        self.total_lits += k as u64;
        if k >= self.len_counts.len() {
            self.len_counts.resize((k + 1).max(self.len_counts.len() * 2), 0);
        }
        if self.len_counts[k] == 0 {
            self.len_order.push(k);
        }
        self.len_counts[k] += 1;
        self.pos_lits += self.cur_pos as u64;
        if self.cur_pos <= 1 {
            self.horn_clauses += 1;
        }
        self.cur_k = 0;
        self.cur_pos = 0;
    }

    fn p_line(&mut self, line: &[u8]) -> Res<()> {
        let parts: Vec<&[u8]> = line.split(|&b| is_py_ws(b)).filter(|t| !t.is_empty()).collect();
        if parts.len() >= 4 && parts[1].eq_ignore_ascii_case(b"cnf") {
            self.declared_vars = parse_int_bytes(parts[2])?;
        }
        Ok(())
    }
}

#[derive(PartialEq, Clone, Copy)]
enum St {
    LineStart,
    SkipLine,
    PLine,
    Data,
    InTok,
}

/// Exact power of two 2^e for e in [-1074, 1023] (0.0 below, matching `2.0 ** e` underflow).
fn pow2(e: i64) -> f64 {
    if e >= -1022 {
        f64::from_bits(((e + 1023) as u64) << 52)
    } else if e >= -1074 {
        f64::from_bits(1u64 << (e + 1074))
    } else {
        0.0
    }
}

fn alpha_c_k(k: usize, ln2: f64) -> f64 {
    match k {
        1 | 2 => 1.000,
        3 => 4.267,
        4 => 9.931,
        5 => 21.117,
        6 => 43.370,
        k if k >= 30 => pow2(30) * ln2,
        k => pow2(k as i64) * ln2 - 0.5 * (1.0 + ln2),
    }
}

/// CPython >= 3.12 `sum()` over floats starting from int 0 (Neumaier compensation).
fn py_fsum_neumaier(xs: impl Iterator<Item = f64>) -> f64 {
    let mut it = xs;
    let Some(first) = it.next() else { return 0.0 };
    let mut f = first;
    let mut c = 0.0f64;
    for x in it {
        let t = f + x;
        if f.abs() >= x.abs() {
            c += (f - t) + x;
        } else {
            c += (x - t) + f;
        }
        f = t;
    }
    if c != 0.0 && c.is_finite() {
        f += c;
    }
    f
}

fn cmd_analyze_cnf(args: &[String]) -> Res<()> {
    let [path] = args else {
        return Err(format!("analyze-cnf needs exactly one <in.cnf[.xz]>\n{USAGE}"));
    };
    let path = path.as_str();
    let mut inp = Input::open(path)?;
    let mut acc = CnfAcc::new();
    let mut buf = vec![0u8; 1 << 20];
    let mut pline: Vec<u8> = Vec::new();
    let mut st = St::LineStart;
    let mut stopped = false;
    // Current integer token state.
    let (mut tok_neg, mut tok_val, mut tok_digits, mut tok_bad) = (false, 0i64, 0usize, false);

    macro_rules! finish_tok {
        () => {{
            if tok_bad || tok_digits == 0 || tok_digits > 18 {
                return Err(format!("{path}: invalid literal token in CNF body"));
            }
            acc.lit(if tok_neg { -tok_val } else { tok_val })?;
        }};
    }

    'outer: loop {
        let n = inp.reader.read(&mut buf).map_err(|e| format!("{path}: {e}"))?;
        if n == 0 {
            break;
        }
        for &b in &buf[..n] {
            let nl = b == b'\n' || b == b'\r';
            match st {
                St::LineStart => {
                    if is_py_ws(b) {
                        continue;
                    }
                    match b {
                        b'c' | b'C' => st = St::SkipLine,
                        b'%' => {
                            stopped = true;
                            break 'outer;
                        }
                        b'p' => {
                            pline.clear();
                            pline.push(b);
                            st = St::PLine;
                        }
                        _ => {
                            // Start of a data line: this byte must begin a literal token.
                            if b == b'-' || b == b'+' || b.is_ascii_digit() {
                                tok_neg = b == b'-';
                                tok_val = if b.is_ascii_digit() { i64::from(b - b'0') } else { 0 };
                                tok_digits = usize::from(b.is_ascii_digit());
                                tok_bad = false;
                                st = St::InTok;
                            } else {
                                return Err(format!("{path}: unexpected byte {b:#04x} in CNF body"));
                            }
                        }
                    }
                }
                St::SkipLine => {
                    if nl {
                        st = St::LineStart;
                    }
                }
                St::PLine => {
                    if nl {
                        acc.p_line(&pline)?;
                        st = St::LineStart;
                    } else {
                        pline.push(b);
                    }
                }
                St::Data => {
                    if nl {
                        st = St::LineStart;
                    } else if is_py_ws(b) {
                    } else if b == b'%' {
                        st = St::SkipLine;
                    } else if b == b'-' || b == b'+' || b.is_ascii_digit() {
                        tok_neg = b == b'-';
                        tok_val = if b.is_ascii_digit() { i64::from(b - b'0') } else { 0 };
                        tok_digits = usize::from(b.is_ascii_digit());
                        tok_bad = false;
                        st = St::InTok;
                    } else {
                        return Err(format!("{path}: unexpected byte {b:#04x} in CNF body"));
                    }
                }
                St::InTok => {
                    if b.is_ascii_digit() {
                        if tok_digits < 18 {
                            tok_val = tok_val * 10 + i64::from(b - b'0');
                        }
                        tok_digits += 1;
                    } else if is_py_ws(b) {
                        finish_tok!();
                        st = if nl { St::LineStart } else { St::Data };
                    } else {
                        tok_bad = true;
                        finish_tok!();
                    }
                }
            }
        }
    }
    if !stopped {
        match st {
            St::InTok => finish_tok!(),
            St::PLine => acc.p_line(&pline)?,
            _ => {}
        }
    } else {
        // Drain the decompressor so it exits cleanly (Python stops reading at `%`).
        while inp.reader.read(&mut buf).map_err(|e| format!("{path}: {e}"))? > 0 {}
    }
    acc.flush();
    inp.finish()?;

    // ---- metrics (same float op order as analyze_benchmarks.analyze_cnf) ----
    let nvlen = acc.pos_deg.len();
    let mut n: u64 = 0;
    let mut deg_sum: u64 = 0;
    let mut deg_max: u64 = 0;
    let mut pure_vars: u64 = 0;
    for v in 1..nvlen {
        let (pd, nd) = (u64::from(acc.pos_deg[v]), u64::from(acc.neg_deg[v]));
        if pd + nd == 0 {
            continue;
        }
        n += 1;
        deg_sum += pd + nd;
        deg_max = deg_max.max(pd + nd);
        if pd == 0 || nd == 0 {
            pure_vars += 1;
        }
    }
    let m = acc.num_clauses;
    let mut o = String::with_capacity(1024);
    let ff = |x: f64| format!("{x:?}");
    if n == 0 || m == 0 {
        o.push_str(&format!(
            "{{\"trivial\": true, \"declared_vars\": {}, \"active_vars\": {n}, \"clauses\": {m}, \"literals\": {}, \
             \"alpha\": 0.0, \"alpha_c_eff\": 0.0, \"rho_crit\": 0.0, \"kappa\": 0.0, \"alpha_2\": 0.0, \
             \"k_avg\": 0.0, \"k_max\": 0, \"pct_unit\": 0.0, \"pct_bin\": 0.0, \"pct_tern\": 0.0, \
             \"pct_long\": 0.0, \"pct_horn\": 0.0, \"pct_pos\": 0.0, \"pure_vars\": 0, \"deg_mean\": 0.0, \
             \"deg_max\": 0, \"deg_cv\": 0.0, \"vig_components\": 0}}",
            acc.declared_vars, acc.total_lits
        ));
        println!("{o}");
        return Ok(());
    }
    let ln2 = 2.0f64.ln();
    let (nf, mf) = (n as f64, m as f64);
    let alpha = mf / nf;
    let mut rho_crit = 0.0f64;
    let mut kappa = 0.0f64;
    for &k in &acc.len_order {
        let cnt = acc.len_counts[k] as f64;
        rho_crit += (cnt / nf) / alpha_c_k(k, ln2);
        let ki = k as i64;
        if k < 53 {
            kappa += (cnt / nf) * (-(1.0 - pow2(-ki)).log2());
        } else {
            kappa += (cnt / nf) * (pow2(-ki) / ln2);
        }
    }
    let alpha_c_eff = if rho_crit > 0.0 { alpha / rho_crit } else { 0.0 };

    let deg_mean = deg_sum as f64 / nf;
    let deg_cv = if n > 1 && deg_mean > 0.0 {
        let two = std::hint::black_box(2.0f64); // genuine libm pow(x, 2.0), like CPython `** 2`
        let degs = (1..nvlen).filter_map(|v| {
            let d = u64::from(acc.pos_deg[v]) + u64::from(acc.neg_deg[v]);
            (d > 0).then(|| (d as f64 - deg_mean).powf(two))
        });
        let var_d = py_fsum_neumaier(degs) / nf;
        var_d.sqrt() / deg_mean
    } else {
        0.0
    };
    let vig_components = n - acc.unions;
    let k_max = acc.len_order.iter().copied().max().unwrap_or(0);
    let lc = |k: usize| acc.len_counts.get(k).copied().unwrap_or(0) as f64;
    let (m1, m2, m3) = (lc(1), lc(2), lc(3));
    let m_long: u64 = acc.len_order.iter().filter(|&&k| k >= 4).map(|&k| acc.len_counts[k]).sum();
    let tl = acc.total_lits as f64;

    o.push_str(&format!(
        "{{\"trivial\": false, \"declared_vars\": {}, \"active_vars\": {n}, \"clauses\": {m}, \"literals\": {}, \
         \"alpha\": {}, \"alpha_c_eff\": {}, \"rho_crit\": {}, \"kappa\": {}, \"alpha_2\": {}, \
         \"k_avg\": {}, \"k_max\": {k_max}, \"pct_unit\": {}, \"pct_bin\": {}, \"pct_tern\": {}, \
         \"pct_long\": {}, \"pct_horn\": {}, \"pct_pos\": {}, \"pure_vars\": {pure_vars}, \"deg_mean\": {}, \
         \"deg_max\": {deg_max}, \"deg_cv\": {}, \"vig_components\": {vig_components}}}",
        acc.declared_vars,
        acc.total_lits,
        ff(alpha),
        ff(alpha_c_eff),
        ff(rho_crit),
        ff(kappa),
        ff(m2 / nf),
        ff(tl / mf),
        ff(100.0 * m1 / mf),
        ff(100.0 * m2 / mf),
        ff(100.0 * m3 / mf),
        ff(100.0 * m_long as f64 / mf),
        ff(100.0 * acc.horn_clauses as f64 / mf),
        ff(100.0 * acc.pos_lits as f64 / tl),
        ff(deg_mean),
        ff(deg_cv),
    ));
    println!("{o}");
    Ok(())
}
