"""Tier 3 instances: uniform random 3-SAT at clause/variable ratio 4.26, fixed seeds. No shortcut is known for these.
Writes cnf/tier3/*.cnf and prints a sha256 for each. Usage: python tier3.py"""
import os, hashlib, gen
os.makedirs('cnf/tier3', exist_ok=True)
for n in (300, 350, 400, 450, 500):
    for seed in range(1, 6):
        name, _, cl = gen.random3(n, seed); fn = f"cnf/tier3/{name}.cnf"; gen.write(cl, fn)
        print(hashlib.sha256(open(fn, 'rb').read()).hexdigest(), f"tier3/{name}.cnf")
