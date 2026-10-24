import hashlib
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
LOGIN_CHECK = LAB_DIR / ".loginCheck"


def login_hash(user: str, pw: str) -> str:
    h = hashlib.sha256()
    h.update((user + pw).encode("utf-8"))
    for _ in range(90000):
        h.update(h.digest())
    return h.hexdigest()


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_login_hashes() -> dict:
    d = {}
    for line in LOGIN_CHECK.read_text().splitlines():
        if not line.strip():
            continue
        u, h = line.strip().split(",")
        d[u] = h
    return d


def load_lines(path) -> list:
    return [l.rstrip("\n\r") for l in Path(path).read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]


def verify(qdir: str, user: str, pw: str):
    """Verify via LoginTemplate.py (the exact source of Login.pyc; the .pyc was
    compiled for Python 3.12 (magic cb0d0d0a), which isn't installed here, so the
    bytecode can't be imported. Both read the same ../.loginCheck oracle)."""
    qpath = LAB_DIR / qdir
    script = LAB_DIR / "LoginTemplate.py"
    result = subprocess.run(
        [sys.executable, str(script), user, pw],
        cwd=str(qpath),
        capture_output=True, text=True,
    )
    return result.stdout.strip() or result.stderr.strip()
