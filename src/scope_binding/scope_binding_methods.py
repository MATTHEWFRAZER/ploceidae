from scope_binding.scope_enum import ScopeEnum


class ScopeBindingMethods(object):
    @classmethod
    def scope_binding_decorator(cls, resolved_dependency_graph, dependency_obj, scope_key):
        if scope_key.scope == ScopeEnum.INSTANCE:
            cls.decorate_instance_obj(resolved_dependency_graph, dependency_obj.obj, scope_key)

    @staticmethod
    def decorate_instance_obj(resolved_dependency_graph, obj, scope_key):
        try:
            obj_instance = obj.__self__
        except AttributeError:
            raise ValueError("{} is not bound to class instance, and can not be defined with instance scope")
        def new_del(_):
            if hasattr(obj, "__del__"):
                obj_instance.__del__()
            resolved_dependency_graph[obj.__name__].delete_entry_from_service_locator(str(scope_key))
        obj_instance.__class__.__del__ = new_del

