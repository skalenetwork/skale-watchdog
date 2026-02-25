#!/usr/bin/env bash
set -e

export PYTHONPATH=${PYTHONPATH}:.
export SETTINGS_FOLDER_PATH=./tests/settings

docker-compose up --build --force-recreate -d
uv run pytest tests/test_uwsgi.py $@
docker-compose down -v
