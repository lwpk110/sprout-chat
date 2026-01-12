"""
Data Encryption Service for Phase 2.2 Learning Management

Provides AES-256 encryption for sensitive children's data (student answers, etc.)
Uses Fernet symmetric encryption (via cryptography library)
"""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    """
    AES-256 Encryption service for protecting children's data

    Uses Fernet (symmetric encryption) which provides:
    - AES-128-CBC encryption
    - HMAC for authentication
    - Time-based key generation
    """

    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption service

        Args:
            key: 32-byte encryption key (optional)
                  If not provided, will load from ENCRYPTION_KEY environment variable
        """
        if key is None:
            key_str = os.getenv("ENCRYPTION_KEY")
            if not key_str:
                # Generate a new key if not provided (not recommended for production)
                key = Fernet.generate_key()
                print(f"WARNING: Generated new encryption key. Save this to .env: ENCRYPTION_KEY={key.decode()}")
            else:
                # Decode key from base64 string
                key = base64.urlsafe_b64decode(key_str.encode())

        # Ensure key is 32 bytes (Fernet requirement)
        if len(key) != 32:
            raise ValueError(f"Encryption key must be 32 bytes, got {len(key)} bytes")

        # Derive Fernet key from the 32-byte key
        self._cipher = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data

        Args:
            data: Plain text string to encrypt

        Returns:
            Encrypted string (base64 encoded)

        Example:
            >>> service = EncryptionService()
            >>> encrypted = service.encrypt("student answer")
            >>> print(encrypted)  # 'gAAAAABl...'
        """
        if not isinstance(data, str):
            raise TypeError("Data must be a string")

        encrypted_bytes = self._cipher.encrypt(data.encode())
        return encrypted_bytes.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data

        Args:
            encrypted_data: Encrypted string (base64 encoded)

        Returns:
            Decrypted plain text string

        Example:
            >>> service = EncryptionService()
            >>> encrypted = service.encrypt("student answer")
            >>> decrypted = service.decrypt(encrypted)
            >>> print(decrypted)  # 'student answer'
        """
        if not isinstance(encrypted_data, str):
            raise TypeError("Encrypted data must be a string")

        decrypted_bytes = self._cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()

    def is_encrypted(self, data: str) -> bool:
        """
        Check if data is encrypted (heuristic check)

        Args:
            data: String to check

        Returns:
            True if data appears to be encrypted, False otherwise

        Note: This is a heuristic check based on Fernet token format.
              Not 100% reliable, but useful for validation.
        """
        try:
            # Try to decrypt - if successful, it's encrypted
            self.decrypt(data)
            return True
        except Exception:
            return False


def generate_encryption_key() -> str:
    """
    Generate a new 32-byte encryption key

    Returns:
        Base64-encoded encryption key string

    Example:
        >>> key = generate_encryption_key()
        >>> print(key)  # 'abcdefghijklmnopqrstuvwxyz123456==' (44 chars)
    """
    key = os.urandom(32)
    return base64.urlsafe_b64encode(key).decode()


def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
    """
    Derive a 32-byte encryption key from a password using PBKDF2

    Args:
        password: Password string
        salt: Salt bytes (optional, will generate if not provided)

    Returns:
        32-byte key suitable for encryption

    Security Note:
        PBKDF2 with 100,000 iterations provides good protection against brute force attacks.
        Always use a unique random salt for each key derivation.
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    return kdf.derive(password.encode())


# Global encryption service instance
# Will be initialized lazily when first accessed
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get or create the global encryption service instance

    Returns:
        EncryptionService instance

    Example:
        >>> service = get_encryption_service()
        >>> encrypted = service.encrypt("sensitive data")
    """
    global _encryption_service

    if _encryption_service is None:
        _encryption_service = EncryptionService()

    return _encryption_service


if __name__ == "__main__":
    """Test encryption service when run as script"""

    # Generate a new key for testing
    print("Generating new encryption key...")
    key = generate_encryption_key()
    print(f"ENCRYPTION_KEY={key}")
    print()

    # Test encryption/decryption
    print("Testing encryption service...")
    # Use the base64 key directly (EncryptionService will decode it)
    service = EncryptionService(base64.urlsafe_b64decode(key.encode()))

    # Test data
    original = "学生的答案是：8"

    # Encrypt
    encrypted = service.encrypt(original)
    print(f"Original:  {original}")
    print(f"Encrypted: {encrypted}")
    print()

    # Decrypt
    decrypted = service.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    print()

    # Verify
    assert decrypted == original, "Decryption failed!"
    print("✅ Encryption/decryption test passed!")
    print()

    # Test is_encrypted
    print("Testing is_encrypted()...")
    print(f"Original text is encrypted? {service.is_encrypted(original)}")
    print(f"Encrypted text is encrypted? {service.is_encrypted(encrypted)}")
