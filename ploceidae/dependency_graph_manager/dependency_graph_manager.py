from threading import Lock

from ploceidae.dependency_graph_manager.dependency_graph_cycle_check_methods import DependencyGraphCycleCheckMethods
from ploceidae.dependency_graph_manager.dependency_resolution_methods import DependencyResolutionMethods
from ploceidae.dependency_graph_manager.cache_item import CacheItem
from ploceidae.dependency_graph_manager.dependency_graph import DependencyGraph
from ploceidae.utilities.lib import get_group


class DependencyGraphManager(DependencyGraphCycleCheckMethods, DependencyResolutionMethods):

    DEPENDENCY_GRAPH = DependencyGraph()
    LOCK = Lock()

    @classmethod
    def add_dependency(cls, dependency_obj, global_dependency=None):
        cache_item = CacheItem.cache_item_factory_method(dependency_obj, global_dependency)
        with cls.LOCK:
            if cache_item in cls.DEPENDENCY_GRAPH:
                raise ValueError("dependency with name {0} already exists in dependency graph".format(dependency_obj.dependency_name))
            cls.DEPENDENCY_GRAPH[cache_item] = dependency_obj
            if not cls.dependency_graph_is_acyclic(cls.DEPENDENCY_GRAPH):
                raise ValueError("dependency makes graph cyclic")

    @classmethod
    def resolve_dependencies(cls, dependency_obj, time_stamp, *dependencies_to_ignore):
        # need to be able to use the other default scopes
        resolved_dependencies = cls.resolve_dependencies_inner(dependency_obj, time_stamp, *dependencies_to_ignore)
        # if we have kwargs, we have a group by name of argument representing kwargs
        group = get_group(dependency_obj.dependency_obj)
        resolved_dependencies_by_group = []
        if group:
            resolved_dependencies_by_group = cls.resolve_dependencies_by_group(dependency_obj, group, time_stamp)
        return type("ResolvedArgs", (), cls.get_attributes_from_resolved_dependencies(resolved_dependencies, resolved_dependencies_by_group))

    @staticmethod
    def get_attributes_from_resolved_dependencies(resolved_dependencies, resolved_dependencies_by_group):
        return {"all_resolved_dependencies": resolved_dependencies + resolved_dependencies_by_group,
                      "resolved_dependencies" : resolved_dependencies,
                      "resolved_dependencies_by_group": resolved_dependencies_by_group}

