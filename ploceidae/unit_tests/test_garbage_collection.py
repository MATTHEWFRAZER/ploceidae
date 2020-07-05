import gc
from threading import Event
import time

import pytest

from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum
from ploceidae.dependency.garbage_collection.garbage_collection_observer import GarbageCollectionObserver
from ploceidae.dependency.dependency_wrapper import DependencyWrapper
from ploceidae.dependency.garbage_collection.scheduler import Scheduler

COLLECTION_EVENT = Event()

class GarbageCollectionObserverFake(GarbageCollectionObserver):

    def __call__(self):
        has_callbacks_before_call = bool(self.callbacks)
        ret = super(GarbageCollectionObserverFake, self).__call__()
        if has_callbacks_before_call and not self.callbacks:
            COLLECTION_EVENT.set()
        return ret

@pytest.fixture
def monkey_patcher(monkeypatch):
    def monkey_patch():
        # scheduler needs to be monkey patched first or else the scheduling interval will not be changed
        monkeypatch.setattr(Scheduler, "SCHEDULING_INTERVAL_IN_SECONDS", 1)
        monkeypatch.setattr(DependencyWrapper, "GARBAGE_COLLECTION_OBSERVER", GarbageCollectionObserverFake.get_instance())
    return monkey_patch

class TestGarbageCollection:
    def teardown_method(self):
        COLLECTION_EVENT.clear()

    def test_instance_resolved_dependency_is_cleaned_up_when_instance_is_cleaned_up(self, basic_configurator, monkey_patcher):
        monkey_patcher()

        container  = basic_configurator.get_container()
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        @d
        def a():
            return type("A", (), {})()

        class B:
            def __init__(self, a):
                pass

        b =  container.wire_dependencies(B)
        del b
        gc.collect()

        if not COLLECTION_EVENT.wait(5):
            raise Exception("collection event was not set")
        assert not d.services

    def test_instance_resolved_dependency_is_cleaned_up_when_instance_is_cleaned_up_2(self, basic_configurator, monkey_patcher):
        monkey_patcher()

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

        if not COLLECTION_EVENT.wait(5):
            raise Exception("collection event was not set")
        assert not d.services

    def test_instance_resolved_dependency_is_not_cleaned_up_when_instance_is_not_cleaned_up(self, basic_configurator, monkey_patcher):
        monkey_patcher()

        container  = basic_configurator.get_container()
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        @d
        def a():
            return type("A", (), {})()

        class B:
            def __init__(self, a):
                pass

        b =  container.wire_dependencies(B)
        gc.collect()

        time.sleep(5)
        assert d.services
        # no collection allowed
        assert b

    def test_session_locator_does_not_get_deleted_from_cache(self, basic_configurator, monkey_patcher):
        monkey_patcher()

        container = basic_configurator.get_container()
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)
        d2 = dependency(lifetime=DependencyLifetimeEnum.SESSION)

        @d
        def a():
            return type("A", (), {})()

        @d2
        def c():
            return type("C", (), {})()

        class B:
            def __init__(self, a, c):
                pass

        b = container.wire_dependencies(B)
        del b
        gc.collect()

        time.sleep(5)
        assert not d.services
        assert d2.services