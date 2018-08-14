from scope_binding.scope_key import ScopeKey
from scope_binding.scope_enum import ScopeEnum

class DependencyServiceLocator(object):
    def __init__(self, scope, dependency_obj):
        self.scope = scope
        self.services = {}
        self.dependency_obj = dependency_obj

    def delete_entry_from_service_locator(self, scope_key):
        del self.services[scope_key]

    def purge_service_locator_of_function_scope_keys(self):
        for key in self.services.keys():
            if ScopeKey.is_function_scope(key):
                self.delete_entry_from_service_locator(key)

    def locate(self, scope_key_string, *resolved_dependencies):
        try:
            return self.services[scope_key_string]
        except KeyError:
            if "x" == self.dependency_name:
                import pdb; pdb.set_trace()
            cached = self.dependency_obj(*resolved_dependencies)
            if self.scope != ScopeEnum.FUNCTION:
                self.services[scope_key_string] = cached
            return cached