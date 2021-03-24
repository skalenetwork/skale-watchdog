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
import time

from uwsgidecorators import cron

from utils.healthchecks import request_all_healthchecks
from utils.cache import get_cache

logger = logging.getLogger(__name__)

rcache = get_cache()


@cron(-1, -1, -1, -1, -1)
def cronjob(num):
    logger.info(f'IVD HERE {int(time.time())}')
    request_all_healthchecks(rcache)
