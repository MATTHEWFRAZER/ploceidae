from scope_binding.scope_enum import ScopeEnum

class Dummy(): pass

class TestScopeManagement:
    # this also needs to be tested along a dependency heirarchy
    def test_function_scope_dependency_obj_entry_is_deleted_after_delivered_to_function(self, container_constructor, dependency_decorator):
        @dependency_decorator(scope=ScopeEnum.FUNCTION)
        def a():
            return Dummy()

        def b(a):
            return a

        first_x = container_constructor.wire_dependencies(b)
        second_x = container_constructor.wire_dependencies(b)

        assert type(first_x) is Dummy
        assert type(second_x) is Dummy
        assert first_x is not second_x

        #check that service locator entries are done



    def test_instance_scope_dependency_obj_entry_is_deleted_after_delivered_to_instance(self): pass
    def test_class_scope_allows_for_multiple_objects(self): pass
    def test_module_scope_allows_for_multiple_objects(self): pass
    def test_session_scope_does_not_allow_for_multiple_objects(self): pass