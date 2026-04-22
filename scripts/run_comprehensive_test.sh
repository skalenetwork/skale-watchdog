#!/usr/bin/env bash
set -e

export PYTHONPATH=${PYTHONPATH}:.
export SETTINGS_FOLDER_PATH=./tests/settings
export DEFAULT_TASK_INTERVAL=10

docker-compose up --build --force-recreate -d
uv run pytest --timeout=300 tests/test_uwsgi.py $@
docker-compose down -v
