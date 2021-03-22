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


class UwsgiCache(Cache):
    def __init__(self):
        self.uwsgi = importlib.import_module('uwsgi')

    def get_item(self, url):
        return self.uwsgi.cache_get(url)

    def set_item(self, url, value):
        self.uwsgi.cache_set(url, value)


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def get_item(self, url):
        return self.cache.get(url)

    def save_item(self, url, value):
        self.cache[url] = value


def init_cache():
    if os.getenv('ENV') == 'dev':
        return MemoryCache()
    else:
        return UwsgiCache()


_cache = init_cache()


def get_cache():
    return _cache
