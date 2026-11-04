from flask_bcrypt import Bcrypt
from app.config import BCRYPT_ROUNDS

bcrypt = Bcrypt()

class CryptoService:
    @staticmethod
    def hash_pwd(raw_password: str) -> str:
        """生成加盐哈希"""
        return bcrypt.generate_password_hash(raw_password, rounds=BCRYPT_ROUNDS).decode("utf‑8")

    @staticmethod
    def verify_pwd(raw_password: str, stored_hash: str) -> bool:
        """校验密码"""
        return bcrypt.check_password_hash(stored_hash, raw_password)
