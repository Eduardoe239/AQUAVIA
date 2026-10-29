import base64
import hashlib
import hmac
import json
import os
import time


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${h.hex()}"


_DUMMY = hash_password("dummy-password-for-timing")


def verify_password(password: str, stored: str | None) -> bool:
    """Sempre executa o scrypt (inclusive sem usuário) para igualar o tempo de resposta."""
    try:
        _, salt, expected = (stored or _DUMMY).split("$")
        h = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(h.hex(), expected) and stored is not None
    except ValueError:
        return False


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_token(sub: str, secret: str, ttl: int) -> str:
    if not secret:
        raise RuntimeError("SECRET_KEY ausente")
    body = _b64(json.dumps({"sub": sub, "exp": int(time.time()) + ttl}).encode())
    sig = _b64(hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def read_token(token: str, secret: str) -> str | None:
    try:
        body, sig = token.split(".")
        good = _b64(hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest())
        if not secret or not hmac.compare_digest(sig, good):
            return None
        data = json.loads(_unb64(body))
        return data["sub"] if data["exp"] > time.time() else None
    except (ValueError, KeyError, TypeError):
        return None
