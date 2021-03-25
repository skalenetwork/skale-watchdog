#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE Containers Watchdog
#
#   Copyright (C) 2020 SKALE Labs
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


from flask import Flask, request

import utils.background_tasks  # noqa
from configs.flask import FLASK_APP_HOST, FLASK_APP_PORT, FLASK_DEBUG_MODE
from utils.healthchecks import get_healthcheck_from_skale_api
from utils.log import init_default_logger

from configs import HEALTHCHECKS_ROUTES
init_default_logger()

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.port = FLASK_APP_PORT
app.host = FLASK_APP_HOST
app.use_reloader = False


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


if __name__ == '__main__':
    logger.info('Starting SKALE docker containers Watchdog')
    app.run(debug=FLASK_DEBUG_MODE, port=FLASK_APP_PORT,
            host=FLASK_APP_HOST, use_reloader=False)
