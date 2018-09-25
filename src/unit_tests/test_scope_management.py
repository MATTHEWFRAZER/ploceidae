from scope_binding.scope_enum import ScopeEnum


class TestScopeManagement:
    # this also needs to be tested along a dependency heirarchy
    def test_function_scope_dependency_obj_entry_is_deleted_after_delivered_to_function(self, container_constructor, dependency_decorator, dummy):
        @dependency_decorator(scope=ScopeEnum.FUNCTION)
        def a():
            return type(dummy)()

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
        @dependency_decorator(scope=ScopeEnum.INSTANCE)
        def a():
            return type("T", (), {})

        class A:
            def __init__(self, a):
                self.a = a

            def x(self, a):
                assert a is self.a

        x = container_constructor.wire_dependencies(A)
        container_constructor.wire_dependencies(x.x)

        if a.__name__ not in dependency_graph_manager.DEPENDENCY_GRAPH:
           raise Exception("dependency a was never inserted into dependency graph")

        del x

        assert a.__name__ in dependency_graph_manager.DEPENDENCY_GRAPH


    def test_class_scope_allows_for_multiple_objects(self): pass

    def test_module_scope_resolves_different_objects_to_different_modules(self, resolved_object, container_with_no_setup, dummy):

        def b(a):
            return a

        first = container_with_no_setup.wire_dependencies(b)

        assert type(resolved_object) is type(dummy)
        assert type(first) is type(dummy)
        assert resolved_object is not first

    def test_conflicting_scopes(self): pass

    def test_module_scope_resolves_same_object_in_same_module(self, container_with_no_setup, dependency_decorator, dummy):
        self.scope_test(ScopeEnum.MODULE, container_with_no_setup, dependency_decorator, dummy)

    def test_session_scope_does_not_allow_for_multiple_objects(self, container_with_no_setup, dependency_decorator, dummy):
        self.scope_test(ScopeEnum.SESSION, container_with_no_setup, dependency_decorator, dummy)

    def scope_test(self, scope_name, container_with_no_setup, dependency_decorator, dummy):
        @dependency_decorator(scope=scope_name)
        def a():
            return dummy

        def b(a):
            return a

        def c(a):
            return a

        first = container_with_no_setup.wire_dependencies(b)
        second = container_with_no_setup.wire_dependencies(b)
        third = container_with_no_setup.wire_dependencies(c)

        assert type(first) is type(dummy)
        assert type(second) is type(dummy)
        assert type(third) is type(dummy)
        assert first is second
        assert third is second
        assert first is third
