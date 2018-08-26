class TestDependencyGrouping:
    def test_grouped_dependencies_are_resolved_to_dependent(self, container_with_no_setup, dependency_decorator):
        @dependency_decorator(group="deps")
        def a():
            return "a"

        @dependency_decorator(group="deps")
        def b():
            return "b"

        @dependency_decorator(group="deps")
        def c(b):
            return b + "c"

        def x(*deps):
            return deps

        resolved_deps = container_with_no_setup.wire_dependencies(x)
        assert all(dep in resolved_deps for dep in (a(), b(), c(b())))

    def test_dependency_that_is_grouped_can_resolved_independently(self, container_with_no_setup): pass

