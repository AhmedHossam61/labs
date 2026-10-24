import time
from common import login_hash, load_login_hashes, load_lines, verify, LAB_DIR

USER = "Magdy"
DICT = LAB_DIR / "Q1" / "MostCommonPWs"

hashes = load_login_hashes()
target = hashes[USER]
pws = load_lines(DICT)

start = time.perf_counter()
found = None
for pw in pws:
    if login_hash(USER, pw) == target:
        found = pw
        break
elapsed = time.perf_counter() - start

if found:
    print(f"[Q1] user={USER}  password={found}  elapsed={elapsed:.3f}s")
    print(f"     verify: {verify('Q1', USER, found)}")
else:
    print(f"[Q1] NOT FOUND  elapsed={elapsed:.3f}s")
