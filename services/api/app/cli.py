"""Uso: python -m app.cli create-device [device_id]  — imprime a chave UMA vez."""

import secrets
import sys

from sqlalchemy.orm import Session

from app.db.models import Device
from app.db.session import get_engine
from app.domains.telemetry.service import hash_key


def create_device(device_id: str | None = None) -> tuple[str, str]:
    device_id = device_id or f"dev-{secrets.token_hex(6)}"
    key = secrets.token_urlsafe(32)
    with Session(get_engine()) as s:
        s.add(Device(device_id=device_id, api_key_hash=hash_key(key)))
        s.commit()
    return device_id, key


def seed_demo(email: str, password: str) -> dict[str, str]:
    """Dados sintéticos de desenvolvimento: usuário, organização, propriedade e um dispositivo
    ainda não ativado (código de ativação impresso uma única vez)."""
    from app.core.security import hash_password
    from app.db.models import Membership, Organization, Property, User

    code = secrets.token_urlsafe(12)
    did, key = f"dev-{secrets.token_hex(6)}", secrets.token_urlsafe(32)
    with Session(get_engine()) as s:
        user = User(email=email.lower(), password_hash=hash_password(password))
        org = Organization(name="Organização Demo")
        s.add_all([user, org])
        s.flush()
        prop = Property(org_id=org.id, name="Casa Demo")
        s.add_all([prop, Membership(user_id=user.id, org_id=org.id, role="owner")])
        s.add(
            Device(device_id=did, api_key_hash=hash_key(key), activation_code_hash=hash_key(code))
        )
        s.commit()
        return {
            "property_id": prop.id,
            "device_id": did,
            "device_key": key,
            "activation_code": code,
        }


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "create-device":
        did, k = create_device(sys.argv[2] if len(sys.argv) > 2 else None)
        print(f"device_id={did}\ndevice_key={k}")
    elif len(sys.argv) == 4 and sys.argv[1] == "seed-demo":
        for k, v in seed_demo(sys.argv[2], sys.argv[3]).items():
            print(f"{k}={v}")
    else:
        sys.exit("uso: python -m app.cli create-device [id] | seed-demo <email> <senha>")
