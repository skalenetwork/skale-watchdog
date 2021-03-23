import json
from dataclasses import dataclass

from flask import Response


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
            code=deserialized['code'],
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
