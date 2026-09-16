#!/usr/bin/env bash
set -e

export PYTHONPATH=.
export UPSTREAM_PORT=3107
export REFRESH_INTERVAL=10

cleanup() {
    docker compose down -v
}
trap cleanup EXIT

docker compose up --build --force-recreate -d
uv run pytest --timeout=300 tests/test_wire.py "$@"
