import types

from six import with_metaclass
import pytest

from ploceidae.scope_binding.scope_enum import ScopeEnum

class Dummy(object):
    def __init__(self, a, b, c):
        self.message = a + b + c
        self.__name__ = "test"

    def __call__(self, a, b, c):
        return a + b + c

    def method(self, a, b, c):
        return a + b + c

    @classmethod
    def class_method(cls, a, b, c):
        return a + b + c


class TestContainer(object):

    def test_dependencies_can_be_delivered_to_bound_method(self, container):
        wired = container.wire_dependencies(Dummy(1, 2, 3).method, "function")
        assert "abcbcc" == wired

    def test_dependencies_can_be_delivered_to_class_method(self, container):
        wired = container.wire_dependencies(Dummy(1, 2, 3).class_method)
        assert "abcbcc" == wired

    def test_partial_wire_up_dependencies_works_when_dependencies_to_ignore_is_empty(self, obj_to_wire_up, container):
        wired = container.partial_wire_dependencies(obj_to_wire_up.dependency_obj)
        assert "xabcbcc" == wired()

    # make sure that exceptions bubble up
    def test_wire_up_dependencies_with_obj_that_is_in_dependency_graph(self, obj_to_wire_up, container):
        try:
            wired = container.wire_dependencies(obj_to_wire_up.dependency_obj)
        except Exception as ex:
            pytest.fail("exception occurred while wiring dependencies: {}".format(ex))

        assert "xabcbcc" == wired

    def test_wire_up_dependencies_with_multiple_connected_components(self, obj_to_wire_up, obj_to_wire_up2, container2):
        wired_up = container2.wire_dependencies(obj_to_wire_up.dependency_obj)
        wired_up2 = container2.wire_dependencies(obj_to_wire_up2.dependency_obj)
        assert wired_up == "xabcbcc"
        assert wired_up2 == "def"

    def test_wire_up_dependencies_with_class_obj(self, container):
        wired_up_dummy = container.wire_dependencies(Dummy)
        assert "abcbcc" == wired_up_dummy.message

    def test_wire_up_dependencies_with_instance_callable(self, container):
        wired_up_call = container.wire_dependencies(Dummy("a", "b", "c"))
        assert wired_up_call == "abcbcc"

    def test_partial_wire_up_dependencies(self, partial_dependency_fixture):

        def expect_specific_types(a, b):
            assert a == "abc"
            assert b == "bc"

        try:
            partially_wired = partial_dependency_fixture.container.partial_wire_dependencies(expect_specific_types, *partial_dependency_fixture.ignored_dependencies)
        except Exception as ex:
            pytest.fail(". Ex {0}".format(ex))
        else:
            partially_wired(*partial_dependency_fixture.left_over_dependencies)

    def test_partial_wire_up_dependencies_to_instance_obj(self, partial_dependency_fixture):
        try:
            partial_wired = partial_dependency_fixture.container.partial_wire_dependencies(Dummy("a", "b", "c").method, *partial_dependency_fixture.ignored_dependencies)
        except Exception as ex:
            pytest.fail(". Ex {0}".format(ex))
        else:
            obj = partial_wired(*partial_dependency_fixture.left_over_dependencies)
        assert obj == "abcbcc"

    def test_wire_up_dependencies_with_dynamically_generated_methods(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def inner_a(): return "a"

        class A(object): pass

        a = A()
        # using non standard wa
        a.non_valid_method = lambda inner_a: inner_a
        # eventually don't use self as a first argument (e.g. _) as one might
        a.method = types.MethodType(lambda self, inner_a: inner_a, a)

        assert "a" == default_container.wire_dependencies(a.non_valid_method) == default_container.wire_dependencies(a.method)

    @pytest.mark.skip(reason="not supported")
    def test_wire_up_dependencies_with_class_introspection_generated_method(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def inner_a(): return "a"

        class A(object): pass

        setattr(A, "method", lambda inner_a: inner_a)
        # eventually don't use cls as first argument (e.g use _ as one might)
        setattr(A, "classmethod", classmethod(lambda cls, inner_a: inner_a))
        setattr(A, "staticmethod", staticmethod(lambda inner_a: inner_a))

        assert "a" == default_container.wire_dependencies(A.method) == default_container.wire_dependencies(A.staticmethod) == default_container.wire_dependencies(A.classmethod)

    def test_partial_wire_up_dependencies_gets_correct_value_with_instance_scope_when_later_call_to_wire_up(self, dependency_decorator, default_container):
        @dependency_decorator(scope=ScopeEnum.CLASS, global_dependency=True)
        def conflict(): return WireUp()

        class WireUp:
            def method(self, conflict):
                return conflict

        partially_wired = default_container.partial_wire_dependencies(WireUp().method)
        assert default_container.wire_dependencies(WireUp().method) is partially_wired()

    def test_mixed_scope(self, dependency_decorator, default_container):
        @dependency_decorator(scope=ScopeEnum.MODULE)
        def a(): return type("A", (), {})()

        @dependency_decorator(scope=ScopeEnum.CLASS)
        def b(): return type("B", (), {})()

        @dependency_decorator(scope=ScopeEnum.INSTANCE)
        def c(): return type("C", (), {})()

        @dependency_decorator(scope=ScopeEnum.SESSION)
        def d(): return type("D", (), {})()

        @dependency_decorator(scope=ScopeEnum.FUNCTION)
        def e(): return type("E", (), {})()

        # need a more robust way of testing this
        a_cache = []
        b_cache = []
        c_cache = []
        d_cache = []
        e_cache = []
        class Class(object):
            def x(self, a, b, c, d, e):
                assert all(a is item for item in a_cache)
                assert all(b is item for item in b_cache)
                assert all(not c is item for item in c_cache)
                assert all(d is item for item in d_cache)
                assert all(not e is item for item in e_cache)

                a_cache.append(a)
                b_cache.append(b)
                c_cache.append(c)
                d_cache.append(d)
                e_cache.append(e)

        # had an issue where an instance would get the same address as a previous one
        obj_cache = []
        for _ in range(10):
            instance = Class()
            obj_cache.append(instance)
            default_container.wire_dependencies(instance.x)

    def test_wire_up_dependencies_with_instance_introspection_generated_method(self, default_container, dependency_decorator):
        # test two instances that generate the same methods, class scope should get the same, instance and below should not
        @dependency_decorator(scope=ScopeEnum.CLASS, global_dependency=True)
        def introspection_class_test():
            return type("Class", (), {})

        @dependency_decorator(scope=ScopeEnum.INSTANCE, global_dependency=True)
        def introspection_instance_test():
            return type("Instance", (), {})

        class A(object):
            def __init__(self):
                new_lambda = lambda self, introspection_class_test, introspection_instance_test: (introspection_class_test, introspection_instance_test)
                new_method = types.MethodType(new_lambda, self)
                setattr(self, "method", new_method)

        one = A()
        two = A()
        first_class, first_instance   = default_container.wire_dependencies(one.method)
        second_class, second_instance = default_container.wire_dependencies(two.method)
        assert first_class is second_class
        assert first_instance is not second_instance

    @pytest.mark.skip(reason="lambda can't get __self__.__class__")
    def test_wire_up_dependencies_with_instance_introspection_incorrectly_generated_method(self, container_constructor, dependency_decorator):
        # test two instances that generate the same methods, class scope should get the same, instance and below should not
        @dependency_decorator(scope=ScopeEnum.CLASS, global_dependency=True)
        def introspection_class_test():
            return type("Class", (), {})

        @dependency_decorator(scope=ScopeEnum.INSTANCE, global_dependency=True)
        def introspection_instance_test():
            return type("Instance", (), {})

        class A(object):
            def __init__(self):
                new_lambda = lambda self, introspection_class_test, introspection_instance_test: (
                introspection_class_test, introspection_instance_test)
                setattr(self, "method", new_lambda)

        one = A()
        two = A()
        first_class, first_instance = container_constructor.wire_dependencies(one.method)
        second_class, second_instance = container_constructor.wire_dependencies(two.method)
        assert first_class is second_class
        assert first_instance is not second_instance

    def test_wire_up_dependencies_with_metaclass_generated_methods(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def meta_test():
            return meta_test.__name__

        class MetaClass(type):
            def __new__(mcs, name, bases, attributes):
                class_instance = type(name, bases, attributes)
                setattr(class_instance, "method", lambda self, meta_test: meta_test)
                return class_instance

        class A(with_metaclass(MetaClass)): pass

        assert default_container.wire_dependencies(A().method) == meta_test.__name__

    def test_wire_up_dependencies_to_staticmethod_from_getattr(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def staticmethod_getattr_test():
            return staticmethod_getattr_test.__name__

        class A(object):
            @staticmethod
            def s(staticmethod_getattr_test): return staticmethod_getattr_test

        assert default_container.wire_dependencies(getattr(A, "s")) == staticmethod_getattr_test.__name__

    def test_wire_up_dependencies_to_classmethod_from_getattr(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def classmethod_getattr_test():
            return classmethod_getattr_test.__name__

        class A(object):
            @classmethod
            def c(cls, classmethod_getattr_test): return classmethod_getattr_test

        assert default_container.wire_dependencies(getattr(A, "c")) == classmethod_getattr_test.__name__

    def test_wire_up_dependencies_to_instance_method_from_getattr(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def instance_method_getattr_test():
            return instance_method_getattr_test.__name__

        class A(object):
            def i(self, instance_method_getattr_test): return instance_method_getattr_test

        assert default_container.wire_dependencies(getattr(A(), "i")) == instance_method_getattr_test.__name__

    def test_wire_up_dependencies_to_dereferenced_classmethod(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def classmethod_test():
            return classmethod_test.__name__

        class A(object):
            @classmethod
            def c(cls, classmethod_test): return classmethod_test

        assert default_container.wire_dependencies(A.c) == classmethod_test.__name__

    def test_wire_up_dependencies_to_staticmethod(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def static_dereference_test():
            return static_dereference_test.__name__

        class A(object):
            @staticmethod
            def s(static_dereference_test): return static_dereference_test

        assert default_container.wire_dependencies(A.s) == static_dereference_test.__name__

    @pytest.mark.skip(reason="will fail because the class reference will not be resolved to dereferenced function")
    def test_wire_up_dependencies_to_dereferenced_classmethod(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def dereferenced_test():
            return dereferenced_test.__name__

        class A(object):
            @classmethod
            def c(cls, dereferenced_test):
                return dereferenced_test

        assert default_container.wire_dependencies(A.__dict__["c"].__func__) == dereferenced_test.__name__

    def test_wire_up_dependencies_to_dereferenced_staticmethod(self, default_container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def dereferenced_test():
            return dereferenced_test.__name__

        class A(object):
            @staticmethod
            def s(dereferenced_test):
                return dereferenced_test

        assert default_container.wire_dependencies(A.__dict__["s"].__func__) == dereferenced_test.__name__

    @pytest.mark.xfail(raises=BaseException)
    def test_wire_up_dependencies_with_missing_dependencies(self, default_container):
        def a(b): pass

        default_container.wire_dependencies(a)

    @pytest.mark.xfail(raises=BaseException)
    def test_wire_up_dependencies_to_dependency_with_missing_dependency(self, default_container, dependency_decorator):
        # we can't validate dependencies before actual dependency resolution, because we might add a dependency
        # after something declares it in its argument list
        @dependency_decorator(global_dependency=True)
        def a(b): pass

        default_container.wire_dependencies(a)

    @pytest.mark.xfail(raises=BaseException)
    def test_wire_up_dependencies_with_missing_terminal_node(self, default_container, dependency_decorator):

        @dependency_decorator(global_dependency=True)
        def x(y): pass

        @dependency_decorator(global_dependency=True)
        def y(not_exist): pass

        def test(x): pass

        default_container.wire_dependencies(test)