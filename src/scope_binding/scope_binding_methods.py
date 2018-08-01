from inspect import getmodulename

from scope_binding.scope_enum import ScopeEnum


class ScopeBindingMethods(object):
    @classmethod
    def scope_binding_decorator(cls, resolved_dependency_graph, dependency_obj):
        if dependency_obj.scope == ScopeEnum.INSTANCE:
            cls.decorate_instance_obj(resolved_dependency_graph, dependency_obj.obj)
        elif dependency_obj.scope == ScopeEnum.FUNCTION: pass


    @staticmethod
    def decorate_instance_obj(resolved_dependency_graph, obj):
        try:
            obj_instance = obj.__self__
        except AttributeError:
            raise ValueError("{} is not bound to class instance, and can not be defined with instance scope")
        def new_del(_):
            if hasattr(obj, "__del__"):
                obj_instance.__del__()
            resolved_dependency_graph[obj.__name__].delete_from_scope(ScopeEnum.INSTANCE)
        obj_instance.__class__.__del__ = new_del

    @staticmethod
    def decorate_function(resolved_dependency_graph, dependency_obj):
        def del_entry_in_resolved_dependency_graph():
            resolved_dependency_graph[dependency_obj.obj.__name__].delete_from_scope(ScopeEnum.FUNCTION)
        dependency_obj.register_callback_after_function(del_entry_in_resolved_dependency_graph)

    @classmethod
    def get_service_locator_key(cls, obj, scope):
        if scope == ScopeEnum.SESSION:
            return "null"
        elif scope == ScopeEnum.MODULE:
            return "{0}".format(getmodulename(obj))
        elif scope == ScopeEnum.CLASS:
            return "{0}".format(obj.__self__.__class__)
        elif scope == ScopeEnum.INSTANCE:
            return "{0}".format(obj.__self__)
        elif scope == ScopeEnum.FUNCTION:
            return "{0}::{1}".format(obj.__self__, obj.__qualname__)
        else:
            raise NotImplementedError("{0} not a valid scope".format(scope))

