#!/usr/bin/env bash
set -euo pipefail

: "${BRANCH:?set BRANCH to develop, beta or stable}"
base=$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml)
: "${base:?no version in pyproject.toml}"
git fetch --quiet --tags

n=0
while git rev-parse --quiet --verify "refs/tags/$base-$BRANCH.$n" >/dev/null; do
    n=$((n + 1))
done

case $BRANCH in
    develop) pep440="$base.dev$n" ;;
    beta) pep440="${base}b$n" ;;
    stable) pep440=$base; [ "$n" = 0 ] || pep440="$base.post$n" ;;
    *) echo "unknown branch: $BRANCH" >&2; exit 1 ;;
esac

echo "tag=$base-$BRANCH.$n"
echo "pep440=$pep440"
