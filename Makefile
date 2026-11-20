PYTHON ?= python
DOCKER_IMAGE ?= mike-survival

.PHONY: install test lint format run docker-build docker-test compose-up compose-down

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

run:
	$(PYTHON) main.py

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-test:
	docker run --rm -e SDL_VIDEODRIVER=dummy -e SDL_AUDIODRIVER=dummy $(DOCKER_IMAGE) python -m pytest -q

compose-up:
	docker compose up --build

compose-down:
	docker compose down
