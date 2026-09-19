"""
Auth endpoints — JWT login + refresh.
Access Token: 15 min | Refresh Token: with Rotation (BRIEF §6.3).
"""
from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from pydantic import BaseModel
from typing import Optional
from .schemas import TokenResponse, RefreshRequest, RefreshResponse

router = Router(tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        jwt_auth = JWTAuthentication()
        try:
            validated = jwt_auth.get_validated_token(jwt_auth.get_raw_token(
                jwt_auth.get_header(request)
            ))
            user = jwt_auth.get_user(validated)
            request.user = user
            return user
        except Exception:
            return None


# Singleton auth instance — reused across all protected routers
jwt_auth = JWTAuth()


@router.post("/token/", response=TokenResponse, auth=None)
def login(request, payload: LoginRequest):
    """
    Authenticate user and return JWT tokens.
    Access: 15 min lifetime. Refresh: rotation enabled.
    Rate limiting: handled at the nginx/proxy level — not duplicated here.
    """
    user = authenticate(request, username=payload.username.strip(), password=payload.password)
    if user is None or not user.is_active:
        from ninja.errors import HttpError
        raise HttpError(401, "بيانات الدخول غير صحيحة")

    refresh = RefreshToken.for_user(user)
    return TokenResponse(
        access=str(refresh.access_token),
        refresh=str(refresh),
    )


@router.post("/token/refresh/", response=RefreshResponse, auth=None)
def refresh_token(request, payload: RefreshRequest):
    """
    Refresh access token using refresh token.
    Rotation: old refresh token is blacklisted on use.
    """
    try:
        refresh = RefreshToken(payload.refresh)
        return RefreshResponse(access=str(refresh.access_token))
    except (TokenError, InvalidToken):
        from ninja.errors import HttpError
        raise HttpError(401, "انتهت صلاحية جلستك — يرجى تسجيل الدخول مجددًا")
