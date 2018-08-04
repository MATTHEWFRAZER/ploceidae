class DependencyServiceLocator(object):
    def __init__(self, dependency_obj):
        self.services = {}
        self.dependency_obj = dependency_obj

    def delete_entry_from_service_locator(self, scope_key):
        del self.services[scope_key]

    def locate(self, scope_key_string, *resolved_dependencies):
        if scope_key_string not in self.services:
            self.services[scope_key_string] = self.dependency_obj(*resolved_dependencies)
        return self.services[scope_key_string]


    def add_dependency_to_services(self, scope_key):
        if scope_key in self.services:
            raise ValueError("dependency with scope key {0} already exists".format(str(scope_key)))
        self.services[str(scope_key)] = self