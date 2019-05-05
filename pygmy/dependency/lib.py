from functools import wraps
from re import compile

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


def invoke_callbacks_after(callbacks, func):
    callbacks = callbacks[:]
    @wraps(func)
    def nested(*unresolved_dependencies, **kwargs):
        cached = func(*unresolved_dependencies, **kwargs)
        for callback in callbacks: callback()
        return cached
    return nested