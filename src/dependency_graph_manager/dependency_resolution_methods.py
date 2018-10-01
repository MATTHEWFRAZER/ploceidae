from scope_binding.scope_key import ScopeKey


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
        scope_key.alt_key_init(time_stamp)
        with cls.LOCK:
            dependencies = dependency_retrieval_method()
            ret = cls.resolve_dependencies_as_list(dependencies, scope_key)

    @classmethod
    def replace_alt_keys_with_valid_scope_from_instance(cls, instance, time_stamp):
        scope_key = ScopeKey(instance)
        scope_key.alt_key_init(time_stamp)
        with cls.LOCK:
            for dependency in cls.DEPENDENCY_GRAPH.values():
                dependency.replace_alt_keys_with_valid_scope_from_instance(scope_key, instance)


    @classmethod
    def resolve_dependencies_as_list(cls, dependencies, scope_key):
        resolved_dependencies = []
        for dependency in dependencies:
            # if there is no need to resolve arguments
            if not cls.DEPENDENCY_GRAPH[dependency].dependencies:
                resolved_dependencies.append(cls.DEPENDENCY_GRAPH[dependency].locate(scope_key))
            else:
                dependency_obj_inner = cls.DEPENDENCY_GRAPH[dependency]
                resolved_args = cls.resolve_dependencies(cls.DEPENDENCY_GRAPH[dependency])
                resolved_dependencies.append(dependency_obj_inner.locate(scope_key, *resolved_args.all_resolved_dependencies))
        return resolved_dependencies
