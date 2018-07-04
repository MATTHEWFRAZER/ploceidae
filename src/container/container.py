from dependency_graph_manager import DependencyGraphManager
from dependency import Dependency
from dependency.dependency_helper_methods import DependencyHelperMethods
from container.partial_injection import PartialInjection


class Container(object):

    @classmethod
    def wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        return cls.partial_wire_dependencies(obj_to_wire_up, *dependencies_to_ignore)()

    @classmethod
    def partial_wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        # need to be able to use the other default scopes
        DependencyHelperMethods.input_validation_for_dependency_obj(obj_to_wire_up)
        dependency_obj = Dependency.get_dependency_without_decoration(obj_to_wire_up)
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(dependency_obj, *dependencies_to_ignore)
        args_to_apply_as_dict = cls.get_args_to_apply_as_dict(dependency_obj.dependencies, dependencies_to_ignore, resolved_dependencies)
        args_to_apply_as_group = resolved_dependencies.resolved_dependencies_by_group
        return PartialInjection(obj_to_wire_up, dependencies_to_ignore, *args_to_apply_as_group, **args_to_apply_as_dict)

    @classmethod
    def get_args_to_apply_as_dict(cls, dependencies, dependencies_to_ignore, resolved_dependencies):
        enumerator_on_dependencies = enumerate(filter(lambda dependency: dependency not in dependencies_to_ignore, dependencies))
        return {dependency: resolved_dependencies.resolved_dependencies[index] for index, dependency in enumerator_on_dependencies}
