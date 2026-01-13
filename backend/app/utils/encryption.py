"""
数据加密工具

提供学生答案等敏感数据的加密和解密功能

注意：生产环境建议使用专业的加密库如 cryptography
这里提供基础实现用于开发环境
"""
import base64
import os
import hashlib
from sqlalchemy import TypeDecorator, String
from sqlalchemy.ext.mutable import Mutable


class EncryptionHelper:
    """
    加密助手类（基础实现）

    使用 XOR + Base64 进行简单的数据混淆
    注意：这仅用于开发环境，生产环境应使用 Fernet/AES
    """

    def __init__(self, secret_key: str = None):
        """
        初始化加密助手

        Args:
            secret_key: 加密密钥（如果不提供，从环境变量读取）
        """
        if secret_key is None:
            secret_key = os.getenv("ENCRYPTION_KEY", "")

        if not secret_key:
            # 开发环境使用默认密钥
            secret_key = "sprout-chat-dev-key"

        # 生成固定长度的密钥
        self.key = hashlib.sha256(secret_key.encode()).digest()

    def encrypt(self, plaintext: str) -> str:
        """
        加密文本（XOR + Base64）

        Args:
            plaintext: 明文

        Returns:
            加密后的文本（Base64 编码）
        """
        if not plaintext:
            return ""

        # XOR 加密
        plaintext_bytes = plaintext.encode()
        encrypted = []

        for i, byte in enumerate(plaintext_bytes):
            key_byte = self.key[i % len(self.key)]
            encrypted.append(byte ^ key_byte)

        # Base64 编码
        return base64.urlsafe_b64encode(bytes(encrypted)).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        解密文本

        Args:
            ciphertext: 加密文本（Base64 编码）

        Returns:
            明文
        """
        if not ciphertext:
            return ""

        try:
            # Base64 解码
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode())

            # XOR 解密
            decrypted = []
            for i, byte in enumerate(encrypted_bytes):
                key_byte = self.key[i % len(self.key)]
                decrypted.append(byte ^ key_byte)

            return bytes(decrypted).decode()
        except Exception:
            # 如果解密失败，返回原始文本（向后兼容）
            return ciphertext


# 全局加密助手实例
_encryption_helper = None


def get_encryption_helper() -> EncryptionHelper:
    """
    获取加密助手实例（单例模式）

    Returns:
        EncryptionHelper 实例
    """
    global _encryption_helper
    if _encryption_helper is None:
        _encryption_helper = EncryptionHelper()
    return _encryption_helper


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy 自定义类型：自动加密/解密字符串字段

    用法：
        student_answer = Column(EncryptedString(255))
    """
    impl = String

    def process_bind_param(self, value, dialect):
        """存储时加密"""
        if value is None:
            return value
        return get_encryption_helper().encrypt(value)

    def process_result_value(self, value, dialect):
        """读取时解密"""
        if value is None:
            return value
        return get_encryption_helper().decrypt(value)
