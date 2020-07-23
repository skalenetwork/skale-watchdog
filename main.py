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

from configs.flask import FLASK_APP_HOST, FLASK_APP_PORT, FLASK_DEBUG_MODE
from utils.helper import construct_ok_response
from utils.helper import init_default_logger
from utils.docker_utils import DockerUtils

init_default_logger()

logger = logging.getLogger(__name__)
app = Flask(__name__)
docker_utils = DockerUtils()


@app.route('/status/all', methods=['GET'])
def containers_status_all():
    logger.debug(request)
    containers_list = docker_utils.get_all_skale_containers(all=all, format=True)
    return construct_ok_response(containers_list)


@app.route('/status/schain', methods=['GET'])
def containers_schains_status():
    logger.debug(request)
    containers_list = docker_utils.get_all_schain_containers(all=all, format=True)
    return construct_ok_response(containers_list)


@app.route('/status/core', methods=['GET'])
def containers_core_status():
    logger.debug(request)
    containers_list = docker_utils.get_core_skale_containers(all=all, format=True)
    return construct_ok_response(containers_list)


if __name__ == '__main__':
    logger.info(f'Starting SKALE docker containers Watchdog')
    app.run(debug=FLASK_DEBUG_MODE, port=FLASK_APP_PORT, host=FLASK_APP_HOST, use_reloader=False)
