.PHONY: bootstrap up down logs test smoke demo backup pull-model
bootstrap:
	./scripts/bootstrap.sh
up:
	./scripts/start.sh
down:
	./scripts/stop.sh
logs:
	docker compose logs -f --tail=200
test:
	./scripts/test.sh
smoke:
	./scripts/smoke-test.sh

demo:
	./scripts/task-demo.sh
backup:
	./scripts/backup.sh
pull-model:
	./scripts/pull-model.sh
