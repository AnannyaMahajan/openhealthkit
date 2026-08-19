import hashlib
import hmac
import os

try:
    from pwdlib import PasswordHash
    from pwdlib.hashers.argon2 import Argon2Hasher

    password_hash = PasswordHash((Argon2Hasher(),))
    _USE_PWD_LIB = True
except ImportError:
    _USE_PWD_LIB = False


def hash_password(password: str) -> str:
    """Securely hash password using Argon2id or salted PBKDF2-HMAC-SHA256 fallback."""
    if _USE_PWD_LIB:
        return password_hash.hash(password)

    # Fallback to PBKDF2 SHA256 with 600,000 iterations and random salt
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000)
    return f"pbkdf2:sha256:600000${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    if _USE_PWD_LIB and not hashed_password.startswith("pbkdf2:"):
        try:
            return password_hash.verify(plain_password, hashed_password)
        except Exception:
            return False

    if hashed_password.startswith("pbkdf2:sha256:"):
        try:
            parts = hashed_password.split("$")
            if len(parts) != 3:
                return False
            salt = bytes.fromhex(parts[1])
            expected_key = bytes.fromhex(parts[2])
            computed_key = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt, 600_000
            )
            return hmac.compare_digest(expected_key, computed_key)
        except Exception:
            return False

    return False
