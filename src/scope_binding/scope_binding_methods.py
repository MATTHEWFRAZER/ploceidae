from scope_binding.scope_enum import ScopeEnum


class ScopeBindingMethods(object):

    DECORATED = {}

    @classmethod
    def scope_binding_decorator(cls, dependency_graph, dependency_obj, scope_key):
        if scope_key.scope == ScopeEnum.INSTANCE and not cls.is_decorated(scope_key.obj):
            cls.decorate_instance_obj(dependency_graph, dependency_obj.obj)

    @staticmethod
    def decorate_instance_obj(dependency_graph, obj):
        try:
            obj_instance = obj.__self__
        except AttributeError:
            raise ValueError("{} is not bound to class instance, and can not be defined with instance scope")
        def new_del(_):
            if hasattr(obj, "__del__"):
                obj_instance.__del__()
            dependency_graph[obj.__name__].delete_entry_from_service_locator(str(obj_instance.__self__))
        obj_instance.__class__.__del__ = new_del

    @classmethod
    def is_decorated(cls, obj):
        cls.DECORATED[obj] = True

