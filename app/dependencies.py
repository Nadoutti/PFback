from typing import Any
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from app.config import settings

_jwks_cache: dict[str, Any] = {}

bearer_scheme = HTTPBearer()


async def _get_jwks() -> dict[str, Any]:
    if not _jwks_cache:
        url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            _jwks_cache.update(response.json())
    return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

    jwks = await _get_jwks()
    kid = unverified_header.get("kid")
    key = next((k for k in jwks.get("keys", []) if k["kid"] == kid), None)

    if key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signing key not found")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return payload


def extract_roles(payload: dict) -> list[str]:
    return payload.get(f"{settings.AUTH0_NAMESPACE}/roles", [])


def extract_email(payload: dict) -> str:
    return payload.get(f"{settings.AUTH0_NAMESPACE}/email", payload.get("sub", ""))


def require_role(role: str):
    async def checker(payload: dict = Depends(get_current_user)) -> dict:
        if role not in extract_roles(payload):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return payload

    return checker


def require_role_any(*roles: str):
    async def checker(payload: dict = Depends(get_current_user)) -> dict:
        user_roles = extract_roles(payload)
        if not any(r in user_roles for r in roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return payload

    return checker
