#   -*- coding: utf-8 -*-
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
from http import HTTPStatus
from typing import Optional

import requests

from configs import API_HOST, API_PORT, API_TIMEOUT, HEALTHCHECK_ROUTES
from utils.cache import Cache, get_cache
from utils.structures import (
    RouteType,
    SkaleApiResponse,
    construct_err_response,
    construct_ok_response,
)

logger = logging.getLogger(__name__)


def get_healthcheck_result(
    route_type: RouteType,
    check: str,
    rcache=None,
    no_cache=False,
    params=None,
):
    route = HEALTHCHECK_ROUTES[route_type][check]
    return get_result_by_route(route, rcache=rcache, no_cache=no_cache, params=params)


def get_result_by_route(
    route,
    rcache=None,
    no_cache=False,
    params=None,
):
    if not no_cache:
        rcache = rcache or get_cache()
        cached_response = SkaleApiResponse.from_bytes(rcache.get_item(route))
    else:
        logger.info(f'API request for {route}: no cache mode is enabled')
        cached_response = None
    response = cached_response or request_healthcheck_from_skale_api(route, params=params)
    if cached_response:
        logger.info(f'API request for {route}: cached response founded')
        logger.debug(f'API request for {route}. Cached response: {response}')
    else:
        logger.info(f'API request for {route}: no cached response founded')
        logger.debug(f'API request for {route}. Cold response: {response}')
    return response.to_flask_response()


def request_healthcheck_from_skale_api(route, task=None, params=None):
    url = get_healthcheck_url(route)
    logger.info(f'[TASK {task}] Requesting data from {url}')
    try:
        response = requests.get(url, timeout=API_TIMEOUT, params=params)
    except requests.exceptions.ConnectionError as err:
        err_msg = f'Could not connect to {route}'
        logger.error(f'[TASK {task}] {err_msg}. {err}')
        return construct_err_response(HTTPStatus.BAD_REQUEST, err_msg)
    except Exception as err:
        err_msg = f'Could not get data from {route}. {err}'
        logger.error(f'[TASK {task}] {err_msg}. {err}')
        return construct_err_response(HTTPStatus.BAD_REQUEST, err_msg)

    if response.status_code != requests.codes.ok:
        err_msg = f'Request to {route} failed, code: {response.status_code}'
        logger.error(f'[TASK {task}] {err_msg}')
        return construct_err_response(response.status_code, err_msg)

    res = response.json()
    if res.get('status') == 'error':
        logger.error(f'[TASK {task}] {res["payload"]}')
        return construct_err_response(HTTPStatus.BAD_REQUEST, res['payload'])

    data = res.get('payload')

    if data is None:
        err_msg = f'No data found in response from {route}'
        logger.info(f'[TASK {task}] {err_msg}')
        return construct_err_response(HTTPStatus.BAD_REQUEST, err_msg)

    if route == HEALTHCHECK_ROUTES['common'].get('sgx', None):
        data.pop('sgx_keyname', None)
        data.pop('sgx_server_url', None)

    return construct_ok_response(data)


def get_healthcheck_url(route):
    return f'http://{API_HOST}:{API_PORT}/{route}'


def healthcheck_urls_from_routes():
    for group_routes in HEALTHCHECK_ROUTES.values():
        for route in group_routes.values():
            yield route, get_healthcheck_url(route)


def update_check_cache(
    group: str,
    check: str,
    task: Optional[str] = None,
    rcache: Optional[Cache] = None,
):
    rcache = rcache or get_cache()
    try:
        route = HEALTHCHECK_ROUTES[group][check]
    except KeyError:
        logger.error(f'[TASK {task}] Unknown healthcheck {group}:{check}')
        return construct_err_response(
            HTTPStatus.BAD_REQUEST, f'Unknown healthcheck {group}:{check}'
        )
    response = request_healthcheck_from_skale_api(route, task=task)
    stored = rcache.update_item(route, response.to_bytes())
    if not stored:
        logger.error(f'[TASK {task}] Updating cache item for {group}:{check} failed')
    return response
