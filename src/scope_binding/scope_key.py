from inspect import getsourcefile

from scope_binding.scope_enum import ScopeEnum


class ScopeKey(object):
    def __init__(self, obj):
        self.obj = obj
        self.alt_key = None

    def init_scope(self, scope):
        """resolves scope here because we don't get scope until wiring up dependencies"""
        self.scope = scope

    def init_alt_key(self, time_stamp):
        self.alt_key_format = "alt::" + "{}::" + self.obj + time_stamp

    def __repr__(self):
        if self.scope == ScopeEnum.SESSION:
            return "null"
        elif self.scope == ScopeEnum.MODULE:
            return "{0}".format(getsourcefile(self.obj))
        elif self.scope == ScopeEnum.CLASS:
            if self.obj.__name__ == "__init__":
                return self.alt_key.format(self.scope)
            return "{0}".format(self.obj.__self__.__class__)
        elif self.scope == ScopeEnum.INSTANCE:
            return "{0}".format(self.obj.__self__)
        elif self.scope == ScopeEnum.FUNCTION:
            try:
                instance_binding = self.obj.__self__
            except AttributeError:
                instance_binding = "null"
            try:
                used_name = self.obj.__qualname__
            except:
                used_name = str(self.obj)
            return "{0}::{1}".format(instance_binding, used_name)
        else:
            raise NotImplementedError("{0} not a valid scope".format(self.scope))

    @staticmethod
    def is_function_scope(scope_key):
        return "::" in scope_key.scope