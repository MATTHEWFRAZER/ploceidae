from inspect import getargspec

from dependency_graph.dependency_graph_manager import DependencyGraphManager
from framework_primivites.dependency_validation_methods import DependencyValidationMethods
from framework_primivites.partial_injection import PartialInjection
from framework_primivites.primitive_marker import MarionettePrimitive


class Container(MarionettePrimitive):

    @classmethod
    def wire_dependencies(self, obj_to_wire_up):
        DependencyValidationMethods.input_validation_for_dependency_obj(obj_to_wire_up)
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(obj_to_wire_up)
        return obj_to_wire_up(*resolved_dependencies)

    @classmethod
    def partial_wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore):
        DependencyValidationMethods.input_validation_for_dependency_obj(obj_to_wire_up)
        args_to_apply = [arg for arg in getargspec(obj_to_wire_up)[0] if arg not in dependencies_to_ignore]
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(obj_to_wire_up, *dependencies_to_ignore)
        args_to_apply_as_dict = dict(zip(args_to_apply, resolved_dependencies))
        return PartialInjection(obj_to_wire_up, dependencies_to_ignore,**args_to_apply_as_dict)