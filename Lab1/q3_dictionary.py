import time
from common import login_hash, load_login_hashes, load_lines, verify, LAB_DIR

USERS = LAB_DIR / "Q3" / "users"
DICT = LAB_DIR / "Q3" / "LeakedPWs100k"
# Users already cracked in prior questions (updated as we discover them)
ALREADY = {"Magdy", "Mostafa"}  # cracked in Q1/Q2

hashes = load_login_hashes()
users = [u for u in load_lines(USERS) if u not in ALREADY]
targets = {u: hashes[u] for u in users if u in hashes}
pws = load_lines(DICT)

print(f"[Q3] attacking {len(targets)} users with {len(pws)} candidates...")
start = time.perf_counter()
found = None
for i, pw in enumerate(pws):
    for u, t in targets.items():
        if login_hash(u, pw) == t:
            found = (u, pw)
            break
    if found:
        break
    if i and i % 2000 == 0:
        print(f"     ...{i}/{len(pws)} tried  ({time.perf_counter()-start:.1f}s)")
elapsed = time.perf_counter() - start

if found:
    u, pw = found
    print(f"[Q3] user={u}  password={pw}  elapsed={elapsed:.3f}s")
    print(f"     verify: {verify('Q3', u, pw)}")
else:
    print(f"[Q3] NOT FOUND  elapsed={elapsed:.3f}s")
