from inspect import getargspec

from dependency_graph.dependency_graph_manager import DependencyGraphManager
from framework_primivites.dependency_primitives.dependency_validation_methods import DependencyValidationMethods
from framework_primivites.primitive_marker import MarionettePrimitive
from scope_binding.scope_binding_methods import ScopeBindingMethods

__all__ = ["dependency"]


class Dependency(MarionettePrimitive):
    """decorator is a class object because that will make it easier to hook into later"""

    def __init__(self, **kwargs):
        DependencyValidationMethods.input_validation_to_init(kwargs)
        self.scope = kwargs.get("scope", "function")
        self.treat_as_resolved_obj = False

    def __call__(self, decorated_obj):
        # we need to take this algorithm into somne place else, question do we want the end caller to be in the dependency_primitives graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        self.decorated_obj = decorated_obj
        self.dependencies = [dependency for dependency in getargspec(decorated_obj)[0] if dependency not in ("self", "mcs", "cls")]
        DependencyValidationMethods.input_validation_for_dependency_obj(decorated_obj)

        DependencyGraphManager.add_dependency(self)

        ScopeBindingMethods.scope_binding_decorator(self, self.scope)

        def nested(*unresolved_dependencies):
            resolved_dependencies = DependencyGraphManager.resolve_dependencies(decorated_obj)
            dependencies = unresolved_dependencies + resolved_dependencies
            return decorated_obj(*dependencies)

        return nested

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
