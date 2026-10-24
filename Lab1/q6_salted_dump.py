import time
from common import sha256_hex, load_lines, verify, LAB_DIR

USERS = LAB_DIR / "Q6" / "users"
SALTED = LAB_DIR / "Q6" / "SaltedPWs"
DICT = LAB_DIR / "Q6" / "LeakedPWs100k"
ALREADY = {"Magdy", "Mostafa"}

salted = {}
for line in load_lines(SALTED):
    u, s, h = line.split(",")
    salted[u] = (s, h)

targets = {u: salted[u] for u in load_lines(USERS) if u in salted and u not in ALREADY}
print(f"[Q6] overlap users: {list(targets)}")

pws = load_lines(DICT)
print(f"[Q6] {len(pws)} words x 10 suffixes per user")

start = time.perf_counter()
hits = []  # collisions in salted dump
for user, (salt, h) in targets.items():
    for pw in pws:
        for d in range(10):
            cand = f"{pw}{d}"
            if sha256_hex(salt + cand) == h:
                hits.append((user, cand))
                break
        else:
            continue
        break  # one hit per user is enough (salt makes each unique)
scan_elapsed = time.perf_counter() - start
print(f"[Q6] salted-hash scan done in {scan_elapsed:.3f}s; {len(hits)} collisions")

# Confirm each collision against Login — only the user who actually reused the
# password on our system will authenticate.
found = None
for u, pw in hits:
    out = verify("Q6", u, pw)
    print(f"     candidate {u}/{pw} -> {out}")
    if "successful" in out.lower():
        found = (u, pw)
        break
elapsed = time.perf_counter() - start

if found:
    u, pw = found
    print(f"[Q6] user={u}  password={pw}  elapsed={elapsed:.3f}s")
else:
    print(f"[Q6] no reused password verified against Login  elapsed={elapsed:.3f}s")
