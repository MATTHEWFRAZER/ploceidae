from functools import partial
import logging
import sys

import pytest

sys.path.append("..")
from pygmy.dependency_graph_manager import DependencyGraphManager
from pygmy.container import Container
from pygmy.dependency import dependency
from pygmy.dependency import Dependency
from pygmy.scope_binding.scope_enum import ScopeEnum
from pygmy.scope_binding.scope_key import ScopeKey

class Dummy(): pass

@pytest.fixture
def dependency_class_obj():
    return Dependency

@pytest.fixture
def dependency_graph_manager():
    yield DependencyGraphManager
    DependencyGraphManager.DEPENDENCY_GRAPH.clear()

@pytest.fixture
def dependency_graph_with_cycle(dependency_init):
    # permute these
    def a(b): pass
    def b(c): pass
    def c(a): pass

    return dependency_init(a), dependency_init(b), dependency_init(c)


@pytest.fixture
def dependency_graph(dependency_init):
    def a(b): return "a" + b
    def b(c): return "b" + c
    def c(): return "c"

    return dependency_init(a), dependency_init(b), dependency_init(c)

@pytest.fixture
def scope_key():
    return ScopeKey

@pytest.fixture
def dependency_graph2(dependency_init):
    def d(e): return "d" + e
    def e(f): return "e" + f
    def f(): return "f"

    return dependency_init(d), dependency_init(e), dependency_init(f)


@pytest.fixture
def dependency_graph_with_obj_that_depends_on_all_other_nodes(dependency_init, dependency_graph):
    def x(a, b, c): return "x" + a + b + c
    return (dependency_init(x),) + dependency_graph

@pytest.fixture
def dependency_graph_node_with_in_edges(dependency_init):
    return dependency_init(lambda _: _)


@pytest.fixture
def dependency_graph_node_with_no_in_edges(dependency_init):
    return dependency_init(lambda: None)

@pytest.fixture
def dependency_init(dependency_class_obj):
    return partial(dependency_class_obj.get_dependency_without_decoration, global_dependency=True)

@pytest.fixture
def container_with_no_setup():
    return Container

@pytest.fixture
def dummy():
    return Dummy()

@pytest.fixture
def object_to_resolve(dependency_decorator):
    @dependency_decorator(scope=ScopeEnum.MODULE, global_dependency=True)
    def a():
        return Dummy()
    return a

@pytest.fixture
def resolved_object(container_with_no_setup, object_to_resolve):
    def b(a):
        return a
    return container_with_no_setup.wire_dependencies(b)

@pytest.fixture
def container(dependency_graph_with_obj_that_depends_on_all_other_nodes, dependency_graph_manager):
    for dependency in dependency_graph_with_obj_that_depends_on_all_other_nodes:
        dependency_graph_manager.add_dependency(dependency, global_dependency=True)
    return Container

@pytest.fixture
def container_constructor():
    DependencyGraphManager.DEPENDENCY_GRAPH.clear()
    return Container

@pytest.fixture
def container2(dependency_graph2, dependency_graph_manager, container):
    for dependency in dependency_graph2:
        dependency_graph_manager.add_dependency(dependency, global_dependency=True)
    return container

@pytest.fixture
def multiple_module_setup_with_global(dependency_decorator):
    @dependency_decorator(global_dependency=True)
    def b():
        return "global b"

@pytest.fixture
def multiple_module_setup_with_global_c(dependency_decorator):
    @dependency_decorator(global_dependency=True)
    def c():
        return "global c"

@pytest.fixture
def multiple_module_setup_with_module(dependency_decorator):
    @dependency_decorator
    def b():
        return "module b"

@pytest.fixture
def obj_to_wire_up(dependency_graph_with_obj_that_depends_on_all_other_nodes):
    return dependency_graph_with_obj_that_depends_on_all_other_nodes[0]


@pytest.fixture
def obj_to_wire_up2(dependency_graph2):
    return dependency_graph2[0]


@pytest.fixture
def dependency_graph_node():
    return None


@pytest.fixture
def dependency_decorator():
    yield dependency
    DependencyGraphManager.DEPENDENCY_GRAPH.clear()


@pytest.fixture(params=[(("a",), ("abc",)), (("b",), ("bc",)), (("a", "b"), ("abc", "bc"))])
def partial_dependency_fixture(request, container):
    attributes = {"ignored_dependencies": request.param[0], "left_over_dependencies": request.param[1], "container": container}
    return type("PartialDependencyFixture", (), attributes)

@pytest.fixture
def separate_decorator():
    def dec(func):
        def nested(*args, **kwargs):
            return func(*args, **kwargs)
        return nested
    return dec