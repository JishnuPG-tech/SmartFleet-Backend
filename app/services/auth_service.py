import hmac
import random
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)

# In-memory OTP store for Driver Login: phone -> otp
driver_otp_cache: Dict[str, str] = {
    "+91 94471 23456": "1234",
    "+91 98460 78901": "1234",
    "+91 97455 11223": "1234"
}

def generate_driver_otp(phone: str) -> str:
    # Deterministic or random OTP
    otp = "1234" # Default easy PIN for testing; or str(random.randint(1000, 9999))
    driver_otp_cache[phone.strip()] = otp
    return otp

def verify_driver_otp_code(phone: str, otp: str) -> bool:
    expected = driver_otp_cache.get(phone.strip(), "1234")
    return hmac.compare_digest(expected, otp.strip())

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not credentials:
        # Default mock admin fallback for dev / simulator if no token provided
        result = await db.execute(select(User).filter(User.role == "admin").limit(1))
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Bearer token"
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    user_id = payload["sub"]
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return user
