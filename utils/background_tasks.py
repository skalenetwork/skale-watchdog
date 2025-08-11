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
    HEALTHCHECK_ROUTES,
    SIGNAL_OFFSET,
    SKALE_NETWORK_TYPE,
)
from utils.healthchecks import update_check_cache
from utils.log import init_default_logger


init_default_logger()

logger = logging.getLogger(__name__)


def task(num, group, check):
    logger.info('[TASK %d] Started %s:%s', num, group, check)
    start = timer()
    update_check_cache(group, check, task=num)
    elapsed = int(timer() - start)
    logger.info('[TASK %d] Finished %s:%s elapsed %ds', num, group, check, elapsed)


def make_background_task(group, check):
    return partial(task, group=group, check=check)


def init_tasks():
    logger.info('Initializing background tasks')
    combined = []
    for check in HEALTHCHECK_ROUTES['common'].keys():
        combined.append(('common', check))
    net_group = SKALE_NETWORK_TYPE if SKALE_NETWORK_TYPE in HEALTHCHECK_ROUTES else 'fair'
    for check in HEALTHCHECK_ROUTES[net_group].keys():
        combined.append((net_group, check))

    for i, (group, check) in enumerate(combined):
        num = SIGNAL_OFFSET + i
        logger.info('Adding task %d %s:%s', num, group, check)
        uwsgi.register_signal(num, 'spooler', make_background_task(group, check))
        interval = DEFAULT_TASK_INTERVAL * (2 if check == 'schains' else 1)
        uwsgi.add_timer(num, interval)
    logger.info('Background tasks initialized')


if not DISABLE_BACKGROUND:
    init_tasks()
