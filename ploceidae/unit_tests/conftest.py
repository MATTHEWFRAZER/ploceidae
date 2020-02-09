import attr
from functools import partial
from itertools import chain

import pytest

from ploceidae.dependency_management import DependencyGraphManager
from ploceidae.dependency_management.dependency_graph import DependencyGraph
from ploceidae.utilities.dependency_visibility_enum import DependencyVisibilityEnum

#sys.path.append("..")
from ploceidae.dependency.dependency_wrapper import DependencyWrapper
from ploceidae.core.configurators.basic_configurator import BasicConfigurator
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum

class Dummy(): pass

@attr.s
class ResolvedDependencyGraphContext(object):
    dependency_graph_manager  = attr.ib()
    resolved_dependency_graph = attr.ib()

    @classmethod
    def get_instance(cls, dependency_graph_manager, dependency_graph):
        resolved_dependency_graph = (dependency(dependency_graph_manager=dependency_graph_manager) for dependency in dependency_graph)
        return cls(dependency_graph_manager, resolved_dependency_graph)

@attr.s
class ResolvedObjectToWireUpContext(object):
    resolved_object_to_wire_up = attr.ib()
    container                  = attr.ib()


@pytest.fixture
def basic_configurator():
    basic_configurator = BasicConfigurator()
    yield basic_configurator
    basic_configurator.dependency_graph_manager.dependency_graph.clear()

@pytest.fixture
def default_dependency_graph_manager():
    dependency_graph_manager = DependencyGraphManager(DependencyGraph())
    yield dependency_graph_manager
    dependency_graph_manager.dependency_graph.clear()


@pytest.fixture
def configurator_with_dependency_nodes(resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context):
    resolved_dependency_graph = resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context.resolved_dependency_graph
    dependency_graph_manager  = resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context.dependency_graph_manager
    for dependency in resolved_dependency_graph:
        dependency_graph_manager.add_dependency(dependency)
    configurator = BasicConfigurator()
    configurator.dependency_graph_manager = dependency_graph_manager
    yield configurator
    configurator.dependency_graph_manager.dependency_graph.clear()

@pytest.fixture
def configurator_with_dependency_nodes2(resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context2):
    resolved_dependency_graph = resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context2.resolved_dependency_graph
    dependency_graph_manager  = resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context2.dependency_graph_manager
    for dependency in resolved_dependency_graph:
        dependency_graph_manager.add_dependency(dependency)
    configurator = BasicConfigurator()
    configurator.dependency_graph_manager = dependency_graph_manager
    yield configurator
    configurator.dependency_graph_manager.dependency_graph.clear()

@pytest.fixture
def dependency_graph_with_cycle(dependency_init):
    # permute these
    def a(b): pass
    def b(c): pass
    def c(a): pass

    return partial(dependency_init, dependency_object=a), partial(dependency_init, dependency_object=b), partial(dependency_init, dependency_object=c)

@pytest.fixture
def resolved_dependency_graph_with_cycle_context(default_dependency_graph_manager, dependency_graph_with_cycle):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, dependency_graph_with_cycle)

@pytest.fixture
def dependency_graph(dependency_init):
    def a(b): return "a" + b
    def b(c): return "b" + c
    def c(): return "c"

    return partial(dependency_init, dependency_object=a), partial(dependency_init, dependency_object=b), partial(dependency_init, dependency_object=c)

@pytest.fixture
def resolved_dependency_graph_context(default_dependency_graph_manager, dependency_graph):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, dependency_graph)

@pytest.fixture
def dependency_graph2(dependency_init):
    def d(e): return "d" + e
    def e(f): return "e" + f
    def f(): return "f"

    return partial(dependency_init, dependency_object=d), partial(dependency_init, dependency_object=e), partial(dependency_init, dependency_object=f)

@pytest.fixture
def resolved_dependency_graph2_context(default_dependency_graph_manager, dependency_graph2):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, dependency_graph2)

@pytest.fixture
def dependency_graph_with_object_that_depends_on_all_other_nodes(dependency_init, dependency_graph):
    def x(a, b, c): return "x" + a + b + c
    return (partial(dependency_init, dependency_object=x),) + dependency_graph

@pytest.fixture
def resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context(default_dependency_graph_manager, dependency_graph_with_object_that_depends_on_all_other_nodes):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, dependency_graph_with_object_that_depends_on_all_other_nodes)

@pytest.fixture
def resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context2(default_dependency_graph_manager, dependency_graph2, dependency_graph_with_object_that_depends_on_all_other_nodes):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, chain.from_iterable((dependency_graph2, dependency_graph_with_object_that_depends_on_all_other_nodes)))

@pytest.fixture
def dependency_graph_node_with_in_edges(dependency_init):
    return (partial(dependency_init, dependency_object=lambda _: _),)

@pytest.fixture
def resolved_dependency_graph_node_with_in_edges_context(default_dependency_graph_manager, dependency_graph_node_with_in_edges):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, dependency_graph_node_with_in_edges)

@pytest.fixture
def dependency_graph_node_with_no_in_edges(dependency_init):
    return (partial(dependency_init, dependency_object=lambda: None),)

@pytest.fixture
def resolved_dependency_graph_node_with_no_in_edges_context(default_dependency_graph_manager, dependency_graph_node_with_no_in_edges):
    return ResolvedDependencyGraphContext.get_instance(default_dependency_graph_manager, dependency_graph_node_with_no_in_edges)

@pytest.fixture
def dependency_init():
    return partial(DependencyWrapper.get_dependency_without_decoration, visibility=DependencyVisibilityEnum.GLOBAL)

@pytest.fixture
def dummy():
    return Dummy()

@pytest.fixture
def object_to_resolve(basic_configurator):

    dependency_wrapper = basic_configurator.get_dependency_wrapper()
    @dependency_wrapper(lifetime=DependencyLifetimeEnum.MODULE, visibility=DependencyVisibilityEnum.GLOBAL)
    def a():
        return Dummy()
    return a

@pytest.fixture
def resolved_object(object_to_resolve, basic_configurator):
    def b(a):
        return a
    return basic_configurator.get_container().wire_dependencies(b)

@pytest.fixture
def multiple_module_setup_with_global(basic_configurator):
    dependency_wrapper = basic_configurator.get_dependency_wrapper()
    @dependency_wrapper(visibility=DependencyVisibilityEnum.GLOBAL)
    def b():
        return "global b"

@pytest.fixture
def multiple_module_setup_with_global_c(basic_configurator):
    dependency_wrapper = basic_configurator.get_dependency_wrapper()
    @dependency_wrapper(visibility=DependencyVisibilityEnum.GLOBAL)
    def c():
        return "global c"

@pytest.fixture
def multiple_module_setup_with_module(basic_configurator):
    dependency_wrapper = basic_configurator.get_dependency_wrapper()
    @dependency_wrapper
    def b():
        return "module b"

@pytest.fixture
def object_to_wire_up(resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context):
    return next(resolved_dependency_graph_with_object_that_depends_on_all_other_nodes_context.resolved_dependency_graph)


@pytest.fixture
def object_to_wire_up2(resolved_dependency_graph2_context):
    return next(resolved_dependency_graph2_context.resolved_dependency_graph)


@pytest.fixture
def dependency_graph_node():
    return None


@pytest.fixture
def dependency_wrapper(basic_configurator):
    return basic_configurator.get_dependency_wrapper()


@pytest.fixture(params=[(("a",), ("abc",)), (("b",), ("bc",)), (("a", "b"), ("abc", "bc"))])
def partial_dependency_fixture(request, configurator_with_dependency_nodes):
    attributes = {"ignored_dependencies": request.param[0], "left_over_dependencies": request.param[1], "container": configurator_with_dependency_nodes.get_container()}
    return type("PartialDependencyFixture", (), attributes)

@pytest.fixture
def separate_decorator():
    def inner_decorator(func):
        def nested(*args, **kwargs):
            return func(*args, **kwargs)
        return nested
    return inner_decorator