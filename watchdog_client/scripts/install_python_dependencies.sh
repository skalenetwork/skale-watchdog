#!/usr/bin/env bash

set -ea

uv pip install build hatchling
uv pip install -e .
uv pip install -e .[dev]
uv pip install codecov pytest-cov
