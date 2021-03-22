import logging
import time

from uwsgidecorators import cron

from utils.helper import request_all_healthchecks
from utils.cache import get_cache

logger = logging.getLogger(__name__)

rcache = get_cache()


@cron(-1, -1, -1, -1, -1)
def cronjob(num):
    logger.info(f'IVD HERE {int(time.time())}')
    request_all_healthchecks(rcache)
