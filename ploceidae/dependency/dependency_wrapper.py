from functools import wraps
import logging

from ploceidae.constants import BINDINGS
from ploceidae.utilities.common import DEPENDENCY_GRAPH_MANAGER
from ploceidae.utilities.visibility_enum import VisibilityEnum
from ploceidae.dependency.dependency_helper_methods import DependencyHelperMethods
from ploceidae.dependency.dependency_locator import DependencyLocator
from ploceidae.dependency.garbage_collection.garbage_collection_observer import GarbageCollectionObserver

logger = logging.getLogger(__name__)

class DependencyWrapper(DependencyLocator, DependencyHelperMethods):
    """decorator is a class object because that will make it easier to hook into later"""

    GARBAGE_COLLECTION_OBSERVER = GarbageCollectionObserver.get_instance()
    DEPENDENCY_GRAPH_MANAGER = DEPENDENCY_GRAPH_MANAGER

    def __init__(self, **kwargs):
        """
        :param kwargs: lifetime determines how the dependency is delivered (if we cache it or not), allows for grouping dependencies,
        visibility determines the visibility of dependency (True means dependency is visible independent of its module position)
        """
        # super does get called... in this method
        self.input_validation_to_init(kwargs)
        self.lifetime = kwargs.get("lifetime", "function")
        self.group = kwargs.get("group")
        self.visibility = kwargs.get("visibility")
        self.callbacks = []

    def __call__(self, dependency_object):
        # we should put this algorithm somne place else, question do we want the end caller to be in the dependency graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        self.input_validation_for_dependency_object(dependency_object)

        # get dependencies before because we need to keep the dependencies for the callable object
        dependencies = self.get_dependencies_from_callable_object(dependency_object, *BINDINGS)
        logger.info("register callbacks to invoke after")
        dependency_object = self.invoke_callbacks_after(dependency_object)
        self.init_dependency_inner(dependency_object)
        self.dependencies = dependencies
        try:
            logger.info("adding dependency to dependency graph")
            self.DEPENDENCY_GRAPH_MANAGER.add_dependency(self, self.visibility)
        except ValueError as ex:
            logger.error("problem with adding dependency to dependency graph: {}".format(ex))
        return dependency_object

    def init_dependency_inner(self, dependency_object):
        super(DependencyWrapper, self).__init__(self.GARBAGE_COLLECTION_OBSERVER, self.lifetime, dependency_object)
        self.dependencies = self.get_dependencies_from_callable_object(dependency_object, *BINDINGS)
        self.dependency_name = dependency_object.__name__

    def invoke_callbacks_after(self, func):
        @wraps(func)
        def nested(*unresolved_dependencies, **kwargs):
            cached = func(*unresolved_dependencies, **kwargs)
            for callback in self.callbacks: callback()
            return cached
        return nested

    @classmethod
    def get_dependency_without_decoration(cls, dependency_object, visibility=VisibilityEnum.Module):
        dependency = cls(visibility=visibility)
        dependency.init_dependency_inner(dependency_object)
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
