from contextlib import contextmanager
from datetime import datetime

from dependency_graph_manager import DependencyGraphManager
from dependency import Dependency
from dependency.dependency_helper_methods import DependencyHelperMethods
from container.partial_injection import PartialInjection


__all__ = ["Container"]

class Container(object):

    @classmethod
    def wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        return cls.partial_wire_dependencies(obj_to_wire_up, *dependencies_to_ignore)()

    @classmethod
    def partial_wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        # need to be able to use the other default scopes
        #with object_init_cache(obj_to_wire_up):
        time_stamp = datetime.now()
        DependencyHelperMethods.input_validation_for_dependency_obj(obj_to_wire_up)
        dependency_obj = Dependency.get_dependency_without_decoration(obj_to_wire_up)
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(dependency_obj, time_stamp, *dependencies_to_ignore)
        args_to_apply_as_dict = cls.get_args_to_apply_as_dict(dependency_obj.dependencies, dependencies_to_ignore, resolved_dependencies)
        args_to_apply_as_group = resolved_dependencies.resolved_dependencies_by_group
        partial_injection = PartialInjection(obj_to_wire_up, dependencies_to_ignore, *args_to_apply_as_group, **args_to_apply_as_dict)
        ret = cls.decorate_partial_injection(partial_injection, obj_to_wire_up, time_stamp)
        return ret

    @classmethod
    def get_args_to_apply_as_dict(cls, dependencies, dependencies_to_ignore, resolved_dependencies):
        enumerator_on_dependencies = enumerate(filter(lambda dependency: dependency not in dependencies_to_ignore, dependencies))
        return {dependency: resolved_dependencies.resolved_dependencies[index] for index, dependency in enumerator_on_dependencies}

    @staticmethod
    def decorate_partial_injection(partial_injection, object_to_wire_up, time_stamp):
        def when_called(*args, **kwargs):
            ret = partial_injection(*args, **kwargs)
            DependencyGraphManager.replace_alt_keys_with_valid_scope_from_instance(ret, object_to_wire_up, time_stamp)
            return ret
        return when_called

@contextmanager
def object_init_cache(obj_to_wire_up):
    if hasattr(obj_to_wire_up, "__init__"):
        cached_init = getattr(obj_to_wire_up, "__init__")
        yield
        setattr(obj_to_wire_up, "__init__", cached_init)
    else:
        yield



