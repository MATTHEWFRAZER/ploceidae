from ploceidae.constants import GLOBAL_NAMESPACE
from ploceidae.utilities.module_name_helper import ModuleNameHelper

__all__ = ["CacheItem"]


builtin_dependencies = {}


class CacheItem(object):
    def __init__(self, obj, dependency_name):
        self.obj = obj
        self.module = ModuleNameHelper.get_module_name(obj)
        self.dependency_name = dependency_name

    @classmethod
    def cache_item_factory_method(cls, dependency_obj, global_dependency):
        cache_item = cls(dependency_obj.dependency_obj, dependency_obj.dependency_name)
        if global_dependency:
            cache_item.module = GLOBAL_NAMESPACE

        return cache_item