"""
Security utilities for authentication and encryption
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.config import settings
import secrets
import hashlib

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Token encryption (for QuickBooks tokens)
cipher = Fernet(settings.ENCRYPTION_KEY.encode())


# ============================================
# PASSWORD UTILITIES
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes for bcrypt
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    # Truncate password to 72 bytes for bcrypt
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)


# ============================================
# JWT TOKEN UTILITIES
# ============================================

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to encode (user_id, company_id, etc.)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """Create a long-lived refresh token"""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(data, expires_delta)


def verify_token(token: str) -> Dict:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


# ============================================
# TOKEN ENCRYPTION (for OAuth tokens)
# ============================================

def encrypt_token(token: str) -> str:
    """Encrypt a token for database storage (e.g., QuickBooks OAuth tokens)"""
    if not token:
        return None
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token from database"""
    if not encrypted_token:
        return None
    return cipher.decrypt(encrypted_token.encode()).decode()


# ============================================
# API KEY UTILITIES
# ============================================

def generate_api_key() -> str:
    """
    Generate a secure API key
    
    Returns:
        API key in format: sk_live_xxxxx...
    """
    random_part = secrets.token_urlsafe(32)
    return f"sk_live_{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_api_key_prefix(api_key: str) -> str:
    """Get the first 10 characters of an API key for display"""
    return api_key[:10] + "..."


# ============================================
# CSRF TOKEN UTILITIES
# ============================================

def generate_csrf_token() -> str:
    """Generate a CSRF token for OAuth state parameter"""
    return secrets.token_urlsafe(32)


def generate_state_token() -> str:
    """Alias for generate_csrf_token"""
    return generate_csrf_token()
