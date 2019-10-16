import logging
import weakref

from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum
from ploceidae.dependency_lifetime.dependency_lifetime_key import DependencyLifetimeKey

logger = logging.getLogger(__name__)

class DependencyLocator(object):

    def __init__(self, garbage_collection_observer, dependency_lifetime, dependency_object):
        self.garbage_collection_observer = garbage_collection_observer
        self.dependency_lifetime = dependency_lifetime
        self.services = {}
        self.dependency_object = dependency_object

    def locate(self, dependency_lifetime_key, *resolved_dependencies):
        dependency_lifetime_key.init_dependency_lifetime(self.dependency_lifetime)
        dependency_lifetime_key_string = str(dependency_lifetime_key)
        logger.debug("locating service {0} on dependency {1}".format(str(dependency_lifetime_key), self.dependency_object))
        # need to check alt_key because __init__ and possibly other methods won't get instance until wired but
        # are still valid
        try:
            value = self.services[dependency_lifetime_key_string]
            if value is not None:
                return value
            else:
                raise KeyError
        except KeyError:
            resolved_dependencies = self.dependency_object(*resolved_dependencies)
            if self.dependency_lifetime != DependencyLifetimeEnum.FUNCTION:
                self.services[dependency_lifetime_key_string] = resolved_dependencies
            return resolved_dependencies

    def replace_alt_keys_with_valid_dependency_lifetime_from_instance(self, instance, object_to_wire_up, time_stamp):
        # all this "instance issue stuff" has to do with delivering to an __init__; with an instance dependency_lifetime with an __init__,
        # the issue is that the instance doesn't exist until __init__ is called, thus the dependency_lifetime key must be replaced at a latter time
        dependency_lifetime_key_string = DependencyLifetimeKey.generate_alt_dependency_lifetime_key(object_to_wire_up, DependencyLifetimeEnum.INSTANCE, time_stamp)
        new_dependency_lifetime_key = DependencyLifetimeKey(instance)
        new_dependency_lifetime_key.init_dependency_lifetime(DependencyLifetimeEnum.INSTANCE)
        for key, _ in self.services.items():
            logger.info("key {0} ==== key string {1}".format(key, dependency_lifetime_key_string))
            if key == dependency_lifetime_key_string:
                logger.debug("replacing alt key {0} with new key {1}".format(dependency_lifetime_key_string, str(new_dependency_lifetime_key)))
                service = self.services[dependency_lifetime_key_string]
                new_dependency_lifetime_key_string = str(new_dependency_lifetime_key)
                self.services[new_dependency_lifetime_key_string] = service
                del self.services[dependency_lifetime_key_string]
                del new_dependency_lifetime_key
                # only for instance dependency_lifetime do we care about how long lived the objects are so we set a callback in the gc module
                self.garbage_collection_observer.register(self.generate_callback_from_instance(instance, service, new_dependency_lifetime_key_string))

    def generate_callback_from_instance(self, instance, service, dependency_lifetime_key_string):
        weak = weakref.ref(instance)
        # we only need to know about the "phase". if it is stop we want to run this bad boy, we don't care about info
        def nested(phase, info):
            reference = weak()
            if reference is None:
                try:
                    if dependency_lifetime_key_string in self.services:
                        del self.services[dependency_lifetime_key_string]
                    del service
                finally:
                    # if we fail here, means service was unbound and has already been collected
                    return True
            return False
        return nested
