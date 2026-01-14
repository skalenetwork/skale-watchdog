#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION=$(grep '^version = ' $DIR/../../pyproject.toml | cut -d'"' -f2)

USAGE_MSG='Usage: BRANCH=[BRANCH] calculate_version.sh'

if [ -z "$BRANCH" ]
then
    (>&2 echo 'You should provide branch')
    echo $USAGE_MSG
    exit 1
fi


if [ -z $VERSION ]; then
      echo "The base version is not set."
      exit 1
fi


if [[ $BRANCH == 'stable' ]]; then
    echo "$VERSION"
    exit 0
elif [[ $BRANCH == 'develop' ]]; then
    OUTPUT_TYPE=".dev"
elif [[ $BRANCH == 'beta' ]]; then
    OUTPUT_TYPE="b"
else
    echo "Branch is not valid, couldn't calculate version"
    exit 1
fi

git fetch --tags > /dev/null

NUMBER=0

while true; do
    CANDIDATE="${VERSION}${OUTPUT_TYPE}${NUMBER}"
    GITHUB_TAG="${VERSION}-${BRANCH}.${NUMBER}"

    if git tag -l "${GITHUB_TAG}" | grep -q "^${GITHUB_TAG}$"; then
        NUMBER=$((NUMBER+1))
    else
        echo "${CANDIDATE}" | tr / -
        break
    fi
done
