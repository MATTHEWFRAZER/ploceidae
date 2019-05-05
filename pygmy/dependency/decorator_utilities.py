from re import compile

from pygmy.dependency.dependency import Dependency

def control_initialization(*args, **kwargs):
    """
    this makes it so that dependency can be invoked as a decorator without calling it with empty args. need args and
    kwargs here because it needs to be called like __init__ or __call__
    """
    if kwargs:
        # if we're calling it like __init__
        return Dependency(**kwargs)
    else:
        # if we're calling it like __call__
        return Dependency()(*args)

def dependency_from_class(*args, **kwargs):
    """a class decorator for loading class definitions directly into the dependency graph"""
    if kwargs:
        return handle_init_arguments(**kwargs)
    else:
        return handle_call_arguments(*args)

def handle_init_arguments(**kwargs):
    dependency = Dependency.control_initialization(**kwargs)
    return lambda *args: handle_class_instance(dependency, *args)

def handle_call_arguments(*args):
    dependency = handle_class_instance(Dependency(), get_class_instance_from_args(*args))
    return dependency(*args)

def get_class_instance_from_args(*args):
    try:
        return args[0]
    except:
        raise ValueError("empty argument list to dependency factory")

def handle_class_instance(dependency, cls):
    dependency_name = class_name_to_dependency_name(cls.__name__)
    dependency.dependency_name = dependency_name
    return dependency

capital_letter_pattern = compile(r"[A-Z][a-z|0-9]*")
illegal_characters     = compile(r"[&*^%$#@`~[]{}!?/<>,.|;:\\]")
whitespace             = compile(r"\s")

def class_name_to_dependency_name(class_name):
    if not class_name:
        raise ValueError("invalid class name, name is empty string")

    if whitespace.match(class_name):
        raise ValueError("invalid class name, name contains whitespace")

    if illegal_characters.match(class_name):
        raise ValueError("Illegal character in class name")

    if not class_name[0].isupper():
        raise ValueError("invalid class name {0}. Name must follow Pascal Case conventions".format(class_name))

    lower_case_list = map(lambda x: x.lower(), capital_letter_pattern.findall(class_name))
    return "_".join(lower_case_list)