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

import json
import time
from functools import partial
from typing import Any

from flask import Flask, Response, request

from health import CACHE, ROUTES, Ok, Outcome, Route, fetch, start_refresher
from log import init_default_logger
from settings import REQUEST_READ_TIMEOUT

init_default_logger()

app = Flask(__name__)

LOOPBACK = frozenset({'127.0.0.1', '::1'})


def cold() -> bool:
    if request.args.get('_no_cache') not in ('1', 'true'):
        return False
    return request.headers.get('X-Real-IP') in LOOPBACK


def render(outcome: Outcome, age: int | None) -> Response:
    if isinstance(outcome, Ok):
        body: dict[str, Any] = {'data': outcome.payload, 'error': None}
        status = 200
    else:
        body = {'data': None, 'error': outcome.message}
        status = outcome.code
    response = Response(json.dumps(body), status=status, mimetype='application/json')
    if age is not None:
        response.headers['X-Cache-Age'] = str(age)
    return response


def serve(route: Route) -> Response:
    entry = None if cold() else CACHE.get(route)
    if entry is None:
        return render(fetch(route, REQUEST_READ_TIMEOUT), None)
    return render(entry.outcome, int(time.monotonic() - entry.fetched_at))


for _route in ROUTES:
    app.add_url_rule(
        _route.path,
        endpoint=f'{_route.group}.{_route.check}',
        view_func=partial(serve, _route),
    )

start_refresher()
