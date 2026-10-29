.PHONY: up down api-test api-lint fw-test simulate migrate
up:        ; docker compose -f infra/compose/docker-compose.yml up --build
down:      ; docker compose -f infra/compose/docker-compose.yml down
api-test:  ; cd services/api && pytest
api-lint:  ; cd services/api && ruff check . && ruff format --check .
fw-test:   ; $(MAKE) -C firmware/aquavia_node/components/metering/test
migrate:   ; cd services/api && alembic upgrade head
simulate:  ; python tools/simulator/simulate.py --help
