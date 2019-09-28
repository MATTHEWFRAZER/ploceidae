class TestDependencyGrouping:
    def test_grouped_dependencies_are_resolved_to_dependent(self, dependency_decorator, default_container):
        @dependency_decorator(group="deps", global_dependency=True)
        def a():
            return "a"

        @dependency_decorator(group="deps", global_dependency=True)
        def b():
            return "b"

        @dependency_decorator(group="deps", global_dependency=True)
        def c(b):
            return b + "c"

        def x(*deps):
            return deps

        resolved_deps = default_container.wire_dependencies(x)
        assert all(dep in resolved_deps for dep in (a(), b(), c(b())))

    def test_dependencies_that_are_grouped_can_be_resolved_with_normal_dependencies(self, dependency_decorator, default_container):
        @dependency_decorator(group="deps", global_dependency=True)
        def a():
            return "a"

        @dependency_decorator(group="deps", global_dependency=True)
        def b():
            return "b"

        @dependency_decorator(group="deps", global_dependency=True)
        def c(b):
            return b + "c"

        def x(a, b, c, *deps):
            return (a, b, c), deps

        resolved_deps = default_container.wire_dependencies(x)
        assert resolved_deps[0] == (a(), b(), c(b()))
        assert all(dep in resolved_deps[1] for dep in (a(), b(), c(b())))

    def test_dependency_that_is_both_grouped_and_normal(self, dependency_decorator, default_container):
        @dependency_decorator(group="deps", global_dependency=True)
        def a():
            return "a"

        def b(a, *deps):
            return (a,) + deps

        assert default_container.wire_dependencies(b) == ("a", "a")


    def test_dependency_that_is_grouped_can_be_resolved_independently_of_group(self, dependency_decorator, default_container):
        @dependency_decorator(group="deps", global_dependency=True)
        def a():
            return "a"

        def b(a):
            return "b" + a

        def c(*deps):
            return deps

        assert default_container.wire_dependencies(b) == "ba"
        assert default_container.wire_dependencies(c) == ("a",)