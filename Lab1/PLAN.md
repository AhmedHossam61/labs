# Lab 1 — Password Cracking: Implementation Plan

## Target hash function (from `LoginTemplate.py`)

```
H(user, pw) = sha256_iter( sha256(user || pw) , 90_000 )
# where sha256_iter does: for _ in range(90000): h.update(h.digest())
```

- `../.loginCheck` holds `user,hashedPW` pairs — this is the oracle for all cracking.
- Cracking is done **offline** against `.loginCheck` (never shell out to `Login.pyc` in the inner loop — too slow).
- `Login.pyc` is only used at the end to **verify** each cracked credential.

## Shared helpers (`common.py`)

- `load_users(path)` → list[str]
- `load_hashes(path=".loginCheck")` → dict[user → hash]
- `login_hash(user, pw)` → hex digest using the 90k iteration scheme
- `sha256_hex(s)` → simple one-shot for Q5/Q6
- `verify(user, pw)` → `subprocess.run(["python", "Login.pyc", user, pw])`
- Timing wrapper that prints `user`, `password`, `elapsed`.

Precompute `hashes = load_hashes()` once per script; also build a **reverse index** `hash_to_user` so each candidate hash is checked in O(1) against all users at once (critical for Q2–Q4 speedup).

---

## Q1 — Crack Magdy with `MostCommonPWs` (10 pts)

1. Load `Q1/MostCommonPWs` (~20 words).
2. For each pw: compute `login_hash("Magdy", pw)`; compare to `hashes["Magdy"]`.
3. Print pw + runtime; call `python Q1/Login.pyc Magdy <pw>` to verify.

Expected: trivial, <1s per candidate × ~20 = fast.

---

## Q2 — Find any user in `Q2/users` with a `MostCommonPWs` password (10 pts)

1. Load user list and dictionary.
2. Loop `pw` outer, `user` inner (recomputes per user — unavoidable since user is salted into hash). Compare to `hashes[user]`.
3. Stop at first hit (excluding Magdy).

Complexity: |users| × |dict| × 90k iterations. ~18 × 20 = 360 candidates — still seconds.

---

## Q3 — Dictionary attack with `LeakedPWs100k` (10 pts)

Same as Q2 but with 100k dictionary.
- Cost: 18 × 100k = 1.8M expensive hashes. Will take minutes.
- Optimizations: skip users already cracked in Q1/Q2; print progress every N candidates.
- Candidate for the **Bonus** multithreading task (split dictionary across threads/processes; use `multiprocessing.Pool` since Python threads can't parallelize CPU-bound SHA work — GIL).

---

## Q4 — Pwned-password reuse (`Q4/PwnedPWfile`) (10 pts)

Identical structure to Q3 but using `PwnedPWfile`.
- Skip previously cracked users.
- Report first new hit + runtime; verify via `Login.pyc`.

---

## Q5 — Offline attack on leaked hash dump (`Q5/HashedPWs`) (10 pts)

`HashedPWs` lines: `user,hash` where `hash = sha256(password || dd)` (plain SHA-256, dd = 2 digits).

1. Load `HashedPWs` into dict `leaked = {user: hash}`.
2. Intersect `Q5/users` with `leaked.keys()` → candidate users to attack.
3. For each candidate user:
   - For each pw in `LeakedPWs100k`:
     - For dd in `00..99`: compute `sha256_hex(pw + dd)`; compare to `leaked[user]`.
   - On match: that's the plaintext password.
4. Verify against `Login.pyc` (uses the full 90k-iter scheme on `user+password`).

Cost per user: 100k × 100 = 10M SHA-256 (single-round) — order of a minute per user. Cheaper than Q3 because single-round SHA.

Optimization: build `hash_to_user = {hash: user}` from the leaked file so a single candidate hash is tested against **all** users in one dict lookup → one pass over (pw, dd) finds every reused credential at once.

---

## Q6 — Salted leaked file (`Q6/SaltedPWs`) (10 pts)

Lines: `user,salt,h(salt||pw)` where pw = leaked-pw + 1 digit, `h = sha256`.

1. Load `SaltedPWs` into `{user: (salt, hash)}`.
2. Intersect with `Q6/users`.
3. Per-salt attack is unavoidable (salt kills the reverse-index trick across users). For each target user:
   - For each pw in `LeakedPWs100k`:
     - For d in `0..9`: `sha256_hex(salt + pw + d)` vs stored hash.
4. Verify via `Login.pyc`.

Cost per user: 100k × 10 = 1M SHA. Fast.

---

## Bonus — Multithreading (10 pts)

Pick **Q3** (slowest). Use `multiprocessing.Pool`:
- Split `LeakedPWs100k` into N chunks (N = `os.cpu_count()`).
- Worker function: iterate chunk × users; return first match.
- Use `pool.imap_unordered` and `terminate()` on first hit.
- Report wall-clock vs single-threaded run for comparison in the report.

(Threads won't help — SHA-256 is CPU-bound and GIL-locked; must use processes.)

---

## File layout to produce

```
Lab1/
  common.py            # shared helpers
  q1_crack_magdy.py
  q2_crack_users.py
  q3_dictionary.py
  q4_pwned.py
  q5_hashed_dump.py
  q6_salted_dump.py
  bonus_q3_parallel.py
  REPORT.md            # results: user, password, runtime per question
```

Each script prints:
```
[Qn] user=<x> password=<y> elapsed=<s> seconds
Verification: <output of Login.pyc>
```

## Execution order

1. Implement `common.py` + reverse-index helpers.
2. Q1 → confirm hash scheme matches `.loginCheck`.
3. Q2 → Q4 share the same oracle; reuse code.
4. Q5, Q6 use their own leaked files (no 90k iteration during cracking).
5. Bonus parallelizes Q3.
6. Fill `REPORT.md` with cracked `(user, password, runtime)` tuples and verification screenshots/logs.
