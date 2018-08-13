from threading import RLock

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.dependency_graph_resolver import DependencyGraphResolver
from scope_binding.scope_key import ScopeKey

class SentinalForServiceLocatorCheck(object): pass

class DependencyGraphManager(DependencyGraphResolver):

    DEPENDENCY_GRAPH = DependencyGraph()
    LOCK = RLock()

    @classmethod
    def add_dependency(cls, dependency_obj):
        with cls.LOCK:
            cls.DEPENDENCY_GRAPH.add_node(dependency_obj)

    @classmethod
    def resolve_dependencies(cls, dependency_obj, scope_key_string, *dependencies_to_ignore):
        with cls.LOCK:
            if dependency_obj.services.get(scope_key_string, SentinalForServiceLocatorCheck) is SentinalForServiceLocatorCheck:
                cls.resolve_dependency_graph(cls.DEPENDENCY_GRAPH, scope_key_string)
            dependencies = filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
            resolved_dependencies = [cls.get_dependency_obj_from_dependency_name(dependency).locate(scope_key_string) for dependency in dependencies]
            cls.purge_dependency_graph_of_function_scope_keys()
            return resolved_dependencies

    @classmethod
    def purge_dependency_graph_of_function_scope_keys(cls):
        for dependency_obj in cls.DEPENDENCY_GRAPH.values():
            dependency_obj.purge_service_locator_of_function_scope_keys()

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

    @classmethod
    def get_dependency_obj_from_dependency_name(cls, dependency_name):
        with cls.LOCK:
            try:
                return cls.DEPENDENCY_GRAPH[dependency_name]
            except KeyError:
                raise ValueError("dependency_primitives {0} is not part of dependency_primitives graph".format(dependency_name))

    @staticmethod
    def node_has_no_in_edges(node, temp_graph):
        return all(dependency not in temp_graph for dependency in node.dependencies)
