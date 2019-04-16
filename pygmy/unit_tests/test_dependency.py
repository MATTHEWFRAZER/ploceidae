from functools import partial
from itertools import product

import pytest

from pygmy.dependency_graph_manager.cache_item import CacheItem
from pygmy.container import Container
from pygmy.constants import GLOBAL_NAMESPACE

class TestDependency:

    @pytest.mark.parametrize("global_bool1,global_bool2", product([True, False], repeat=2))
    def test_duplicate_dependency_name_with_different_dependency_resolution_scheme(self, global_bool1, global_bool2, dependency_decorator, dependency_graph_manager):
        @dependency_decorator(global_dependency=global_bool1)
        def a(): pass

        @dependency_decorator(global_dependency=global_bool2)
        def a(): pass

        cache_item = CacheItem(a, a.__name__)
        if global_bool1 == global_bool2:
            cache_item.module = GLOBAL_NAMESPACE if global_bool1 else cache_item.module
            assert dependency_graph_manager.DEPENDENCY_GRAPH[cache_item] is not a
        else:
            assert cache_item in dependency_graph_manager.DEPENDENCY_GRAPH
            cache_item.module = GLOBAL_NAMESPACE
            assert  cache_item in dependency_graph_manager.DEPENDENCY_GRAPH


    @pytest.mark.skip(reason="skipped because a will get overwrote")
    @pytest.mark.xfail(raises=ValueError)
    def test_duplicate_dependency_name_module_level_dependency_resolution_scheme(self, dependency_decorator):
        @dependency_decorator
        def a(): pass

        @dependency_decorator
        def a(): pass

    def test_dependency_decorator_has_correct_module(self, dependency_decorator, separate_decorator):
        decorated = dependency_decorator(separate_decorator)
        assert CacheItem(decorated, None).module == "pygmy.unit_tests.conftest"

    def test_dependency_application_with_runtime_syntax(self, dependency_decorator):
        application_callback = lambda: dependency_decorator(lambda: None)
        self.dependency_application("runtime", application_callback)

    def test_dependency_application_with_decorator_syntax(self, dependency_decorator):
        application_callback = partial(self.decorator_dependency_application, dependency_decorator)
        self.dependency_application("decorator", application_callback)

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_to_obj_that_depends_on_itself(self, dependency_decorator):
        @dependency_decorator
        def a(a): pass

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_to_obj_that_is_missing_name_attribute(self, dependency_decorator):
        # assumes partial object will not have __name__ attribute
        dependency_decorator(partial(lambda: None))

    @pytest.mark.xfail(raises=ValueError)
    def test_dependency_application_to_obj_that_is_not_callable(self, dependency_decorator):
        dependency_decorator("invalid")

    def test_dependency_application_with_decorator_syntax_with_a_second_decorator(self, dependency_decorator, separate_decorator):
        try:
            @dependency_decorator
            @separate_decorator
            def a(b): pass
        except Exception as ex:
            pytest.fail("could not decorate previously decorated function. Ex: {0}".format(ex))

    @pytest.mark.skip(reason="decorator renames dependency")
    def test_dependency_with_second_decorator_correctly_resolves_dependencies(self, dependency_decorator, container, separate_decorator): pass

    @pytest.mark.skip(reason="decorator renames dependency")
    def test_decorator_renames_dependency(self, dependency_decorator, container, separate_decorator):
        @dependency_decorator
        @separate_decorator
        def b(): return "b"

        def a(b): return b

        # problem is inner function of decorator renames dependency
        assert "b" == container.wire_dependencies(a)

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly(self, dependency_decorator, multiple_module_setup_with_global):
        @dependency_decorator
        def b(): return "inner_b"

        def a(b): return b

        assert Container.wire_dependencies(a) == "inner_b"

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly_as_a_non_leaf_node(self, multiple_module_setup_with_global, dependency_decorator):
        @dependency_decorator
        def b(): return "inner_b"

        @dependency_decorator
        def c(b): return b

        def a(c): return c

        assert Container.wire_dependencies(a) == "inner_b"

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly_as_sibling_leaf_node(self, multiple_module_setup_with_global, multiple_module_setup_with_global_c, dependency_decorator):
        @dependency_decorator
        def b(): return "inner_b"

        @dependency_decorator
        def c(): return "inner_c"

        def a(b, c): return (b, c)

        assert Container.wire_dependencies(a) == ("inner_b", "inner_c")

    def test_dependency_with_same_name_as_previous_dependency_gets_resolved_correctly_module_level(self, multiple_module_setup_with_module, container, dependency_decorator):
        # look so in cache_item somehow, the module name is getting resolved incorrecty as conftest
        @dependency_decorator
        def b(): return "inner_b"

        def a(b): return b

        assert container.wire_dependencies(a) == "inner_b"


    def test_dependent_with_decorator_correctly_receives_dependencies(self, dependency_graph_manager, dependency_decorator, container):
        dependency_graph_manager.DEPENDENCY_GRAPH.clear()

        def inner_decorator(func):
            def nested(b):
                return func(b)
            return nested

        @dependency_decorator(global_dependency=True)
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
    def test_dependent_with_decorator_with_different_argument_list_raises(self, dependency_decorator, container, separate_decorator):
        @dependency_decorator
        def b(): return "b"

        @separate_decorator
        def a(b): return b

        container.wire_dependencies(a)


    def test_dependency_application_with_scope_passed_as_argument(self, dependency_decorator):
        try:
            @dependency_decorator(scope="function")
            def a(): pass
        except Exception as ex:
            pytest.fail("could not decorate function. Ex: {0}".format(ex))

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