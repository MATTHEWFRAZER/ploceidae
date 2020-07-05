from copy import copy
from itertools import chain
from sys import modules


class ModuleCaches(object):
    def __init__(self):
        self.caches = {}

    def __bool__(self):
        return any(bool(cache) for cache in self.caches.values())

    def __zero__(self):
        return self.__bool__()

    def __contains__(self, cache_item):
        return cache_item.dependency_module in self.caches and cache_item.dependency_name in self.caches[cache_item.dependency_module]

    def __getitem__(self, cache_item):
        try:
            self.caches[cache_item.dependency_module]
        except KeyError:
            raise KeyError("module does exist in cache")

        try:
            return self.caches[cache_item.dependency_module][cache_item.dependency_name]
        except KeyError:
            raise KeyError("{0} does not contain entry with name {1}".format(cache_item.dependency_module, cache_item.dependency_name))

    def __len__(self):
        lengths = map(len, self.caches.values())
        return sum(lengths)

    def __setitem__(self, cache_item, obj):
        if cache_item.dependency_module not in modules:
            raise ValueError("cache item is not a valid module")
        if cache_item.dependency_module not in self.caches:
            self.caches[cache_item.dependency_module] = {}
        self.caches[cache_item.dependency_module][cache_item.dependency_name] = obj

    def clear(self):
        self.caches.clear()

    def copy(self):
        cache_copy = copy(self)
        cache_copy.caches = {module: cache.copy() for module, cache in self.caches.items()}
        return cache_copy

    def pop(self, cache_item):
        self.caches[cache_item.dependency_module].pop(cache_item.dependency_name)

    def values(self):
        return chain.from_iterable(cache.values() for cache in self.caches.values())

    def items(self):
        return chain.from_iterable(cache.items() for cache in self.caches.values())