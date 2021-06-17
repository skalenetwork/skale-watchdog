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
from functools import partial
from timeit import default_timer as timer

import uwsgi

from configs import (
    DEFAULT_TASK_INTERVAL,
    DISABLE_BACKGROUND,
    HEALTHCHECKS_ROUTES,
    SIGNAL_OFFSET
)
from utils.healthchecks import request_health

logger = logging.getLogger(__name__)


def task(num, route, mode):
    logger.info('[TASK %d] Started', num)
    start = timer()
    request_health(route, mode)
    elapsed = int(timer() - start)
    logger.info('[TASK %d] Finished, elapsed time %ds', num, elapsed)


def make_background_task(route):
    return partial(task, route=route, mode='background')


def init_tasks():
    logger.info('Initializing backgound tasks')
    for i, check in enumerate(HEALTHCHECKS_ROUTES):
        num = SIGNAL_OFFSET + i
        logger.info('Adding task %d %s', i, check)
        uwsgi.register_signal(num, 'worker', make_background_task(check))
        interval = DEFAULT_TASK_INTERVAL
        if check == 'schains':
            interval *= 2
        uwsgi.add_timer(num, interval)
    logger.info('Background tasks initialized')


if not DISABLE_BACKGROUND:
    init_tasks()
