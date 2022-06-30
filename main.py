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

import logging
import time
from functools import wraps

import flask
from flask import Flask, g, request
from werkzeug.exceptions import InternalServerError

import utils.background_tasks  # noqa
from configs.flask import FLASK_APP_HOST, FLASK_APP_PORT, FLASK_DEBUG_MODE
from utils.healthchecks import get_healthcheck_result
from utils.log import init_default_logger
from utils.structures import construct_err_response

init_default_logger()

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.port = FLASK_APP_PORT
app.host = FLASK_APP_HOST
app.use_reloader = False


def healthcheck(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Incoming request %s', request)
        data = request.data or '{}'
        g.options = flask.json.loads(data)
        logger.debug('%s, options: %s', request, g.options)
        g.cold = g.options.get('_no_cache', False) if g.options else False
        return func(*args, **kwargs)
    return wrapper


@app.before_request
def before_request():
    g.request_start_time = time.time()


@app.teardown_request
def teardown_request(response):
    elapsed = int(time.time() - g.request_start_time)
    logger.info(f'Request time elapsed: {elapsed}s')
    return response


@app.errorhandler(InternalServerError)
def handle_500(e):
    original = getattr(e, "original_exception", None)
    return construct_err_response(status=500, err=original).to_flask_response()


@app.route('/status/core', methods=['GET'])
@healthcheck
def containers_core_status(options, cold):
    params = {'all': 'True'}
    return get_healthcheck_result(
        'containers',
        no_cache=g.cold,
        params=params
    )


@app.route('/status/sgx', methods=['GET'])
@healthcheck
def sgx_status():
    return get_healthcheck_result('sgx', no_cache=g.cold)


@app.route('/status/schains', methods=['GET'])
@healthcheck
def schains_status():
    return get_healthcheck_result('schains', no_cache=g.cold)


@app.route('/status/hardware', methods=['GET'])
@healthcheck
def hardware_status():
    return get_healthcheck_result('hardware', no_cache=g.cold)


@app.route('/status/endpoint', methods=['GET'])
@healthcheck
def endpoint_status():
    return get_healthcheck_result('endpoint', no_cache=g.cold)


@app.route('/status/schain-containers-versions', methods=['GET'])
@healthcheck
def schain_containers_versions_status():
    return get_healthcheck_result('schain_versions', no_cache=g.cold)


@app.route('/status/meta-info', methods=['GET'])
@healthcheck
def meta_status():
    return get_healthcheck_result('meta', no_cache=g.cold)


@app.route('/status/btrfs', methods=['GET'])
@healthcheck
def btrfs_status():
    return get_healthcheck_result('btrfs', no_cache=g.cold)


@app.route('/status/ssl', methods=['GET'])
@healthcheck
def ssl_status():
    return get_healthcheck_result('ssl', no_cache=g.cold)


@app.route('/status/ima', methods=['GET'])
@healthcheck
def ima_status():
    return get_healthcheck_result('ima', no_cache=g.cold)


@app.route('/status/public-ip', methods=['GET'])
@healthcheck
def public_ip():
    return get_healthcheck_result('public-ip', no_cache=g.cold)


@app.route('/status/validator-nodes', methods=['GET'])
@healthcheck
def validator_nodes():
    return get_healthcheck_result('validator-nodes', no_cache=g.cold)


@app.route('/status/check-report', methods=['GET'])
@healthcheck
def check_report():
    return get_healthcheck_result('check-report', no_cache=g.cold)


@app.route('/status/sm-abi', methods=['GET'])
@healthcheck
def sm_abi_hash():
    return get_healthcheck_result('sm-abi', no_cache=g.cold)


@app.route('/status/ima-abi', methods=['GET'])
@healthcheck
def ima_abi_hash():
    return get_healthcheck_result('ima-abi', no_cache=g.cold)


if __name__ == '__main__':
    logger.info('Starting SKALE docker containers Watchdog')
    app.run(debug=FLASK_DEBUG_MODE, port=FLASK_APP_PORT,
            host=FLASK_APP_HOST, use_reloader=False)
