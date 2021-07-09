#!/usr/bin/env bash
set -e

export PYTHONPATH=${PYTHONPATH}:.

docker-compose up --build --force-recreate -d
py.test tests/test_uwsgi.py $@
docker-compose down -v
