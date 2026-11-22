PY := .venv/bin/python
PORT ?= 8000
UV := $(shell command -v uv 2>/dev/null)

.venv/bin/python:
	@if [ -n "$(UV)" ]; then uv venv --python 3.12 .venv; else python3 -m venv .venv; fi

install: .venv/bin/python
	@if [ -n "$(UV)" ]; then uv pip install --python $(PY) -r requirements.txt; else $(PY) -m pip install -r requirements.txt; fi

run:
	$(PY) -m uvicorn app.main:app --reload --port $(PORT)

seed:
	$(PY) scripts/seed_demo.py

test:
	$(PY) -m pytest -q

verify: test
	$(PY) scripts/smoke.py

report:
	$(PY) scripts/evaluate.py

.PHONY: install run seed test verify report
