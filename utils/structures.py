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

import json
from http import HTTPStatus

from flask import Response

from dataclasses import dataclass


@dataclass
class SkaleApiResponse:
    code: int
    data: dict

    def to_json(self):
        return json.dumps({
            'code': self.code,
            'data': self.data,
        })

    def to_bytes(self):
        return self.to_json().encode('utf-8')

    @classmethod
    def from_json(cls, json_data):
        if json_data is None:
            return None
        deserialized = json.loads(json_data)
        return cls(
            code=HTTPStatus(deserialized['code']),
            data=deserialized['data'],
        )

    @classmethod
    def from_bytes(cls, bytes_data):
        if bytes_data is None:
            return None
        json_data = bytes_data.decode('utf-8')
        return cls.from_json(json_data)

    def to_flask_response(self):
        return Response(
            response=json.dumps(self.data),
            status=self.code,
            mimetype='application/json'
        )


def construct_err_response(status, err):
    return SkaleApiResponse(
        code=status, data={'data': None, 'error': str(err)}
    )


def construct_ok_response(data=None):
    return SkaleApiResponse(
        code=HTTPStatus.OK,
        data={'data': data, 'error': None}
    )
