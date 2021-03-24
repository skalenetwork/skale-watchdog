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

import importlib
import logging
import os

from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class Cache(metaclass=ABCMeta):
    @abstractmethod
    def get_item(self, url):
        pass

    @abstractmethod
    def set_item(self, url, value):
        pass

    @abstractmethod
    def del_item(self, url):
        pass


class UwsgiCache(Cache):
    def __init__(self):
        self.uwsgi = importlib.import_module('uwsgi')

    def get_item(self, url):
        logger.debug(f'Retrieving {url} request result from cache')
        return self.uwsgi.cache_get(url)

    def set_item(self, url, value):
        self.uwsgi.cache_set(url, value)

    def del_item(self, url):
        self.uwsgi.cache_del(url)


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def get_item(self, url):
        return self.cache.get(url)

    def set_item(self, url, value):
        self.cache[url] = value

    def del_item(self, url):
        del self.cache[url]


def init_cache():
    if os.getenv('ENV') == 'dev':
        return MemoryCache()
    else:
        return UwsgiCache()


_cache = init_cache()


def get_cache():
    return _cache
