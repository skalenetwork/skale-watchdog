from collections.abc import Iterator
from typing import Any
from unittest import mock

import pytest
import requests

import health
from health import Failure, Ok, Route, build_routes, fetch, store

HARDWARE = Route('common', 'hardware', '/api/v1/info/hardware')
SGX = Route('common', 'sgx', '/api/v1/info/sgx', ('sgx_keyname', 'sgx_server_url'))


class Response:
    def __init__(self, status: int, body: Any) -> None:
        self.status_code = status
        self._body = body

    def json(self) -> Any:
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


@pytest.fixture(autouse=True)
def clear_cache() -> Iterator[None]:
    health.CACHE.clear()
    yield
    health.CACHE.clear()


def upstream(status: int = 200, body: Any = None) -> mock._patch[mock.MagicMock]:
    return mock.patch('health.requests.get', return_value=Response(status, body))


@pytest.mark.parametrize('group', ['skale', 'fair'])
def test_passive_drops_privileged_checks(group: health.RouteGroup) -> None:
    privileged = {'sgx', 'schains', 'ima', 'validator-nodes'}
    active = {r.check for r in build_routes(group, False)}
    assert {r.check for r in build_routes(group, True)} == active - privileged


@pytest.mark.parametrize('group', ['skale', 'fair'])
def test_routes_are_unique_and_single_group(group: health.RouteGroup) -> None:
    routes = build_routes(group, False)
    assert len({r.path for r in routes}) == len(routes)
    assert {r.group for r in routes} == {'common', group}


def test_path_is_public_url() -> None:
    assert HARDWARE.path == '/api/v1/common/hardware'


def test_fetch_ok() -> None:
    with upstream(body={'status': 'ok', 'payload': {'cpu': 4}}):
        assert fetch(HARDWARE, 1) == Ok({'cpu': 4})


def test_fetch_scrubs_sgx_secrets() -> None:
    payload = {'sgx': 'ok', 'sgx_keyname': 'NEK:abc', 'sgx_server_url': 'https://sgx'}
    with upstream(body={'status': 'ok', 'payload': payload}):
        assert fetch(SGX, 1) == Ok({'sgx': 'ok'})


@pytest.mark.parametrize('code', [400, 500, 599])
def test_fetch_passes_upstream_code_through(code: int) -> None:
    with upstream(status=code):
        outcome = fetch(HARDWARE, 1)
    assert outcome == Failure(code, f'Request to {HARDWARE.upstream} failed, code: {code}', True)


def test_fetch_does_not_echo_upstream_error_text() -> None:
    with upstream(body={'status': 'error', 'payload': 'sgx key NEK:secret rejected'}):
        outcome = fetch(HARDWARE, 1)
    assert outcome == Failure(400, f'Request to {HARDWARE.upstream} failed', True)


def test_fetch_missing_payload() -> None:
    with upstream(body={'status': 'ok'}):
        outcome = fetch(HARDWARE, 1)
    assert outcome == Failure(400, f'No data found in response from {HARDWARE.upstream}', True)


def test_fetch_connection_error_is_unanswered() -> None:
    with mock.patch('health.requests.get', side_effect=requests.exceptions.ConnectionError):
        outcome = fetch(HARDWARE, 1)
    assert outcome == Failure(400, f'Could not connect to {HARDWARE.upstream}', False)


def test_fetch_non_json_body_is_answered() -> None:
    with upstream(body=ValueError('not json')):
        outcome = fetch(HARDWARE, 1)
    assert outcome == Failure(400, f'Could not get data from {HARDWARE.upstream}', True)


def test_store_keeps_last_good_on_unanswered_failure() -> None:
    store(HARDWARE, Ok({'cpu': 4}))
    store(HARDWARE, Failure(400, 'Could not connect', False))
    assert health.CACHE[HARDWARE].outcome == Ok({'cpu': 4})


def test_store_overwrites_on_answered_failure() -> None:
    store(HARDWARE, Ok({'cpu': 4}))
    failure = Failure(500, 'upstream broke', True)
    store(HARDWARE, failure)
    assert health.CACHE[HARDWARE].outcome == failure


def test_store_records_unanswered_failure_when_cache_is_cold() -> None:
    failure = Failure(400, 'Could not connect', False)
    store(HARDWARE, failure)
    assert health.CACHE[HARDWARE].outcome == failure
