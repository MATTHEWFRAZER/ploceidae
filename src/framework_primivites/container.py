from framework_primivites.primitive_marker import MarionettePrimitive

from dependency_graph.dependency_graph_manager import DependencyGraphManager


class Container(MarionettePrimitive):

    def wire_dependencies(self, obj_to_wire_up):
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(obj_to_wire_up)
        return obj_to_wire_up(*resolved_dependencies)