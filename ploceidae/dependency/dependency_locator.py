import logging

from ploceidae.scope_binding.scope_enum import ScopeEnum
from ploceidae.scope_binding.scope_key import ScopeKey

logger = logging.getLogger(__name__)

class DependencyLocator(object):
    def __init__(self, scope, dependency_obj):
        self.scope = scope
        self.services = {}
        self.dependency_obj = dependency_obj

    def locate(self, scope_key, *resolved_dependencies):
        scope_key.init_scope(self.scope)
        scope_key_string = str(scope_key)
        logger.debug("locating service {0} on dependency {1}".format(str(scope_key), self.dependency_obj))
        # need to check alt_key because __init__ and possibly other methods won't get instance until wired but
        # are still valid
        try:
            value = self.services[scope_key_string]
            if value is not None:
                return value
            else:
                raise KeyError
        except KeyError:
            resolved_dependencies = self.dependency_obj(*resolved_dependencies)
            if self.scope != ScopeEnum.FUNCTION:
                self.services[scope_key_string] = resolved_dependencies
            return resolved_dependencies

    def replace_alt_keys_with_valid_scope_from_instance(self, obj, obj_to_wire_up, time_stamp):
        # all this "instance issue stuff" has to do with delivering to an __init__; with an instance scope with an __init__,
        # the issue is that the instance doesn't exist until __init__ is called, thus the scope key must be replaced at a latter time
        scope_key_string = ScopeKey.generate_alt_scope_key(obj_to_wire_up, ScopeEnum.INSTANCE, time_stamp)
        new_scope_key = ScopeKey(obj)
        new_scope_key.init_scope(ScopeEnum.INSTANCE)
        for key, obj in self.services.items():
            logger.info("key {0} ==== key string {1}".format(key, scope_key_string))
            if key == scope_key_string:
                logger.debug("replacing alt key {0} with new key {1}".format(scope_key_string, str(new_scope_key)))
                self.services[str(new_scope_key)] = self.services[scope_key_string]
                del self.services[scope_key_string]
