#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2020-Present SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
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
import pickle
import requests
from http import HTTPStatus
from unittest import mock
from configs import HEALTHCHECKS_ROUTES

from utils.healthchecks import (
    get_healthcheck_from_skale_api,
    get_healthcheck_url,
    request_all_healthchecks
)
from utils.cache import get_cache
from utils.structures import construct_ok_response

data_ok1 = {
    'name': 'container_name1',
    'state': {'Running': True, 'Paused': False},
    'sgx_keyname': 'test-keyname1', 'sgx_server_url': 'test-url1'
}
data_ok2 = {
    'name': 'container_name2',
    'state': {'Running': False, 'Paused': True},
    'sgx_keyname': 'test-keyname2', 'sgx_server_url': 'test-url2'
}


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == get_healthcheck_url(HEALTHCHECKS_ROUTES['sgx']):
        return MockResponse({'status': 'ok', 'payload': data_ok1}, 200)
    elif args[0] == get_healthcheck_url('url_bad1'):
        return MockResponse({'status': 'error', 'payload': 'any_error'}, 200)
    elif args[0] == get_healthcheck_url('url_bad2'):
        return MockResponse({'status': 'ok', 'data': data_ok1}, 500)
    elif args[0] == get_healthcheck_url('url_bad3'):
        return MockResponse({'status': 'ok'}, 200)

    return MockResponse(None, 404)


def connection_error(*args, **kwargs):
    raise requests.exceptions.ConnectionError


def unknown_error(*args, **kwargs):
    raise Exception


@mock.patch('utils.healthchecks.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_pos(mock_get):
    route = HEALTHCHECKS_ROUTES['sgx']
    # Check with cold cache
    res = get_healthcheck_from_skale_api(route)
    expected = construct_ok_response(data_ok1).to_flask_response()
    assert res.status_code == expected.status_code
    assert res.response == expected.response
    assert pickle.dumps(res) == pickle.dumps(expected)

    # Check using cached data
    cache = get_cache()
    cache.update_item(
        HEALTHCHECKS_ROUTES['sgx'],
        json.dumps(
            {
                'code': HTTPStatus.OK,
                'data': {
                    'data': {
                        **data_ok2
                    },
                    'error': None
                }
            }
        ).encode('utf-8')
    )
    res = get_healthcheck_from_skale_api(route)
    expected = construct_ok_response(data_ok2).to_flask_response()
    assert res.status_code == expected.status_code
    assert res.response == expected.response
    assert pickle.dumps(res) == pickle.dumps(expected)

    # Check using no_cache option
    res = get_healthcheck_from_skale_api(route, no_cache=True)
    expected = construct_ok_response(data_ok1).to_flask_response()
    assert res.status_code == expected.status_code
    assert res.response == expected.response
    assert pickle.dumps(res) == pickle.dumps(expected)


@mock.patch('utils.healthchecks.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_neg(mock_get):
    res = get_healthcheck_from_skale_api('url_bad1')
    expected = [b'{"data": null, "error": "any_error"}']
    assert res.response == expected
    assert res.status_code == HTTPStatus.BAD_REQUEST
    res = get_healthcheck_from_skale_api('url_bad2')
    assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    route = 'url_bad3'
    res = get_healthcheck_from_skale_api(route)
    res_expected = f'{{"data": null, "error": "No data found in response from {route}"}}'  # noqa
    assert res.response[0].decode("utf-8") == res_expected


@mock.patch('utils.healthchecks.requests.get', side_effect=connection_error)
def test_healthcheck_connection_error(mock_get):
    route = 'url_ok1'
    res = get_healthcheck_from_skale_api(route)
    assert res.status_code == HTTPStatus.BAD_REQUEST
    res_expected = f'{{"data": null, "error": "Could not connect to {route}"}}'  # noqa
    assert res.response[0].decode("utf-8") == res_expected


@mock.patch('utils.healthchecks.requests.get', side_effect=unknown_error)
def test_healthcheck_unknown_error(mock_get):
    route = 'url_ok1'
    res = get_healthcheck_from_skale_api(route)
    assert res.status_code == HTTPStatus.BAD_REQUEST
    res_expected = f'{{"data": null, "error": "Could not get data from {route}. "}}'  # noqa
    assert res.response[0].decode("utf-8") == res_expected


@mock.patch('utils.healthchecks.requests.get', side_effect=mocked_requests_get)
def test_request_all_healthchecks(mock_get):
    rcache = get_cache()
    request_all_healthchecks(rcache)
