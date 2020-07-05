from datetime import datetime

import pytest

from ploceidae.dependency.dependency_wrapper import DependencyWrapper
from ploceidae.dependency_lifetime.dependency_lifetime_key import DependencyLifetimeEnum
from ploceidae.dependency_lifetime.dependency_lifetime_key import DependencyLifetimeKey
from ploceidae.dependency_management.cache_item import CacheItem
from ploceidae.dependency_management.dependency_graph import DependencyGraph
from ploceidae.constants import GLOBAL_NAMESPACE
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum


class TestDependencyGraphManager(object):

    @pytest.mark.xfail(raises=ValueError)
    def test_acyclic_check_with_indirectly_cyclic_graph(self, resolved_dependency_graph_with_cycle_context):
        resolved_dependency_graph = resolved_dependency_graph_with_cycle_context.resolved_dependency_graph
        dependency_graph_manager  = resolved_dependency_graph_with_cycle_context.dependency_graph_manager
        self.add_dependencies(dependency_graph_manager, *resolved_dependency_graph)
        assert not dependency_graph_manager.dependency_graph_is_acyclic(dependency_graph_manager.dependency_graph)

    @pytest.mark.xfail(raises=ValueError)
    def test_acyclic_check_with_cyclic_graph(self, default_dependency_graph_manager):

        def a(b): pass
        def b(a): pass

        a = DependencyWrapper.get_dependency_without_decoration(a, None, default_dependency_graph_manager)
        b = DependencyWrapper.get_dependency_without_decoration(b, None, default_dependency_graph_manager)

        self.add_dependencies(default_dependency_graph_manager, a, b)
        assert not default_dependency_graph_manager.dependency_graph_is_acyclic(default_dependency_graph_manager.dependency_graph)

    def test_acyclic_check_with_valid_graph(self, resolved_dependency_graph_context):
        resolved_dependency_graph = resolved_dependency_graph_context.resolved_dependency_graph
        dependency_graph_manager = resolved_dependency_graph_context.dependency_graph_manager
        self.add_dependencies(dependency_graph_manager, *resolved_dependency_graph)

        dependencies_not_in_graph = []
        for dependency in resolved_dependency_graph:
            cache_item = CacheItem(dependency, dependency.dependency_name)
            cache_item.dependency_module = GLOBAL_NAMESPACE
            if cache_item not in dependency_graph_manager.dependency_graph:
                dependencies_not_in_graph.append(dependency)
        assert not dependencies_not_in_graph

    @pytest.mark.xfail(raises=ValueError)
    def test_topological_sort_with_graph_that_has_no_sort(self, resolved_dependency_graph_with_cycle_context):

        resolved_dependency_graph = resolved_dependency_graph_with_cycle_context.resolved_dependency_graph
        dependency_graph_manager  = resolved_dependency_graph_with_cycle_context.dependency_graph_manager

        self.add_dependencies(dependency_graph_manager, *resolved_dependency_graph)

        assert not dependency_graph_manager.topological_sort(dependency_graph_manager.dependency_graph)

    def test_topological_sort_with_graph_that_has_sort(self, resolved_dependency_graph_context):

        resolved_dependency_graph = resolved_dependency_graph_context.resolved_dependency_graph
        dependency_graph_manager  = resolved_dependency_graph_context.dependency_graph_manager
        self.add_dependencies(dependency_graph_manager, *resolved_dependency_graph)

        assert dependency_graph_manager.topological_sort(dependency_graph_manager.dependency_graph)

    def test_node_has_no_in_edges_with_node_that_has_in_edges(self, resolved_dependency_graph_node_with_in_edges_context):
        resolved_dependency_graph = resolved_dependency_graph_node_with_in_edges_context.resolved_dependency_graph
        dependency_graph_manager  = resolved_dependency_graph_node_with_in_edges_context.dependency_graph_manager
        resolved_dependency = next(resolved_dependency_graph)
        mocked_graph = self.get_mocked_graph(resolved_dependency)
        assert not dependency_graph_manager.node_has_no_in_edges(resolved_dependency, mocked_graph)

    def test_node_has_no_in_edges_with_node_that_has_no_edges(self, resolved_dependency_graph_node_with_no_in_edges_context):
        resolved_dependency_graph = resolved_dependency_graph_node_with_no_in_edges_context.resolved_dependency_graph
        dependency_graph_manager  = resolved_dependency_graph_node_with_no_in_edges_context.dependency_graph_manager
        resolved_dependency = next(resolved_dependency_graph)
        mocked_graph = self.get_mocked_graph(resolved_dependency)
        assert dependency_graph_manager.node_has_no_in_edges(resolved_dependency, mocked_graph)

    def test_add_depenendency_with_callable(self, default_dependency_graph_manager):
        l = DependencyWrapper.get_dependency_without_decoration(lambda _:_, None, default_dependency_graph_manager)
        default_dependency_graph_manager.add_dependency(l, visibility=DependencyVisibilityEnum.GLOBAL)
        assert len(default_dependency_graph_manager.dependency_graph) == 1

    @pytest.mark.xfail(raises=ValueError)
    def test_add_dependency_that_already_exists_in_graph(self, default_dependency_graph_manager):
        def a(): pass

        b = a
        a = DependencyWrapper.get_dependency_without_decoration(a, None, default_dependency_graph_manager)
        b = DependencyWrapper.get_dependency_without_decoration(b, None, default_dependency_graph_manager)
        self.add_dependencies(default_dependency_graph_manager, a, b)

    # do we want to test this behavior?
    def test_resolve_dependencies_after_adding_dependency(self, resolved_dependency_graph_context):
        resolved_dependency_graph = list(resolved_dependency_graph_context.resolved_dependency_graph)
        dependency_graph_manager  = resolved_dependency_graph_context.dependency_graph_manager

        dependency_lifetime_key = self.dependency_lifetime_key_init(resolved_dependency_graph[-1], DependencyLifetimeEnum.FUNCTION, datetime.now())
        dependency_lifetime_key2 = self.dependency_lifetime_key_init(resolved_dependency_graph[-2], DependencyLifetimeEnum.FUNCTION, datetime.now())
        assert not dependency_graph_manager.resolve_dependencies(resolved_dependency_graph[-1], dependency_lifetime_key).all_resolved_dependencies
        dependency_graph_manager.add_dependency(resolved_dependency_graph[-1], visibility=DependencyVisibilityEnum.GLOBAL)
        assert dependency_graph_manager.resolve_dependencies(resolved_dependency_graph[-2], dependency_lifetime_key2).resolved_dependencies[0] == resolved_dependency_graph[-1].dependency_object.__name__

    def test_resolve_dependencies_with_dependent_that_has_no_dependencies(self, resolved_dependency_graph_context):
        resolved_dependency_graph = list(resolved_dependency_graph_context.resolved_dependency_graph)
        dependency_graph_manager  = resolved_dependency_graph_context.dependency_graph_manager
        dependency_lifetime_key = self.dependency_lifetime_key_init(resolved_dependency_graph[-1], DependencyLifetimeEnum.FUNCTION, datetime.now())
        assert not dependency_graph_manager.resolve_dependencies(resolved_dependency_graph[-1], dependency_lifetime_key).all_resolved_dependencies

    def test_resolve_dependencies(self, resolved_dependency_graph_context):
        resolved_dependency_graph = resolved_dependency_graph_context.resolved_dependency_graph
        dependency_graph_manager  = resolved_dependency_graph_context.dependency_graph_manager
        resolved_dependency = next(resolved_dependency_graph)
        dependency_lifetime_key = self.dependency_lifetime_key_init(resolved_dependency.dependency_object, DependencyLifetimeEnum.FUNCTION, datetime.now())
        try:
            self.add_dependencies(dependency_graph_manager, *resolved_dependency_graph)
            dependencies = dependency_graph_manager.resolve_dependencies(resolved_dependency, dependency_lifetime_key)
            resolved_dependency.dependency_object(*dependencies.all_resolved_dependencies)
        except ValueError as ex:
            pytest.fail("dependency resolution failed:{0}".format(ex))

    @pytest.mark.xfail(raises=ValueError)
    def test_resolve_dependencies_with_missing_dependency(self, default_dependency_graph_manager):
        # we can't validate dependencies before actual dependency resolution, because we might add a dependency
        # after something declares it in its argument list
        def a(b): pass

        default_dependency_graph_manager.add_dependency(DependencyWrapper.get_dependency_without_decoration(a, DependencyVisibilityEnum.GLOBAL, default_dependency_graph_manager), visibility=DependencyVisibilityEnum.GLOBAL)

        default_dependency_graph_manager.resolve_dependencies(DependencyWrapper.get_dependency_without_decoration(a, None, default_dependency_graph_manager), datetime.now)

    @pytest.mark.xfail(raises=ValueError)
    def test_resolve_dependencies_with_missing_terminal_node(self, default_dependency_graph_manager):

        def x(y): pass

        def y(not_exist): pass

        def test(x): pass

        default_dependency_graph_manager.add_dependency(DependencyWrapper.get_dependency_without_decoration(x, DependencyVisibilityEnum.GLOBAL, default_dependency_graph_manager), visibility=DependencyVisibilityEnum.GLOBAL)
        default_dependency_graph_manager.add_dependency(DependencyWrapper.get_dependency_without_decoration(y, DependencyVisibilityEnum.GLOBAL, default_dependency_graph_manager), visibility=DependencyVisibilityEnum.GLOBAL)

        default_dependency_graph_manager.resolve_dependencies(DependencyWrapper.get_dependency_without_decoration(test, None, default_dependency_graph_manager), datetime.now())

    @classmethod
    def get_mocked_graph(cls, dependency_graph_node):
        mocked_graph = DependencyGraph()
        mocked_graph.global_cache = {"test": dependency_graph_node}
        mocked_graph.global_cache.update({dependency: None for dependency in dependency_graph_node.dependencies})
        return mocked_graph

    @classmethod
    def add_dependencies(cls, dependency_graph_manager, *dependencies):
        for dependency in dependencies:
            dependency_graph_manager.add_dependency(dependency, visibility=DependencyVisibilityEnum.GLOBAL)

    @staticmethod
    def dependency_lifetime_key_init(obj, lifetime, time_stamp):
        dependency_lifetime_key = DependencyLifetimeKey(obj)
        dependency_lifetime_key.init_dependency_lifetime(lifetime)
        dependency_lifetime_key.init_alt_key(time_stamp)
        return dependency_lifetime_key