from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum
from ploceidae.dependency_management.cache_item import CacheItem
from ploceidae.constants import GLOBAL_NAMESPACE
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum


class TestDependencyLifetimeManagement:
    # this also needs to be tested along a dependency hierarchy
    def test_function_dependency_lifetime_entry_is_deleted_after_delivered_to_function(self, basic_configurator, dummy):

        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION, visibility=DependencyVisibilityEnum.GLOBAL)
        def a():
            return dummy.__class__()

        def b(a):
            return a

        def c(a):
            return a

        first = container.wire_dependencies(b)
        second = container.wire_dependencies(b)
        third = container.wire_dependencies(c)

        assert type(first) is type(dummy)
        assert type(second) is type(dummy)
        assert type(third) is type(dummy)
        assert first is not second
        assert third is not second
        assert first is not third

        #check that service locator entries are done


    def test_instance_dependency_lifetime_object_entry_is_deleted_after_instance_is_deleted(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(lifetime=DependencyLifetimeEnum.INSTANCE, visibility=DependencyVisibilityEnum.GLOBAL)
        def a():
            return type("T", (), {})()

        class A:
            def __init__(self, a):
                self.a = a

            def x(self, a):
                # we do this check to show that we have a correctly resolved instance dependency
                assert a is self.a
        #issue here is that you have to have it wired before you can generated the write key, that's why i did a temp and would call it again, not sure what to do
        x = container.wire_dependencies(A)
        container.wire_dependencies(x.x)

        cache_item = CacheItem(a, a.__name__)
        cache_item.dependency_module = GLOBAL_NAMESPACE

        if cache_item not in container.dependency_graph_manager.dependency_graph:
           raise Exception("dependency a was never inserted into dependency graph")

        del x

        assert cache_item in container.dependency_graph_manager.dependency_graph

    def test_class_dependency_lifetime_allows_for_multiple_objects(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(lifetime=DependencyLifetimeEnum.CLASS, visibility=DependencyVisibilityEnum.GLOBAL)
        def mult():
            return type("B", (), {})()

        class A(object):
            def x(self, mult):
                return mult

        one = A()
        two = A()

        assert container.wire_dependencies(one.x) is container.wire_dependencies(two.x)


    COUNT = 0
    def test_instance_dependency_lifetime_wires_up_different_dependency_for_each_istance(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(lifetime=DependencyLifetimeEnum.INSTANCE, visibility=DependencyVisibilityEnum.GLOBAL)
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

    def test_module_dependency_lifetime_resolves_different_objects_to_different_modules(self, resolved_object, dummy, basic_configurator):
        container = basic_configurator.get_container()

        def b(a):
            return a

        first = container.wire_dependencies(b)
        assert type(first) is type(resolved_object) is type(dummy)
        assert resolved_object is not first

    def test_overriding_fixtures(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        # expected behavior as of now is that a new fixture loaded at module load time should override the old one
        # -- the alternative is to raise an exception when decoration happens, but the current decision parallels pytest's behavior

        @dependency_decorator(lifetime=DependencyLifetimeEnum.INSTANCE, visibility=DependencyVisibilityEnum.GLOBAL)
        def conflict(): return conflict.__name__

        @dependency_decorator(lifetime=DependencyLifetimeEnum.CLASS, visibility=DependencyVisibilityEnum.GLOBAL)
        def conflict(): return WireUp()

        class WireUp:
            def method(self, conflict):
                return conflict

            @classmethod
            def method2(cls, conflict):
                return conflict
        assert container.wire_dependencies(WireUp.method2) is container.wire_dependencies(WireUp().method)

    def test_module_dependency_lifetime_resolves_same_object_in_same_module(self, dummy, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        self._test_dependency_lifetime(DependencyLifetimeEnum.MODULE, dependency_decorator, dummy, container)

    def test_session_dependency_lifetime_does_not_allow_for_multiple_objects(self, dummy, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        self._test_dependency_lifetime(DependencyLifetimeEnum.SESSION, dependency_decorator, dummy, container)

    def _test_dependency_lifetime(self, lifetime, dependency_decorator, dummy, container):
        @dependency_decorator(lifetime=lifetime)
        def a():
            return dummy

        def b(a):
            return a

        def c(a):
            return a

        first = container.wire_dependencies(a)
        second = container.wire_dependencies(b)
        third = container.wire_dependencies(c)

        assert type(first) is type(second) is type(third) is type(dummy)
        assert first is second
        assert third is second
        assert first is third
