"""Bonus: parallelize Q3 across CPU cores using multiprocessing."""
import os
import time
from multiprocessing import Pool, cpu_count
from common import login_hash, load_login_hashes, load_lines, verify, LAB_DIR

USERS = LAB_DIR / "Q3" / "users"
DICT = LAB_DIR / "Q3" / "LeakedPWs100k"
ALREADY = {"Magdy", "Mostafa"}  # already exposed in Q1/Q2; Q3 wants a new user

hashes = load_login_hashes()
users = [u for u in load_lines(USERS) if u not in ALREADY]
TARGETS = {u: hashes[u] for u in users if u in hashes}


def worker(chunk):
    for pw in chunk:
        for u, t in TARGETS.items():
            if login_hash(u, pw) == t:
                return (u, pw)
    return None


def chunked(lst, n):
    k = max(1, len(lst) // n)
    return [lst[i:i + k] for i in range(0, len(lst), k)]


if __name__ == "__main__":
    pws = load_lines(DICT)
    n = cpu_count()
    chunks = chunked(pws, n)
    print(f"[Bonus] {len(pws)} pws across {n} workers ({len(chunks)} chunks)")

    start = time.perf_counter()
    found = None
    with Pool(n) as pool:
        for result in pool.imap_unordered(worker, chunks):
            if result is not None:
                found = result
                pool.terminate()
                break
    elapsed = time.perf_counter() - start

    if found:
        u, pw = found
        print(f"[Bonus] user={u}  password={pw}  elapsed={elapsed:.3f}s")
        print(f"        verify: {verify('Q3', u, pw)}")
    else:
        print(f"[Bonus] NOT FOUND  elapsed={elapsed:.3f}s")
