# Password hashing
import bcrypt

class PasswordHandler:
    """Handle password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """ Hash a password using bcrypt """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """ Verify a password against its hash """
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False