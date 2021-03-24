from utils.structures import SkaleApiResponse


def test_skale_api_response():
    r = SkaleApiResponse(code=200, data={'test': 'ok'})
    assert r.to_bytes() == b'{"code": 200, "data": {"test": "ok"}}'
    assert r.to_json() == '{"code": 200, "data": {"test": "ok"}}'
    fr = r.to_flask_response()
    assert fr.status == '200 OK'

    bytes_response = r.to_bytes()

    from_none = SkaleApiResponse.from_bytes(None)
    assert from_none is None
    from_none = SkaleApiResponse.from_json(None)
    assert from_none is None
    converted = SkaleApiResponse.from_bytes(bytes_response)
    assert converted.data == r.data
    assert converted.code == r.code
