#
#   This file is part of SKALE Containers Watchdog
#
#   Copyright (C) 2020-Present SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import time
from dataclasses import dataclass
from threading import Thread
from typing import Any, Final, Literal, NoReturn

import requests

from settings import (
    NODE_GROUP,
    PASSIVE,
    REFRESH_INTERVAL,
    REFRESH_READ_TIMEOUT,
    UPSTREAM_CONNECT_TIMEOUT,
    UPSTREAM_PORT,
)

logger = logging.getLogger(__name__)

type RouteGroup = Literal['common', 'skale', 'fair']


@dataclass(frozen=True, slots=True)
class Route:
    group: RouteGroup
    check: str
    upstream: str
    scrub: tuple[str, ...] = ()

    @property
    def path(self) -> str:
        return f'/api/v1/{self.group}/{self.check}'


@dataclass(frozen=True, slots=True)
class Ok:
    payload: dict[str, Any] | list[Any]


@dataclass(frozen=True, slots=True)
class Failure:
    code: int
    message: str
    answered: bool


type Outcome = Ok | Failure


@dataclass(frozen=True, slots=True)
class Entry:
    outcome: Outcome
    fetched_at: float


def build_routes(group: RouteGroup, passive: bool) -> tuple[Route, ...]:
    common = [
        Route('common', 'hardware', '/api/v1/info/hardware'),
        Route('common', 'meta-info', '/api/v1/info/meta-info'),
        Route('common', 'btrfs', '/api/v1/info/btrfs-info'),
        Route('common', 'check-report', '/api/v1/info/check-report'),
        Route('common', 'endpoint', '/api/v1/info/endpoint-info'),
        Route('common', 'containers', '/api/v1/info/containers?all=True'),
        Route('common', 'ssl', '/api/v1/ssl/status'),
    ]
    if not passive:
        common.append(Route('common', 'sgx', '/api/v1/info/sgx', ('sgx_keyname', 'sgx_server_url')))
    if group == 'fair':
        return (
            *common,
            Route('fair', 'chain-checks', '/api/v1/fair-chain/checks'),
            Route('fair', 'chain-record', '/api/v1/fair-chain/record'),
        )
    skale = [
        Route('skale', 'schain-containers-versions', '/api/v1/schains/container-versions'),
        Route('skale', 'public-ip', '/api/v1/node/public-ip'),
    ]
    if not passive:
        skale += [
            Route('skale', 'schains', '/api/v1/health/schains'),
            Route('skale', 'ima', '/api/v1/health/ima'),
            Route('skale', 'validator-nodes', '/api/v1/node/validator-nodes'),
        ]
    return (*common, *skale)


ROUTES: Final[tuple[Route, ...]] = build_routes(NODE_GROUP, PASSIVE)
CACHE: Final[dict[Route, Entry]] = {}


def fetch(route: Route, read_timeout: int) -> Outcome:
    url = f'http://127.0.0.1:{UPSTREAM_PORT}{route.upstream}'
    try:
        response = requests.get(url, timeout=(UPSTREAM_CONNECT_TIMEOUT, read_timeout))
    except Exception:
        logger.error('Could not connect to %s', route.upstream)
        return Failure(400, f'Could not connect to {route.upstream}', False)

    if response.status_code != 200:
        logger.error('Request to %s failed, code: %s', route.upstream, response.status_code)
        return Failure(
            response.status_code,
            f'Request to {route.upstream} failed, code: {response.status_code}',
            True,
        )
    try:
        body = response.json()
    except ValueError:
        body = None
    if not isinstance(body, dict):
        return Failure(400, f'Could not get data from {route.upstream}', True)
    if body.get('status') == 'error':
        logger.error('Upstream %s reported: %s', route.upstream, body.get('payload'))
        return Failure(400, f'Request to {route.upstream} failed', True)

    payload = body.get('payload')
    if payload is None:
        return Failure(400, f'No data found in response from {route.upstream}', True)
    if route.scrub and isinstance(payload, dict):
        payload = {k: v for k, v in payload.items() if k not in route.scrub}
    return Ok(payload)


def store(route: Route, outcome: Outcome) -> None:
    if isinstance(outcome, Failure) and not outcome.answered and route in CACHE:
        return
    CACHE[route] = Entry(outcome, time.monotonic())


def _refresh_forever() -> NoReturn:
    while True:
        for route in ROUTES:
            store(route, fetch(route, REFRESH_READ_TIMEOUT))
        failed = sum(isinstance(e.outcome, Failure) for e in CACHE.values())
        oldest = max((time.monotonic() - e.fetched_at for e in CACHE.values()), default=0.0)
        logger.info(
            'Sweep finished: %d ok, %d failed, oldest %ds',
            len(CACHE) - failed,
            failed,
            oldest,
        )
        time.sleep(REFRESH_INTERVAL)


def start_refresher() -> None:
    Thread(target=_refresh_forever, name='refresher', daemon=True).start()
    logger.info('Refresher started for %d routes', len(ROUTES))
