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
import re
import sys
from urllib.parse import urlparse

from flask import has_request_context, request
from configs import ENDPOINT, SGX_SERVER_URL

LOG_FORMAT = '[%(asctime)s %(levelname)s] (%(threadName)s) %(name)s:%(lineno)d - %(message)s'  # noqa


def compose_hiding_patterns():
    sgx_ip = urlparse(SGX_SERVER_URL).hostname
    eth_ip = urlparse(ENDPOINT).hostname
    return {
        rf'{sgx_ip}': '[SGX_IP]',
        rf'{eth_ip}': '[ETH_IP]',
        r'NEK\:\w+': '[SGX_KEY]'
    }


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if not isinstance(record, str):
            if has_request_context():
                record.url = request.full_path[:-1]
            else:
                record.url = None
        return super().format(record)


class HidingFormatter(RequestFormatter):
    def __init__(self, log_format: str, patterns: dict) -> None:
        super().__init__(log_format)
        self._patterns: dict = patterns

    def _filter_sensitive(self, msg) -> str:
        for match, replacement in self._patterns.items():
            pat = re.compile(match)
            msg = pat.sub(replacement, msg)
        return msg

    def format(self, record) -> str:
        msg = super().format(record)
        return self._filter_sensitive(msg)

    def formatException(self, exc_info) -> str:
        msg = super().formatException(exc_info)
        return self._filter_sensitive(msg)

    def formatStack(self, stack_info) -> str:
        msg = super().formatStack(stack_info)
        return self._filter_sensitive(msg)


def init_default_logger():  # pragma: no cover
    handlers = []
    formatter = HidingFormatter(LOG_FORMAT, compose_hiding_patterns())

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    handlers.append(stream_handler)
    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
