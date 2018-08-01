from threading import RLock

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.dependency_graph_resolver import DependencyGraphResolver


class DependencyGraphManager(DependencyGraphResolver):

    DEPENDENCY_GRAPH = DependencyGraph()
    IS_RESOLVED = False

    @classmethod
    def add_dependency(cls, dependency_obj, scope_key):
        cls.DEPENDENCY_GRAPH.add_node(dependency_obj, scope_key)

    @classmethod
    def resolve_dependencies(cls, dependency_obj, scope_key, *dependencies_to_ignore):
        #if len(cls.DEPENDENCY_GRAPH) != len(cls.RESOLVED_DEPENDENCY_GRAPH):
        #    cls.resolve_dependency_graph(cls.DEPENDENCY_GRAPH)
        if not cls.IS_RESOLVED:
            cls.IS_RESOLVED = True
            cls.resolve_dependency_graph(cls.DEPENDENCY_GRAPH, str(scope_key))
        dependencies = filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
        return [cls.get_dependency_obj_from_dependency_name(dependency, str(scope_key)) for dependency in dependencies]

    @classmethod
    def dependency_graph_is_acyclic(cls, dependency_graph, scope_key_string):
        temp_graph = dependency_graph.copy()
        graph_has_topological_sort = cls.topological_sort(temp_graph, scope_key_string)
        del temp_graph
        return graph_has_topological_sort

    @classmethod
    def topological_sort(cls, temp_graph, scope_key_string):
        while temp_graph:
            node_with_no_in_edges = cls.get_node_with_no_in_edges(temp_graph, scope_key_string)
            if node_with_no_in_edges is None:
                return False
            temp_graph.pop(node_with_no_in_edges)
        return True

    @classmethod
    def get_node_with_no_in_edges(cls, temp_graph, scope_key_string):
        """finds the first node in the graph it can find with no in edges, if it can not find any, None is returned"""
        for node_name, node in temp_graph.items(scope_key_string):
            if cls.node_has_no_in_edges(node, temp_graph):
                return node_name

    @classmethod
    def get_dependency_obj_from_dependency_name(cls, dependency_name, scope_key_string):
        try:
            return cls.RESOLVED_DEPENDENCY_GRAPH[dependency_name][scope_key_string]
        except KeyError:
            raise ValueError("dependency_primitives {0}::{1} is not part of dependency_primitives graph".format(dependency_name, scope_key_string))

    @staticmethod
    def node_has_no_in_edges(node, temp_graph):
        return all(dependency not in temp_graph for dependency in node.dependencies)
