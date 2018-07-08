import pytest

from dependency_graph.dependency_graph_manager import DependencyGraphManager


class TestDependencyGraphManager(object):
    @pytest.xfail(raises=ValueError)
    def test_acyclic_check_with_indirectly_cyclic_graph(self): pass

    @pytest.xfail(raises=ValueError)
    def test_acyclic_check_with_cyclic_graph(self): pass

    def test_acylclic_check_with_graph_with_multiple_cycles(self): pass

    def test_acyclic_check_with_valid_graph(self): pass

    def test_topological_sort_with_graph_that_has_no_sort(self): pass

    def test_topological_sort_with_graph_that_has_sort(self): pass

    def test_topological_sort_with_graph_with_multiple_cycles(self): pass

    def test_node_has_no_in_edges_with_node_that_has_only_out_edges(self): pass

    def test_node_has_no_in_edges_with_node_that_has_in_edges(self): pass

    def test_node_has_no_in_edges_with_node_that_has_no_edges(self): pass