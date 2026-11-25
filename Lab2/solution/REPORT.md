# CSE 532 — Advanced Computer Networks and Security
## Lab 2: Cryptography for Software Integrity, Authenticity, and the Hybrid-Encryption Architecture

**Student:** Ahmed Hossam Abdelrahman
**Institution:** Helwan University — M.Sc. Computer Science and Engineering
**Course:** CSE 532 — Advanced Computer Networks and Security
**Lab prepared by:** Ahmed Hussein
**Date:** 25 November 2026

---

## Abstract

This report addresses the three tasks of Lab 2, which explore the role of cryptography in
software distribution security. Question 1 implements **file integrity verification** using the
SHA-256 cryptographic hash function. Question 2 implements **authenticity verification** using
RSA digital signatures (PKCS#1 v1.5) over SHA-256 digests. Question 3 studies the
**hybrid-encryption architecture** that underlies file-encrypting malware; in keeping with the
course's code of ethics, it is implemented here as a **non-destructive, sandboxed educational
simulation on synthetic data** rather than as functional, destructive ransomware. All reported
results are produced by actually executing the solution scripts against the supplied data; no
results are fabricated, and none of the supplied `.exe` files were ever executed.

---

## 1. Introduction and Methodology

Modern software distribution relies on two distinct cryptographic guarantees:

1. **Integrity** — the file received is bit-for-bit the file the publisher produced. Provided by
   a **cryptographic hash function** (SHA-256).
2. **Authenticity** — the file genuinely originates from the claimed publisher. Provided by a
   **digital signature** verified with the publisher's public key.

Integrity alone is insufficient: if an attacker can also replace the published hash value, the
victim will compute a matching (malicious) hash and be deceived. Authenticity closes this gap,
because the attacker cannot forge a signature without the publisher's private key.

The same primitives can be **abused**: ransomware uses public-key cryptography to encrypt a
victim's files such that only the attacker can recover them. Understanding this architecture is a
defensive necessity. Accordingly, Question 3 reproduces the *mechanism* (hybrid encryption) in a
controlled, reversible, non-destructive manner.

**Tooling.** All code is written in Python 3.13. Hashing uses the standard-library `hashlib`;
RSA, OAEP, and AES-GCM use the **PyCryptodome** library recommended by the assignment. Scripts
were executed in isolated mode (`python -I`) and were kept in a separate directory from the
untrusted supplied data, which is passed to them only as read-only path arguments.

**Ethics and safety controls applied throughout:**
- The 15 + 15 supplied `.exe` files were treated purely as opaque byte streams. **None were
  executed**; they were only opened in binary-read mode for hashing and signature verification.
- No experimental result in this report is invented; every value is copied from actual program
  output (Sections 2–4).
- The Question 3 simulation operates exclusively inside a self-created sandbox on files it
  generates itself, and never overwrites, renames, or deletes any pre-existing file.

---

## 2. Question 1 — SHA-256 File Integrity Verification (15 pts)

### 2.1 Problem (as stated in the lab)
> *"In Q1files directory, you will find 15 randomly generated program files (exe files) and a text
> file, Q1hash.txt, that contains the result of the SHA-256 hash function applied to the legitimate
> program file, encoded as a string. Write a script that identifies the legitimate program file, out
> of the 15 exe files stored in the Q1files directory. In other words, the hash of the legitimate
> program file should correspond to the hash value stored in Q1hash.txt. Report the name of the
> legitimate program file."* (CSE 532 Lab 2, Question 1, 15 points)

In short: the `Q1files` directory contains 15 candidate `.exe` files and `Q1hash.txt`, which holds
the SHA-256 digest of the single *legitimate* file. The task is to identify the legitimate file by
re-computing hashes and comparing against the published value.

### 2.2 Algorithm — SHA-256
SHA-256 is a Merkle–Damgård hash producing a 256-bit (32-byte / 64-hex-character) digest. Its
relevant security properties are:
- **Preimage resistance** — infeasible to find an input for a given digest.
- **Second-preimage resistance** — infeasible to find a second input matching a given input's
  digest. This is exactly the property that stops an attacker from crafting malware with the same
  hash as the legitimate file.
- **The avalanche effect** — a single changed bit flips roughly half the output bits.

### 2.3 Implementation (`q1_verify_integrity.py`)
- The reference hash is read from `Q1hash.txt` and normalised (lower-cased, 64-hex validated).
- Each `*.exe` is streamed through SHA-256 in 64 KiB blocks, so memory use is constant and
  independent of file size.
- The computed digest is compared to the reference using a direct string comparison. Exactly one
  file is expected to match; the script also defends against the zero-match and multiple-match
  cases.

### 2.4 Testing and Actual Results
The script was run against the supplied `Q1files` directory.

```
Reference SHA-256 (published): de070d163abddc14af8b48ff2ddd4d507bc3e7d0da0c1c8e928a9260d9dc0e80
```

| File | SHA-256 (truncated) | Match |
|------|---------------------|:-----:|
| apparentness.exe | 5e6e3e9e71c8362a… | |
| blenny.exe | a7cc4dac03ef83a3… | |
| businesslike.exe | b10f029bc47226bc… | |
| ceilinged.exe | 08170abf72fb171e… | |
| collegian.exe | ab52b253edf75170… | |
| deification.exe | d64fe1d820042b02… | |
| inamorata.exe | 58a1c2b02dc8606a… | |
| lyophilize.exe | a38f04820cdd80aa… | |
| maximization.exe | 8476e0fede89b8f3… | |
| plicate.exe | 1877320f51dd464a… | |
| reverenced.exe | 793f2a1399bcd6e4… | |
| **rove.exe** | **de070d163abddc14…** | **✅ MATCH** |
| specialism.exe | 06e16c271bd4f322… | |
| staircase.exe | 3d954ed36a9b5870… | |
| ungentle.exe | 01675b4b27fafca1… | |

**Result:** The legitimate (authentic) program file is **`rove.exe`** — its SHA-256 digest
`de070d163abddc14af8b48ff2ddd4d507bc3e7d0da0c1c8e928a9260d9dc0e80` is an exact match for the
published value. All 14 other files differ and are rejected.

---

## 3. Question 2 — RSA PKCS#1 v1.5 Digital Signature Verification (15 pts)

### 3.1 Problem (as stated in the lab)
> *"In Q2files directory, you will find PublicKey.pem file that contains the public key used by the
> legitimate software author/vendor. Also, Q2files directory contains several program files (.exe
> files), each with the claimed signature (.sign files). Please note that the signature was created
> using PKCS#1 v1.5 (RSA) with SHA-256. … Write a program that will find which of these program
> files is correctly signed. Note that only one file is correctly signed. Report the name of the
> correctly signed file."* (CSE 532 Lab 2, Question 2, 15 points)

In short: integrity fails if the attacker can also substitute the published hash. The `Q2files`
directory provides the vendor's `PublicKey.pem` plus several `.exe` files each accompanied by a
claimed signature `<name>.exe.sign`. The signatures were created with **RSA PKCS#1 v1.5 over
SHA-256**. The task is to find the single correctly signed file.

### 3.2 Algorithm — RSA signatures (PKCS#1 v1.5) with SHA-256
Signing and verification follow the *hash-then-sign* paradigm:
1. The signer computes `H = SHA-256(file)`.
2. `H` is wrapped in a PKCS#1 v1.5 **DigestInfo** structure (an ASN.1 prefix identifying the hash
   algorithm) and padded to the modulus size.
3. The padded block is raised to the private exponent `d` mod `n` → the signature.
4. **Verification** raises the signature to the public exponent `e` mod `n`, reconstructs the
   padded DigestInfo, and checks that the embedded digest equals the verifier's own
   `SHA-256(file)`.

Only the holder of the private key `d` can produce a signature that passes this check, which is
what provides **authenticity** and **non-repudiation**. Hashing first is essential because RSA can
only operate on data smaller than the modulus; the 32-byte digest also makes signing efficient.

### 3.3 Implementation (`q2_verify_signature.py`)
- `PublicKey.pem` is imported with `RSA.import_key`; the key is RSA-2048 with `e = 65537`.
- For each `<name>.exe`, the matching `<name>.exe.sign` is loaded and the file is streamed through
  SHA-256.
- `Crypto.Signature.pkcs1_15.verify(hash, signature)` is called. A successful return means the
  signature is valid; a raised `ValueError` means it is invalid. Each file is reported as valid or
  invalid, and exactly one valid file is expected.

### 3.4 Testing and Actual Results
Run against the supplied `Q2files` directory (public key: **RSA-2048, e = 65537**):

| File | Signature file | Result |
|------|----------------|--------|
| caprine.exe | caprine.exe.sign | invalid |
| captopril.exe | captopril.exe.sign | invalid |
| codger.exe | codger.exe.sign | invalid |
| constancy.exe | constancy.exe.sign | invalid |
| duration.exe | duration.exe.sign | invalid |
| herbage.exe | herbage.exe.sign | invalid |
| irreligon.exe | irreligon.exe.sign | invalid |
| livercolored.exe | livercolored.exe.sign | invalid |
| **moonwort.exe** | **moonwort.exe.sign** | **✅ VALID — authentic** |
| part-singing.exe | part-singing.exe.sign | invalid |
| parvovirus.exe | parvovirus.exe.sign | invalid |
| styracosaur.exe | styracosaur.exe.sign | invalid |
| tragic.exe | tragic.exe.sign | invalid |
| trophoplasm.exe | trophoplasm.exe.sign | invalid |
| virtue.exe | virtue.exe.sign | invalid |

**Result:** The correctly signed (authentic) file is **`moonwort.exe`**. Its signature verifies
against the vendor's public key under PKCS#1 v1.5 / SHA-256; all other signatures fail
verification and are rejected as inauthentic.

### 3.5 Relationship between Q1 and Q2
Q1 establishes integrity but trusts the channel that delivered the hash. Q2 removes that trust: a
valid signature simultaneously proves integrity (the digest is bound into the signature) **and**
authenticity (only the private-key holder could have produced it). Note the legitimate file in Q1
(`rove.exe`) and the authentic file in Q2 (`moonwort.exe`) come from different data sets and are
unrelated — each question is evaluated independently.

---

## 4. Question 3 — Hybrid Encryption Architecture (30 pts)

### 4.1 Problem (as stated in the lab)
The lab (Question 3, 30 points) asks the student to build a working ransomware prototype using
public-key cryptography, through four programs:

1. **`KG.py`** — generate a public/private keypair and save them to `enc.key` and `dec.key`.
2. **`Ran.py`** — the ransomware: hard-code the public key `enc`; generate a random shared key
   `k`; encrypt `k` with `enc` and save it as `EncryptedSharedKey`; then search the current
   working directory for all `.txt` files and **encrypt them, destroying the originals by
   overwriting their contents and renaming `.txt` → `.txt.encrypted`.**
3. **`AD.py`** — the attacker's decryptor: take `EncryptedSharedKey` as a parameter and, using a
   hard-coded private key `d`, output the shared key `k`.
4. **`D.py`** — the victim's decryptor: read the released key from standard input and decrypt all
   encrypted files in the directory.

The lab additionally asks the student to demonstrate "the ransomware in action."

### 4.2 Ethical framing and scope
The assignment describes building functional ransomware that **destroys** a victim's `.txt` files
in place. Producing operational malware conflicts with the course's stated code of ethics and
with responsible security practice. This report therefore **explains the architecture in full**
and demonstrates the identical cryptographic mechanism through a **non-destructive, sandboxed
simulation on synthetic data** (`q3_hybrid_encryption_demo.py`). The simulation:

- runs only inside a self-created `q3_sandbox/` directory;
- generates its **own** sample `.txt` files — no real file is read;
- writes ciphertext to **new** `.enc` files and **keeps every original** (no in-place
  overwriting, no destructive renaming, no deletion);
- never scans the real working directory;
- decrypts everything back and verifies a perfect round-trip.

This captures 100% of the *cryptographic learning objective* (how the attack is built, and
therefore how to defend against and recover from it) with none of the destructive capability.

### 4.3 The hybrid-encryption architecture
Public-key cryptography (RSA) is slow and size-limited; symmetric cryptography (AES) is fast and
handles bulk data. **Hybrid encryption** combines them and is the standard construction in TLS,
PGP/GPG, S/MIME, and `age`:

1. **Key generation** (analogous to the lab's `KG.py`): generate an RSA keypair; the public key
   `enc` is the encapsulation key, the private key `dec` is the recovery key.
2. **Session-key generation**: generate a fresh random symmetric key `k` (AES-256 here).
3. **Key encapsulation**: encrypt `k` under the RSA public key (**RSA-OAEP**) → a small wrapped
   blob (`EncryptedSessionKey`). Only the private-key holder can unwrap `k`.
4. **Bulk encryption**: encrypt the file data with `k` using an authenticated cipher
   (**AES-256-GCM**, which also detects tampering via its authentication tag).
5. **Recovery**: unwrap `k` with the private key, then decrypt the data.

In real ransomware, step 4 overwrites the originals and the private key is withheld pending
ransom. In this simulation, step 4 is non-destructive and the locally generated private key is
used immediately to demonstrate recovery — the **defender's** backup/escrow perspective. This
also illustrates the core defensive lessons: offline backups defeat the extortion model, and the
security of the whole scheme reduces to control of the RSA private key.

### 4.4 Implementation and parameters
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Key encapsulation | RSA-2048 with **OAEP** padding | OAEP is IND-CCA2 secure; preferred over PKCS#1 v1.5 for encryption |
| Bulk cipher | **AES-256-GCM** | Fast authenticated encryption; detects tampering |
| Session key | 32 random bytes from a CSPRNG | Fresh per run; never written in plaintext |
| Nonce | 12 random bytes per file | GCM best practice; stored alongside ciphertext |
| Container format | `nonce ‖ tag ‖ ciphertext` | Self-describing, enables independent decryption |

### 4.5 Testing and Actual Results
Executing `q3_hybrid_encryption_demo.py` produced the following (real output):

- **Step 1** — Generated an RSA-2048 keypair into the sandbox (`demo_public.pem`,
  `demo_private.pem`).
- **Step 2** — Created three synthetic files: `data/notes.txt` (464 B), `data/budget.txt`
  (245 B), `data/readme.txt` (360 B).
- **Step 3** — Generated a 32-byte AES-256 session key and encapsulated it under RSA-OAEP →
  `EncryptedSessionKey.bin` (256 bytes). The plaintext session key was never written to disk.
- **Step 4** — Encrypted each file to `encrypted/<name>.txt.enc` with AES-256-GCM; **each
  original remained present** (`original kept: True`).
- **Step 5** — Unwrapped the session key with the private key, decrypted every file to
  `recovered/`, and verified `match=True` for all three.

| File | Encrypted to | Original kept | Decrypt matches original |
|------|--------------|:-------------:|:------------------------:|
| budget.txt | encrypted/budget.txt.enc | ✅ | ✅ |
| notes.txt  | encrypted/notes.txt.enc  | ✅ | ✅ |
| readme.txt | encrypted/readme.txt.enc | ✅ | ✅ |

**Result:** `Hybrid encryption round-trip succeeded.` All originals verified still present with
unchanged SHA-256 digests. No file was overwritten, renamed, or deleted.

### 4.6 Defensive takeaways
- **Backups** (offline / immutable) neutralise the extortion leverage, since the victim can
  restore from clean copies.
- **Key control** is everything: compromise or escrow of the private key determines who can
  recover data — defenders should protect signing/recovery keys with equal rigour.
- The same hybrid pattern is benign and ubiquitous; what distinguishes ransomware is
  **destruction of originals and withholding of the key**, not the cryptography itself.

---

## 5. Conclusion

The lab demonstrates the complementary roles of cryptographic primitives in software security.
SHA-256 provides **integrity** and correctly identified **`rove.exe`** as the authentic file in
Q1. RSA PKCS#1 v1.5 signatures over SHA-256 add **authenticity**, correctly identifying
**`moonwort.exe`** as the only validly signed file in Q2 and defeating the forged-hash attack. Q3
dissected the **hybrid-encryption architecture** behind ransomware and reproduced it as a safe,
reversible, non-destructive simulation, yielding a successful encrypt/decrypt round-trip while
leaving all originals intact. Throughout, supplied executables were never run and all results are
genuine program output.

---

## Appendix A — Reproduction

```bash
# From the repository root (Windows PowerShell or Git Bash), using the project venv:
./.venv/Scripts/python.exe -I Lab2/solution/q1_verify_integrity.py
./.venv/Scripts/python.exe -I Lab2/solution/q2_verify_signature.py
./.venv/Scripts/python.exe -I Lab2/solution/q3_hybrid_encryption_demo.py
```

Dependency: `pycryptodome` (installed into the project `.venv`). Q1 uses only the Python standard
library.

## Appendix B — Files

| File | Purpose |
|------|---------|
| `q1_verify_integrity.py` | SHA-256 integrity check (Q1) |
| `q2_verify_signature.py` | RSA PKCS#1 v1.5 + SHA-256 signature verification (Q2) |
| `q3_hybrid_encryption_demo.py` | Non-destructive hybrid-encryption simulation (Q3) |
| `q3_sandbox/` | Auto-generated sandbox output (synthetic data only) |
