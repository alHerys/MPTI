# Decisions

- 2026-11-22: Python 3.11+ is not preinstalled. Installed `uv` and provisioned Python 3.12 into `.venv`; `make install` prefers `uv` and falls back to `python3 -m venv`.
