import time
from common import login_hash, load_login_hashes, load_lines, verify, LAB_DIR

USERS = LAB_DIR / "Q2" / "users"
DICT = LAB_DIR / "Q2" / "MostCommonPWs"
ALREADY = {"Magdy"}

hashes = load_login_hashes()
users = [u for u in load_lines(USERS) if u not in ALREADY]
pws = load_lines(DICT)

start = time.perf_counter()
found = None
for user in users:
    target = hashes.get(user)
    if target is None:
        continue
    for pw in pws:
        if login_hash(user, pw) == target:
            found = (user, pw)
            break
    if found:
        break
elapsed = time.perf_counter() - start

if found:
    u, pw = found
    print(f"[Q2] user={u}  password={pw}  elapsed={elapsed:.3f}s")
    print(f"     verify: {verify('Q2', u, pw)}")
else:
    print(f"[Q2] NOT FOUND  elapsed={elapsed:.3f}s")
