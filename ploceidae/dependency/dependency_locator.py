import logging
import weakref

from ploceidae.scope_binding.scope_enum import ScopeEnum
from ploceidae.scope_binding.scope_key import ScopeKey

logger = logging.getLogger(__name__)

class DependencyLocator(object):

    def __init__(self, garbage_collection_observer, scope, dependency_object):
        self.garbage_collection_observer = garbage_collection_observer
        self.scope = scope
        self.services = {}
        self.dependency_object = dependency_object

    def locate(self, scope_key, *resolved_dependencies):
        scope_key.init_scope(self.scope)
        scope_key_string = str(scope_key)
        logger.debug("locating service {0} on dependency {1}".format(str(scope_key), self.dependency_object))
        # need to check alt_key because __init__ and possibly other methods won't get instance until wired but
        # are still valid
        try:
            value = self.services[scope_key_string]
            if value is not None:
                return value
            else:
                raise KeyError
        except KeyError:
            resolved_dependencies = self.dependency_object(*resolved_dependencies)
            if self.scope != ScopeEnum.FUNCTION:
                self.services[scope_key_string] = resolved_dependencies
            return resolved_dependencies

    def replace_alt_keys_with_valid_scope_from_instance(self, instance, object_to_wire_up, time_stamp):
        # all this "instance issue stuff" has to do with delivering to an __init__; with an instance scope with an __init__,
        # the issue is that the instance doesn't exist until __init__ is called, thus the scope key must be replaced at a latter time
        scope_key_string = ScopeKey.generate_alt_scope_key(object_to_wire_up, ScopeEnum.INSTANCE, time_stamp)
        new_scope_key = ScopeKey(instance)
        new_scope_key.init_scope(ScopeEnum.INSTANCE)
        for key, _ in self.services.items():
            logger.info("key {0} ==== key string {1}".format(key, scope_key_string))
            if key == scope_key_string:
                logger.debug("replacing alt key {0} with new key {1}".format(scope_key_string, str(new_scope_key)))
                service = self.services[scope_key_string]
                new_scope_key_string = str(new_scope_key)
                self.services[new_scope_key_string] = service
                del self.services[scope_key_string]
                del new_scope_key
                # only for instance scope do we care about how long lived the objects are so we set a callback in the gc module
                self.garbage_collection_observer.register(self.generate_callback_from_instance(instance, service, new_scope_key_string))

    def generate_callback_from_instance(self, instance, service, scope_key_string):
        weak = weakref.ref(instance)
        # we only need to know about the "phase". if it is stop we want to run this bad boy, we don't care about info
        def nested(phase, info):
            reference = weak()
            if reference is None:
                try:
                    if scope_key_string in self.services:
                        del self.services[scope_key_string]
                    del service
                finally:
                    # if we fail here, means service was unbound and has already been collected
                    return True
            return False
        return nested
