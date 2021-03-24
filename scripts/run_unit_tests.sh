#!/usr/bin/env bash
set -e

export PYTHONPATH=.
export ENV=dev
py.test -v -s --cov=./ tests/ --ignore tests/test_uwsgi.py --cov-report term-missing
