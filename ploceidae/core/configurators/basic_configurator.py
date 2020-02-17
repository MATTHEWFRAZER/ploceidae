import attr

from ploceidae.container import Container
from ploceidae.dependency_management.dependency_graph import DependencyGraph
from ploceidae.dependency_management.dependency_graph_manager import DependencyGraphManager
from ploceidae.dependency.dependency_wrapper import DependencyWrapper
from ploceidae.dependency_lifetime.dependency_lifetime_enum import DependencyLifetimeEnum

@attr.s
class BasicConfigurator(object):
    dependency_graph_manager = attr.ib(init=False, default=DependencyGraphManager(DependencyGraph()))

    def get_container(self):
        return Container(self.dependency_graph_manager)

    def get_dependency_wrapper(self):
        def dependency(*args, **kwargs):
            if kwargs:
                if any(key for key in kwargs.keys() if key not in ("lifetime", "visibility", "group")):
                    raise ValueError("invalid argument to dependency wrapper")
                kwargs["dependency_graph_manager"] = self.dependency_graph_manager
                kwargs["lifetime"] = kwargs.get("lifetime", DependencyLifetimeEnum.FUNCTION)
                kwargs["group"] = kwargs.get("group")
                kwargs["visibility"] = kwargs.get("visibility")
                return DependencyWrapper(**kwargs)
            else:
                if len(args) != 1:
                    raise ValueError("dependency registration takes only one dependency argument")
                return DependencyWrapper(DependencyLifetimeEnum.FUNCTION, None, None, self.dependency_graph_manager)(*args)
        return dependency
