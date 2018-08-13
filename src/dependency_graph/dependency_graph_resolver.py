from framework_primivites.dependency_primitives.dependency_with_mutable_dependencies import DependencyWithMutableDependencies


class DependencyGraphResolver(object):

    @classmethod
    def resolve_dependency_graph(cls, dependency_graph, scope_key_string):
        dependency_graph_copy = {key : DependencyWithMutableDependencies(value) for key, value in dependency_graph.items()}
        resolved_dependencies = {}
        while dependency_graph_copy:
            dependency_obj = cls.get_node_with_no_out_edges(dependency_graph_copy)
            dependency_obj_name = dependency_obj.dependency_name
            if cls.is_resolvable_dependency(dependency_graph, dependency_obj, scope_key_string):
                cls.apply_dependencies(dependency_graph, dependency_obj, scope_key_string, resolved_dependencies)
                cls.pop_all_references_to_dependency(dependency_graph_copy, dependency_obj_name)

    @classmethod
    def is_resolvable_dependency(cls, dependency_graph, dependency_obj, scope_key_string):
        return all(not cls.is_resolved(dependency_graph[dependency_name], scope_key_string) for dependency_name in dependency_obj.dependencies) and not dependency_obj.mutable_dependencies

    @classmethod
    def is_resolved(cls, dependency_obj, scope_key_string):
        return scope_key_string in dependency_obj.services

    @classmethod
    def apply_dependencies(cls, dependency_graph, dependency_obj, scope_key_string, resolved_dependencies):
            resolved_dependency_list = [resolved_dependencies[dependency_inner] for dependency_inner in
                                        dependency_obj.dependencies]
            resolved_dependencies[dependency_obj.dependency_name] = dependency_obj.locate(str(scope_key_string),
                                                                             *resolved_dependency_list)
            dependency_obj.mutable_dependencies.remove(dependency_obj.dependency_name)

        # temp_dependencies = dependency_obj.dependencies.copy()
        # for dependency in temp_dependencies.copy():
        #     dependency_graph_node = dependency_graph[dependency]
        #     try:
        #         resolved = dependency_graph_node.locate_with_no_resolved_dependencies(str(scope_key_string))
        #     except KeyError:
        #         pass
        #     else:
        #         resolved_dependencies[dependency] = resolved
        #         temp_dependencies.remove(dependency)
        #         continue
        #
        #     try:
        #         resolved_dependency_list = [resolved_dependencies[dependency_inner] for dependency_inner in
        #                                     dependency_graph_node.dependencies]
        #         resolved = dependency_graph_node.locate(str(scope_key_string), *resolved_dependency_list)
        #     except:
        #         resolved_dependencies[dependency] = cls.apply_dependencies(dependency_graph,
        #                                                                    dependency_graph[dependency],
        #                                                                    scope_key_string, resolved_dependencies)
        #         temp_dependencies.remove(dependency)
        #     else:
        #         resolved_dependencies[dependency] = resolved
        #         temp_dependencies.remove(dependency)
        #         continue
        # dependencies_resolved_to_obj = []
        # for dependency_inner in dependency_obj.dependencies: dependencies_resolved_to_obj.append(resolved_dependencies[dependency_inner])
        # try:
        #     return dependency_obj.locate_with_no_resolved_dependencies(str(scope_key_string))
        # except KeyError:
        #     return dependency_obj.locate(scope_key_string, *dependencies_resolved_to_obj)
        ##########################################
        #resolved_dependencies = [dependency_graph[dependency].locate_with_no_resolved_dependencies(scope_key_string) for dependency in dependency_obj.dependencies]
        #return dependency_obj.locate(scope_key_string, *resolved_dependencies)

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