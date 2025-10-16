#!/usr/bin/env bash

set -e

CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

if [ -z "$VERSION" ]; then
    echo "VERSION environment variable is not set"
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/version = \"${CURRENT_VERSION}\"/version = \"${VERSION}\"/g" pyproject.toml
else
    sed -i "s/version = \"${CURRENT_VERSION}\"/version = \"${VERSION}\"/g" pyproject.toml
fi

rm -rf ./dist/*

python -m build

echo "==================================================================="
echo "Done build: skale-watchdog-client $VERSION/"

