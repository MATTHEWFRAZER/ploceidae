import logging

from pymonad import Functor

from pygmy.constants import GLOBAL_NAMESPACE
from pygmy.dependency_graph_manager.cache_item import CacheItem
from pygmy.utilities.pygmy_reduce import pygmy_reduce
from pygmy.utilities.reduce_operand import ReduceOperand

logger = logging.getLogger(__name__)

class DependencyGraphCycleCheckMethods(object):
    @classmethod
    def dependency_graph_is_acyclic(cls, dependency_graph):
        temp_graph = dependency_graph.copy()
        graph_has_topological_sort = cls.topological_sort(temp_graph)
        del temp_graph
        logger.info("dependency graph has topological sort: {0}".format(graph_has_topological_sort))
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
                return CacheItem(node.dependency_obj, node_name)

    @classmethod
    def node_has_no_in_edges(cls, node, temp_graph):
        def no_dependencies_appear_in_temp_graph(*dependencies):
            return not any(cls.dependency_appears_in_temp_graph(dependency, node, temp_graph) for dependency in dependencies)

        reduce_operand = ReduceOperand(no_dependencies_appear_in_temp_graph)
        return pygmy_reduce(lambda x, y: x & Functor(y), node.dependencies, reduce_operand).invoke()

    @staticmethod
    def dependency_appears_in_temp_graph(dependency, node, temp_graph):
        # we use dependency object here because it gives us access to a module (doesn't have to be a valid module in this case)
        cache_item = CacheItem(node.dependency_obj, dependency)
        if cache_item in temp_graph:
            return True
        cache_item.module = GLOBAL_NAMESPACE
        if cache_item in temp_graph:
            return True

        return False