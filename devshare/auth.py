from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass

SESSION_COOKIE = "devshare_session"
SHARE_COOKIE = "devshare_share"
SESSION_TTL = 24 * 3600


def generate_pin() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_pin(pin: str, salt: bytes) -> str:
    return hashlib.sha256(salt + pin.encode("utf-8")).hexdigest()


@dataclass
class ShareLink:
    token: str
    path: str
    created_at: float
    expires_at: float | None
    allow_upload: bool = True
    password_hash: str | None = None


class AuthManager:
    def __init__(self, pin: str | None, share_expire_hours: float = 24.0):
        self._salt = secrets.token_bytes(16)
        self.pin_hash = _hash_pin(pin, self._salt) if pin else None
        self.sessions: dict[str, float] = {}
        self.shares: dict[str, ShareLink] = {}
        self.share_expire_hours = share_expire_hours

    @property
    def auth_enabled(self) -> bool:
        return self.pin_hash is not None

    def verify_pin(self, pin: str) -> bool:
        if not self.auth_enabled:
            return True
        digest = _hash_pin(pin.strip(), self._salt)
        return secrets.compare_digest(digest, self.pin_hash)

    def create_session(self) -> str:
        token = secrets.token_urlsafe(32)
        self.sessions[token] = time.time() + SESSION_TTL
        return token

    def validate_session(self, token: str | None) -> bool:
        if not self.auth_enabled:
            return True
        if not token:
            return False
        expiry = self.sessions.get(token)
        if expiry is None:
            return False
        if time.time() > expiry:
            self.sessions.pop(token, None)
            return False
        return True

    def revoke_session(self, token: str | None) -> None:
        if token:
            self.sessions.pop(token, None)

    def create_share(self, path: str, allow_upload: bool = True) -> ShareLink:
        token = secrets.token_urlsafe(32)
        now = time.time()
        expires_at = None
        if self.share_expire_hours > 0:
            expires_at = now + self.share_expire_hours * 3600
        link = ShareLink(
            token=token,
            path=path.replace("\\", "/").lstrip("/"),
            created_at=now,
            expires_at=expires_at,
            allow_upload=allow_upload,
            password_hash=None,
        )
        self.shares[token] = link
        return link

    def create_share_with_password(self, path: str, password: str | None, allow_upload: bool = True) -> ShareLink:
        link = self.create_share(path, allow_upload=allow_upload)
        if password:
            link.password_hash = _hash_pin(password, self._salt)
            self.shares[link.token] = link
        return link

    def verify_share_password(self, token: str | None, password: str | None) -> bool:
        if not token:
            return False
        link = self.shares.get(token)
        if not link:
            return False
        if link.password_hash is None:
            return True
        if not password:
            return False
        digest = _hash_pin(password.strip(), self._salt)
        return secrets.compare_digest(digest, link.password_hash)

    def get_share(self, token: str | None) -> ShareLink | None:
        if not token:
            return None
        link = self.shares.get(token)
        if link is None:
            return None
        if link.expires_at is not None and time.time() > link.expires_at:
            self.shares.pop(token, None)
            return None
        return link

    def revoke_share(self, token: str) -> bool:
        return self.shares.pop(token, None) is not None
