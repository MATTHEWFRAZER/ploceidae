from ploceidae.container import Container
from ploceidae.dependency_management.dependency_graph import DependencyGraph
from ploceidae.dependency_management.dependency_graph_manager import DependencyGraphManager
from ploceidae.dependency.dependency_wrapper import DependencyWrapper
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum

__all__ = ["BasicConfigurator"]

DEPENDENCY_GRAPH_MANAGER_KEY = "dependency_graph_manager"
LIFETIME_KEY = "lifetime"
VISIBILITY_KEY = "visibility"
GROUP_KEY = "group"
RESOLVABLE_NAME_KEY = "resolvable_name"
TRANSFORMATION_KEY = "transformation"

class BasicConfigurator(object):

    def __init__(self, dependency_graph_manager=None):
        dependency_graph = DependencyGraph()
        self.dependency_graph_manager = DependencyGraphManager(dependency_graph) if dependency_graph_manager is None else dependency_graph_manager

    def get_container(self):
        return Container(self.dependency_graph_manager)

    def get_dependency_wrapper(self):
        def dependency(*args, **kwargs):
            if kwargs:
                if any(key for key in kwargs.keys() if key not in (LIFETIME_KEY, VISIBILITY_KEY, GROUP_KEY, RESOLVABLE_NAME_KEY, TRANSFORMATION_KEY)):
                    raise ValueError("invalid argument to dependency wrapper")
                kwargs[DEPENDENCY_GRAPH_MANAGER_KEY] = self.dependency_graph_manager
                kwargs[LIFETIME_KEY] = kwargs.get(LIFETIME_KEY, DependencyLifetimeEnum.FUNCTION)
                kwargs[GROUP_KEY] = kwargs.get(GROUP_KEY)
                kwargs[VISIBILITY_KEY] = kwargs.get(VISIBILITY_KEY)
                kwargs[RESOLVABLE_NAME_KEY] = kwargs.get(RESOLVABLE_NAME_KEY)
                kwargs[TRANSFORMATION_KEY] = kwargs.get(TRANSFORMATION_KEY)
                return DependencyWrapper(**kwargs)
            else:
                if len(args) != 1:
                    raise ValueError("dependency registration takes only one dependency argument")
                return DependencyWrapper(DependencyLifetimeEnum.FUNCTION, None, None, self.dependency_graph_manager, None, None)(*args)
        return dependency
