import pytest


class TestDependencyGraphManager(object):

    # is this the same as saying the graph has cycles? No because the "terminal nodes" can have dependencies that have references to nothing <- valid?
    def test_resolve_dependencies_when_there_are_no_terminal_nodes(self): pass

    def test_acyclic_check_with_indirectly_cyclic_graph(self, dependency_graph_manager, dependency_graph_with_cycle):
        self.add_dependencies(dependency_graph_manager, *dependency_graph_with_cycle)
        assert not dependency_graph_manager.dependency_graph_is_acyclic(dependency_graph_manager.DEPENDENCY_GRAPH)

    def test_acyclic_check_with_cyclic_graph(self, dependency_graph_manager):
        def a(b): pass
        def b(a): pass

        self.add_dependencies(dependency_graph_manager, a, b)
        assert not dependency_graph_manager.dependency_graph_is_acyclic(dependency_graph_manager.DEPENDENCY_GRAPH)

    def test_acyclic_check_with_valid_graph(self, dependency_graph_manager, dependency_graph):

        self.add_dependencies(dependency_graph_manager, *dependency_graph)

        assert all(dependency.__name__ in dependency_graph_manager.DEPENDENCY_GRAPH for dependency in dependency_graph)

    def test_topological_sort_with_graph_that_has_no_sort(self, dependency_graph_manager, dependency_graph_with_cycle):

        self.add_dependencies(dependency_graph_manager, *dependency_graph_with_cycle)

        assert not dependency_graph_manager.topological_sort(dependency_graph_manager.DEPENDENCY_GRAPH)

    def test_topological_sort_with_graph_that_has_sort(self, dependency_graph_manager, dependency_graph):

        self.add_dependencies(dependency_graph_manager, *dependency_graph)

        assert dependency_graph_manager.topological_sort(dependency_graph_manager.DEPENDENCY_GRAPH)

    def test_node_has_no_in_edges_with_node_that_has_in_edges(self, dependency_graph_manager, dependency_graph_node_with_in_edges):
        mocked_graph = self.get_mocked_graph(dependency_graph_node_with_in_edges)
        assert not dependency_graph_manager.node_has_no_in_edges(dependency_graph_node_with_in_edges, mocked_graph)

    def test_node_has_no_in_edges_with_node_that_has_no_edges(self, dependency_graph_manager, dependency_graph_node_with_no_in_edges):
        mocked_graph = self.get_mocked_graph(dependency_graph_node_with_no_in_edges)
        assert dependency_graph_manager.node_has_no_in_edges(dependency_graph_node_with_no_in_edges, mocked_graph)

    @pytest.mark.skip(reason="the logic for checking for a dependency_primitives being a valid callable does not reside in the dependency_primitives graph manager")
    @pytest.mark.xfail(raises=ValueError)
    def test_add_dependency_with_non_callable_throws(self, dependency_graph_manager):
        dependency_graph_manager.add_dependency(None)

    def test_add_depenendency_with_callable(self, dependency_graph_manager):
        dependency_graph_manager.add_dependency(lambda _: _)
        assert len(dependency_graph_manager.DEPENDENCY_GRAPH) == 1

    @pytest.mark.xfail(raises=ValueError)
    def test_add_dependency_that_already_exists_in_graph(self, dependency_graph_manager):
        def a(): pass

        b = a

        self.add_dependencies(dependency_graph_manager, a, b)

    # do we want to test this behavior?
    def test_resolve_dependencies_after_adding_dependency(self, dependency_graph_manager):
        def a(): return "a"
        def b(a): pass
        assert not dependency_graph_manager.resolve_dependencies(a)
        dependency_graph_manager.add_dependency(a)
        assert dependency_graph_manager.resolve_dependencies(b)[0] == "a"

    def test_resolve_dependencies_with_dependent_that_has_no_dependencies(self, dependency_graph_manager):
        def a(): pass
        assert not dependency_graph_manager.resolve_dependencies(a)

    @pytest.mark.skip(reason="the logic for checking for a dependency_primitives being a dependency_primitives to itself does not reside in the dependency_primitives graph manager")
    @pytest.mark.xfail(raises=ValueError)
    def test_resolve_dependencies_with_dependent_that_declares_dependency_on_itself(self, dependency_graph_manager):
        def a(a): pass
        dependency_graph_manager.add_dependency(a)
        dependency_graph_manager.resolve_dependencies(a)

    def test_resolve_dependencies(self, dependency_graph_manager, dependency_graph):
        try:
            self.add_dependencies(dependency_graph_manager, *dependency_graph)
            dependencies = dependency_graph_manager.resolve_dependencies(dependency_graph[0])
            dependency_graph[0](*dependencies)
        except ValueError as ex:
            pytest.fail("dependency_primitives resolution failed:{0}".format(ex))

    @pytest.mark.xfail(raises=BaseException)
    def test_resolve_dependencies_with_missing_dependency(self, dependency_graph_manager):
        def a(b): pass

        dependency_graph_manager.add_dependency(a)
        dependency_graph_manager.resolve_dependencies(a)

    @classmethod
    def get_mocked_graph(cls, dependency_graph_node):
        mocked_graph = {"test": dependency_graph_node}
        mocked_graph.update({dependency: None for dependency in dependency_graph_node.dependencies})
        return mocked_graph

    @classmethod
    def add_dependencies(cls, dependency_graph_manager, *dependencies):
        for dependency in dependencies:
            dependency_graph_manager.add_dependency(dependency)