#!/usr/bin/env bash
set -e

export PYTHONPATH=${PYTHONPATH}:.

docker-compose up --build --force-recreate -d
uv run pytest tests/test_uwsgi.py $@
docker-compose down -v
