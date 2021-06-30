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
    def update_item(self, route, value):
        pass

    @abstractmethod
    def del_item(self, route):
        pass


class UwsgiCache(Cache):
    def __init__(self):
        self.uwsgi = importlib.import_module('uwsgi')

    def get_item(self, route):
        logger.debug(f'Retrieving {route} request result from the cache')
        res = self.uwsgi.cache_get(route)
        logger.debug(f'Retrieved for {route} result: {res}')
        return res

    def update_item(self, route, value):
        logger.debug(f'Saving {route} request result {value}')
        r = self.uwsgi.cache_update(route, value)
        logger.debug(f'Update for {route} finished with {r}')
        return r is True

    def del_item(self, route):
        logger.debug(f'Trying to delete {route} request result from the cache')
        r = True
        if self.get_item(route) is not None:
            logger.debug(f'Deleting {route} request result from the cache')
            r = self.uwsgi.cache_del(route)
            logger.debug(f'Deleting for {route} finished with {r}')
        return r


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def get_item(self, route):
        return self.cache.get(route)

    def update_item(self, route, value):
        self.cache[route] = value
        return True

    def del_item(self, route):
        if route in self.cache:
            del self.cache[route]
        return True


def init_cache():
    if ENV == 'dev':
        return MemoryCache()
    else:
        return UwsgiCache()


_cache = init_cache()


def get_cache():
    return _cache
