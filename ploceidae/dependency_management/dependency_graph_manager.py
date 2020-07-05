from threading import Lock

from ploceidae.dependency_management.dependency_graph_cycle_check_methods import DependencyGraphCycleCheckMethods
from ploceidae.dependency_management.dependency_resolution_methods import DependencyResolutionMethods
from ploceidae.dependency_management.cache_item import CacheItem
from ploceidae.dependency_management.resolved_dependencies import ResolvedDependencies
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum


class DependencyGraphManager(DependencyGraphCycleCheckMethods, DependencyResolutionMethods):

    def __init__(self, dependency_graph):
        self.dependency_graph = dependency_graph
        self.lock = Lock()

    def add_dependency(self, dependency_wrapper, visibility=DependencyVisibilityEnum.MODULE):
        cache_item = CacheItem.cache_item_factory_method(dependency_wrapper, visibility)
        with self.lock:
            if cache_item in self.dependency_graph:
                raise ValueError("dependency with name {0} already exists in dependency graph".format(dependency_wrapper.dependency_name))
            self.dependency_graph[cache_item] = dependency_wrapper
            if not self.dependency_graph_is_acyclic(self.dependency_graph):
                raise ValueError("dependency makes graph cyclic")

    def resolve_dependencies(self, dependency_wrapper, time_stamp, *dependencies_to_ignore):
        # need to be able to use the other default dependency lifetimes
        resolved_dependencies = self.resolve_dependencies_inner(dependency_wrapper, time_stamp, *dependencies_to_ignore)
        # if we have kwargs, we have a group by name of argument representing kwargs
        group = self.get_group(dependency_wrapper.dependency_object)
        resolved_dependencies_by_group = []
        if group:
            resolved_dependencies_by_group = self.resolve_dependencies_by_group(dependency_wrapper, group, time_stamp)
        return ResolvedDependencies(resolved_dependencies + resolved_dependencies_by_group, resolved_dependencies, resolved_dependencies_by_group)
