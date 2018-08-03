from dependency_graph.dependency_graph_manager import DependencyGraphManager
from framework_primivites.dependency_primitives.dependency import Dependency
from framework_primivites.dependency_primitives.dependency_initialization_methods import DependencyInitializationMethods
from framework_primivites.partial_injection import PartialInjection
from framework_primivites.primitive_marker import MarionettePrimitive
from scope_binding.scope_key import ScopeKey


class Container(MarionettePrimitive):

    @classmethod
    def wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore, scope="function"):
        return cls.partial_wire_dependencies(obj_to_wire_up, *dependencies_to_ignore, scope=scope)()

    @classmethod
    def partial_wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore, scope="function"):
        # need to be able to use the other default scopes
        DependencyInitializationMethods.input_validation_for_dependency_obj(obj_to_wire_up)
        dependency_obj = Dependency.get_dependency_without_decoration(obj_to_wire_up, scope)
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(dependency_obj, ScopeKey(dependency_obj.dependency_obj, scope), *dependencies_to_ignore)
        resolved_dependency_names = [dependency for dependency in dependency_obj.dependencies if dependency not in dependencies_to_ignore]
        args_to_apply_as_dict = dict(zip(resolved_dependency_names, resolved_dependencies))
        return PartialInjection(obj_to_wire_up, dependencies_to_ignore,**args_to_apply_as_dict)