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
from timeit import default_timer as timer

from uwsgidecorators import cron

from configs import CRON_SCHEDULE
from utils.healthchecks import request_all_healthchecks
from utils.cache import get_cache


logger = logging.getLogger(__name__)

rcache = get_cache()


@cron(*CRON_SCHEDULE)
def cronjob(num):
    logger.info('Background job started')
    start = timer()
    request_all_healthchecks(rcache)
    elapsed = int(timer() - start)
    logger.info(f'Background job finished, elapsed time {elapsed}s')
