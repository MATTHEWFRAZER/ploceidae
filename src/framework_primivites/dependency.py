import pprint

from framework_primivites.primitive_marker import MarionettePrimitive
from dependency_graph.dependency_graph_manager import DependencyGraphManager

__all__ = ["dependency"]


class Dependency(MarionettePrimitive):
    """decorator is a class object because that will make it easier to hook into later"""

    def __init__(self, **kwargs):
        DependencyKeyWordValidationMethods.input_validation_to_init(kwargs)
        self.scope = kwargs.get("scope", "function")

    def __call__(self, func):
        # we need to take this algorithm into somne place else, question do we want the end caller to be in the dependency graph
        # do I need to do classmethod check here? Maybe because the class method itself (unbounded will not be callable). If a user does class
        # introspection and decides to decorate a classmethod accessed via __dict__ yeah
        if not callable(func):
            raise ValueError("Can not decorate non callables")

        DependencyGraphManager.add_dependency(func)
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(func)

        def inner(*unresolved_dependencies):
            dependencies = unresolved_dependencies + resolved_dependencies
            return func(*dependencies)

        return inner


class DependencyKeyWordValidationMethods(object):
    VALID_KWARGS = ("scope",)

    @classmethod
    def input_validation_to_init(cls, kwargs):
        if not cls.kwargs_are_valid(kwargs):
            invalid_keys = pprint.pformat([key not in cls.is_valid_key(key) for key in kwargs.keys()])
            raise ValueError("the following key word arguments are invalid: \n{0}".format(invalid_keys))

    @classmethod
    def kwargs_are_valid(cls, kwargs):
        return all(cls.is_valid_key(key) for key in kwargs.keys())

    @classmethod
    def is_valid_key(cls, key):
        return key in cls.VALID_KWARGS


dependency = Dependency
