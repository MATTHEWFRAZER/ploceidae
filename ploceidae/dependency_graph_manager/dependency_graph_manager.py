from threading import Lock

from ploceidae.dependency_graph_manager.dependency_graph_cycle_check_methods import DependencyGraphCycleCheckMethods
from ploceidae.dependency_graph_manager.dependency_resolution_methods import DependencyResolutionMethods
from ploceidae.dependency_graph_manager.cache_item import CacheItem
from ploceidae.utilities.lib import get_group


class DependencyGraphManager(DependencyGraphCycleCheckMethods, DependencyResolutionMethods):

    def __init__(self, dependency_graph):
        self.dependency_graph = dependency_graph
        self.lock = Lock()

    def add_dependency(self, dependency_obj, global_dependency=None):
        cache_item = CacheItem.cache_item_factory_method(dependency_obj, global_dependency)
        with self.lock:
            if cache_item in self.dependency_graph:
                raise ValueError("dependency with name {0} already exists in dependency graph".format(dependency_obj.dependency_name))
            self.dependency_graph[cache_item] = dependency_obj
            if not self.dependency_graph_is_acyclic(self.dependency_graph):
                raise ValueError("dependency makes graph cyclic")

    def resolve_dependencies(self, dependency_obj, time_stamp, *dependencies_to_ignore):
        # need to be able to use the other default scopes
        resolved_dependencies = self.resolve_dependencies_inner(dependency_obj, time_stamp, *dependencies_to_ignore)
        # if we have kwargs, we have a group by name of argument representing kwargs
        group = get_group(dependency_obj.dependency_obj)
        resolved_dependencies_by_group = []
        if group:
            resolved_dependencies_by_group = self.resolve_dependencies_by_group(dependency_obj, group, time_stamp)
        return type("ResolvedArgs", (), self.get_attributes_from_resolved_dependencies(resolved_dependencies, resolved_dependencies_by_group))

    @staticmethod
    def get_attributes_from_resolved_dependencies(resolved_dependencies, resolved_dependencies_by_group):
        return {"all_resolved_dependencies": resolved_dependencies + resolved_dependencies_by_group,
                      "resolved_dependencies" : resolved_dependencies,
                      "resolved_dependencies_by_group": resolved_dependencies_by_group}

