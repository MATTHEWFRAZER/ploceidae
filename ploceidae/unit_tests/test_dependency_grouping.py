from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum


class TestDependencyGrouping:
    def test_grouped_dependencies_are_resolved_to_dependent(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def a():
            return "a"

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def b():
            return "b"

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def c(b):
            return b + "c"

        def x(*deps):
            return deps

        resolved_deps = container.wire_dependencies(x)
        assert all(dep in resolved_deps for dep in (a(), b(), c(b())))

    def test_grouped_dependencies_with_tranformations_are_resolved_to_dependent(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        class A(object):
            def __init__(self):
                self.x = 0
            def increment_and_return(self):
                self.x += 1
                return self

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL, transformation=lambda x: x.increment_and_return())
        def a():
            return A()

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL, transformation=lambda x: x.increment_and_return())
        def b():
            x = A()
            x.x = 2
            return x

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL, transformation=lambda x: x.increment_and_return())
        def c(b):
            x = A()
            x.x = 2 + b.x
            return x

        def x(*deps):
            return deps

        resolved_deps = container.wire_dependencies(x)
        assert all(y in [x.x for x in resolved_deps] for y in [1, 3, 6])

    def test_grouped_dependencies_with_tranformations_are_resolved_to_dependent2(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        class A(object):
            def __init__(self):
                self.x = 0
            def increment_and_return(self):
                self.x += 1
                return self

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL, transformation=lambda x: x.increment_and_return())
        def a():
            return A()

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def b():
            x = A()
            x.x = 2
            return x

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL, transformation=lambda x: x.increment_and_return())
        def c(b):
            x = A()
            x.x = b.x + 1
            return x

        def x(*deps):
            return deps

        resolved_deps = container.wire_dependencies(x)
        assert all(y in [x.x for x in resolved_deps] for y in [1, 2, 4])

    def test_dependencies_that_are_grouped_can_be_resolved_with_normal_dependencies(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def a():
            return "a"

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def b():
            return "b"

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def c(b):
            return b + "c"

        def x(a, b, c, *deps):
            return (a, b, c), deps

        resolved_deps = container.wire_dependencies(x)
        assert resolved_deps[0] == (a(), b(), c(b()))
        assert all(dep in resolved_deps[1] for dep in (a(), b(), c(b())))

    def test_dependency_that_is_both_grouped_and_normal(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def a():
            return "a"

        def b(a, *deps):
            return (a,) + deps

        assert container.wire_dependencies(b) == ("a", "a")


    def test_dependency_that_is_grouped_can_be_resolved_independently_of_group(self, basic_configurator):
        container = basic_configurator.get_container()
        dependency_decorator = basic_configurator.get_dependency_wrapper()

        @dependency_decorator(group="deps", visibility=DependencyVisibilityEnum.GLOBAL)
        def a():
            return "a"

        def b(a):
            return "b" + a

        def c(*deps):
            return deps

        assert container.wire_dependencies(b) == "ba"
        assert container.wire_dependencies(c) == ("a",)

    def test_dependency_that_has_same_name_as_group(self, basic_configurator):
        dep = 3

        dependency_decorator = basic_configurator.get_dependency_wrapper()
        container = basic_configurator.get_container()

        @dependency_decorator(group="group", visibility=DependencyVisibilityEnum.GLOBAL)
        def group():
            return dep

        def a(group):
            return group

        def b(*group):
            return group

        assert container.wire_dependencies(a) == dep
        assert container.wire_dependencies(b) == (dep,)