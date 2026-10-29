from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from app.api.v1.deps import COOKIE, SessionDep, UserDep, csrf_guard
from app.core.config import get_settings
from app.core.errors import ApiError
from app.core.security import make_token
from app.domains.identity import service

router = APIRouter(tags=["auth"])


class LoginIn(BaseModel):
    email: Annotated[str, Field(min_length=3, max_length=254)]
    password: Annotated[str, Field(min_length=1, max_length=256)]


@router.post("/auth/login")
def login(body: LoginIn, request: Request, response: Response, session: SessionDep):
    s = get_settings()
    key = f"{body.email.strip().lower()}|{request.client.host if request.client else '-'}"
    if service.too_many_failures(key, s.login_max_failures, s.login_window_seconds):
        raise ApiError(429, "RATE_LIMITED", "Muitas tentativas. Tente novamente mais tarde.")
    user = service.authenticate_user(session, body.email, body.password)
    if not user:
        service.register_failure(key)
        raise ApiError(401, "INVALID_CREDENTIALS", "E-mail ou senha incorretos.")
    response.set_cookie(
        COOKIE,
        make_token(user.id, s.secret_key, s.session_ttl_seconds),
        max_age=s.session_ttl_seconds,
        httponly=True,
        samesite="strict",
        secure=s.app_env == "production",
        path="/",
    )
    return {"user": {"id": user.id, "email": user.email}}


@router.post("/auth/logout", dependencies=[Depends(csrf_guard)])
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
def me(user: UserDep, session: SessionDep):
    ms = service.memberships(session, user.id)
    names = service.org_names(session, [m.org_id for m in ms])
    return {
        "id": user.id,
        "email": user.email,
        "organizations": [
            {"id": m.org_id, "name": names.get(m.org_id), "role": m.role} for m in ms
        ],
    }
