import time
from common import login_hash, load_login_hashes, load_lines, verify, LAB_DIR

USERS = LAB_DIR / "Q4" / "users"
PWNED = LAB_DIR / "Q4" / "PwnedPWfile"
ALREADY = {"Magdy", "Mostafa"}

hashes = load_login_hashes()
live_users = {u for u in load_lines(USERS) if u not in ALREADY}

# PwnedPWfile is a breach dump: every line is "breachedUser,password".
# A password-reuse attack only needs to test each breached user's own password
# against the same account on our system -- not brute-force all 5001 passwords
# against all live users. Keep breach entries whose account also exists here.
breach = {}
for line in load_lines(PWNED):
    if "," not in line:
        continue
    u, pw = line.split(",", 1)
    if u in live_users and u in hashes:
        breach.setdefault(u, pw)

print(f"[Q4] {len(breach)} breach accounts overlap live users: {sorted(breach)}")
start = time.perf_counter()
found = None
for u, pw in breach.items():
    if login_hash(u, pw) == hashes[u]:
        found = (u, pw)
        break
elapsed = time.perf_counter() - start

if found:
    u, pw = found
    print(f"[Q4] user={u}  password={pw}  elapsed={elapsed:.3f}s")
    print(f"     verify: {verify('Q4', u, pw)}")
else:
    print(f"[Q4] NOT FOUND  elapsed={elapsed:.3f}s")
