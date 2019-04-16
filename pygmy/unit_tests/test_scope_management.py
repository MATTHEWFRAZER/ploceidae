import pytest

from pygmy.scope_binding.scope_enum import ScopeEnum
from pygmy.dependency_graph_manager.cache_item import CacheItem
from pygmy.constants import GLOBAL_NAMESPACE


class TestScopeManagement:
    # this also needs to be tested along a dependency heirarchy
    def test_function_scope_dependency_obj_entry_is_deleted_after_delivered_to_function(self, container_constructor, dependency_decorator, dummy):
        @dependency_decorator(scope=ScopeEnum.FUNCTION, global_dependency=True)
        def a():
            return dummy.__class__()

        def b(a):
            return a

        def c(a):
            return a

        first = container_constructor.wire_dependencies(b)
        second = container_constructor.wire_dependencies(b)
        third = container_constructor.wire_dependencies(c)

        assert type(first) is type(dummy)
        assert type(second) is type(dummy)
        assert type(third) is type(dummy)
        assert first is not second
        assert third is not second
        assert first is not third

        #check that service locator entries are done


    def test_instance_scope_dependency_obj_entry_is_deleted_after_instance_is_deleted(self, dependency_graph_manager, container_constructor, dependency_decorator):

        @dependency_decorator(scope=ScopeEnum.INSTANCE, global_dependency=True)
        def a():
            return type("T", (), {})()

        class A:
            def __init__(self, a):
                self.a = a

            def x(self, a):
                # we do this check to show that we have a correctly resolved instance dependency
                assert a is self.a
        #issue here is that you have to have it wired before you can generated the write key, that's why i did a temp and would call it again, not sure what to do
        x = container_constructor.wire_dependencies(A)
        container_constructor.wire_dependencies(x.x)

        cache_item = CacheItem(a, a.__name__)
        cache_item.module = GLOBAL_NAMESPACE

        if cache_item not in dependency_graph_manager.DEPENDENCY_GRAPH:
           raise Exception("dependency a was never inserted into dependency graph")

        del x

        assert cache_item in dependency_graph_manager.DEPENDENCY_GRAPH


    def test_class_scope_allows_for_multiple_objects(self): pass

    COUNT = 0
    def test_instance_scope_wires_up_different_dependency_for_each_istance(self, dependency_decorator, container):

        @dependency_decorator(scope=ScopeEnum.INSTANCE, global_dependency=True)
        def instance_a():
            self.COUNT += 1
            return self.COUNT

        class A:
            def method(self, instance_a): return instance_a

        a1 = A()
        a2 = A()

        result_a1 = container.wire_dependencies(a1.method)
        result_a2 = container.wire_dependencies(a2.method)
        result_a1_prime = container.wire_dependencies(a1.method)

        assert result_a1 != result_a2
        assert result_a1 == result_a1_prime

    def test_module_scope_resolves_different_objects_to_different_modules(self, resolved_object, container_with_no_setup, dummy):

        def b(a):
            return a

        first = container_with_no_setup.wire_dependencies(b)

        assert type(first) is type(resolved_object) is type(dummy)
        assert resolved_object is not first

    def test_overriding_fixtures(self, dependency_decorator, container):
        # expected behavior as of now is that a new fixture loaded at module load time should override the old one
        # the alternative is to raise an exception when decoration happens, but the decision parallels python's behavior
        @dependency_decorator(scope=ScopeEnum.INSTANCE, global_dependency=True)
        def conflict(): return conflict.__name__

        @dependency_decorator(scope=ScopeEnum.CLASS, global_dependency=True)
        def conflict(): return WireUp()

        class WireUp:
            def method(self, conflict):
                return conflict

            @classmethod
            def method2(cls, conflict):
                return conflict
        assert container.wire_dependencies(WireUp.method2) is container.wire_dependencies(WireUp().method)

    def test_module_scope_resolves_same_object_in_same_module(self, container_with_no_setup, dependency_decorator, dummy):
        self.scope_test(ScopeEnum.MODULE, container_with_no_setup, dependency_decorator, dummy)

    def test_session_scope_does_not_allow_for_multiple_objects(self, container_with_no_setup, dependency_decorator, dummy):
        self.scope_test(ScopeEnum.SESSION, container_with_no_setup, dependency_decorator, dummy)

    def scope_test(self, scope_name, container_with_no_setup, dependency_decorator, dummy):
        @dependency_decorator(scope=scope_name, global_dependency=True)
        def a():
            return dummy

        def b(a):
            return a

        def c(a):
            return a

        first = container_with_no_setup.wire_dependencies(b)
        second = container_with_no_setup.wire_dependencies(b)
        third = container_with_no_setup.wire_dependencies(c)

        assert type(first) is type(second) is type(third) is type(dummy)
        assert first is second
        assert third is second
        assert first is third
