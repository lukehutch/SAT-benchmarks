#!/usr/bin/env python3
"""Download deduplicated SAT Competition 2024, 2025, and 2026 Main Track CNF benchmarks (1,166 unique MD5s).

Requires URI lists (`main_2024.uri`, `main_2025.uri`, `main_2026.uri`) from the official SAT Competition
benchmark archives (e.g., https://satcompetition.github.io/2024/, /2025/, /2026/).
"""
import argparse
import concurrent.futures
import pathlib
import time
import urllib.error
import urllib.request


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--uri-dir", default="/tmp/sc-bench", help="Directory containing main_202{4,5,6}.uri")
    ap.add_argument("--cache-dir", default=str(pathlib.Path.home() / ".cache/sc-main-cnfs"))
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    cache_dir = pathlib.Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    uri_dir = pathlib.Path(args.uri_dir)

    url_by_hash = {}
    for yr in (2024, 2025, 2026):
        p = uri_dir / f"main_{yr}.uri"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            u = line.strip()
            if not u:
                continue
            h = u.rsplit("/", 1)[-1].split("-")[0].split(".")[0]
            url_by_hash[h] = u

    print(f"Total unique benchmarks across SC24/SC25/SC26: {len(url_by_hash)}", flush=True)

    def download_one(item):
        h, url = item
        dst = cache_dir / f"{h}.cnf.xz"
        if dst.exists() and dst.stat().st_size > 20:
            return ("cached", h, dst.stat().st_size)
        tmp = cache_dir / f"{h}.cnf.xz.part"
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FrobeniusBench/1.0"})
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = resp.read()
                if len(data) < 20:
                    raise IOError(f"short read {len(data)} bytes")
                tmp.write_bytes(data)
                tmp.rename(dst)
                return ("ok", h, len(data))
            except Exception as e:
                if attempt == 3:
                    return ("err", h, str(e))
                time.sleep(1.5 * (attempt + 1))

    todo = list(url_by_hash.items())
    t0 = time.time()
    ok = cached = err = 0
    total_bytes = 0
    errs = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for idx, res in enumerate(ex.map(download_one, todo), 1):
            st, h, val = res
            if st == "ok":
                ok += 1
                total_bytes += val
            elif st == "cached":
                cached += 1
                total_bytes += val
            else:
                err += 1
                errs.append((h, val))
            if idx % 100 == 0 or idx == len(todo):
                dt = time.time() - t0
                print(
                    f"[{idx:4}/{len(todo)}] ok={ok} cached={cached} err={err} total={total_bytes/1e9:.2f}GB ({dt:.1f}s)",
                    flush=True,
                )

    if errs:
        print("ERRORS:", errs[:15], flush=True)
    print("DOWNLOAD COMPLETE", flush=True)


if __name__ == "__main__":
    main()
