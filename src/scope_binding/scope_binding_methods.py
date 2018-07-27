from scope_binding.scope_enum import ScopeEnum


class ScopeBindingMethods(object):
    @classmethod
    def scope_binding_decorator(cls, resolved_dependency_graph, dependency_obj):
        if dependency_obj.scope == ScopeEnum.INSTANCE:
            cls.decorate_instance_obj(resolved_dependency_graph, dependency_obj.obj)
        elif dependency_obj.scope == ScopeEnum.FUNCTION:


    @staticmethod
    def decorate_instance_obj(resolved_dependency_graph, obj):
        try:
            obj_instance = obj.__self__
        except AttributeError:
            raise ValueError("{} is not bound to class instance, and can not be defined with instance scope")
        def new_del(self_ref):
            if hasattr(obj, "__del__"):
                obj_instance.__del__()
            del resolved_dependency_graph[str(obj)]
        obj_instance.__class__.__del__ = new_del

    @staticmethod
    def decorate_function(resolved_dependency_graph, dependency_obj):
        def del_entry_in_resolved_dependency_graph():
            del resolved_dependency_graph[str(dependency_obj.obj)]
        dependency_obj.register_callback_after_function(del_entry_in_resolved_dependency_graph)

    @staticmethod
    def get_