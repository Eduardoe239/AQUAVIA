import time
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.models import Membership, Organization, Property, User

_failures: dict[str, list[float]] = defaultdict(list)


def reset_limiter() -> None:
    _failures.clear()


def too_many_failures(key: str, max_failures: int, window: int) -> bool:
    now = time.time()
    _failures[key] = [t for t in _failures[key] if now - t < window]
    return len(_failures[key]) >= max_failures


def register_failure(key: str) -> None:
    _failures[key].append(time.time())


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = session.scalar(select(User).where(User.email == email.strip().lower()))
    ok = verify_password(password, user.password_hash if user else None)
    return user if (user and ok) else None


def memberships(session: Session, user_id: str) -> list[Membership]:
    return list(session.scalars(select(Membership).where(Membership.user_id == user_id)))


def org_ids(session: Session, user_id: str) -> list[str]:
    return [m.org_id for m in memberships(session, user_id)]


def role_in_org(session: Session, user_id: str, org_id: str) -> str | None:
    m = session.scalar(
        select(Membership).where(Membership.user_id == user_id, Membership.org_id == org_id)
    )
    return m.role if m else None


def org_names(session: Session, ids: list[str]) -> dict[str, str]:
    rows = session.scalars(select(Organization).where(Organization.id.in_(ids)))
    return {o.id: o.name for o in rows}


def get_property(session: Session, property_id: str) -> Property | None:
    return session.get(Property, property_id)
