from inspect import getargspec
from threading import RLock

from dependency_graph_manager.dependency_graph_cycle_check_methods import DependencyGraphCycleCheckMethods
from dependency_graph_manager.dependency_resolution_methods import DependencyResolutionMethods


class DependencyGraphManager(DependencyGraphCycleCheckMethods, DependencyResolutionMethods):

    DEPENDENCY_GRAPH = {}
    LOCK = RLock()

    class ResolutionType:
        DEFAULT = "default"
        GROUP = "group"

    @classmethod
    def add_dependency(cls, dependency_obj):
        with cls.LOCK:
            if dependency_obj.dependency_name in cls.DEPENDENCY_GRAPH:
                raise ValueError("dependency with name {0} already exists in dependency graph".format(dependency_obj.dependency_name))
            cls.DEPENDENCY_GRAPH[dependency_obj.dependency_name] = dependency_obj
            if not cls.dependency_graph_is_acyclic(cls.DEPENDENCY_GRAPH):
                raise ValueError("dependency makes graph cyclic")

    @classmethod
    def resolve_dependencies(cls, dependency_obj, time_stamp, *dependencies_to_ignore):
        # need to be able to use the other default scopes
        resolved_dependencies = cls.resolve_dependencies_inner(dependency_obj, time_stamp, *dependencies_to_ignore)
        group = getargspec(dependency_obj.dependency_obj)[1]
        resolved_dependencies_by_group = []
        if group:
            resolved_dependencies_by_group = cls.resolve_dependencies_by_group(dependency_obj, group, time_stamp)

        attributes = {"all_resolved_dependencies": resolved_dependencies + resolved_dependencies_by_group,
                      "resolved_dependencies" : resolved_dependencies,
                      "resolved_dependencies_by_group": resolved_dependencies_by_group}
        return type("ResolvedArgs", (), attributes)
