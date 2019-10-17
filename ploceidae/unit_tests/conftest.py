from functools import partial
from itertools import chain
import sys

import pytest

from ploceidae.dependency_graph_manager.dependency_graph import DependencyGraph
from ploceidae.utilities.visibility_enum import VisibilityEnum

sys.path.append("..")
from ploceidae.dependency_graph_manager import DependencyGraphManager
from ploceidae.container import Container
from ploceidae.dependency import DependencyWrapper
from ploceidae.dependency import dependency
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum

class Dummy(): pass

@pytest.fixture
def default_dependency_graph_manager():
    dependency_graph_manager = DependencyGraphManager(DependencyGraph())
    DependencyWrapper.DEPENDENCY_GRAPH_MANAGER = dependency_graph_manager
    yield dependency_graph_manager
    dependency_graph_manager.dependency_graph.clear()

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
def dependency_graph2(dependency_init):
    def d(e): return "d" + e
    def e(f): return "e" + f
    def f(): return "f"

    return dependency_init(d), dependency_init(e), dependency_init(f)


@pytest.fixture
def dependency_graph_with_object_that_depends_on_all_other_nodes(dependency_init, dependency_graph):
    def x(a, b, c): return "x" + a + b + c
    return (dependency_init(x),) + dependency_graph

@pytest.fixture
def dependency_graph_node_with_in_edges(dependency_init):
    return dependency_init(lambda _: _)


@pytest.fixture
def dependency_graph_node_with_no_in_edges(dependency_init):
    return dependency_init(lambda: None)

@pytest.fixture
def dependency_init():
    return partial(DependencyWrapper.get_dependency_without_decoration, visibility=VisibilityEnum.GLOBAL)

@pytest.fixture
def dummy():
    return Dummy()

@pytest.fixture
def object_to_resolve(dependency_decorator, default_dependency_graph_manager):

    #TODO: HACK ALERT
    dependency_decorator.__self__.DEPENDENCY_GRAPH_MANAGER = default_dependency_graph_manager
    @dependency_decorator(dependency_lifetime=DependencyLifetimeEnum.MODULE, visibility=VisibilityEnum.GLOBAL)
    def a():
        return Dummy()
    return a

@pytest.fixture
def resolved_object(object_to_resolve, dependency_decorator, default_container):

    # TODO: HACK ALERT
    default_container.dependency_graph_manager = dependency_decorator.__self__.DEPENDENCY_GRAPH_MANAGER
    def b(a):
        return a
    return default_container.wire_dependencies(b)

@pytest.fixture
def container(dependency_graph_with_object_that_depends_on_all_other_nodes):
    dependency_graph_manager = DependencyGraphManager(DependencyGraph())
    for dependency in dependency_graph_with_object_that_depends_on_all_other_nodes:
        dependency_graph_manager.add_dependency(dependency, visibility=VisibilityEnum.GLOBAL)
    container = Container(dependency_graph_manager)
    return container

@pytest.fixture
def default_container(default_dependency_graph_manager):
    return Container(default_dependency_graph_manager)

@pytest.fixture
def container2(dependency_graph2, dependency_graph_with_object_that_depends_on_all_other_nodes, default_dependency_graph_manager):
    for dependency in chain.from_iterable((dependency_graph2, dependency_graph_with_object_that_depends_on_all_other_nodes)):
        default_dependency_graph_manager.add_dependency(dependency, visibility=VisibilityEnum.GLOBAL)
    container = Container(default_dependency_graph_manager)
    return container

@pytest.fixture
def multiple_module_setup_with_global(dependency_decorator):
    @dependency_decorator(visibility=VisibilityEnum.GLOBAL)
    def b():
        return "global b"

@pytest.fixture
def multiple_module_setup_with_global_c(dependency_decorator):
    @dependency_decorator(visibility=VisibilityEnum.GLOBAL)
    def c():
        return "global c"

@pytest.fixture
def multiple_module_setup_with_module(dependency_decorator):
    @dependency_decorator
    def b():
        return "module b"

@pytest.fixture
def object_to_wire_up(dependency_graph_with_object_that_depends_on_all_other_nodes):
    return dependency_graph_with_object_that_depends_on_all_other_nodes[0]


@pytest.fixture
def object_to_wire_up2(dependency_graph2):
    return dependency_graph2[0]


@pytest.fixture
def dependency_graph_node():
    return None


@pytest.fixture
def dependency_decorator():
    return dependency


@pytest.fixture(params=[(("a",), ("abc",)), (("b",), ("bc",)), (("a", "b"), ("abc", "bc"))])
def partial_dependency_fixture(request, container):
    attributes = {"ignored_dependencies": request.param[0], "left_over_dependencies": request.param[1], "container": container}
    return type("PartialDependencyFixture", (), attributes)

@pytest.fixture
def separate_decorator():
    def inner_decorator(func):
        def nested(*args, **kwargs):
            return func(*args, **kwargs)
        return nested
    return inner_decorator