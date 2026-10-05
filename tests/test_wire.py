import json
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
import requests

WATCHDOG = 'http://127.0.0.1:3009'
UPSTREAM_PORT = 3107
SGX_PAYLOAD = {'sgx': 'ok', 'sgx_keyname': 'NEK:secret', 'sgx_server_url': 'https://sgx.internal'}


class Upstream(BaseHTTPRequestHandler):
    def log_message(self, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        body: dict[str, Any]
        if self.path.startswith('/api/v1/info/meta-info'):
            body = {'status': 'error', 'payload': 'meta-info is broken'}
        elif self.path.startswith('/api/v1/info/sgx'):
            body = {'status': 'ok', 'payload': SGX_PAYLOAD}
        else:
            body = {'status': 'ok', 'payload': {'route': self.path}}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


@pytest.fixture(scope='module', autouse=True)
def upstream() -> Iterator[None]:
    server = ThreadingHTTPServer(('127.0.0.1', UPSTREAM_PORT), Upstream)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        response = requests.get(f'{WATCHDOG}/api/v1/common/hardware', timeout=5)
        if response.headers.get('X-Cache-Age') and response.json()['data']:
            break
        time.sleep(1)
    else:
        pytest.fail('watchdog never served a warm response')
    yield
    server.shutdown()


def get(path: str, **kwargs: Any) -> requests.Response:
    return requests.get(f'{WATCHDOG}{path}', timeout=10, **kwargs)


def test_warm_response_is_cached_and_aged() -> None:
    response = get('/api/v1/common/hardware')
    assert response.status_code == 200
    assert response.json() == {'data': {'route': '/api/v1/info/hardware'}, 'error': None}
    assert int(response.headers['X-Cache-Age']) >= 0


def test_no_cache_from_the_node_fetches_live() -> None:
    response = get('/api/v1/common/hardware?_no_cache=1')
    assert response.status_code == 200
    assert 'X-Cache-Age' not in response.headers


def test_nginx_overwrites_client_supplied_real_ip() -> None:
    response = get('/api/v1/common/hardware?_no_cache=1', headers={'X-Real-IP': '8.8.8.8'})
    assert 'X-Cache-Age' not in response.headers


def test_sgx_secrets_are_scrubbed() -> None:
    assert get('/api/v1/common/sgx').json()['data'] == {'sgx': 'ok'}


def test_upstream_error_is_not_echoed() -> None:
    response = get('/api/v1/common/meta-info')
    assert response.status_code == 400
    assert response.json() == {
        'data': None,
        'error': 'Request to /api/v1/info/meta-info failed',
    }


def test_unknown_route_is_404() -> None:
    assert get('/api/v1/common/nope').status_code == 404
