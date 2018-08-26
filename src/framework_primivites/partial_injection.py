from inspect import getargspec

from framework_primivites.primitive_marker import MarionettePrimitive


class PartialInjection(MarionettePrimitive):
    def __init__(self, dependent_obj, dependencies_to_ignore, *grouped_dependencies_to_be_injected, **dependencies_to_be_injected):
        self.dependent_obj = dependent_obj
        self.dependencies_to_ignore = dependencies_to_ignore
        self.dependencies_to_be_injected = dependencies_to_be_injected
        self.grouped_dependencies_to_be_injected = grouped_dependencies_to_be_injected

    def __call__(self, *dependencies_to_be_injected):
        zipped_dependencies_to_be_injected = zip(self.dependencies_to_ignore, dependencies_to_be_injected)
        self.dependencies_to_be_injected.update(dict(zipped_dependencies_to_be_injected))

        dependencies = filter(lambda x: x not in ("self", "mcs", "cls"), getargspec(self.dependent_obj)[0])
        dependencies_to_be_injected = [self.dependencies_to_be_injected[dependency] for dependency in dependencies] + list(self.grouped_dependencies_to_be_injected)

        return self.dependent_obj(*dependencies_to_be_injected)