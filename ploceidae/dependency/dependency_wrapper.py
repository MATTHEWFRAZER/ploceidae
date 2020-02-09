import logging

from ploceidae.constants import BINDINGS
from ploceidae.dependency.dependency_wrapper_helper_methods import DependencyWrapperHelperMethods
from ploceidae.dependency.dependency_locator import DependencyLocator
from ploceidae.dependency.garbage_collection.garbage_collection_observer import GarbageCollectionObserver
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum

logger = logging.getLogger(__name__)

class DependencyWrapper(object):
    """decorator is a class object because that will make it easier to hook into later"""

    GARBAGE_COLLECTION_OBSERVER = GarbageCollectionObserver.get_instance()

    def __init__(self, lifetime, group, visibility, dependency_graph_manager):
        """
        :param kwargs: lifetime determines how the dependency is delivered (if we cache it or not), allows for grouping dependencies,
        visibility determines the visibility of dependency (True means dependency is visible independent of its module position)
        """
        self.lifetime = lifetime
        self.group = group
        self.visibility = visibility
        self.dependency_graph_manager = dependency_graph_manager
        self.callbacks = []

    def __call__(self, dependency_object):
        # TODO: we should move this algorithm somewhere else, question do we want the end caller to be in the dependency graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        DependencyWrapperHelperMethods.input_validation_for_dependency_object(dependency_object)

        self.dependencies = DependencyWrapperHelperMethods.get_dependencies_from_callable_object(dependency_object, *BINDINGS)
        logger.info("register callbacks to invoke after")
        decorated_dependency_object = DependencyWrapperHelperMethods.register_callbacks_with_dependency_object(self.callbacks, dependency_object)
        self.dependency_locator = DependencyLocator(self.GARBAGE_COLLECTION_OBSERVER, self.lifetime, decorated_dependency_object)
        self.dependency_name = dependency_object.__name__
        try:
            logger.info("adding dependency to dependency graph")
            self.dependency_graph_manager.add_dependency(self, self.visibility)
        except ValueError as ex:
            logger.error("problem with adding dependency to dependency graph: {0}".format(ex))
        return decorated_dependency_object

    def locate(self, dependency_lifetime_key, *resolved_dependencies):
        return self.dependency_locator.locate(dependency_lifetime_key, *resolved_dependencies)

    def replace_alt_keys_with_valid_dependency_lifetime_from_instance(self, instance, object_to_wire_up, time_stamp):
        return self.dependency_locator.replace_alt_keys_with_valid_dependency_lifetime_from_instance(instance, object_to_wire_up, time_stamp)

    @property
    def dependency_object(self):
        return self.dependency_locator.dependency_object

    @property
    def services(self):
        return self.dependency_locator.services

    @classmethod
    def get_dependency_without_decoration(cls, dependency_object, visibility, dependency_graph_manager):
        dependency_wrapper = cls(None, None, visibility, dependency_graph_manager)
        dependency_wrapper.dependency_locator = DependencyLocator(cls.GARBAGE_COLLECTION_OBSERVER, DependencyLifetimeEnum.FUNCTION, dependency_object)
        dependency_wrapper.dependencies = DependencyWrapperHelperMethods.get_dependencies_from_callable_object(dependency_object, *BINDINGS)
        dependency_wrapper.dependency_name = dependency_object.__name__
        return dependency_wrapper
