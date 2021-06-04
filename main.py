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

from flask import Flask, g, request
from werkzeug.exceptions import InternalServerError

import utils.background_tasks  # noqa
from configs import HEALTHCHECKS_ROUTES
from configs.flask import FLASK_APP_HOST, FLASK_APP_PORT, FLASK_DEBUG_MODE
from utils.healthchecks import get_healthcheck_from_skale_api
from utils.ima import get_ima_healthchecks
from utils.log import init_default_logger
from utils.structures import construct_err_response

init_default_logger()

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.port = FLASK_APP_PORT
app.host = FLASK_APP_HOST
app.use_reloader = False


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
def containers_core_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['containers'])


@app.route('/status/sgx', methods=['GET'])
def sgx_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['sgx'])


@app.route('/status/schains', methods=['GET'])
def schains_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['schains'])


@app.route('/status/hardware', methods=['GET'])
def hardware_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['hardware'])


@app.route('/status/endpoint', methods=['GET'])
def endpoint_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['endpoint'])


@app.route('/status/schain-containers-versions', methods=['GET'])
def schain_containers_versions_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(
        HEALTHCHECKS_ROUTES['schain_versions']
    )


@app.route('/status/meta-info', methods=['GET'])
def meta_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['meta'])


@app.route('/status/btrfs', methods=['GET'])
def btrfs_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['btrfs'])


@app.route('/status/ssl', methods=['GET'])
def ssl_status():
    logger.debug(request)
    return get_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['ssl'])


@app.route('/status/ima', methods=['GET'])
def ima_status():
    logger.debug(request)
    return get_ima_healthchecks().to_flask_response()


if __name__ == '__main__':
    logger.info('Starting SKALE Watchdog')
    app.run(debug=FLASK_DEBUG_MODE, port=FLASK_APP_PORT,
            host=FLASK_APP_HOST, use_reloader=False)
