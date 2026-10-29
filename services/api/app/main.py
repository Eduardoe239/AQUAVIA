from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core import errors
from app.core.config import get_settings


def create_app() -> FastAPI:
    get_settings()  # falha cedo se a configuração for inválida
    app = FastAPI(title="AQUAVIA API", version="0.1.0")
    errors.install(app)
    app.include_router(api_router)

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
