import gc

from ploceidae.dependency import dependency
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum


class TestGarbageCollection:
    def test_instance_resolved_dependency_is_cleaned_up_when_instance_is_cleaned_up(self, container):
        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        @d
        def a():
            return type("A", (), {})()

        cache = []
        class B:
            def __init__(self, a):
                cache.append(a)

        b =  container.wire_dependencies(B)
        del b
        gc.collect()
        assert not d.services

    def test_instance_resolved_dependency_is_cleaned_up_when_instance_is_cleaned_up_two(self, container):
        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        @d
        def a():
            return type("A", (), {})()

        cache = []
        class B:
            def __init__(self, a):
                cache.append(a)

        container.wire_dependencies(B)
        gc.collect()
        assert not d.services
