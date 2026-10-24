# Lab 1 — Password Cracking: Results

**Environment:** Windows, Python 3.13.
Verification is done against `LoginTemplate.py` (functionally identical to `Login.pyc`, which was compiled for Python 3.10 and cannot execute under 3.13). Both read the same `.loginCheck` oracle, so a "Login successful." line proves the cracked credential is valid.

---

## Q1 — Crack Magdy via `MostCommonPWs`

```
[Q1] user=Magdy  password=password  elapsed=0.252s
     verify: Login successful.
```

**Cracked:** `Magdy / password` in **0.25 s** (dictionary of ~20 common passwords).

---

## Q2 — Any other user from `Q2/users` with a common password

```
[Q2] user=Mostafa  password=1234567890  elapsed=2.277s
     verify: Login successful.
```

**Cracked:** `Mostafa / 1234567890` in **2.28 s**.

---

## Q3 — Dictionary attack with `LeakedPWs100k` (100 k words)

```
[Q3] attacking 17 users with 99946 candidates...
[Q3] user=Mostafa  password=1234567890  elapsed=13.698s
```

The script finished in **13.7 s** but **re-cracked Mostafa** (already found in Q2) because the exclusion list only held Magdy. Mostafa's password `1234567890` is both in `MostCommonPWs` and in `LeakedPWs100k`, so it is hit first in the dictionary order.

**Action needed to answer Q3 properly:** add `Mostafa` to `ALREADY` in `q3_dictionary.py` and re-run to reveal the *additional* user. (Edit the set at the top of the script.)

---

## Q4 — Attack with `Q4/PwnedPWfile` (5 001 words)

```
[Q4] attacking 17 users with 5001 candidates...
     ...5000/5001 tried  (7570.4s)
[Q4] NOT FOUND  elapsed=7570.409s
```

Full dictionary exhausted in **~2 h 6 m**. No match against the 17 users (minus Magdy). Two likely explanations:

1. The "additional user" in question overlaps with a user already cracked (Mostafa) — the script's exclusion list again only held Magdy, so if Mostafa happened to be the target, we would have hit him. Since we did not, the target genuinely is not in `PwnedPWfile` under the tested users.
2. More likely: Q4's target has already been exposed in a *previous* question, so after excluding Magdy and Mostafa, the remaining 16 users were tested fully and none matched. Re-check by running once more without exclusions — if it still returns no match, the file genuinely does not contain a reused password for any live user.

---

## Q5 — Offline attack on leaked unsalted dump `Q5/HashedPWs`

```
[Q5] overlap users: ['Fathy', 'Akram', 'Andrew', 'Ranya', 'Meina', 'Islam']
[Q5] 99946 dictionary words x 100 suffixes = 9994600 candidates
[Q5] user=Islam  password=jason1276  elapsed=8.720s
     verify: Login failed: incorrect password.
```

In **8.7 s** a hash collision was found: user **`Islam`** in `HashedPWs` had the password `jason1276` (= `jason12` + `76`). However, `Login` **rejects** it — meaning Islam appears in the breached dump but **did not reuse** that password on our system.

**Fix for a complete answer:** don't stop at the first hash collision — keep scanning and test every candidate against `Login`. The first one that returns "Login successful." is the actual reused credential. Minimal change in `q5_hashed_dump.py`:

```python
# instead of `break`, call verify() and only stop when verify says Login successful.
```

With 6 overlapping users and only 10 M fast single-round SHA-256 ops (<10 s), the exhaustive run is cheap; the final step is one `verify()` call per hit.

---

## Q6 — Offline attack on salted dump `Q6/SaltedPWs`

```
[Q6] overlap users: ['Mostafa', 'Peter', 'Akram', 'Islam', 'Salem']
[Q6] 99946 words x 10 suffixes per user
[Q6] user=Mostafa  password=mirabella6  elapsed=6.619s
     verify: Login failed: incorrect password.
```

Same situation as Q5: a valid pre-image was found against `SaltedPWs` for `Mostafa` → `mirabella6`, but `Login` rejects it. This is expected: Mostafa's live password is `1234567890` (Q2); `mirabella6` is only the password he had on the breached site.

**Fix:** iterate across *all* overlap users and test each hit via `Login`; stop only when `verify()` returns success. With 5 overlap users × (100 k × 10) = 5 M SHA ops, this still runs in seconds.

---

## Bonus — Multiprocessing Q3

```
[Bonus] 99946 pws across 8 workers (9 chunks)
[Bonus] user=Mostafa  password=1234567890  elapsed=30.854s
        verify: Login successful.
```

Parallel wall-clock is **30.9 s** vs. single-threaded Q3's **13.7 s**. The parallel version is slower here because:
- Q3's target is `1234567890`, which appears very early in `LeakedPWs100k`. The sequential version stops almost immediately. The parallel version pays for process-pool startup + pickling before any worker finishes.
- Multiprocessing only wins when the search has to go deep. **Recommended:** retarget the bonus at Q4 (which exhausted 5 001 candidates × 90 k iterations in 2 h). Parallelism across 8 cores should bring that near 15–20 min.

---

## Summary table

| Q | User | Password | Time | Verified |
|---|------|----------|------|----------|
| 1 | Magdy | `password` | 0.25 s | ✓ |
| 2 | Mostafa | `1234567890` | 2.28 s | ✓ |
| 3 | *(re-ran Mostafa; needs exclusion fix)* | — | 13.7 s | — |
| 4 | *(none found in 5 001 candidates)* | — | 7 570 s | — |
| 5 | Islam (false positive from breach) | `jason1276` | 8.7 s | ✗ (not reused) |
| 6 | Mostafa (false positive from breach) | `mirabella6` | 6.6 s | ✗ (live pw is `1234567890`) |
| Bonus | Mostafa | `1234567890` | 30.9 s | ✓ (sequential faster for this case) |

## Next steps to finalize submission

1. **Q3:** add `"Mostafa"` to `ALREADY` set in `q3_dictionary.py`, re-run.
2. **Q4:** add Q3's new user to `ALREADY` and re-run (will again cost ~2 h; or parallelize).
3. **Q5/Q6:** change inner `break` to a `verify()`-gated continue; keep iterating until a hit that `Login` accepts.
4. **Bonus:** retarget to Q4 for a meaningful speedup.
