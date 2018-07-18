import inspect

from dependency_graph.dependency_graph import DependencyGraphNode
from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.dependency_with_mutable_dependencies import DependencyWithMutableDependencies


class DependencyGraphManager(object):

    DEPENDENCY_GRAPH = DependencyGraph()
    RESOLVED_DEPENDENCY_GRAPH = {}

    @classmethod
    def add_dependency(cls, callable_obj):
        dependency_obj = cls.make_depency_obj_from_callable(callable_obj)
        cls.DEPENDENCY_GRAPH.add_node(dependency_obj)

    @classmethod
    def resolve_dependencies(cls, callable_obj, *dependencies_to_ignore):
        if not cls.RESOLVED_DEPENDENCY_GRAPH:
            cls.resolve_dependency_graph()
        dependency_obj = cls.make_depency_obj_from_callable(callable_obj)
        dependencies = filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
        return [cls.RESOLVED_DEPENDENCY_GRAPH[dependency] for dependency in dependencies]

    @classmethod
    def resolve_dependency_graph(cls):
        # resolve the dependency objects to their dependencies and apply at end
        dependency_graph_copy = {key : DependencyWithMutableDependencies(value) for key, value in cls.DEPENDENCY_GRAPH.items()}
        while dependency_graph_copy:
            dependency_obj = cls.find_node_with_no_out_edges(dependency_graph_copy)
            dependency_obj_name = dependency_obj.dependency_obj.__name__
            cls.pop_all_references_to_dependency(dependency_graph_copy, dependency_obj_name)
            graph_node = cls.apply_dependencies(dependency_obj) if cls.is_resolvable_dependency(dependency_obj) else dependency_obj
            cls.RESOLVED_DEPENDENCY_GRAPH[dependency_obj_name] = graph_node

    @staticmethod
    def find_node_with_no_out_edges(dependency_graph):
        for dependency in dependency_graph.values():
            if not dependency.mutable_dependencies:
                return dependency
        else:
            raise BaseException("dependency graph has some unresolvable dependencies")

    @classmethod
    def is_resolvable_dependency(cls, dependency_obj):
        # maybe we want to return dependencies from a function
        return all(type(cls.RESOLVED_DEPENDENCY_GRAPH[dependency_name]).__name__ != "Dependency" for dependency_name in dependency_obj.dependencies)

    @staticmethod
    def pop_all_references_to_dependency(dependency_graph, dependency_name):
        dependency_graph.pop(dependency_name)
        for dependency_obj in dependency_graph.values():
            dependency_obj.mutable_dependencies = [dependency for dependency in dependency_obj.mutable_dependencies if dependency != dependency_name]

    @classmethod
    def apply_dependencies(cls, dependency_obj):
        resolved_dependencies = [cls.RESOLVED_DEPENDENCY_GRAPH[dependency] for dependency in dependency_obj.dependencies]
        return dependency_obj.dependency_obj(*resolved_dependencies)

    @classmethod
    def dependency_graph_is_acyclic(cls, dependency_graph):
        # topological sort
        # with start node remove the in edges one with no in edges must be left if there are no nodes with no in edges raise
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
    def get_dependency_on_dependency(dependency_graph_copy, dependency_on_dependency_name):
        try:
            return dependency_graph_copy[dependency_on_dependency_name]
        except KeyError:
            raise ValueError(
                "Could not resolve {0} in dependency graph".format(dependency_on_dependency_name))

    @staticmethod
    def make_depency_obj_from_callable(callable_obj):
        dependencies = [dependency for dependency in inspect.getargspec(callable_obj)[0] if
                        dependency not in ("self", "mcs", "cls")]
        return DependencyGraphNode(callable_obj, *dependencies)

    @staticmethod
    def node_has_no_in_edges(node, temp_graph):
        return all(dependency not in temp_graph for dependency in node.dependencies)
