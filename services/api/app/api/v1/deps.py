from typing import Annotated

from fastapi import Cookie, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ApiError
from app.core.security import read_token
from app.db.models import User
from app.db.session import get_session

SessionDep = Annotated[Session, Depends(get_session)]
COOKIE = "aquavia_session"


def current_user(
    session: SessionDep, aquavia_session: Annotated[str | None, Cookie()] = None
) -> User:
    uid = read_token(aquavia_session, get_settings().secret_key) if aquavia_session else None
    user = session.get(User, uid) if uid else None
    if not user:
        raise ApiError(401, "UNAUTHENTICATED", "Sessão ausente ou expirada.")
    return user


def csrf_guard(request: Request, x_requested_with: Annotated[str | None, Header()] = None) -> None:
    """Defesa em profundidade além de SameSite=Strict: mutações exigem cabeçalho custom."""
    if request.method not in ("GET", "HEAD", "OPTIONS") and x_requested_with != "aquavia-web":
        raise ApiError(403, "CSRF_REJECTED", "Requisição não autorizada.")


UserDep = Annotated[User, Depends(current_user)]
