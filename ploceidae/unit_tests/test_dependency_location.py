from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum
from ploceidae.dependency_lifetime.dependency_lifetime_key import DependencyLifetimeKey

class TestDependencyLocation:

    def test_function_dependency_lifetime(self, basic_configurator):
        dependency_instance = basic_configurator.get_dependency_wrapper()(lifetime=DependencyLifetimeEnum.FUNCTION)
        l = lambda: type("T", (), {})
        dependency_instance(l)
        key = DependencyLifetimeKey(l)
        assert dependency_instance.locate(key) != dependency_instance.locate(key)

    def test_non_instance_dependency_lifetime_can_be_located(self, basic_configurator):
        dependency_instance = basic_configurator.get_dependency_wrapper()(lifetime=DependencyLifetimeEnum.SESSION)
        test = "test"
        l = lambda: test
        dependency_instance(l)
        key = DependencyLifetimeKey(l)
        key.init_dependency_lifetime(DependencyLifetimeEnum.SESSION)
        assert dependency_instance.locate(key) == test
        assert test in [item[1] for item in dependency_instance.services.items()]