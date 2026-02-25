#!/usr/bin/env bash
set -e

export PYTHONPATH=.
export ENV_TYPE=dev
uv run pytest -v -s --cov=./ tests/ --ignore tests/test_uwsgi.py --cov-report term-missing $@
