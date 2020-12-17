#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2019-2020 SKALE Labs
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

from unittest import mock
import pickle

from configs import API_HOST, API_PORT
from utils.helper import get_healthcheck_from_skale_api, construct_ok_response

data_ok1 = [{'name': 'container_name', 'state': {'Running': True, 'Paused': False}}]


def get_test_url(api_url):
    return f'http://{API_HOST}:{API_PORT}/{api_url}'


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == get_test_url('url_ok1'):
        return MockResponse({'error': None, 'data': data_ok1}, 200)

    return MockResponse(None, 404)


@mock.patch('utils.helper.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_pos(mock_get):
    res = get_healthcheck_from_skale_api('url_ok1')
    expected = construct_ok_response(data_ok1)
    assert res.status_code == expected.status_code
    assert res.response == expected.response
    assert pickle.dumps(res) == pickle.dumps(expected)
