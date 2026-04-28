from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.schemas.models import Token, TokenData
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(tenant_id: str, user_id: str) -> Token:
    """
    Authenticate user and return access token.
    
    In production, verify credentials against a proper identity provider.
    """
    if not tenant_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    access_token = create_access_token(
        data={"tenant_id": tenant_id, "user_id": user_id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
