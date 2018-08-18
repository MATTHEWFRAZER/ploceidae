from threading import RLock


class DependencyGraphManager(object):

    DEPENDENCY_GRAPH = {}
    LOCK = RLock()

    @classmethod
    def add_dependency(cls, dependency_obj):
        with cls.LOCK:
            if dependency_obj.dependency_name in cls.DEPENDENCY_GRAPH:
                raise ValueError("dependency_primitives with name {0} already exists in dependency_primitives graph".format(dependency_obj.dependency_name))
            cls.DEPENDENCY_GRAPH[dependency_obj.dependency_name] = dependency_obj

    @classmethod
    def resolve_dependencies(cls, dependency_obj, scope_key_string, *dependencies_to_ignore):
        with cls.LOCK:
            dependencies = filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
            resolved_dependencies = []
            for dependency in dependencies:
                if not cls.DEPENDENCY_GRAPH[dependency].dependencies:
                    resolved_dependencies.append(cls.DEPENDENCY_GRAPH[dependency].locate(scope_key_string))
                else:
                    dependency_obj_inner = cls.DEPENDENCY_GRAPH[dependency]
                    resolved_dependencies.append(
                        dependency_obj_inner.locate(scope_key_string, *cls.resolve_dependencies(cls.DEPENDENCY_GRAPH[dependency], scope_key_string)))
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
