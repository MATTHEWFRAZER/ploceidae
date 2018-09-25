from functools import wraps

from dependency_graph_manager  import DependencyGraphManager
from dependency.dependency_helper_methods import DependencyHelperMethods
from dependency.dependency_locator import DependencyLocator
from scope_binding.scope_binding_methods import ScopeBindingMethods

__all__ = ["dependency", "Dependency"]


class Dependency(DependencyLocator, ScopeBindingMethods, DependencyHelperMethods):
    """decorator is a class object because that will make it easier to hook into later"""

    def __init__(self, **kwargs):
        self.input_validation_to_init(kwargs)
        self.scope = kwargs.get("scope", "function")
        self.group = kwargs.get("group")
        self.callbacks = []

    def __call__(self, dependency_obj):
        # we need to take this algorithm into somne place else, question do we want the end caller to be in the dependency graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        self.input_validation_for_dependency_obj(dependency_obj)

        #self.scope_binding_decorator(DependencyGraphManager.DEPENDENCY_GRAPH, self, dependency_obj)
        # get dependencies before because we need to keep the dependencies for the callable object
        dependencies = self.get_dependencies_from_callable_obj(dependency_obj, *("self", "cls", "mcs"))
        dependency_obj = self.invoke_callbacks_after(dependency_obj)
        self.init_dependency_inner(dependency_obj)
        self.dependencies = dependencies
        try:
            DependencyGraphManager.add_dependency(self)
        except ValueError:
            pass#log
        return dependency_obj

    def init_dependency_inner(self, callable_obj):
        super(Dependency, self).__init__(self.scope, callable_obj)
        self.dependencies = self.get_dependencies_from_callable_obj(callable_obj, *("self", "cls", "mcs"))
        self.dependency_name = callable_obj.__name__

    def invoke_callbacks_after(self, func):
        @wraps(func)
        def nested(*unresolved_dependencies):
            cached = func(*unresolved_dependencies)
            for callback in self.callbacks: callback()
            return cached
        return nested

    def register_callback_after_function(self, callback):
        self.callbacks.append(callback)

    @classmethod
    def get_dependency_without_decoration(cls, dependency_obj):
        dependency = cls()
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
