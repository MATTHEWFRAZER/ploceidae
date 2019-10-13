from datetime import datetime

import pytest

from ploceidae.dependency import DependencyWrapper
from ploceidae.scope_binding.scope_key import ScopeEnum
from ploceidae.scope_binding.scope_key import ScopeKey
from ploceidae.dependency_graph_manager.cache_item import CacheItem
from ploceidae.dependency_graph_manager.dependency_graph import DependencyGraph
from ploceidae.constants import GLOBAL_NAMESPACE


class TestDependencyGraphManager(object):

    @pytest.mark.xfail(raises=ValueError)
    def test_acyclic_check_with_indirectly_cyclic_graph(self, dependency_graph_with_cycle, default_dependency_graph_manager):
        self.add_dependencies(default_dependency_graph_manager, *dependency_graph_with_cycle)
        assert not default_dependency_graph_manager.dependency_graph_is_acyclic(default_dependency_graph_manager.dependency_graph)

    @pytest.mark.xfail(raises=ValueError)
    def test_acyclic_check_with_cyclic_graph(self, default_dependency_graph_manager):
        def a(b): pass
        def b(a): pass

        a = DependencyWrapper.get_dependency_without_decoration(a)
        b = DependencyWrapper.get_dependency_without_decoration(b)

        self.add_dependencies(default_dependency_graph_manager, a, b)
        assert not default_dependency_graph_manager.dependency_graph_is_acyclic(default_dependency_graph_manager.dependency_graph)

    def test_acyclic_check_with_valid_graph(self, default_dependency_graph_manager, dependency_graph):

        self.add_dependencies(default_dependency_graph_manager, *dependency_graph)

        dependencies_not_in_graph = []
        for dependency in dependency_graph:
            cache_item = CacheItem(dependency, dependency.dependency_name)
            cache_item.dependency_module = GLOBAL_NAMESPACE
            if cache_item not in default_dependency_graph_manager.dependency_graph:
                dependencies_not_in_graph.append(dependency)
        assert not dependencies_not_in_graph

    @pytest.mark.xfail(raises=ValueError)
    def test_topological_sort_with_graph_that_has_no_sort(self, default_dependency_graph_manager, dependency_graph_with_cycle):

        self.add_dependencies(default_dependency_graph_manager, *dependency_graph_with_cycle)

        assert not default_dependency_graph_manager.topological_sort(default_dependency_graph_manager.dependency_graph)

    def test_topological_sort_with_graph_that_has_sort(self, default_dependency_graph_manager, dependency_graph):

        self.add_dependencies(default_dependency_graph_manager, *dependency_graph)

        assert default_dependency_graph_manager.topological_sort(default_dependency_graph_manager.dependency_graph)

    def test_node_has_no_in_edges_with_node_that_has_in_edges(self, default_dependency_graph_manager, dependency_graph_node_with_in_edges):
        mocked_graph = self.get_mocked_graph(dependency_graph_node_with_in_edges)
        assert not default_dependency_graph_manager.node_has_no_in_edges(dependency_graph_node_with_in_edges, mocked_graph)

    def test_node_has_no_in_edges_with_node_that_has_no_edges(self, default_dependency_graph_manager, dependency_graph_node_with_no_in_edges):
        mocked_graph = self.get_mocked_graph(dependency_graph_node_with_no_in_edges)
        assert default_dependency_graph_manager.node_has_no_in_edges(dependency_graph_node_with_no_in_edges, mocked_graph)

    def test_add_depenendency_with_callable(self, default_dependency_graph_manager):
        l = DependencyWrapper.get_dependency_without_decoration(lambda _:_)
        default_dependency_graph_manager.add_dependency(l, global_dependency=True)
        assert len(default_dependency_graph_manager.dependency_graph) == 1

    @pytest.mark.xfail(raises=ValueError)
    def test_add_dependency_that_already_exists_in_graph(self, default_dependency_graph_manager):
        def a(): pass

        b = a
        a = DependencyWrapper.get_dependency_without_decoration(a)
        b = DependencyWrapper.get_dependency_without_decoration(b)
        self.add_dependencies(default_dependency_graph_manager, a, b)

    # do we want to test this behavior?
    def test_resolve_dependencies_after_adding_dependency(self, dependency_graph, default_dependency_graph_manager):
        scope_key_object = self.scope_key_init(dependency_graph[-1], ScopeEnum.FUNCTION, datetime.now())
        scope_key_object2 = self.scope_key_init(dependency_graph[-2], ScopeEnum.FUNCTION, datetime.now())
        assert not default_dependency_graph_manager.resolve_dependencies(dependency_graph[-1], scope_key_object).all_resolved_dependencies
        default_dependency_graph_manager.add_dependency(dependency_graph[-1], global_dependency=True)
        assert default_dependency_graph_manager.resolve_dependencies(dependency_graph[-2], scope_key_object2).resolved_dependencies[0] == dependency_graph[-1].dependency_object.__name__

    def test_resolve_dependencies_with_dependent_that_has_no_dependencies(self, dependency_graph, default_dependency_graph_manager):
        scope_key_object = self.scope_key_init(dependency_graph[-1], ScopeEnum.FUNCTION, datetime.now())
        assert not default_dependency_graph_manager.resolve_dependencies(dependency_graph[-1], scope_key_object).all_resolved_dependencies

    def test_resolve_dependencies(self, default_dependency_graph_manager, dependency_graph):
        scope_key_object = self.scope_key_init(dependency_graph[0].dependency_object, ScopeEnum.FUNCTION, datetime.now())
        try:
            self.add_dependencies(default_dependency_graph_manager, *dependency_graph)
            dependencies = default_dependency_graph_manager.resolve_dependencies(dependency_graph[0], scope_key_object)
            dependency_graph[0].dependency_object(*dependencies.all_resolved_dependencies)
        except ValueError as ex:
            pytest.fail("dependency resolution failed:{0}".format(ex))

    @pytest.mark.xfail(raises=BaseException)
    def test_resolve_dependencies_with_missing_dependency(self, default_dependency_graph_manager):
        # we can't validate depenencies before actual dependency resolution, because we might add a dependency
        # after something declares it in its argument list
        def a(b): pass

        default_dependency_graph_manager.add_dependency(DependencyWrapper.get_dependency_without_decoration(a), global_dependency=True)
        default_dependency_graph_manager.resolve_dependencies(a, ScopeKey(a))

    @pytest.mark.xfail(raises=BaseException)
    def test_resolve_dependencies_with_missing_terminal_node(self, default_dependency_graph_manager):

        def x(y): pass

        def y(not_exist): pass

        def test(x): pass

        default_dependency_graph_manager.add_dependency(DependencyWrapper.get_dependency_without_decoration(x), global_dependency=True)
        default_dependency_graph_manager.add_dependency(DependencyWrapper.get_dependency_without_decoration(y), global_dependency=True)
        default_dependency_graph_manager.resolve_dependencies(test, ScopeKey(test))

    @classmethod
    def get_mocked_graph(cls, dependency_graph_node):
        mocked_graph = DependencyGraph()
        mocked_graph.global_cache = {"test": dependency_graph_node}
        mocked_graph.global_cache.update({dependency: None for dependency in dependency_graph_node.dependencies})
        return mocked_graph

    @classmethod
    def add_dependencies(cls, dependency_graph_manager, *dependencies):
        for dependency in dependencies:
            dependency_graph_manager.add_dependency(dependency, global_dependency=True)

    @staticmethod
    def scope_key_init(obj, scope, time_stamp):
        scope_key_obj = ScopeKey(obj)
        scope_key_obj.init_scope(scope)
        scope_key_obj.init_alt_key(time_stamp)
        return scope_key_obj