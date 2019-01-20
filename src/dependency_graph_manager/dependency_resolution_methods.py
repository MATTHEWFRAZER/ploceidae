from scope_binding.scope_key import ScopeKey
from scope_binding.scope_enum import ScopeEnum
from dependency_graph_manager.cache_item import CacheItem


class DependencyResolutionMethods(object):
    @classmethod
    def resolve_dependencies_by_group(cls, dependency_obj, group, time_stamp):
        dependency_retrieval_method = lambda: [name for name, dependency in cls.DEPENDENCY_GRAPH.items() if dependency.group == group]
        return cls.dependency_resolution_algorithm(dependency_obj, dependency_retrieval_method, time_stamp)

    @classmethod
    def resolve_dependencies_inner(cls, dependency_obj, time_stamp, *dependencies_to_ignore):
        dependency_retrieval_method = lambda: filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
        return cls.dependency_resolution_algorithm(dependency_obj, dependency_retrieval_method, time_stamp)

    @classmethod
    def dependency_resolution_algorithm(cls, dependency_obj, dependency_retrieval_method, time_stamp):
        scope_key = ScopeKey(dependency_obj.dependency_obj)
        scope_key.init_alt_key(time_stamp)
        with cls.LOCK:
            dependencies = dependency_retrieval_method()
            return cls.resolve_dependencies_as_list(list(dependencies), scope_key)#, time_stamp)

    @classmethod
    def replace_alt_keys_with_valid_scope_from_instance(cls, instance, object_to_wire_up, time_stamp):
        with cls.LOCK:
            for dependency in cls.DEPENDENCY_GRAPH.values():
                dependency.replace_alt_keys_with_valid_scope_from_instance(instance, object_to_wire_up, time_stamp)

    @classmethod
    def resolve_dependencies_as_list(cls, dependencies, scope_key):
        resolved_graph = cls.generate_resolved_dependency_graph(dependencies, scope_key)
        return cls.resolve_arguments_to_dependencies(dependencies, resolved_graph)

    @classmethod
    def generate_resolved_dependency_graph(cls, dependencies, scope_key):
        dependency_stack = [dependencies]
        resolved_graph = {}
        while dependency_stack:
            dependencies = dependency_stack.pop()
            for dependency in dependencies:
                dep_obj = cls.find_dependency_obj(dependency)
                if dep_obj is None:
                    raise BaseException("{0} doesn't exist".format(dependency))
                cache_item = CacheItem(dep_obj.dependency_obj, dep_obj.dependency_name)
                # if there is no need to resolve arguments
                if not cls.DEPENDENCY_GRAPH[cache_item].dependencies:
                    resolved_graph[cache_item.dependency_name] = cls.DEPENDENCY_GRAPH[cache_item].locate(scope_key)
                else:
                    dependency_obj_inner = cls.DEPENDENCY_GRAPH[cache_item]
                    resolved_args = cls.resolve_arguments_to_dependencies(dependency_obj_inner.dependencies,
                                                                          resolved_graph)
                    if resolved_args:
                        resolved_graph[cache_item.dependency_name] = dependency_obj_inner.locate(scope_key,
                                                                                                 *resolved_args)  # .all_resolved_dependencies)
                    else:
                        # do not change the order of these appends, or else endless loop
                        dependency_stack.append([dependency_obj_inner.dependency_name])
                        dependency_stack.append(dependency_obj_inner.dependencies)

        return resolved_graph

    @classmethod
    def find_dependency_obj(cls, dependency):
        for dependency_obj in cls.DEPENDENCY_GRAPH.values():
            if dependency_obj.dependency_name == dependency:
                return dependency_obj


    @classmethod
    def resolve_arguments_to_dependencies(cls, dependencies, resolved_graph):
        resolved_arguments = []
        for dependency in dependencies:
            try:
                resolved_arguments.append(resolved_graph[dependency])
            except:
                return []
        return resolved_arguments


    @classmethod
    def get_cache_item(cls, dependent, dependency_name):
        return CacheItem(dependent, dependency_name)