import gc

import pytest

from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum


class TestGarbageCollection:
    @pytest.mark.skip(reason="gc hook stuff not ready")
    def test_instance_resolved_dependency_is_cleaned_up_when_instance_is_cleaned_up(self, basic_configurator):
        container  = basic_configurator.get_container()
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        @d
        def a():
            return type("A", (), {})()

        #cache = []
        class B:
            def __init__(self, a):
                pass#cache.append(a)

        b =  container.wire_dependencies(B)
        del b
        gc.collect()
        assert not d.services

    @pytest.mark.skip(reason="gc hook stuff not ready")
    def test_instance_resolved_dependency_is_cleaned_up_when_instance_is_cleaned_up_two(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        @d
        def a():
            return type("A", (), {})()

        class B:
            def __init__(self, a):
                pass

        container.wire_dependencies(B)
        gc.collect()
        assert not d.services

    @pytest.mark.skip(reason="gc hook stuff not ready")
    def test_locator_gets_deleted_from_cache_when_all_services_are_gone(self): pass
