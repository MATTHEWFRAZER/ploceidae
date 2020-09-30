from functools import partial
from itertools import product
import sys

import pytest
from trochilidae.interoperable_filter import interoperable_filter

from ploceidae.dependency_management.cache_item import CacheItem
from ploceidae.constants import GLOBAL_NAMESPACE
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum

def a():
    return "a"

def b():
    return "b"

decorators = [lambda x: x(lifetime="function"), lambda x: x(lifetime="function", resolvable_name="a")]
functions = [a, b]
filtered_parameters = interoperable_filter(lambda x: x[0] is not x[1] and not (x[2] is functions[1] and x[0] is decorators[0]), product(decorators, decorators, functions, functions))

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


    @pytest.mark.skip(reason="skipped because a will get ignored")
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

    def test_dependency_can_be_used_as_orignally_defined_after_decoration(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()
        expected_value = 5

        @dependency_decorator
        def a():
            return expected_value

        assert a() == expected_value
        assert container.wire_dependencies(a) == expected_value

    def test_dependency_can_be_used_as_orignally_defined_after_decoration2(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()
        expected_value = 5

        @dependency_decorator
        def a():
            return expected_value

        @dependency_decorator
        def b(a):
            return a

        assert b(expected_value) == expected_value
        assert container.wire_dependencies(b) == expected_value

    def test_dependency_application_with_dependency_lifetime_passed_as_argument(self, basic_configurator):

        dependency_decorator = basic_configurator.get_dependency_wrapper()

        try:
            @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION)
            def a(): pass
        except Exception as ex:
            pytest.fail("could not decorate function. Ex: {0}".format(ex))

    @pytest.mark.skipif(int(sys.version[0]) < 3, reason="python two will not be able to resolve this type of classes' dependencies")
    def test_dependency_application_with_class_that_only_inherits_from_object(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        try:
            @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION)
            class A(object): pass
        except Exception:
            pytest.fail()

    @pytest.mark.skipif(int(sys.version[0]) < 3, reason="python two will not be able to resolve this type of classes' dependencies")
    def test_dependency_application_with_class_that_only_inherits_from_object2(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        try:
            @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION)
            class A: pass
        except Exception:
            pytest.fail()

    def test_class_object_is_resolvable(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION)
        class Resolved(object):
            def __init__(self): pass

        # we don't use resolvable name here because this is still a possible use case
        def a(Resolved):
            return type(Resolved)

        assert container.wire_dependencies(a) is Resolved

    def test_class_object_is_resolvable_by_different_name(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION, resolvable_name="resolved")
        class Resolved(object):
            def __init__(self): pass

        def a(resolved):
            return type(resolved)

        assert container.wire_dependencies(a) is Resolved

    def test_class_object_is_resolvable_by_different_name_with_transformation(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        def set_attr_for_test(x):
            x.x = None
            return x

        @dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION, resolvable_name="resolved", transformation=set_attr_for_test)
        class Resolved(object):
            def __init__(self): pass

        def a(resolved):
            return resolved

        resolved = container.wire_dependencies(a)
        assert type(resolved) is Resolved and hasattr(resolved, "x")

    @pytest.mark.parametrize("decorator_a,decorator_b,function_a,function_b",filtered_parameters)
    def test_dependency_resolvable_name_conflict(self, decorator_a,decorator_b ,function_a, function_b, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        decorator_a(dependency_decorator)(function_a)
        decorator_b(dependency_decorator)(function_b)

        def c(a):
            return a

        assert container.wire_dependencies(c) == function_a()

    def test_resolve_module_objects_as_dependencies(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        dependency_decorator(lifetime=DependencyLifetimeEnum.FUNCTION, resolvable_name="pytest")(lambda: pytest)

        def a(pytest):
            return pytest

        assert container.wire_dependencies(a) is pytest

    def test_filter_with_transformation(self, basic_configurator):
        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        @dependency_decorator(transformation=lambda xs: [x for x in xs if x == 1])
        def a():
            return [1,2,3]

        def b(a):
            return a

        assert container.wire_dependencies(b) == [1]

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_wrapper_raises_exception_when_wrapping_multiple_dependency_objects(self, basic_configurator):
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)

        @d
        def a():
            return type("A", (), {})()

        @d
        def b():
            return type("B", (), {})()

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_wrapper_raises_exception_when_wrapping_multiple_dependency_objects2(self, basic_configurator):
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)

        @d
        def a():
            return type("A", (), {})()

        d(a)

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_wrapper_raises_exception_when_wrapping_multiple_dependency_objects2(self, basic_configurator):
        dependency = basic_configurator.get_dependency_wrapper()

        d = dependency(lifetime=DependencyLifetimeEnum.INSTANCE)

        d(a)
        d(a)

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