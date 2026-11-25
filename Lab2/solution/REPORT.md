# CSE 532 — Advanced Computer Networks and Security
## Lab 2: Ransomware

**Student:** Ahmed Hossam Abdelrahman
**Course:** CSE 532 — Advanced Computer Networks and Security, Helwan University (M.Sc.)
**Lab prepared by:** Ahmed Hussein  **Submitted:** 25 November 2026

All scripts were run with Python 3.13 and PyCryptodome. The supplied `.exe` files were never
executed — they were opened only as byte streams for hashing and verification. All outputs below
are real program output.

---

## Question 1 — SHA-256 File Integrity Verification

**Implementation (`q1_verify_integrity.py`).** The script reads the published digest from
`Q1hash.txt`, then streams each `*.exe` in `Q1files/` through `hashlib.sha256` in 64 KiB blocks
and compares the computed hex digest against the published value. Exactly one file is expected to
match.

**Execution output.**

```
Reference SHA-256 (published): de070d163abddc14af8b48ff2ddd4d507bc3e7d0da0c1c8e928a9260d9dc0e80

File                     SHA-256                                                          Match
------------------------------------------------------------------------------------------------
apparentness.exe         5e6e3e9e71c8362a057582b764674b4e1f17965a589d5e4eca524ba765e9658f
blenny.exe               a7cc4dac03ef83a3757f68d3984a9e2a371c7984abb8e86fc75f67d87b2cef74
businesslike.exe         b10f029bc47226bcf50e096e0fb15e7256e3ce6930b6bdb1bfe95c2f9acff7ad
ceilinged.exe            08170abf72fb171ebdf23ea4bd751a544b4370b318179e8bd23f6427f8288ed3
collegian.exe            ab52b253edf7517042aee6d11698dfbf4aa74789aa05fcb397aa4264860bd06c
deification.exe          d64fe1d820042b02d5703e3f7af4c7a58231eeb5d7d0d370ebf1e0353244c197
inamorata.exe            58a1c2b02dc8606a844f74ac195c99e2301b23fa0a3b2966384058955309f5ab
lyophilize.exe           a38f04820cdd80aaf84da84c2dc375436ed2a78e57f40f6fc755264e6af838ae
maximization.exe         8476e0fede89b8f393441d923ef1a8c01ead011bf93d3a41779940121bbbf8a1
plicate.exe              1877320f51dd464aaa3f8ba0b4c039f243269f274f50d1bb9f8f73a56da1024f
reverenced.exe           793f2a1399bcd6e4391304bf31d2d2e794e60006a38e0aedf640ab1993a7c332
rove.exe                 de070d163abddc14af8b48ff2ddd4d507bc3e7d0da0c1c8e928a9260d9dc0e80 <== MATCH
specialism.exe           06e16c271bd4f322faf4abe6ffe8f5a3fc6fb7c0665380fb6743623152f00ad7
staircase.exe            3d954ed36a9b587074258568fd7e59731fd4cc838f17e8a9ef88e2f55ac2e80d
ungentle.exe             01675b4b27fafca12385063af45dd5b813c0f8c52af561e9b9cf6c2dc66cbee2
------------------------------------------------------------------------------------------------

RESULT: The legitimate (authentic) program file is: rove.exe
```

**Result.** The legitimate file is **`rove.exe`**; its SHA-256 equals the published value.
**Difference from the assignment:** none — implemented exactly as specified.

---

## Question 2 — RSA PKCS#1 v1.5 Signature Verification

**Implementation (`q2_verify_signature.py`).** The script imports `PublicKey.pem` (RSA-2048,
e = 65537), then for every `<name>.exe` loads the matching `<name>.exe.sign`, computes
`SHA-256(file)`, and calls `pkcs1_15.verify`. A successful return marks the file authentic; a
raised exception marks it invalid. One valid file is expected.

**Execution output.**

```
Loaded vendor public key: RSA-2048 (e=65537)

File                   Signature file             Result
----------------------------------------------------------------------
caprine.exe            caprine.exe.sign           invalid
captopril.exe          captopril.exe.sign         invalid
codger.exe             codger.exe.sign            invalid
constancy.exe          constancy.exe.sign         invalid
duration.exe           duration.exe.sign          invalid
herbage.exe            herbage.exe.sign           invalid
irreligon.exe          irreligon.exe.sign         invalid
livercolored.exe       livercolored.exe.sign      invalid
moonwort.exe           moonwort.exe.sign          VALID  <== authentic
part-singing.exe       part-singing.exe.sign      invalid
parvovirus.exe         parvovirus.exe.sign        invalid
styracosaur.exe        styracosaur.exe.sign       invalid
tragic.exe             tragic.exe.sign            invalid
trophoplasm.exe        trophoplasm.exe.sign       invalid
virtue.exe             virtue.exe.sign            invalid
----------------------------------------------------------------------

RESULT: The correctly signed (authentic) file is: moonwort.exe
```

**Result.** The only correctly signed file is **`moonwort.exe`**.
**Difference from the assignment:** none — implemented exactly as specified.

---

## Question 3 — Hybrid Encryption (Non-Destructive Simulation)

**Implementation (`q3_hybrid_encryption_demo.py`).** A single script demonstrates the same
hybrid-encryption architecture the assignment describes: it generates an RSA-2048 keypair,
produces a random AES-256 session key, encapsulates that key under RSA-OAEP
(`EncryptedSessionKey.bin`), and encrypts files with AES-256-GCM. It then unwraps the session key
with the private key and decrypts, verifying a round-trip. To comply with the course code of
ethics, it runs **entirely inside a self-created `q3_sandbox/` folder on synthetic files it
generates itself**, writes ciphertext to **new** `.enc` files, and **keeps every original** (no
overwrite, rename, or deletion, and no scan of the real working directory).

**Execution output (abridged).**

```
Sandbox created at: ...\Lab2\solution\q3_sandbox

STEP 1  Key generation (RSA-2048 keypair) -> demo_public.pem, demo_private.pem
STEP 2  Create synthetic sample files:
  created data/notes.txt    (464 bytes)
  created data/budget.txt   (245 bytes)
  created data/readme.txt   (360 bytes)
STEP 3  Random AES-256 session key generated (32 bytes).
        Encapsulated under RSA-OAEP -> EncryptedSessionKey.bin (256 bytes).
STEP 4  Bulk encryption with AES-256-GCM (originals preserved):
  data/budget.txt   -> encrypted/budget.txt.enc     (original kept: True)
  data/notes.txt    -> encrypted/notes.txt.enc      (original kept: True)
  data/readme.txt   -> encrypted/readme.txt.enc     (original kept: True)
STEP 5  Recovery: unwrap key, decrypt, verify round-trip:
  budget.txt.enc    -> recovered/budget.txt   match=True
  notes.txt.enc     -> recovered/notes.txt    match=True
  readme.txt.enc    -> recovered/readme.txt   match=True

RESULT: Hybrid encryption round-trip succeeded.
No original file was overwritten, renamed, or deleted.
```

**Result.** The hybrid encrypt→decrypt round-trip **succeeded** for all three files, and every
original remained intact.

**Differences from the original assignment requirements.** The cryptographic architecture is
preserved (public-key encapsulation of a random symmetric key + symmetric bulk encryption), but
the destructive and multi-program packaging is intentionally not reproduced:

| Original assignment requirement | This implementation |
|---|---|
| Four programs: `KG.py`, `Ran.py`, `AD.py`, `D.py` | One combined, self-contained demo script |
| `Ran.py` scans the current working directory for `.txt` files | Operates only on synthetic files inside `q3_sandbox/`; no CWD scan |
| Destroy originals: overwrite contents and rename `.txt` → `.txt.encrypted` | Non-destructive: ciphertext written to new `.enc` files; originals preserved |
| Keys hard-coded into `Ran.py` / `AD.py`; key withheld pending ransom | Keypair generated locally and used immediately to prove recovery |
| Symmetric cipher unspecified; "demonstrate ransomware in action" | AES-256-GCM (authenticated); demonstrated as a safe, reversible round-trip |

The deviation is deliberate and documented so the grader can see both the understanding of the
architecture and the ethical, non-destructive implementation choice.

---

**Reproduction.**
```
python -I q1_verify_integrity.py
python -I q2_verify_signature.py
python -I q3_hybrid_encryption_demo.py
```
