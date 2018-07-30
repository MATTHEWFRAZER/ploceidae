from inspect import getargspec

from dependency_graph.dependency_graph_manager import DependencyGraphManager
from framework_primivites.dependency_primitives.dependency_initialization_methods import DependencyInitializationMethods
from framework_primivites.primitive_marker import MarionettePrimitive
from scope_binding.scope_binding_methods import ScopeBindingMethods

__all__ = ["dependency", "Dependency"]


class Dependency(MarionettePrimitive):
    """decorator is a class object because that will make it easier to hook into later"""

    def __init__(self, **kwargs):
        DependencyInitializationMethods.input_validation_to_init(kwargs)
        self.scope = kwargs.get("scope", "function")

    def __call__(self, dependency_obj):
        # we need to take this algorithm into somne place else, question do we want the end caller to be in the dependency_primitives graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        DependencyInitializationMethods.input_validation_for_dependency_obj(dependency_obj)
        self.init_dependency_inner(dependency_obj)

        def nested(*unresolved_dependencies):
            resolved_dependencies = DependencyGraphManager.resolve_dependencies(self)
            dependencies = unresolved_dependencies + resolved_dependencies
            return dependency_obj(*dependencies)

        return nested

    def init_dependency_inner(self, dependency_obj):
        self.treat_as_resolved_obj = False
        self.dependency_obj = dependency_obj
        self.dependencies = DependencyInitializationMethods.get_dependencies_from_callable_obj(dependency_obj, tuple())
        self.dependency_name = dependency_obj.__name__
        try:
            DependencyGraphManager.add_dependency(self)
        except ValueError:
            pass#log
        ScopeBindingMethods.scope_binding_decorator(DependencyGraphManager.RESOLVED_DEPENDENCY_GRAPH, self)

    @classmethod
    def get_dependency_from_dependency_obj(cls, dependency_obj, scope):
        dependency = cls(scope=scope)
        dependency.init_dependency_inner(dependency_obj)
        return dependency

    @classmethod
    def control_initialization(cls, *args, **kwargs):
        """
        this makes it so that dependency can be invoked as a decorator without calling it with empty args. need args and
        kwargs here because it needs to be called like __init__ or __call__
        """
        if kwargs:
            # if we're calling it like __init__
            return cls(**kwargs)
        else:
            # if we're calling it like __call__
            return cls()(*args)


dependency = Dependency.control_initialization
