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


def retry(exceptions, times, delay=0):
    """
    Retry Decorator

    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown

    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param delay: Delay between attempts in seconds. default: 0
    :type delay: Int
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logger.info(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt, times),
                        exc_info=True
                    )
                    attempt += 1
                    sleep(delay)
            return func(*args, **kwargs)
        return newfn
    return decorator


def get_api_healthcheck(api_url):
    """Return 0 if OK or 1 if failed."""
    url = get_containers_healthcheck_url(api_url)
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
    except requests.exceptions.ConnectionError as err:
        logger.info(f'Could not connect to {url}')
        logger.error(err)
        return 1
    except Exception as err:
        logger.info(f'Could not get data from {url}')
        logger.error(err)
        return 1

    if response.status_code != requests.codes.ok:
        logger.info(f'Request to {url} failed, status code: {response.status_code}')
        return 1

    res = response.json()
    if res.get('error') is not None:
        logger.info(res['error'])
        return 1
    data = res.get('data')
    if data is None:
        logger.info(f'No data found checking {url}')
        return 1

    return data


def get_containers_healthcheck_url(api_url):
    return f'http://{API_HOST}:{API_PORT}/{api_url}'
