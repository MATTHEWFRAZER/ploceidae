import logging
from pprint import pformat

from ploceidae.constants import BINDINGS
from ploceidae.dependency_management.dependency_resolution_methods import DependencyResolutionMethods

logger = logging.getLogger(__name__)

class PartialInjection(object):
    def __init__(self, dependent_object, dependencies_to_ignore, *grouped_dependencies_to_be_injected, **dependencies_to_be_injected):
        self.dependent_object = dependent_object
        self.dependencies_to_ignore = dependencies_to_ignore
        self.dependencies_to_be_injected = dependencies_to_be_injected
        self.grouped_dependencies_to_be_injected = grouped_dependencies_to_be_injected

    def __call__(self, *dependencies_to_be_injected):
        dependencies_to_be_injected = self.get_dependencies_to_be_injected(dependencies_to_be_injected)
        try:
            #logger.debug("to {0} fully inject dependencies: \n{1}".format(self.dependent_object, pformat(dependencies_to_be_injected)))
            return self.dependent_object(*dependencies_to_be_injected)
        except TypeError as ex:
            raise ValueError("argument list could not have dependencies resolved to it. Did you decorate your target dependent with function with a different argument list? ex: {0}".format(ex))

    def get_dependencies_to_be_injected(self, dependencies_to_be_injected):
        zipped_dependencies_to_be_injected = zip(self.dependencies_to_ignore, dependencies_to_be_injected)
        self.dependencies_to_be_injected.update(dict(zipped_dependencies_to_be_injected))
        dependencies = (x for x in DependencyResolutionMethods.get_dependencies(self.dependent_object) if x not in BINDINGS)
        return [self.dependencies_to_be_injected[dependency_name] for dependency_name in dependencies] + list(self.grouped_dependencies_to_be_injected)