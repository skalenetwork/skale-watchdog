import pytest
from http import HTTPStatus

from utils.structures import SkaleApiResponse


def test_skale_api_response():
    r = SkaleApiResponse(code=200, data={'test': 'ok'})
    assert r.to_bytes() == b'{"code": 200, "data": {"test": "ok"}}'
    print(repr(r.to_json()))
    assert r.to_json() == '{"code": 200, "data": {"test": "ok"}}'
    print(r.to_flask_response())
    fr = r.to_flask_response()
    assert fr.status == '200 OK'

    bytes_response = r.to_bytes()

    converted = SkaleApiResponse.from_bytes(bytes_response)
    assert converted.data == r.data
    assert converted.code == r.code
