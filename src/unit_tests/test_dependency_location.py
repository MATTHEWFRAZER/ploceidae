class TestDependencyLocation:

    def test_same_node_is_utilized_by_two_different_nodes(self, dependency_class_obj, scope_key):
        dependency_instance = dependency_class_obj()
        l = lambda: type("T", (), {})
        dependency_instance(l)
        key = scope_key(l)
        assert dependency_instance.locate(key) != dependency_instance.locate(key)

    def test_container_scope_override(self): pass