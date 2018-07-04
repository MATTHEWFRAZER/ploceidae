import pytest

from dependency import Dependency


class TestDependencyGraphManager(object):

    # is this the same as saying the graph has cycles? No because the "terminal nodes" can have dependencies that have references to nothing <- valid?
    def test_resolve_dependencies_when_there_are_no_terminal_nodes(self): pass

    def test_resolve_dependencies_for_nodes_that_have_non_linear_sorting(self): pass

    @pytest.mark.xfail(raises=ValueError)
    def test_acyclic_check_with_indirectly_cyclic_graph(self, dependency_graph_manager, dependency_graph_with_cycle):
        self.add_dependencies(dependency_graph_manager, *dependency_graph_with_cycle)
        assert not dependency_graph_manager.dependency_graph_is_acyclic(dependency_graph_manager.DEPENDENCY_GRAPH)

    @pytest.mark.xfail(raises=ValueError)
    def test_acyclic_check_with_cyclic_graph(self, dependency_graph_manager):
        def a(b): pass
        def b(a): pass

        a = Dependency.get_dependency_without_decoration(a)
        b = Dependency.get_dependency_without_decoration(b)

        self.add_dependencies(dependency_graph_manager, a, b)
        assert not dependency_graph_manager.dependency_graph_is_acyclic(dependency_graph_manager.DEPENDENCY_GRAPH)

    def test_acyclic_check_with_valid_graph(self, dependency_graph_manager, dependency_graph):

        self.add_dependencies(dependency_graph_manager, *dependency_graph)

        assert all(dependency.dependency_name in dependency_graph_manager.DEPENDENCY_GRAPH for dependency in dependency_graph)

    @pytest.mark.xfail(raises=ValueError)
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

    def test_add_depenendency_with_callable(self, dependency_graph_manager):
        l = Dependency.get_dependency_without_decoration(lambda _:_)
        dependency_graph_manager.add_dependency(l)
        assert len(dependency_graph_manager.DEPENDENCY_GRAPH) == 1

    @pytest.mark.xfail(raises=ValueError)
    def test_add_dependency_that_already_exists_in_graph(self, dependency_graph_manager):
        def a(): pass

        b = a
        a = Dependency.get_dependency_without_decoration(a)
        b = Dependency.get_dependency_without_decoration(b)
        self.add_dependencies(dependency_graph_manager, a, b)

    # do we want to test this behavior?
    def test_resolve_dependencies_after_adding_dependency(self, dependency_graph, scope_key, dependency_graph_manager):
        assert not dependency_graph_manager.resolve_dependencies(dependency_graph[-1], scope_key(dependency_graph[-1])).all_resolved_dependencies
        dependency_graph_manager.add_dependency(dependency_graph[-1])
        assert dependency_graph_manager.resolve_dependencies(dependency_graph[-2], scope_key(dependency_graph[-2])).resolved_dependencies[0] == dependency_graph[-1].dependency_obj.__name__

    def test_resolve_dependencies_with_dependent_that_has_no_dependencies(self, dependency_graph, dependency_graph_manager, scope_key):
        assert not dependency_graph_manager.resolve_dependencies(dependency_graph[-1], scope_key(dependency_graph[-1])).all_resolved_dependencies

    def test_resolve_dependencies(self, dependency_graph_manager, dependency_graph, scope_key):
        try:
            self.add_dependencies(dependency_graph_manager, *dependency_graph)
            dependencies = dependency_graph_manager.resolve_dependencies(dependency_graph[0], scope_key(dependency_graph[0].dependency_obj))
            dependency_graph[0].dependency_obj(*dependencies.all_resolved_dependencies)
        except ValueError as ex:
            pytest.fail("dependency resolution failed:{0}".format(ex))

    @pytest.mark.xfail(raises=BaseException)
    def test_resolve_dependencies_with_missing_dependency(self, dependency_graph_manager, scope_key):
        def a(b): pass

        dependency_graph_manager.add_dependency(Dependency.get_dependency_without_decoration(a))
        dependency_graph_manager.resolve_dependencies(a, scope_key(a))

    @classmethod
    def get_mocked_graph(cls, dependency_graph_node):
        mocked_graph = {"test": dependency_graph_node}
        mocked_graph.update({dependency: None for dependency in dependency_graph_node.dependencies})
        return mocked_graph

    @classmethod
    def add_dependencies(cls, dependency_graph_manager, *dependencies):
        for dependency in dependencies:
            dependency_graph_manager.add_dependency(dependency)