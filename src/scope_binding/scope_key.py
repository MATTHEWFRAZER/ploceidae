from inspect import getmodulename

from scope_binding.scope_enum import ScopeEnum


class ScopeKey(object):
    def __init__(self, obj, scope):
        self.obj = obj
        self.scope = scope

    def __str__(self):
        if self.scope == ScopeEnum.SESSION:
            return "null"
        elif self.scope == ScopeEnum.MODULE:
            return "{0}".format(getmodulename(self.obj))
        elif self.scope == ScopeEnum.CLASS:
            return "{0}".format(self.obj.__self__.__class__)
        elif self.scope == ScopeEnum.INSTANCE:
            return "{0}".format(self.obj.__self__)
        elif self.scope == ScopeEnum.FUNCTION:
            try:
                instance_binding = self.obj.__self__
            except AttributeError:
                instance_binding = "null"
            return "{0}::{1}".format(instance_binding, self.obj.__qualname__)
        else:
            raise NotImplementedError("{0} not a valid scope".format(self.scope))

    @staticmethod
    def is_function_scope(scope_key):
        return "::" in scope_key.scope