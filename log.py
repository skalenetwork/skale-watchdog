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
import re
import sys
from urllib.parse import urlparse

from skale_core.settings import BaseNodeSettings, FairSettings, SkaleSettings, get_settings

from settings import LOG_LEVEL, NODE_GROUP, PASSIVE

LOG_FORMAT = '[%(asctime)s %(levelname)s] (%(threadName)s) %(name)s:%(lineno)d - %(message)s'
LOCAL_IPS = frozenset({'127.0.0.1', 'localhost'})


def compose_hiding_patterns() -> dict[str, str]:
    patterns = {r'NEK\:\w+': '[SGX_KEY]'}
    if not PASSIVE:
        sgx_ip = urlparse(str(get_settings((SkaleSettings, FairSettings)).sgx_url)).hostname
        if sgx_ip and sgx_ip not in LOCAL_IPS:
            patterns[re.escape(sgx_ip)] = '[SGX_IP]'
    if NODE_GROUP != 'fair':
        eth_ip = urlparse(str(get_settings((BaseNodeSettings, SkaleSettings)).endpoint)).hostname
        if eth_ip and eth_ip not in LOCAL_IPS:
            patterns[re.escape(eth_ip)] = '[ETH_IP]'
    return patterns


class HidingFormatter(logging.Formatter):
    def __init__(self, log_format: str, patterns: dict[str, str]) -> None:
        super().__init__(log_format)
        self._patterns = [(re.compile(p), r) for p, r in patterns.items()]

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern, replacement in self._patterns:
            message = pattern.sub(replacement, message)
        return message


def init_default_logger() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(HidingFormatter(LOG_FORMAT, compose_hiding_patterns()))
    logging.basicConfig(level=LOG_LEVEL, handlers=[handler])
