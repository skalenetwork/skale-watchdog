#!/usr/bin/env bash
set -e

export PYTHONPATH=.
export SETTINGS_FOLDER_PATH=./tests/settings
export UPSTREAM_PORT=3107
export REFRESH_INTERVAL=99999

uv run pytest -v -s --cov=. tests/ --ignore tests/test_wire.py --cov-report term-missing "$@"
