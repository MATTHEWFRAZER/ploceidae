import logging
from inspect import getargspec
from pprint import pformat

from ploceidae.dependency_lifetime.dependency_lifetime_key import DependencyLifetimeKey
from ploceidae.dependency_management.cache_item import CacheItem
from ploceidae.utilities.module_name_helper import ModuleNameHelper

logger = logging.getLogger(__name__)

class DependencyResolutionMethods(object):

    def resolve_dependencies_by_group(self, dependency_object, group, time_stamp):
        logger.info("resolving dependencies as group")
        dependency_retrieval_method = lambda: [name for name, dependency in self.dependency_graph.items() if dependency.group == group]
        return self.dependency_resolution_algorithm(dependency_object, dependency_retrieval_method, time_stamp)

    def resolve_dependencies_inner(self, dependency_wrapper, time_stamp, *dependencies_to_ignore):
        logger.info("resolving dependencies")
        dependency_retrieval_method = lambda: filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_wrapper.dependencies)
        return self.dependency_resolution_algorithm(dependency_wrapper, dependency_retrieval_method, time_stamp)

    def dependency_resolution_algorithm(self, dependency_wrapper, dependency_retrieval_method, time_stamp):
        logger.info("general resolution algorithm start")
        dependency_lifetime_key = DependencyLifetimeKey(dependency_wrapper.dependency_object)
        dependency_lifetime_key.init_alt_key(time_stamp)
        with self.lock:
            dependencies = dependency_retrieval_method()
            ret =  self.resolve_dependencies_as_list(list(dependencies), dependency_lifetime_key)
            return ret

    def replace_alt_keys_with_valid_dependency_lifetime_from_instance(self, instance, object_to_wire_up, time_stamp):
        with self.lock:
            for dependency in self.dependency_graph.values():
                dependency.replace_alt_keys_with_valid_dependency_lifetime_from_instance(instance, object_to_wire_up, time_stamp)

    def resolve_dependencies_as_list(self, dependencies, dependency_lifetime_key):
        resolved_graph = self.generate_resolved_dependency_graph(dependencies, dependency_lifetime_key)
        return self.resolve_arguments_to_dependencies(dependencies, resolved_graph)

    def generate_resolved_dependency_graph(self, dependencies, dependency_lifetime_key):
        dependency_stack = [dependencies]
        resolved_graph = {}
        while dependency_stack:
            self.resolve_dependency_to_dependency_graph(dependency_lifetime_key, resolved_graph, dependency_stack)
        logger.debug("resolved graph : \n{0}".format(pformat(resolved_graph)))
        return resolved_graph

    def resolve_dependency_to_dependency_graph(self, dependency_lifetime_key, resolved_graph, dependency_stack):
        dependencies = dependency_stack.pop()
        for dependency_name in dependencies:
            dependency_wrapper = self.find_dependency_object(dependency_name, dependency_lifetime_key)
            if dependency_wrapper is None:
                # we can't validate dependencies before actual dependency resolution, because we might add a dependency
                # after something declares it in its argument list
                raise ValueError("{0} doesn't exist".format(dependency_name))
            cache_item = CacheItem(dependency_wrapper.dependency_object, dependency_wrapper.dependency_name)
            # if there is no need to resolve arguments
            if not self.dependency_graph[cache_item].dependencies:
                logger.debug("dependency object {0} was resolved with no arguments".format(cache_item.dependency_name))
                resolved_graph[cache_item.dependency_name] = self.dependency_graph[cache_item].locate(dependency_lifetime_key)
            else:
                self.resolve_dependency_with_dependencies_to_dependency_graph(cache_item, resolved_graph, dependency_lifetime_key, dependency_stack)

    def resolve_dependency_with_dependencies_to_dependency_graph(self, cache_item, resolved_graph, dependency_lifetime_key, dependency_stack):
        dependency_object_inner = self.dependency_graph[cache_item]
        resolved_args = self.resolve_arguments_to_dependencies(dependency_object_inner.dependencies,
                                                              resolved_graph)
        if resolved_args:
            logger.debug("dependency object {0} resolved its arguments".format(cache_item.dependency_name))
            resolved_graph[cache_item.dependency_name] = dependency_object_inner.locate(dependency_lifetime_key,
                                                                                     *resolved_args)
        else:
            logger.debug("dependency object {0} doesn't have arguments resolved yet".format(dependency_object_inner.dependency_name))
            # do not change the order of these appends, or else endless loop
            dependency_stack.append([dependency_object_inner.dependency_name])
            dependency_stack.append(dependency_object_inner.dependencies)

    def find_dependency_object(self, dependency_name, dependency_lifetime_key):
        dependency_wrapper = self.resolve_dependency_object_by_module(dependency_name, dependency_lifetime_key)
        return dependency_wrapper if dependency_wrapper is not None else self.resolve_dependency_object_in_dependency_graph(dependency_name)

    def resolve_dependency_object_by_module(self, dependency_name, dependency_lifetime_key):
        for dependency_wrapper in self.dependency_graph.values():
            if self.is_dependency_found_by_module(dependency_wrapper, dependency_name, dependency_lifetime_key):
                logger.debug("found dependency_name object with module match {0}".format(dependency_wrapper.dependency_name))
                return dependency_wrapper

    def resolve_dependency_object_in_dependency_graph(self, dependency_name):
        for dependency_wrapper in self.dependency_graph.values():
            if dependency_wrapper.dependency_name == dependency_name:
                logger.debug("found dependency_name object {0}".format(dependency_wrapper.dependency_name))
                return dependency_wrapper

    @staticmethod
    def is_dependency_found_by_module(dependency_wrapper, dependency_name, dependency_lifetime_key):
        return ModuleNameHelper.get_module_name(dependency_wrapper.dependency_object) == ModuleNameHelper.get_module_name(
            dependency_lifetime_key.dependency_object) and dependency_wrapper.dependency_name == dependency_name

    @staticmethod
    def resolve_arguments_to_dependencies(dependencies, resolved_graph):
        resolved_arguments = []
        for dependency_name in dependencies:
            try:
                resolved_arguments.append(resolved_graph[dependency_name])
            except:
                return []
        logger.debug("resolving dependencies as arguments to dependency object {0}".format(dependencies))
        return resolved_arguments

    @classmethod
    def get_dependencies(cls, dependency_object):
        return cls.get_argspec(dependency_object)[0]

    @classmethod
    def get_group(cls, dependency_object):
        return cls.get_argspec(dependency_object)[1]

    @staticmethod
    def get_argspec(dependency_object):
        try:
            return getargspec(dependency_object)
        except TypeError:
            return getargspec(dependency_object.__init__)
