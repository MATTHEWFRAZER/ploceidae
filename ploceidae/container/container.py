from datetime import datetime
import logging
from pprint import pformat

from ploceidae.dependency.dependency_wrapper import DependencyWrapper
from ploceidae.dependency.dependency_wrapper_helper_methods import DependencyWrapperHelperMethods
from ploceidae.container.partial_injection import PartialInjection

logger = logging.getLogger(__name__)

__all__ = ["Container"]


class Container(object):

    def __init__(self, dependency_graph_manager):
        self.dependency_graph_manager = dependency_graph_manager

    def wire_dependencies(self, object_to_wire_up, *dependencies_to_ignore):
        return self.partially_wire_dependencies(object_to_wire_up, *dependencies_to_ignore)()

    def partially_wire_dependencies(self, object_to_wire_up, *dependencies_to_ignore):
        DependencyWrapperHelperMethods.input_validation_for_dependency_object(object_to_wire_up)

        dependency_wrapper = DependencyWrapper.get_dependency_without_decoration(object_to_wire_up, None, self.dependency_graph_manager)

        return self.partially_wire_dependencies_inner(dependency_wrapper, dependencies_to_ignore, object_to_wire_up)

    def partially_wire_dependencies_inner(self, dependency_wrapper, dependencies_to_ignore, object_to_wire_up):
        time_stamp = datetime.now()
        resolved_dependencies = self.dependency_graph_manager.resolve_dependencies(dependency_wrapper, time_stamp,
                                                                                   *dependencies_to_ignore)
        args_to_apply_as_dict = self.get_args_to_apply_as_dict(dependency_wrapper, dependencies_to_ignore,
                                                               resolved_dependencies)
        args_to_apply_as_group = resolved_dependencies.resolved_dependencies_by_group

        self.log_partial_injection_data(dependency_wrapper, dependencies_to_ignore, args_to_apply_as_dict, args_to_apply_as_group)
        partial_injection = PartialInjection(object_to_wire_up, dependencies_to_ignore, *args_to_apply_as_group,
                                             **args_to_apply_as_dict)
        return self.generate_partial_injection(partial_injection, object_to_wire_up, time_stamp)

    def generate_partial_injection(self, partial_injection, object_to_wire_up, time_stamp):
        def nested(*args, **kwargs):
            #logger.debug("calling replacing alt keys callback")
            ret = partial_injection(*args, **kwargs)
            self.dependency_graph_manager.replace_alt_keys_with_valid_dependency_lifetime_from_instance(ret, object_to_wire_up, time_stamp)
            return ret
        return nested

    @staticmethod
    def log_partial_injection_data(wrapped_dependency_object, dependencies_to_ignore, args_to_apply_as_dict, args_to_apply_as_group):
        message = "\n\nfor {0} ignoring: \n{1}\napplying as dict: \n{2}\napplying as group: \n{3}\n"
        data = map(pformat, (dependencies_to_ignore, args_to_apply_as_dict, args_to_apply_as_group))
        #logger.info(message.format(wrapped_dependency_object.dependency_name, *data))

    @staticmethod
    def get_args_to_apply_as_dict(wrapped_dependency_object, dependencies_to_ignore, resolved_dependencies):
        enumerator_on_dependencies = enumerate(filter(lambda dependency: dependency not in dependencies_to_ignore, wrapped_dependency_object.dependencies))
        return {dependency: resolved_dependencies.resolved_dependencies[index] for index, dependency in enumerator_on_dependencies}
