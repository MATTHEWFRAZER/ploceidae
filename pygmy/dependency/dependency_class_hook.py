from pygmy.dependency.lib import invoke_callbacks_after

class DependencyClassHook(type):
    """
    meta class for intercepting a dependency class' init, this is needed because we still have post delivery callbacks
    """
    _callback_dict = {}

    def __init__(cls, name, bases, attributes):


    def __call__(self, dependency_obj):
        for callback in self._callback_dict[dependency_obj]: callback()


    @classmethod
    def register_callbacks(cls, class_instance, callbacks):
        cls._callback_dict[class_instance] = callbacks

    @classmethod
    def unregister_callbacks(cls, class_instance):
        del cls._callback_dict[class_instance]