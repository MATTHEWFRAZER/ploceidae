from inspect import getsourcefile

import six

from pygmy.scope_binding.scope_enum import ScopeEnum

class ScopeKey(object):
    def __init__(self, obj):
        self.obj = obj
        self.alt_key = None

    def init_scope(self, scope):
        """resolves scope here because we don't get scope until wiring up dependencies"""
        self.scope = scope

    def init_alt_key(self, time_stamp):
        self.alt_key_format = "alt::" + "{}::" + str(self.obj) + "::" + str(time_stamp)

    def __repr__(self):
        if self.scope == ScopeEnum.SESSION:
            return "session"
        elif self.scope == ScopeEnum.MODULE:
            return "{0}".format(getsourcefile(self.obj))
        elif self.scope == ScopeEnum.CLASS:
            return self.handle_class_scope()
        elif self.scope == ScopeEnum.INSTANCE:
            return self.handle_instance_scope()
        elif self.scope == ScopeEnum.FUNCTION:
            return self.handle_function_scope()
        else:
            raise NotImplementedError("{0} not a valid scope".format(self.scope))

    def handle_class_scope(self):
        try:
            return "{0}".format(self.obj.__self__.__class__)
        except AttributeError: # TODO PYGMY 11: if obj is for some reason not bound correctly (i.e. dynamically set method like a lambda)
            raise ValueError("{0} does not have a __self__.__class__ reference to resolve class scope for".format(self.obj))

    def handle_instance_scope(self):
        if isinstance(self.obj, six.class_types):
            return self.alt_key_format.format(self.scope)
        if hasattr(self.obj, "__name__") and self.obj.__name__ == "__init__":
            return self.alt_key_format.format(self.scope)
        if hasattr(self.obj, "__self__"):
            return "{0}".format(self.obj.__self__)
        return "{0}".format(self.obj)

    def handle_function_scope(self):
        try:
            instance_binding = self.obj.__self__
        except AttributeError:
            instance_binding = "null"
        try:
            used_name = self.obj.__qualname__
        except:
            used_name = str(self.obj)
        return "{0}::{1}".format(instance_binding, used_name)

    @staticmethod
    def generate_alt_scope_key(obj, scope, time_stamp):
        return "alt::{}::{}::{}".format(scope, obj, time_stamp)

    @staticmethod
    def is_function_scope(scope_key):
        return "::" in scope_key.scope