from dependency_graph.dependency_graph_manager import DependencyGraphManager
from framework_primivites.dependency_primitives.dependency_initialization_methods import DependencyInitializationMethods
from framework_primivites.dependency_primitives.dependency_service_locator import DependencyServiceLocator
from framework_primivites.primitive_marker import MarionettePrimitive
from scope_binding.scope_binding_methods import ScopeBindingMethods
from scope_binding.scope_key import ScopeKey

__all__ = ["dependency", "Dependency"]


class Dependency(MarionettePrimitive, DependencyServiceLocator):
    """decorator is a class object because that will make it easier to hook into later"""

    def __init__(self, **kwargs):
        DependencyInitializationMethods.input_validation_to_init(kwargs)
        self.scope = kwargs.get("scope", "function")
        self.callbacks = []

    def __call__(self, dependency_obj):
        # we need to take this algorithm into somne place else, question do we want the end caller to be in the dependency_primitives graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        DependencyInitializationMethods.input_validation_for_dependency_obj(dependency_obj)
        self.init_dependency_inner(dependency_obj)

        try:
            DependencyGraphManager.add_dependency(self)
        except ValueError:
            pass#log
        scope_key = ScopeKey(dependency_obj, self.scope)
        ScopeBindingMethods.scope_binding_decorator(DependencyGraphManager.RESOLVED_DEPENDENCY_GRAPH, self, scope_key)

        def nested(*unresolved_dependencies):
            resolved_dependencies = DependencyGraphManager.resolve_dependencies(self, ScopeKey(dependency_obj, self.scope))
            dependencies = unresolved_dependencies + resolved_dependencies
            return dependency_obj(*dependencies)

        return self.invoke_callbacks_after(nested)

    def init_dependency_inner(self, dependency_obj):
        super(Dependency, self).__init__(dependency_obj)
        self.treat_as_resolved_obj = False
        self.dependencies = DependencyInitializationMethods.get_dependencies_from_callable_obj(dependency_obj, tuple())
        self.dependency_name = dependency_obj.__name__

    def invoke_callbacks_after(self, func):
        def nested(*unresolved_dependencies):
            cached = func(*unresolved_dependencies)
            for callback in self.callbacks: callback()
            return cached
        return nested

    def register_callback_after_function(self, callback):
        self.callbacks.append(callback)

    @classmethod
    def get_dependency_without_decoration(cls, dependency_obj, scope):
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
