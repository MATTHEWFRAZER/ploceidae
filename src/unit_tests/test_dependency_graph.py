import pytest


class TestDependencyGraph(object):
    def test_add_node_when_node_appears_in_graph(self): pass
    def test_add_node(self): pass


class TestDependencyGraphNode(object):
    @pytest.mark.skip(reason="the logic for checking for a dependency to have the __name__ attribute does not reside in the dependency graph node")
    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_graph_node_initialization_with_invalid_obj(self, dependency_graph_node):
        dependency_graph_node("invalid obj")

    def test_dependency_graph_node_intialization(self, dependency_graph_node):
        try:
            dependency_graph_node(lambda: True )
        except Exception as ex:
            pytest.fail("can not initialize DependencyGraphNode. Ex {0}".format(ex))