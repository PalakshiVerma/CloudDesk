"""Security & Authentication Utilities.

Provides password hashing via passlib/bcrypt and JWT token encoding/decoding.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import jwt
import bcrypt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed string."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Generates a secure salted hash for a plain-text password."""
    return bcrypt.hashpw(
        password.encode("utf-8")[:72], bcrypt.gensalt()
    ).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str = "AGENT",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generates a signed JWT access token with role claims.

    Args:
        subject: The unique identifier (user ID or email).
        role: The assigned RBAC role (ADMIN, TEAM_LEAD, AGENT).
        expires_delta: Optional custom lifetime duration.

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": now,
        "iss": settings.APP_NAME,
    }

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a signed JWT access token.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.PyJWTError: If token is expired, invalid, or forged.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
