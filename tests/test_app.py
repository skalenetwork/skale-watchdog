from collections.abc import Iterator
from typing import Any
from unittest import mock

import pytest
from flask.testing import FlaskClient

import health
import main
from health import Failure, Ok, Route

HARDWARE = Route('common', 'hardware', '/api/v1/info/hardware')
LOOPBACK_HEADERS = {'X-Real-IP': '127.0.0.1'}
REMOTE_HEADERS = {'X-Real-IP': '8.8.8.8'}
CACHED = Ok({'cpu': 4})


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    health.CACHE.clear()
    with main.app.test_client() as test_client:
        yield test_client
    health.CACHE.clear()


def warm(outcome: health.Outcome = CACHED) -> None:
    health.store(HARDWARE, outcome)


def fetched(payload: Any) -> mock._patch[mock.MagicMock]:
    return mock.patch('main.fetch', return_value=Ok(payload))


def test_warm_response_carries_cache_age(client: FlaskClient) -> None:
    warm()
    response = client.get('/api/v1/common/hardware')
    assert response.status_code == 200
    assert response.get_json() == {'data': {'cpu': 4}, 'error': None}
    assert int(response.headers['X-Cache-Age']) >= 0


def test_cold_miss_fetches_live_and_omits_cache_age(client: FlaskClient) -> None:
    with fetched({'cpu': 8}):
        response = client.get('/api/v1/common/hardware')
    assert response.get_json() == {'data': {'cpu': 8}, 'error': None}
    assert 'X-Cache-Age' not in response.headers


def test_failure_uses_upstream_code_and_envelope(client: FlaskClient) -> None:
    warm(Failure(502, 'upstream is down', True))
    response = client.get('/api/v1/common/hardware')
    assert response.status_code == 502
    assert response.get_json() == {'data': None, 'error': 'upstream is down'}


def test_no_cache_from_loopback_bypasses_cache(client: FlaskClient) -> None:
    warm()
    with fetched({'cpu': 8}) as fetch_mock:
        response = client.get('/api/v1/common/hardware?_no_cache=1', headers=LOOPBACK_HEADERS)
    assert fetch_mock.called
    assert response.get_json()['data'] == {'cpu': 8}
    assert 'X-Cache-Age' not in response.headers


def test_no_cache_from_remote_is_ignored(client: FlaskClient) -> None:
    warm()
    with fetched({'cpu': 8}) as fetch_mock:
        response = client.get('/api/v1/common/hardware?_no_cache=1', headers=REMOTE_HEADERS)
    assert not fetch_mock.called
    assert response.get_json()['data'] == {'cpu': 4}
    assert 'X-Cache-Age' in response.headers


def test_legacy_body_no_cache_is_ignored(client: FlaskClient) -> None:
    warm()
    with fetched({'cpu': 8}) as fetch_mock:
        response = client.get('/api/v1/common/hardware', json={'_no_cache': True})
    assert not fetch_mock.called
    assert response.status_code == 200
    assert response.get_json()['data'] == {'cpu': 4}


def test_every_route_is_registered_once() -> None:
    registered = [str(rule) for rule in main.app.url_map.iter_rules()]
    for route in health.ROUTES:
        assert registered.count(route.path) == 1


def test_routes_are_get_only(client: FlaskClient) -> None:
    assert client.post('/api/v1/common/hardware').status_code == 405
