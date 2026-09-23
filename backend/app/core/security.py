"""Firebase JWT authentication and authorization utilities."""
import json
from pathlib import Path
from typing import Optional

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from app.core.config import settings

# Initialize Firebase Admin SDK once
_firebase_app: Optional[firebase_admin.App] = None


def get_firebase_app() -> firebase_admin.App:
    global _firebase_app
    if _firebase_app is None:
        sa_path = Path(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
        if sa_path.exists():
            cred = credentials.Certificate(str(sa_path))
        else:
            # Fall back to application default credentials (Cloud Run, GKE)
            cred = credentials.ApplicationDefault()
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    """Represents a verified Firebase user."""
    def __init__(self, uid: str, email: Optional[str], is_anonymous: bool):
        self.uid = uid
        self.email = email
        self.is_anonymous = is_anonymous


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[AuthenticatedUser]:
    """
    Extract and verify Firebase JWT from Authorization header.
    Returns None for anonymous/unauthenticated requests if auth is not required.
    """
    if credentials is None:
        if settings.REQUIRE_AUTH_FOR_UPLOAD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None

    try:
        get_firebase_app()  # ensure initialized
        decoded = auth.verify_id_token(credentials.credentials)
        return AuthenticatedUser(
            uid=decoded["uid"],
            email=decoded.get("email"),
            is_anonymous=decoded.get("firebase", {}).get("sign_in_provider") == "anonymous",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_auth(
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
) -> AuthenticatedUser:
    """Dependency that strictly requires an authenticated user."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user
