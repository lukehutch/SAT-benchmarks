"""Independently download the public inputs and verify source and benchmark hashes."""
import argparse
from collections import defaultdict
import hashlib
import io
import lzma
from pathlib import Path
import re
import tarfile
import tempfile
from urllib.request import urlopen

from public_suite import DEFAULT_MANIFEST, read_manifest


def verify_input(row, raw):
    if hashlib.sha256(raw).hexdigest() != row["source_sha256"]:
        raise ValueError(f"Upstream input checksum mismatch: {row['id']}")
    # The uniform random SATLIB files end with a legacy percent and zero trailer.
    data = re.sub(rb"(?m)^%\s*\n0\s*\Z", b"", raw)
    if hashlib.sha256(data).hexdigest() != row["input_sha256"]:
        raise ValueError(f"Benchmark input checksum mismatch: {row['id']}")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new directory for verified CNFs")
    args = parser.parse_args()
    target = args.output.resolve()
    if target.exists():
        parser.error("choose a new output directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    sources = defaultdict(list)
    for row in read_manifest(DEFAULT_MANIFEST):
        sources[row["url"]].append(row)
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        staged = Path(tmp) / "inputs"
        staged.mkdir()
        for url, rows in sources.items():
            with urlopen(url, timeout=60) as response:
                blob = response.read()
            if rows[0]["member"]:
                with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
                    for row in rows:
                        with archive.extractfile(row["member"]) as inp:
                            data = verify_input(row, inp.read())
                        (staged / (row["id"] + ".cnf")).write_bytes(data)
            else:
                for row in rows:
                    data = verify_input(row, lzma.decompress(blob))
                    (staged / (row["id"] + ".cnf")).write_bytes(data)
        staged.rename(target)
    print(f"Verified {sum(map(len, sources.values()))} inputs in {target}")


if __name__ == "__main__":
    main()
