import json
import requests
import time
from concurrent.futures import as_completed, ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process
from timeit import default_timer as timer

import pytest


API_PORT = 3007
WATCHDOG_PORT = 3009
BASE_HOST = '127.0.0.1'
COLD_START_TIMEOUT = 300
MAX_WORKERS = 50

thread_running = True


def compose_watchdog_url(host=BASE_HOST, port=WATCHDOG_PORT, route=''):
    return f'http://{host}:{port}{route}'


class RequestsHandler(BaseHTTPRequestHandler):
    REQUEST_SLEEP = 10

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    @classmethod
    def _get_raw_response(cls, data):
        return json.dumps(data).encode('utf-8')

    def do_GET(self):
        time.sleep(RequestsHandler.REQUEST_SLEEP)
        if self.path == '/api/v1/health/sgx':
            self._set_headers(code=200)
            response = {'status': 'ok', 'payload': {'sgx': 'ok'}}
        else:
            self._set_headers(code=400)
            response = {'status': 'error', 'payload': {'sgx': 'error'}}
        raw_response = RequestsHandler._get_raw_response(response)
        self.wfile.write(raw_response)


def serve_http_server():
    server_address = ('', API_PORT)
    httpd = HTTPServer(server_address, RequestsHandler)
    httpd.serve_forever()


@pytest.fixture(scope='module')
def skale_api_success():
    p = Process(target=serve_http_server)
    p.start()
    time.sleep(COLD_START_TIMEOUT)
    yield
    p.terminate()


def run_request_concurrently(route):
    good_url = compose_watchdog_url(route='/status/sgx')
    futures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as e:
        futures.append(e.submit(requests.get, good_url, timeout=60))

    results = [
        future.result() for future in as_completed(futures)
    ]
    return results


def test_successfull_request(skale_api_success):
    good_url = compose_watchdog_url(route='/status/sgx')

    start_ts = timer()
    response = requests.get(good_url, timeout=60)
    ts_diff = timer() - start_ts

    data = response.json()
    assert data == {'data': {'sgx': 'ok'}, 'error': None}

    assert ts_diff < 2


def test_unsuccessfull_request(skale_api_success):
    bad_url = compose_watchdog_url(route='/status/meta-info')

    start_ts = timer()
    response = requests.get(bad_url, timeout=60)
    ts_diff = timer() - start_ts

    data = response.json()
    assert data == {'data': None, 'error': 'Request to http://localhost:3007/api/v1/node/meta-info failed, code: 400'}  # noqa
    assert ts_diff < 2


def test_concurrent_request():
    start_ts = timer()
    result = run_request_concurrently(route='/status/sgx')
    ts_diff = timer() - start_ts
    for r in result:
        data = r.json()
        assert data == {'data': {'sgx': 'ok'}, 'error': None}
    assert ts_diff < 2


if __name__ == '__main__':
    serve_http_server()
