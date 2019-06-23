import inspect

class ModuleNameHelper(object):

    @staticmethod
    def get_module_name(obj):
        module = inspect.getmodule(obj)
        return str(module).split()[1].replace("'", "")