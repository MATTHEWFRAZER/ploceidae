from ploceidae.constants import GLOBAL_NAMESPACE
from ploceidae.utilities.module_name_helper import ModuleNameHelper
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum

__all__ = ["CacheItem"]


builtin_dependencies = {}


class CacheItem(object):
    def __init__(self, dependency_object, dependency_name):
        self.dependency_object = dependency_object
        self.dependency_module = ModuleNameHelper.get_module_name(dependency_object)
        self.dependency_name   = dependency_name

    @classmethod
    def cache_item_factory_method(cls, dependency_wrapper, visibility):
        cache_item = cls(dependency_wrapper.dependency_object, dependency_wrapper.dependency_name)
        if visibility == DependencyVisibilityEnum.GLOBAL:
            cache_item.dependency_module = GLOBAL_NAMESPACE

        return cache_item