"""Exact checks of Corollary 1 (pattern-class bound) and the GF(2^8) Lagrange identity used in Theorem 6."""
import collections
import itertools
import random


def pattern(p):
    m = {}
    return tuple(m.setdefault(x, len(m)) for x in p)


for n in (4, 6):
    classes = collections.Counter(pattern(p) for p in itertools.product(range(10), repeat=n))
    bound = sum(min(10, v) for v in classes.values()) / 10 ** n
    print(f"{n}-digit PINs: {len(classes)} patterns, smallest class {min(classes.values())}, 10-guess cap {bound:.5f}")
for n, total in ((4, 5040), (6, 151200)):
    print(f"{n}-digit PINs, distinct digits only: 10-guess cap {10 / total:.6f}")


def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r


def gf_inv(a):
    return next(x for x in range(1, 256) if gf_mul(a, x) == 1)


xs = {"D": 1, "P": 2, "R": 3}
for _ in range(2000):
    s, a = random.randrange(256), random.randrange(256)
    shares = {k: s ^ gf_mul(a, x) for k, x in xs.items()}
    for j, k in (("D", "P"), ("D", "R"), ("P", "R")):
        d = gf_inv(xs[j] ^ xs[k])
        lj, lk = gf_mul(xs[k], d), gf_mul(xs[j], d)
        assert gf_mul(lj, shares[j]) ^ gf_mul(lk, shares[k]) == s
print("Shamir 2-of-3 reconstruction over GF(2^8): OK for all share pairs")
