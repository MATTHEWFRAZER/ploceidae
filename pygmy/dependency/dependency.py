import logging

from pygmy.constants import BINDINGS
from pygmy.dependency_graph_manager  import DependencyGraphManager
from pygmy.dependency.dependency_helper_methods import DependencyHelperMethods
from pygmy.dependency.dependency_locator import DependencyLocator
from pygmy.dependency.lib import class_name_to_dependency_name, invoke_callbacks_after

logger = logging.getLogger(__name__)

class Dependency(DependencyLocator, DependencyHelperMethods):
    """decorator is a class object because that will make it easier to hook into later"""

    def __init__(self, **kwargs):
        self.input_validation_to_init(kwargs)
        self.scope = kwargs.get("scope", "function")
        self.group = kwargs.get("group")
        self.global_dependency = kwargs.get("global_dependency")
        self.callbacks = []

    def __call__(self, dependency_obj):
        # we should put this algorithm somne place else, question do we want the end caller to be in the dependency graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        self.input_validation_for_dependency_obj(dependency_obj)

        # get dependencies before because we need to keep the dependencies for the callable object
        dependencies = self.get_dependencies_from_callable_obj(dependency_obj, *BINDINGS)
        logger.info("register callbacks to invoke after")
        dependency_obj = invoke_callbacks_after(self.callbacks, dependency_obj)
        self.init_dependency_inner(dependency_obj)
        self.dependencies = dependencies
        try:
            logger.info("adding dependency to dependency graph")
            DependencyGraphManager.add_dependency(self, self.global_dependency)
        except ValueError as ex:
            logger.error("problem with adding dependency to dependency graph: {}".format(ex))
        return dependency_obj

    def init_dependency_inner(self, callable_obj):
        super(Dependency, self).__init__(self.scope, callable_obj)
        self.dependencies = self.get_dependencies_from_callable_obj(callable_obj, *BINDINGS)
        self.dependency_name = callable_obj.__name__
        if self.dependency_name and self.dependency_name[0].isupper():
            self.dependency_name = class_name_to_dependency_name(self.dependency_name)

    @classmethod
    def get_dependency_without_decoration(cls, dependency_obj, global_dependency=None):
        dependency = cls(global_dependency=global_dependency)
        dependency.init_dependency_inner(dependency_obj)
        return dependency
