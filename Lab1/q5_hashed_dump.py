import time
from common import sha256_hex, load_lines, verify, LAB_DIR

USERS = LAB_DIR / "Q5" / "users"
HASHED = LAB_DIR / "Q5" / "HashedPWs"
DICT = LAB_DIR / "Q5" / "LeakedPWs100k"
ALREADY = {"Magdy", "Mostafa"}

leaked = {}
for line in load_lines(HASHED):
    u, h = line.split(",")
    leaked[u] = h

targets = {u: leaked[u] for u in load_lines(USERS) if u in leaked and u not in ALREADY}
print(f"[Q5] overlap users: {list(targets)}")

hash_to_user = {h: u for u, h in targets.items()}
pws = load_lines(DICT)
print(f"[Q5] {len(pws)} dictionary words x 100 suffixes = {len(pws)*100} candidates")

start = time.perf_counter()
hits = []  # (user, candidate) collisions in leaked dump
for pw in pws:
    for dd in range(100):
        cand = f"{pw}{dd:02d}"
        hh = sha256_hex(cand)
        if hh in hash_to_user:
            hits.append((hash_to_user[hh], cand))
scan_elapsed = time.perf_counter() - start
print(f"[Q5] leaked-hash scan done in {scan_elapsed:.3f}s; {len(hits)} collisions")

# A collision only means the user reused that password on the breached site.
# Confirm via Login (which uses the salted+iterated scheme on .loginCheck).
found = None
for u, pw in hits:
    out = verify("Q5", u, pw)
    print(f"     candidate {u}/{pw} -> {out}")
    if "successful" in out.lower():
        found = (u, pw)
        break
elapsed = time.perf_counter() - start

if found:
    u, pw = found
    print(f"[Q5] user={u}  password={pw}  elapsed={elapsed:.3f}s")
else:
    print(f"[Q5] no reused password verified against Login  elapsed={elapsed:.3f}s")
