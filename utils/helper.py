#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE Containers Watchdog
#
#   Copyright (C) 2020 SKALE Labs
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
import logging
from http import HTTPStatus
from time import sleep
from logging import Formatter, StreamHandler
from flask import Response
import sys
import requests
from configs import API_HOST, API_PORT, API_CONT_HEALTH_URL, API_TIMEOUT
logger = logging.getLogger(__name__)


def init_default_logger():  # pragma: no cover
    handlers = []
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)


def construct_response(status, data):
    return Response(
        response=json.dumps(data),
        status=status,
        mimetype='application/json'
    )


def construct_err_response(status, err):
    return construct_response(status, {'data': None, 'error': str(err)})


def construct_ok_response(data=None):
    return construct_response(HTTPStatus.OK, {'data': data, 'error': None})


def get_api_healthcheck(api_url):
    """Return 0 if OK or 1 if failed."""
    url = get_containers_healthcheck_url(api_url)
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
    except requests.exceptions.ConnectionError as err:
        err_msg = f'Could not connect to {url}'
        logger.error(f'{err_msg}. {err}')
        return construct_err_response(HTTPStatus.BAD_GATEWAY, err_msg)
    except Exception as err:
        err_msg = f'Could not get data from {url}'
        logger.error(f'{err_msg}. {err}')
        return construct_err_response(HTTPStatus.BAD_GATEWAY, err_msg)

    if response.status_code != requests.codes.ok:
        err_msg = f'Request to {url} failed, status code: {response.status_code}'
        logger.error(err_msg)
        return construct_err_response(HTTPStatus.BAD_GATEWAY, err_msg)

    res = response.json()
    if res.get('error') is not None:
        logger.info(res['error'])
        return construct_err_response(HTTPStatus.BAD_GATEWAY, res['error'])
    data = res.get('data')
    if data is None:
        err_msg = f'No data found in response checking {url}'
        logger.info(err_msg)
        return construct_err_response(HTTPStatus.BAD_GATEWAY, err_msg)

    return construct_ok_response(data)


def get_containers_healthcheck_url(api_url):
    return f'http://{API_HOST}:{API_PORT}/{api_url}'
