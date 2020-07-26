#!/usr/bin/env bash

docker run -d --name skale-watchdog --env-file $(pwd)/.env --net=host -v /var/run/docker.sock:/var/run/docker.sock skalenetwork/watchdog
