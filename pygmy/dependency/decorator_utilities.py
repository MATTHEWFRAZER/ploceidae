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

def get_class_instance_from_args(*args):
    try:
        return args[0]
    except:
        raise ValueError("empty argument list to dependency factory")
