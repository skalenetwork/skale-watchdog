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

from abc import ABCMeta, abstractmethod

from configs import ENV

logger = logging.getLogger(__name__)


class Cache(metaclass=ABCMeta):
    @abstractmethod
    def get_item(self, route):
        pass

    @abstractmethod
    def set_item(self, route, value):
        pass

    @abstractmethod
    def del_item(self, route):
        pass


class UwsgiCache(Cache):
    def __init__(self):
        self.uwsgi = importlib.import_module('uwsgi')

    def get_item(self, route):
        logger.debug(f'Retrieving {route} request result from cache')
        return self.uwsgi.cache_get(route)

    def set_item(self, route, value):
        self.uwsgi.cache_set(route, value)

    def del_item(self, route):
        if self.get_item(route) is not None:
            self.uwsgi.cache_del(route)


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def get_item(self, route):
        return self.cache.get(route)

    def set_item(self, route, value):
        self.cache[route] = value

    def del_item(self, route):
        if route in self.cache:
            del self.cache[route]


def init_cache():
    if ENV == 'dev':
        return MemoryCache()
    else:
        return UwsgiCache()


_cache = init_cache()


def get_cache():
    return _cache
