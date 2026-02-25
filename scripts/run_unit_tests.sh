#!/usr/bin/env bash
set -e

export PYTHONPATH=.
export SETTINGS_FOLDER_PATH=./tests/settings
uv run pytest -v -s --cov=./ tests/ --ignore tests/test_uwsgi.py --cov-report term-missing $@
