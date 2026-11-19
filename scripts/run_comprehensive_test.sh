#!/usr/bin/env bash
set -e

trap 'docker compose down' EXIT

docker compose up --build --force-recreate -d
uv run pytest tests/test_wire.py "$@"
