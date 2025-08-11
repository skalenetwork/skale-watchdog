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
from flask import Flask, Blueprint, g, request
from werkzeug.exceptions import InternalServerError

from configs import SKALE_NETWORK_TYPE, HEALTHCHECK_ROUTES, get_api_url
import utils.background_tasks  # noqa
from configs.flask import FLASK_APP_HOST, FLASK_APP_PORT, FLASK_DEBUG_MODE
from utils.healthchecks import get_healthcheck_result
from utils.log import init_default_logger
from utils.structures import construct_err_response, RouteType

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
    original = getattr(e, 'original_exception', None)
    logger.exception('Request failed with error %s', original)
    return construct_err_response(status=500, err=original).to_flask_response()


ROUTE_QUERY_PARAMS = {
    'common': {
        'containers': {'all': 'True'},
    }
}


def build_blueprint(group: RouteType) -> Blueprint:
    bp = Blueprint(group, __name__)
    services = HEALTHCHECK_ROUTES.get(group, {})
    for service_key in services.keys():
        rule = service_key
        params = ROUTE_QUERY_PARAMS.get(group, {}).get(service_key)

        def make_view(_service=service_key, _group=group, _params=params):
            @healthcheck
            def view():
                return get_healthcheck_result(_group, _service, no_cache=g.cold, params=_params)  # type: ignore[arg-type]

            view.__name__ = f'{_group}_{_service}'
            return view

        bp.route(get_api_url(group, rule), methods=['GET'])(make_view())
    return bp


app.register_blueprint(build_blueprint('common'))
if SKALE_NETWORK_TYPE == 'skale':
    app.register_blueprint(build_blueprint('skale'))
else:
    app.register_blueprint(build_blueprint('fair'))


if __name__ == '__main__':
    logger.info('Starting SKALE docker containers Watchdog')
    app.run(debug=FLASK_DEBUG_MODE, port=FLASK_APP_PORT, host=FLASK_APP_HOST, use_reloader=False)
