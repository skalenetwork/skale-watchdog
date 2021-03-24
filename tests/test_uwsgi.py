import json
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process
from timeit import default_timer as timer

import pytest


API_PORT = 3007
WATCHDOG_PORT = 3009
BASE_HOST = '127.0.0.1'
COLD_START_TIMEOUT = 20

thread_running = True


def compose_watchdog_url(host=BASE_HOST, port=WATCHDOG_PORT, route=''):
    return f'http://{host}:{port}{route}'


class RequestsHandler(BaseHTTPRequestHandler):
    REQUEST_SLEEP = 20

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    @classmethod
    def _get_raw_response(cls, data):
        return json.dumps(data).encode('utf-8')

    def do_GET(self):
        time.sleep(RequestsHandler.REQUEST_SLEEP)
        if self.path == '/api/sgx/info':
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


def test_successfull_request(skale_api_success):
    good_url = compose_watchdog_url(route='/status/sgx')

    start_ts = timer()
    response = requests.get(good_url)
    diff = timer() - start_ts

    data = response.json()
    assert data == {'data': {'sgx': 'ok'}, 'error': None}

    assert diff < 2


def test_unsuccessfull_request(skale_api_success):
    good_url = compose_watchdog_url(route='/status/meta-info')

    start_ts = timer()
    response = requests.get(good_url)
    diff = timer() - start_ts

    data = response.json()
    print(data)
    assert data == {'data': {'sgx': 'ok'}, 'error': None}
    assert diff >= RequestsHandler.REQUEST_SLEEP


if __name__ == '__main__':
    serve_http_server()
