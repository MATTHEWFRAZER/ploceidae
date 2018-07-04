from copy import copy
from itertools import chain
from operator import getitem

from constants import GLOBAL_NAMESPACE
from dependency_graph_manager.module_caches import ModuleCaches


class DependencyGraph(object):
    def __init__(self):
        self.module_caches = ModuleCaches()
        self.global_cache = {}
        # where we would put builtins
        self.builtins_cache = {}

    def __bool__(self):
        return bool(self.module_caches) or bool(self.global_cache) or bool(self.builtins_cache)

    def __zero__(self):
        return self.__bool__()

    def __contains__(self, cache_item):
        if cache_item.module == GLOBAL_NAMESPACE:
            return cache_item.dependency_name in self.global_cache or cache_item.dependency_name in self.builtins_cache
        else:
            return cache_item in self.module_caches

    def __getitem__(self, cache_item):
        return self.__general_cache_check(cache_item, getitem)

    def __setitem__(self, cache_item, value):
        if cache_item.module == GLOBAL_NAMESPACE:
            self.global_cache[cache_item.dependency_name] = value
        else:
            self.module_caches[cache_item] = value

    def __len__(self):
        return len(self.module_caches) + len(self.global_cache) + len(self.builtins_cache)

    def pop(self, cache_item):
        self.__general_cache_check(cache_item, lambda x, y: x.pop(y))

    def clear(self):
        self.module_caches.clear()
        self.global_cache.clear()
        self.builtins_cache.clear()

    def copy(self):
        cache_copy = copy(self)
        cache_copy.module_caches = self.module_caches.copy()
        cache_copy.global_cache = self.global_cache.copy()
        cache_copy.builtins_cache = self.builtins_cache.copy()
        return cache_copy

    def values(self):
        all_values = (self.module_caches.values(), self.global_cache.values(), self.builtins_cache.values())
        return list(chain.from_iterable(all_values))

    def items(self):
        all_items = (self.module_caches.items(), self.global_cache.items(), self.builtins_cache.items())
        return list(chain.from_iterable(all_items))

    def __general_cache_check(self, cache_item, to_call_on_caches):
        if cache_item in self.module_caches:
            return to_call_on_caches(self.module_caches, cache_item)
        elif cache_item.dependency_name in self.global_cache:

            return to_call_on_caches(self.global_cache, cache_item.dependency_name)
        elif cache_item.dependency_name in self.builtins_cache:
            return to_call_on_caches(self.builtins_cache, cache_item.dependency_name)
        else:
            raise KeyError("could not find cache_item: {0}::{1}".format(cache_item.module, cache_item.dependency_name))