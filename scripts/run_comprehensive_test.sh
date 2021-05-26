#!/usr/bin/env bash
set -e

export JOB_INTERVAL=240
docker-compose up --build --force-recreate -d
py.test tests/test_uwsgi.py $@
docker-compose down -v
