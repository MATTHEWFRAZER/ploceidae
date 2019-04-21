from pprint import pformat

from pygmy.constants import BINDINGS
from pygmy.utilities.lib import get_dependencies

class DependencyHelperMethods(object):
    VALID_KWARGS = ("scope", "group", "global_dependency")

    @classmethod
    def input_validation_for_dependency_obj(cls, decorated_obj):
        cls.decorated_obj_is_callable(decorated_obj)
        cls.decorated_obj_has_name_attribute(decorated_obj)
        cls.decorated_obj_does_not_depend_on_itself(decorated_obj)

    @classmethod
    def decorated_obj_is_callable(cls, decorated_obj):
        if not callable(decorated_obj):
            raise ValueError("Can not decorate non callables")

    @classmethod
    def decorated_obj_has_name_attribute(cls, decorated_obj):
        try:
            decorated_obj.__name__
        except AttributeError:
            raise ValueError("dependency must have __name__ attribute")

    @classmethod
    def decorated_obj_does_not_depend_on_itself(cls, decorated_obj):
        if decorated_obj.__name__ in get_dependencies(decorated_obj):
            raise ValueError("{0} is a dependency on itself".format(decorated_obj.__name__))

    @classmethod
    def input_validation_to_init(cls, kwargs):
        if not cls.kwargs_are_valid(kwargs):
            invalid_keys = pformat([key for key in kwargs.keys() if not cls.is_valid_key(key)])
            raise ValueError("the following key word arguments are invalid: \n{0}".format(invalid_keys))

    @classmethod
    def kwargs_are_valid(cls, kwargs):
        return all(cls.is_valid_key(key) for key in kwargs.keys())

    @classmethod
    def is_valid_key(cls, key):
        return key in cls.VALID_KWARGS

    @staticmethod
    def get_dependencies_from_callable_obj(callable_obj, *dependencies_to_ignore):
        return [dependency for dependency in get_dependencies(callable_obj) if dependency not in dependencies_to_ignore + BINDINGS]

