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
import requests
from http import HTTPStatus

from configs import (
    API_HOST, API_PORT, API_TIMEOUT, HEALTHCHECKS_ROUTES
)
from utils.cache import get_cache
from utils.structures import (
    construct_err_response,
    construct_ok_response,
    SkaleApiResponse
)


logger = logging.getLogger(__name__)


def get_healthcheck_from_skale_api(route, rcache=None):
    rcache = rcache or get_cache()
    cached_response = SkaleApiResponse.from_bytes(
        rcache.get_item(route)
    )
    response = cached_response or request_healthcheck_from_skale_api(route)
    if cached_response:
        logger.info(f'Cached response for {route} founded')
        logger.debug(f'Cached response for {route}: {response}')
    else:
        logger.info(f'No cached response founded for {route}')
        logger.debug(f'Cold response for {route}: {response}')
    return response.to_flask_response()


def request_healthcheck_from_skale_api(route, mode='direct'):
    url = get_healthcheck_url(route)
    logger.info(f'Requesting data from {url}, mode: {mode}')
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
    except requests.exceptions.ConnectionError as err:
        err_msg = f'Could not connect to {route}'
        logger.error(f'{err_msg}. {err}')
        return construct_err_response(HTTPStatus.BAD_REQUEST, err_msg)
    except Exception as err:
        err_msg = f'Could not get data from {route}. {err}'
        logger.error(f'{err_msg}. {err}')
        return construct_err_response(HTTPStatus.BAD_REQUEST, err_msg)

    if response.status_code != requests.codes.ok:
        err_msg = f'Request to {route} failed, code: {response.status_code}'
        logger.error(err_msg)
        return construct_err_response(response.status_code, err_msg)

    res = response.json()
    if res.get('status') == 'error':
        logger.error(res['payload'])
        return construct_err_response(HTTPStatus.BAD_REQUEST, res['payload'])

    data = res.get('payload')

    if data is None:
        err_msg = f'No data found in response from {route}'
        logger.info(err_msg)
        return construct_err_response(HTTPStatus.BAD_REQUEST, err_msg)

    if route == HEALTHCHECKS_ROUTES['sgx']:
        data.pop('sgx_keyname', None)
        data.pop('sgx_server_url', None)

    return construct_ok_response(data)


def get_healthcheck_url(route):
    return f'http://{API_HOST}:{API_PORT}/{route}'


def healthcheck_urls_from_routes():
    return map(
        lambda r: (r, get_healthcheck_url(r)), HEALTHCHECKS_ROUTES.values()
    )


def request_all_healthchecks(rcache=None):
    rcache = rcache or get_cache()
    logger.info('Requesting and caching data from endpoints')
    for route, url in healthcheck_urls_from_routes():
        response = request_healthcheck_from_skale_api(route, mode='background')
        logger.info(
            f'{route} request returned {response.code} code. Saving to cache')
        logger.debug(
            f'{route} request returned {response.code} status code, '
            f'response: {response}. Saving to cache')
        rcache.update_item(route, response.to_bytes())
