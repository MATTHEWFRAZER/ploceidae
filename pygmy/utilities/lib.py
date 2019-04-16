from inspect import getargspec

def get_dependencies(dependency_obj):
    return safe_get_argspec(dependency_obj)[0]

def get_group(dependency_obj):
    return safe_get_argspec(dependency_obj)[1]

def safe_get_argspec(dependency_obj):
    try:
        return getargspec(dependency_obj)
    except TypeError:
        return getargspec(dependency_obj.__init__)