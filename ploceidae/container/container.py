from datetime import datetime
import logging
from pprint import pformat

from ploceidae.dependency_graph_manager import DependencyGraphManager
from ploceidae.dependency import Dependency
from ploceidae.dependency.dependency_helper_methods import DependencyHelperMethods
from ploceidae.container.partial_injection import PartialInjection

logger = logging.getLogger(__name__)

__all__ = ["Container"]


class Container(object):

    @classmethod
    def wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        return cls.partial_wire_dependencies(obj_to_wire_up, *dependencies_to_ignore)()

    @classmethod
    def partial_wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        DependencyHelperMethods.input_validation_for_dependency_obj(obj_to_wire_up)

        dependency_obj = Dependency.get_dependency_without_decoration(obj_to_wire_up)

        return cls.partial_wire_dependencies_inner(dependency_obj, dependencies_to_ignore, obj_to_wire_up)

    @classmethod
    def partial_wire_dependencies_inner(cls, dependency_obj, dependencies_to_ignore, obj_to_wire_up):
        time_stamp = datetime.now()
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(dependency_obj, time_stamp,
                                                                            *dependencies_to_ignore)
        args_to_apply_as_dict = cls.get_args_to_apply_as_dict(dependency_obj.dependencies, dependencies_to_ignore,
                                                              resolved_dependencies)
        args_to_apply_as_group = resolved_dependencies.resolved_dependencies_by_group

        cls.log_partial_injection_data(dependency_obj.dependency_name, dependencies_to_ignore, args_to_apply_as_dict, args_to_apply_as_group)
        partial_injection = PartialInjection(obj_to_wire_up, dependencies_to_ignore, *args_to_apply_as_group,
                                             **args_to_apply_as_dict)
        return cls.decorate_partial_injection(partial_injection, obj_to_wire_up, time_stamp)

    @classmethod
    def log_partial_injection_data(cls, dependency_name, dependencies_to_ignore, args_to_apply_as_dict, args_to_apply_as_group):
        message = "\n\nfor {0} ignoring: \n{1}\napplying as dict: \n{2}\napplying as group: \n{3}\n"
        data = map(pformat, (dependencies_to_ignore, args_to_apply_as_dict, args_to_apply_as_group))
        logger.info(message.format(dependency_name, *data))

    @classmethod
    def get_args_to_apply_as_dict(cls, dependencies, dependencies_to_ignore, resolved_dependencies):
        enumerator_on_dependencies = enumerate(filter(lambda dependency: dependency not in dependencies_to_ignore, dependencies))
        return {dependency: resolved_dependencies.resolved_dependencies[index] for index, dependency in enumerator_on_dependencies}

    @staticmethod
    def decorate_partial_injection(partial_injection, object_to_wire_up, time_stamp):
        def when_called(*args, **kwargs):
            logger.debug("calling replacing alt keys callback")
            ret = partial_injection(*args, **kwargs)
            DependencyGraphManager.replace_alt_keys_with_valid_scope_from_instance(ret, object_to_wire_up, time_stamp)
            return ret
        return when_called
