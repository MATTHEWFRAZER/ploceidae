from scope_binding.scope_enum import ScopeEnum


class DependencyLocator(object):
    def __init__(self, scope, dependency_obj):
        self.scope = scope
        self.services = {}
        self.dependency_obj = dependency_obj

    def delete_entry_from_service_locator(self, scope_key):
        del self.services[scope_key]

    def locate(self, scope_key, *resolved_dependencies):
        scope_key.init_scope(self.scope)
        scope_key_string = str(scope_key)
        try:
            import pdb; pdb.set_trace()
            return self.services[scope_key_string]
        except KeyError:
            cached = self.dependency_obj(*resolved_dependencies)
            if self.scope != ScopeEnum.FUNCTION:
                self.services[scope_key_string] = cached
            return cached