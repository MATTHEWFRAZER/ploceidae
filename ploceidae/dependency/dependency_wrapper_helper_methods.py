from functools import wraps

from ploceidae.constants import BINDINGS
from ploceidae.dependency_management.dependency_resolution_methods import DependencyResolutionMethods

class DependencyWrapperHelperMethods(object):

    @classmethod
    def input_validation_for_dependency_object(cls, decorated_object):
        cls.decorated_object_is_callable(decorated_object)
        cls.decorated_object_has_name_attribute(decorated_object)
        cls.decorated_object_does_not_depend_on_itself(decorated_object)

    @classmethod
    def decorated_object_is_callable(cls, decorated_object):
        if not callable(decorated_object):
            raise ValueError("Can not decorate non callables")

    @classmethod
    def decorated_object_has_name_attribute(cls, decorated_object):
        try:
            decorated_object.__name__
        except AttributeError:
            raise ValueError("dependency must have __name__ attribute")

    @classmethod
    def decorated_object_does_not_depend_on_itself(cls, decorated_object):
        if decorated_object.__name__ in DependencyResolutionMethods.get_dependencies(decorated_object):
            raise ValueError("{0} is a dependency on itself".format(decorated_object.__name__))

    @classmethod
    def is_valid_keyword(cls, keyword):
        return keyword in cls.VALID_KWARGS

    @staticmethod
    def get_dependencies_from_callable_object(dependency_objects, *dependencies_to_ignore):
        return [dependency_name for dependency_name in DependencyResolutionMethods.get_dependencies(dependency_objects) if dependency_name not in dependencies_to_ignore + BINDINGS]

    @staticmethod
    def register_callbacks_with_dependency_object(callbacks, func):
        @wraps(func)
        def nested(*unresolved_dependencies, **kwargs):
            cached = func(*unresolved_dependencies, **kwargs)
            for callback in callbacks: callback()
            return cached

        return nested