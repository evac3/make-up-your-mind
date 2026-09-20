"""Password hashing utilities using Python's built-in hashlib (no extra deps)."""
from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str) -> str:
    """Return a salted PBKDF2-SHA256 hash in the format ``salt:hex_key``."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
    return f"{salt}:{key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Return True if *password* matches the stored hash, False otherwise."""
    try:
        salt, key_hex = stored_hash.split(":", 1)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False
