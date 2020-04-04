from functools import partial
from itertools import product

import pytest

from ploceidae.dependency_management.cache_item import CacheItem
from ploceidae.constants import GLOBAL_NAMESPACE
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum


class TestDependency:

    @pytest.mark.parametrize("global_visibility,global_visibility2", product([DependencyVisibilityEnum.GLOBAL, DependencyVisibilityEnum.MODULE], repeat=2))
    def test_duplicate_dependency_name_with_different_dependency_resolution_scheme(self, global_visibility, global_visibility2, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        @dependency_decorator(visibility=global_visibility)
        def a(): pass

        @dependency_decorator(visibility=global_visibility2)
        def a(): pass

        dependency_graph = basic_configurator.dependency_graph_manager.dependency_graph

        cache_item = CacheItem(a, a.__name__)
        if global_visibility == global_visibility2:
            cache_item.dependency_module = GLOBAL_NAMESPACE if global_visibility == DependencyVisibilityEnum.GLOBAL else cache_item.dependency_module
            assert dependency_graph[cache_item] is not a
        else:
            assert cache_item in dependency_graph
            cache_item.dependency_module = GLOBAL_NAMESPACE
            assert  cache_item in dependency_graph


    @pytest.mark.skip(reason="skipped because a will get overwrote")
    @pytest.mark.xfail(raises=ValueError)
    def test_duplicate_dependency_name_module_level_dependency_resolution_scheme(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        @dependency_decorator
        def a(): pass

        @dependency_decorator
        def a(): pass

    def test_resolve_dependency_that_is_registered_after_dependent(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_wrapper = basic_configurator.get_dependency_wrapper()

        answer = 2

        def a(b):
            return b

        @dependency_wrapper
        def b():
            return answer

        assert answer == container.wire_dependencies(a)

    def test_resolve_dependency_that_is_registered_after_wrapped_dependent(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_wrapper = basic_configurator.get_dependency_wrapper()

        answer = 2

        @dependency_wrapper
        def a(b):
            return b

        @dependency_wrapper
        def b():
            return answer

        assert answer == container.wire_dependencies(a)

    def test_dependency_decorator_has_correct_module(self, basic_configurator, separate_decorator):

        dependency_decorator = basic_configurator.get_dependency_wrapper()

        decorated = dependency_decorator(separate_decorator)
        assert CacheItem(decorated, None).dependency_module == "ploceidae.unit_tests.conftest"

    def test_dependency_application_with_runtime_syntax(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        application_callback = lambda: dependency_decorator(lambda: None)
        self.dependency_application("runtime", application_callback)

    def test_dependency_application_with_decorator_syntax(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        application_callback = partial(self.decorator_dependency_application, dependency_decorator)
        self.dependency_application("decorator", application_callback)

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_to_object_that_depends_on_itself(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        @dependency_decorator
        def a(a): pass

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_to_object_that_is_missing_name_attribute(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        # assumes partial object will not have __name__ attribute
        dependency_decorator(partial(lambda: None))

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_to_object_that_is_not_callable(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        dependency_decorator("invalid")

    def test_dependency_application_with_decorator_syntax_with_a_second_decorator(self, basic_configurator, separate_decorator):

        dependency_decorator = basic_configurator.get_dependency_wrapper()

        try:
            @dependency_decorator
            @separate_decorator
            def a(b): pass
        except Exception as ex:
            pytest.fail("could not decorate previously decorated function. Ex: {0}".format(ex))

    @pytest.mark.skip(reason="decorator renames dependency")
    def test_dependency_with_second_decorator_correctly_resolves_dependencies(self, basic_configurator, separate_decorator): pass

    @pytest.mark.skip(reason="decorator renames dependency")
    def test_decorator_renames_dependency(self, basic_configurator, separate_decorator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator
        @separate_decorator
        def b(): return "b"

        def a(b): return b

        # problem is inner function of decorator renames dependency
        assert "b" == default_container.wire_dependencies(a)

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly(self, basic_configurator,
                                                                                      multiple_module_setup_with_global):

        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator
        def b(): return "inner_b"

        def a(b): return b

        assert container.wire_dependencies(a) == "inner_b"

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly_as_a_non_leaf_node(self,
                                                                                                         basic_configurator,
                                                                                                         multiple_module_setup_with_global):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator
        def b(): return "inner_b"

        @dependency_decorator
        def c(b): return b

        def a(c): return c

        assert container.wire_dependencies(a) == "inner_b"

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly_as_sibling_leaf_node(self, basic_configurator, multiple_module_setup_with_global,
                                                                                                           multiple_module_setup_with_global_c):

        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator
        def b(): return "inner_b"

        @dependency_decorator
        def c(): return "inner_c"

        def a(b, c): return (b, c)

        assert container.wire_dependencies(a) == ("inner_b", "inner_c")

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly_module_level(self, basic_configurator, multiple_module_setup_with_module):

        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        # look so in cache_item somehow, the module name is getting resolved incorrectly as conftest
        @dependency_decorator
        def b(): return "inner_b"

        def a(b): return b

        assert container.wire_dependencies(a) == "inner_b"


    def test_dependent_with_decorator_correctly_receives_dependencies(self, basic_configurator):

        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        def inner_decorator(func):
            def nested(b):
                return func(b)
            return nested

        @dependency_decorator(visibility=DependencyVisibilityEnum.GLOBAL)
        def b():
            return "b"

        @inner_decorator
        def a(b):
            return b

        assert "b" == container.wire_dependencies(a)

    # reason why it fails is that separate_decorator overshadows argument list of a, i.e. wiring it will see *args not b
    # https://stackoverflow.com/questions/52941573/is-there-a-way-for-a-python-function-to-know-it-is-getting-decorated-at-module-l
    # from the answer, possibly only allow valid decorators with dependencies

    @pytest.mark.xfail
    def test_dependent_with_decorator_with_different_argument_list_raises(self, basic_configurator, separate_decorator):

        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator
        def b(): return "b"

        @separate_decorator
        def a(b): return b

        container.wire_dependencies(a)


    def test_dependency_application_with_dependency_lifetime_passed_as_argument(self, basic_configurator):

        dependency_decorator = basic_configurator.get_dependency_wrapper()

        try:
            @dependency_decorator(lifetime="function")
            def a(): pass
        except Exception as ex:
            pytest.fail("could not decorate function. Ex: {0}".format(ex))

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_with_class_that_only_inherits_from_object(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(lifetime="function")
        class A(object): pass

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_with_class_that_only_inherits_from_object2(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(lifetime="function")
        class A: pass

    def test_class_object_is_resolvable(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        @dependency_decorator(lifetime="function")
        class Resolved(object):
            def __init__(self): pass

        # TODO: allow for lower class conversion so that an argument does not look like this???
        def a(Resolved):
            return type(Resolved)

        assert container.wire_dependencies(a) is Resolved

    @staticmethod
    def dependency_application(syntax, application_callback):
        try:
            application_callback()
        except Exception as ex:
            pytest.fail("could not decorate simple function with {0} syntax. Ex: {1}".format(syntax, ex))

    @staticmethod
    def decorator_dependency_application(dependency_decorator):
        @dependency_decorator
        def a(): pass