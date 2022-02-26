import logging
import weakref

from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum
from ploceidae.dependency_lifetime.dependency_lifetime_key import DependencyLifetimeKey

logger = logging.getLogger(__name__)

class DependencyLocator(object):

    def __init__(self, garbage_collection_observer, lifetime, dependency_object, transformation):
        self.garbage_collection_observer = garbage_collection_observer
        self.lifetime = lifetime
        self.services = {}
        self.dependency_object = dependency_object
        self.transformation = transformation

    def locate(self, dependency_lifetime_key, *resolved_dependencies):
        dependency_lifetime_key.init_dependency_lifetime(self.lifetime)
        dependency_lifetime_key_string = str(dependency_lifetime_key)
        #logger.debug("locating service {0} on dependency {1}".format(str(dependency_lifetime_key), self.dependency_object))
        # need to check alt_key because __init__ and possibly other methods won't get instance until wired but
        # are still valid
        try:
            value = self.services[dependency_lifetime_key_string]
            if value is not None:
                return value
            else:
                raise KeyError
        except KeyError:
            resolved_object = self.dependency_object(*resolved_dependencies)
            if self.transformation is not None:
                resolved_object = self.transformation(resolved_object)
            if self.lifetime != DependencyLifetimeEnum.FUNCTION:
                self.services[dependency_lifetime_key_string] = resolved_object
            return resolved_object

    def replace_alt_keys_with_valid_dependency_lifetime_from_instance(self, instance, object_to_wire_up, time_stamp):
        # all this "instance issue stuff" has to do with delivering to an __init__; with an instance lifetime with an __init__,
        # the issue is that the instance doesn't exist until __init__ is called, thus the lifetime key must be replaced at a latter time
        dependency_lifetime_key_string = DependencyLifetimeKey.generate_alt_dependency_lifetime_key(object_to_wire_up, DependencyLifetimeEnum.INSTANCE, time_stamp)
        new_dependency_lifetime_key = DependencyLifetimeKey(instance)
        new_dependency_lifetime_key.init_dependency_lifetime(DependencyLifetimeEnum.INSTANCE)
        for key, _ in self.services.copy().items():
            #logger.info("key {0} ==== key string {1}".format(key, dependency_lifetime_key_string))
            if key == dependency_lifetime_key_string:
                #logger.debug("replacing alt key {0} with new key {1}".format(dependency_lifetime_key_string, str(new_dependency_lifetime_key)))
                new_dependency_lifetime_key_string = str(new_dependency_lifetime_key)
                self.services[new_dependency_lifetime_key_string] = self.services[dependency_lifetime_key_string]
                del self.services[dependency_lifetime_key_string]
                # only for instance lifetime do we care about how long lived the objects are so we set a callback in the gc module
                self.garbage_collection_observer.register(self.generate_callback_from_instance(instance, new_dependency_lifetime_key_string))

    def generate_callback_from_instance(self, instance, dependency_lifetime_key_string):
        weak_reference = weakref.ref(instance)
        def nested():
            return self.remove_stale_references_in_services(weak_reference, dependency_lifetime_key_string)
        return nested

    def remove_stale_references_in_services(self, weak_reference, dependency_lifetime_key_string):
        reference = weak_reference()
        if reference is None:
            try:
                if dependency_lifetime_key_string in self.services:
                    del self.services[dependency_lifetime_key_string]
            finally:
                # if we fail here, means service was unbound and has already been collected
                return True
        return False
