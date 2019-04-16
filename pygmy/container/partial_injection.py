import logging
from pprint import pformat

from pygmy.utilities.lib import get_dependencies

logger = logging.getLogger(__name__)

class PartialInjection(object):
    def __init__(self, dependent_obj, dependencies_to_ignore, *grouped_dependencies_to_be_injected, **dependencies_to_be_injected):
        self.dependent_obj = dependent_obj
        self.dependencies_to_ignore = dependencies_to_ignore
        self.dependencies_to_be_injected = dependencies_to_be_injected
        self.grouped_dependencies_to_be_injected = grouped_dependencies_to_be_injected

    def __call__(self, *dependencies_to_be_injected):
        zipped_dependencies_to_be_injected = zip(self.dependencies_to_ignore, dependencies_to_be_injected)
        self.dependencies_to_be_injected.update(dict(zipped_dependencies_to_be_injected))

        dependencies = filter(lambda x: x not in ("self", "mcs", "cls"), get_dependencies(self.dependent_obj))
        dependencies_to_be_injected = [self.dependencies_to_be_injected[dependency] for dependency in dependencies] + list(self.grouped_dependencies_to_be_injected)

        try:
            logger.debug("to {0} fully inject dependencies: \n{1}".format(self.dependent_obj, pformat(dependencies_to_be_injected)))
            return self.dependent_obj(*dependencies_to_be_injected)
        except TypeError as ex:
            raise TypeError("argument list could not have dependencies resolved to it. Did you decorate your target dependent with function with a different argument list? ex: {0}".format(ex))
