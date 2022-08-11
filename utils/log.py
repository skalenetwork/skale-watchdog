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

import hashlib
import logging
import re
import sys


HIDING_PATTERNS = [
    r'NEK\:\w+',
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # noqa
    r'ws[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # noqa
    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'  # noqa
]


class HidingFormatter:
    def __init__(self, base_formatter, patterns=HIDING_PATTERNS):
        self.base_formatter = base_formatter
        self._patterns = patterns

    @classmethod
    def convert_match_to_sha3(cls, match):
        return hashlib.sha3_256(match.group(0).encode('utf-8')).digest().hex()

    def format(self, record):
        msg = self.base_formatter.format(record)
        for pattern in self._patterns:
            pat = re.compile(pattern)
            msg = pat.sub(self.convert_match_to_sha3, msg)
        return msg

    def __getattr__(self, attr):
        return getattr(self.base_formatter, attr)


def init_default_logger():  # pragma: no cover
    handlers = []
    base_formatter = logging.Formatter(
        '[%(asctime)s %(levelname)s] (%(threadName)s) %(name)s:%(lineno)d - %(message)s'  # noqa
    )
    formatter = HidingFormatter(base_formatter, HIDING_PATTERNS)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    handlers.append(stream_handler)
    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
