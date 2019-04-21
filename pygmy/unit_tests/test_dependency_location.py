class TestDependencyLocation:

    def test_function_scope(self, dependency_class_obj, scope_key):
        dependency_instance = dependency_class_obj()
        l = lambda: type("T", (), {})
        dependency_instance(l)
        key = scope_key(l)
        assert dependency_instance.locate(key) != dependency_instance.locate(key)