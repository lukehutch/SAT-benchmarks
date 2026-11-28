#!/usr/bin/env python3
"""Download deduplicated SAT Competition & SAT-Race CNF benchmarks (2002–2026) from GBD URI manifests.

Examples:
  # Fetch SC 2023–2026 Main Track (1,548 unique CNFs, default)
  python3 src/download_sc_main.py

  # Fetch specific tracks (e.g. Planning 2020 + Crypto 2021)
  python3 src/download_sc_main.py --tracks planning_2020,crypto_2021

  # Fetch the entire 2002–2026 archive across all 62 track manifests (20,225 unique CNFs)
  python3 src/download_sc_main.py --all
"""
import argparse
import concurrent.futures
import pathlib
import time
import urllib.error
import urllib.request

DEFAULT_URI_DIR = pathlib.Path(__file__).resolve().parent.parent / "uris"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uri-dir", default=str(DEFAULT_URI_DIR), help="Directory containing <track>_<year>.uri manifests")
    ap.add_argument(
        "--tracks",
        default="main_2023,main_2024,main_2025,main_2026",
        help="Comma-separated track names (stems without .uri); ignored when --all is set",
    )
    ap.add_argument("--all", action="store_true", help="Download all *.uri manifests in --uri-dir")
    ap.add_argument("--cache-dir", default=str(pathlib.Path.home() / ".cache/sc-main-cnfs"))
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    cache_dir = pathlib.Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    uri_dir = pathlib.Path(args.uri_dir)

    if args.all:
        uri_files = sorted(uri_dir.glob("*.uri"))
    else:
        uri_files = []
        for tr in (t.strip() for t in args.tracks.split(",") if t.strip()):
            p = uri_dir / (tr if tr.endswith(".uri") else f"{tr}.uri")
            if p.exists():
                uri_files.append(p)
            else:
                print(f"WARNING: manifest not found: {p}", flush=True)

    url_by_hash = {}
    for p in uri_files:
        for line in p.read_text(encoding="utf-8").splitlines():
            u = line.strip()
            if not u or u.startswith("#"):
                continue
            h = u.rsplit("/", 1)[-1].split("-")[0].split(".")[0]
            url_by_hash[h] = u

    print(
        f"Total unique benchmarks across {len(uri_files)} manifest(s): {len(url_by_hash):,}",
        flush=True,
    )

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
                    f"[{idx:5}/{len(todo)}] ok={ok} cached={cached} err={err} total={total_bytes/1e9:.2f}GB ({dt:.1f}s)",
                    flush=True,
                )

    if errs:
        print("ERRORS:", errs[:15], flush=True)
    print("DOWNLOAD COMPLETE", flush=True)


if __name__ == "__main__":
    main()
