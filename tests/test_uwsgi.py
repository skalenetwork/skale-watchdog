import json
import queue
import logging
import requests
import time
from contextlib import contextmanager
from concurrent.futures import as_completed, ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Queue
from timeit import default_timer as timer

import pytest

from configs import DEFAULT_TASK_INTERVAL


logger = logging.getLogger(__name__)

API_PORT = 3007
WATCHDOG_PORT = 3009
BASE_HOST = '127.0.0.1'
COLD_START_TIMEOUT = 2 * DEFAULT_TASK_INTERVAL
MAX_WORKERS = 50
CONCURRENT_REQ_NUMBER = 4

thread_running = True


def compose_watchdog_url(host=BASE_HOST, port=WATCHDOG_PORT, route=''):
    return f'http://{host}:{port}{route}'


mq_schains = Queue()
mq_endpoint = Queue()


class RequestsHandler(BaseHTTPRequestHandler):
    REQUEST_SLEEP = 10
    schains_state = 0
    endpoint_state = 0

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    @classmethod
    def _get_raw_response(cls, data):
        return json.dumps(data).encode('utf-8')

    def get_msg(self, mq):
        try:
            return mq.get(timeout=2)
        except queue.Empty:
            return None

    def do_GET(self):
        time.sleep(RequestsHandler.REQUEST_SLEEP)
        if self.path == '/api/v1/health/sgx':
            self._set_headers(code=200)
            response = {'status': 'ok', 'payload': {'sgx': 'ok'}}
        elif self.path == '/api/v1/health/schains':
            time.sleep(30)
            msg = self.get_msg(mq_schains)
            self._set_headers(code=200)
            if RequestsHandler.schains_state == 1 or msg == 'schains':
                RequestsHandler.schains_state = 1
                response = {'status': 'ok', 'payload': {'schains': True}}
            else:
                response = {'status': 'ok', 'payload': {'schains': False}}
        elif self.path == '/api/v1/node/endpoint-info':
            time.sleep(20)
            msg = self.get_msg(mq_endpoint)
            if RequestsHandler.endpoint_state == 1 or msg == 'endpoint':
                RequestsHandler.endpoint_state = 1
                self._set_headers(code=200)
                response = {'status': 'ok', 'payload': {'endpoint': True}}
            else:
                self._set_headers(code=400)
                response = {'status': 'error',
                            'payload': {'endpoint': 'error'}}

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
def skale_api():
    p = Process(target=serve_http_server)
    p.start()
    time.sleep(COLD_START_TIMEOUT)
    ts = time.time()
    logger.info('API started %d', ts)
    yield
    p.terminate()


@pytest.mark.skip
def test_api_spawner(skale_api):
    time.sleep(5000)
    pass


def run_request_concurrently(route):
    def make_request(url):
        try:
            return requests.get(url, timeout=60)
        except Exception as e:
            logger.error('Request failed with %s', e)
            return None

    good_url = compose_watchdog_url(route='/status/sgx')
    futures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as e:
        futures = [
            e.submit(make_request, good_url)
            for _ in range(CONCURRENT_REQ_NUMBER)
        ]

    results = []
    for f in as_completed(futures):
        r = f.result()
        ts = int(time.time())
        print(f'Completed {ts}: {r}')
        results.append(r)
    return results


@contextmanager
def in_time(seconds):
    start_ts = timer()
    yield
    ts_diff = timer() - start_ts
    if ts_diff > seconds:
        raise TimeoutError(f'Operation executed {ts_diff}s > {seconds}s')


def test_successfull_request(skale_api):
    good_url = compose_watchdog_url(route='/status/sgx')

    response = requests.get(good_url, timeout=60)
    data = response.json()
    assert data == {'data': {'sgx': 'ok'}, 'error': None}

    with in_time(seconds=2):
        response = requests.get(good_url, timeout=60)
        data = response.json()
        assert data == {'data': {'sgx': 'ok'}, 'error': None}

    with in_time(seconds=2):
        response = requests.get(good_url, timeout=60)
        data = response.json()
        assert data == {'data': {'sgx': 'ok'}, 'error': None}


def test_unsuccessfull_request(skale_api):
    bad_url = compose_watchdog_url(route='/status/meta-info')
    with in_time(seconds=2):
        response = requests.get(bad_url, timeout=60)
        data = response.json()
        assert data == {'data': None, 'error': 'Request to api/v1/node/meta-info failed, code: 400'}  # noqa


def test_request_no_cache(skale_api):
    good_url = compose_watchdog_url(route='/status/sgx')

    with pytest.raises(TimeoutError):
        with in_time(seconds=2):
            response = requests.get(
                good_url,
                json={'_no_cache': True},
                timeout=120
            )

    with in_time(seconds=50):
        response = requests.get(
            good_url,
            json={'_no_cache': True},
            timeout=120
        )
        data = response.json()
        assert data == {'data': {'sgx': 'ok'}, 'error': None}

    bad_url = compose_watchdog_url(route='/status/meta-info')

    with pytest.raises(TimeoutError):
        with in_time(seconds=2):
            response = requests.get(
                bad_url,
                json={'_no_cache': True},
                timeout=120
            )

    with in_time(seconds=50):
        response = requests.get(bad_url, json={'_no_cache': True}, timeout=60)
        data = response.json()
        assert data == {'data': None, 'error': 'Request to api/v1/node/meta-info failed, code: 400'}  # noqa


def test_changing_request(skale_api):
    schains_url = compose_watchdog_url(route='/status/schains')
    endpoint_url = compose_watchdog_url(route='/status/endpoint')
    time.sleep(70)

    with in_time(seconds=2):
        response = requests.get(schains_url, timeout=60)
        data = response.json()
        assert data == {'data': {'schains': False}, 'error': None}

    with in_time(seconds=2):
        response = requests.get(endpoint_url, timeout=60)
        data = response.json()
        assert data == {'data': None, 'error': 'Request to api/v1/node/endpoint-info failed, code: 400'}  # noqa

    mq_schains.put('schains')
    mq_endpoint.put('endpoint')
    time.sleep(125)
    with in_time(seconds=2):
        response = requests.get(schains_url, timeout=60)
        data = response.json()
        assert data == {'data': {'schains': True}, 'error': None}

    with in_time(seconds=2):
        response = requests.get(endpoint_url, timeout=60)
        data = response.json()
        assert data == {'data': {'endpoint': True}, 'error': None}


def test_concurrent_request(skale_api):
    start_ts = timer()
    result = run_request_concurrently(route='/status/sgx')
    ts_diff = timer() - start_ts
    for r in result:
        assert r is not None
        data = r.json()
        assert data == {'data': {'sgx': 'ok'}, 'error': None}
    assert ts_diff < 2


if __name__ == '__main__':
    serve_http_server()
