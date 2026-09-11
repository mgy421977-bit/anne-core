"""Private document vault using authenticated AES-128-GCM encryption."""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class PrivateVault:
    """Encrypt private institutional/personal files with a derived 128-bit key.

    The user's passphrase is never stored. A random salt is stored beside the
    ciphertext, while the AES-128 key is derived with scrypt. Files remain
    local unless the user explicitly exports/shares them.
    """

    MAGIC = b"ANNEVAULT1"
    KEY_BYTES = 16  # AES-128
    SALT_BYTES = 16
    NONCE_BYTES = 12

    @staticmethod
    def _key(passphrase: str, salt: bytes) -> bytes:
        if not passphrase:
            raise ValueError("passphrase must not be empty")
        return hashlib.scrypt(
            passphrase.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=PrivateVault.KEY_BYTES
        )

    @classmethod
    def encrypt(cls, data: bytes, passphrase: str) -> bytes:
        salt = os.urandom(cls.SALT_BYTES)
        nonce = os.urandom(cls.NONCE_BYTES)
        key = cls._key(passphrase, salt)
        ciphertext = AESGCM(key).encrypt(nonce, data, cls.MAGIC)
        return cls.MAGIC + salt + nonce + ciphertext

    @classmethod
    def decrypt(cls, blob: bytes, passphrase: str) -> bytes:
        if not blob.startswith(cls.MAGIC):
            raise ValueError("not an ANNE private-vault payload")
        offset = len(cls.MAGIC)
        salt = blob[offset : offset + cls.SALT_BYTES]
        offset += cls.SALT_BYTES
        nonce = blob[offset : offset + cls.NONCE_BYTES]
        offset += cls.NONCE_BYTES
        key = cls._key(passphrase, salt)
        return AESGCM(key).decrypt(nonce, blob[offset:], cls.MAGIC)

    @classmethod
    def encrypt_file(cls, source: str | Path, destination: str | Path, passphrase: str) -> None:
        Path(destination).write_bytes(cls.encrypt(Path(source).read_bytes(), passphrase))

    @classmethod
    def decrypt_file(cls, source: str | Path, destination: str | Path, passphrase: str) -> None:
        Path(destination).write_bytes(cls.decrypt(Path(source).read_bytes(), passphrase))
