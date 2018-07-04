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
            return cls.resolve_dependencies_as_list(dependencies, scope_key, time_stamp)

    @classmethod
    def replace_alt_keys_with_valid_scope_from_instance(cls, instance, object_to_wire_up, time_stamp):
        with cls.LOCK:
            for dependency in cls.DEPENDENCY_GRAPH.values():
                dependency.replace_alt_keys_with_valid_scope_from_instance(instance, object_to_wire_up, time_stamp)


    @classmethod
    def resolve_dependencies_as_list(cls, dependencies, scope_key, time_stamp):
        resolved_dependencies = []
        for dependency in dependencies:
            cache_item = cls.get_cache_item(scope_key.obj, dependency)
            # if there is no need to resolve arguments
            if not cls.DEPENDENCY_GRAPH[cache_item].dependencies:
                resolved_dependencies.append(cls.DEPENDENCY_GRAPH[cache_item].locate(scope_key))
            else:
                dependency_obj_inner = cls.DEPENDENCY_GRAPH[cache_item]
                resolved_args = cls.resolve_dependencies(cls.DEPENDENCY_GRAPH[cache_item], time_stamp)
                resolved_dependencies.append(dependency_obj_inner.locate(scope_key, *resolved_args.all_resolved_dependencies))
        return resolved_dependencies

    @classmethod
    def get_cache_item(cls, dependent, dependency_name):
        return CacheItem(dependent, dependency_name)
