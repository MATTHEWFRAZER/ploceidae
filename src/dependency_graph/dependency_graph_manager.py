import inspect

from dependency_graph.dependency_graph import DependencyGraphNode
from dependency_graph.dependency_graph import DependencyGraph


class DependencyGraphManager(object):

    DEPENDENCY_GRAPH = DependencyGraph()

    @classmethod
    def add_dependency(cls, callable_obj):
        dependency_obj = cls.make_depency_obj_from_callable(callable_obj)
        cls.DEPENDENCY_GRAPH.add_node(dependency_obj)

    @classmethod
    def resolve_dependencies(cls, callable_obj, *dependencies_to_ignore):
        """
        resolves the referenced dependencies declared in an argument list by recursively doing the same for each dependency
        It does this through first resolving the dependencies and calling the actual object to which the dependencies need to be resolved
        as this will deliver to its dependent the object it wants
        This does not include the base dependent object which will be called when its used
        """

        ###### HACKETY HACK HACK, FIX THIS!
        dependency_graph_copy = cls.DEPENDENCY_GRAPH.copy()
        def recursive_resolve_dependencies(callable_obj_inner, *dependencies_to_ignore_inner):
            resolved_dependency_graph = []
            dependency = cls.make_depency_obj_from_callable(callable_obj_inner)
            dependencies = filter(lambda dependency: dependency not in dependencies_to_ignore_inner, dependency.dependencies)
            for dependency_on_dependency_name in dependencies:
                resolved_dependency = cls.apply_dependencies_to_dependency_obj(recursive_resolve_dependencies, dependency_graph_copy, dependency_on_dependency_name, dependency)
                resolved_dependency_graph.append(resolved_dependency)
            return resolved_dependency_graph

        return recursive_resolve_dependencies(callable_obj, *dependencies_to_ignore)
        ###### END HACK

    @classmethod
    def apply_dependencies_to_dependency_obj(cls, recursive_resolve_dependencies, dependency_graph_copy, dependency_on_dependency_name, dependency):
        try:
            dependency_on_dependency = dependency_graph_copy[dependency_on_dependency_name]
        except KeyError:
            raise ValueError(
                "Could not resolve {0} (dependency to {1}) in dependency graph".format(dependency_on_dependency_name, dependency.dependency_obj))
        resolved_dependencies = recursive_resolve_dependencies(dependency_on_dependency.dependency_obj)
        # check on actual dependency object so that the same object can not be bound to a separate name and be passed in as a "different object"
        if dependency_on_dependency.dependency_obj in resolved_dependencies:
            raise ValueError("{0} is a dependency on itself".format(dependency_on_dependency_name))
        return dependency_on_dependency.dependency_obj(*resolved_dependencies)


    @staticmethod
    def make_depency_obj_from_callable(callable_obj):
        dependencies = [dependency for dependency in inspect.getargspec(callable_obj)[0] if dependency not in ("self", "mcs", "cls")]
        return DependencyGraphNode(callable_obj, *dependencies)

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
    def node_has_no_in_edges(node, temp_graph):
        return all(dependency not in temp_graph for dependency in node.dependencies)
