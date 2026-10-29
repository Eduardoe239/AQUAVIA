import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_alembic_upgrade_and_downgrade_on_empty_db():
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "DATABASE_URL": f"sqlite:///{d}/m.db", "APP_ENV": "test"}
        root = Path(__file__).resolve().parents[1]
        for cmd in (["upgrade", "head"], ["downgrade", "base"], ["upgrade", "head"]):
            subprocess.run([sys.executable, "-m", "alembic", *cmd], cwd=root, env=env, check=True)  # noqa: S603
