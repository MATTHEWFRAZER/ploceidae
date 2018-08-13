from framework_primivites.dependency_primitives.dependency_with_mutable_dependencies import DependencyWithMutableDependencies


class DependencyGraphResolver(object):

    @classmethod
    def resolve_dependency_graph(cls, dependency_graph, scope_key_string):
        pass

    @classmethod
    def is_resolvable_dependency(cls, dependency_graph, dependency_obj, scope_key_string):
        return all(not cls.is_resolved(dependency_graph[dependency_name], scope_key_string) for dependency_name in dependency_obj.dependencies) and not dependency_obj.mutable_dependencies

    @classmethod
    def is_resolved(cls, dependency_obj, scope_key_string):
        return scope_key_string in dependency_obj.services

    #@classmethod
    #def apply_dependencies(cls, dependency_graph, dependency_obj, scope_key_string, resolved_dependencies):
    #    resolved_dependencies[dependency_graph]

    @staticmethod
    def pop_all_references_to_dependency(dependency_graph, dependency_name):
        dependency_graph.pop(dependency_name)
        for dependency_obj in dependency_graph.values():
            dependency_obj.mutable_dependencies = [dependency for dependency in dependency_obj.mutable_dependencies if
                                                   dependency != dependency_name]

    @staticmethod
    def get_node_with_no_out_edges(dependency_graph):
        for dependency in dependency_graph.values():
            if not dependency.mutable_dependencies:
                return dependency
        else:
            raise BaseException("dependency_primitives graph has some unresolvable dependencies")