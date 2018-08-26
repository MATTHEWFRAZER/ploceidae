from inspect import getargspec
from threading import RLock

from scope_binding.scope_key import ScopeKey


class DependencyGraphManager(object):

    DEPENDENCY_GRAPH = {}
    LOCK = RLock()

    class ResolutionType:
        DEFAULT = "default"
        GROUP = "group"

    @classmethod
    def add_dependency(cls, dependency_obj):
        with cls.LOCK:
            if dependency_obj.dependency_name in cls.DEPENDENCY_GRAPH:
                raise ValueError("dependency_primitives with name {0} already exists in dependency_primitives graph".format(dependency_obj.dependency_name))
            cls.DEPENDENCY_GRAPH[dependency_obj.dependency_name] = dependency_obj

    @classmethod
    def resolve_dependencies(cls, dependency_obj, *dependencies_to_ignore):
        # need to be able to use the other default scopes
        resolved_dependencies = cls.resolve_dependencies_inner(dependency_obj, *dependencies_to_ignore)
        group = getargspec(dependency_obj.dependency_obj)[1]
        resolved_dependencies_by_group = []
        if group:
            resolved_dependencies_by_group = cls.resolve_dependencies_by_group(dependency_obj, group)

        attributes = {"all_resolved_dependencies": resolved_dependencies + resolved_dependencies_by_group,
                      "resolved_dependencies" : resolved_dependencies,
                      "resolved_dependencies_by_group": resolved_dependencies_by_group}
        return type("ResolvedArgs", (), attributes)

    @classmethod
    def resolve_dependencies_by_group(cls, dependency_obj, group):
        dependency_retrieval_method = lambda: [name for name, dependency in cls.DEPENDENCY_GRAPH.items() if dependency.group == group]
        return cls.dependency_resolution_algorithm(dependency_obj, dependency_retrieval_method)

    @classmethod
    def resolve_dependencies_inner(cls, dependency_obj, *dependencies_to_ignore):
        dependency_retrieval_method = lambda: filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
        return cls.dependency_resolution_algorithm(dependency_obj, dependency_retrieval_method)

    @classmethod
    def dependency_resolution_algorithm(cls, dependency_obj, dependency_retrieval_method):
        scope_key = ScopeKey(dependency_obj.dependency_obj)
        with cls.LOCK:
            dependencies = dependency_retrieval_method()
            resolved_dependencies = []
            for dependency in dependencies:
                # if there is no need to resolve arguments
                if not cls.DEPENDENCY_GRAPH[dependency].dependencies:
                    resolved_dependencies.append(cls.DEPENDENCY_GRAPH[dependency].locate(scope_key))
                else:
                    dependency_obj_inner = cls.DEPENDENCY_GRAPH[dependency]
                    resolved_args = cls.resolve_dependencies(cls.DEPENDENCY_GRAPH[dependency])
                    resolved_dependencies.append(dependency_obj_inner.locate(scope_key, *resolved_args.all_resolved_dependencies))
            return resolved_dependencies

    @classmethod
    def dependency_graph_is_acyclic(cls, dependency_graph):
        temp_graph = dependency_graph.copy()
        graph_has_topological_sort = cls.topological_sort(temp_graph)
        del temp_graph
        return graph_has_topological_sort

    @classmethod
    def topological_sort(cls, temp_graph):
        while temp_graph:
            node_with_no_in_edges = cls.get_node_with_no_in_edges(temp_graph)
            if node_with_no_in_edges is None:
                return False
            temp_graph.pop(node_with_no_in_edges)
        return True

    @classmethod
    def get_node_with_no_in_edges(cls, temp_graph):
        """finds the first node in the graph it can find with no in edges, if it can not find any, None is returned"""
        for node_name, node in temp_graph.items():
            if cls.node_has_no_in_edges(node, temp_graph):
                return node_name

    @staticmethod
    def node_has_no_in_edges(node, temp_graph):
        return all(dependency not in temp_graph for dependency in node.dependencies)
