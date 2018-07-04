class DependencyGraphNode(object):
    def __init__(self, dependency_name, dependency_obj, *dependencies):
        if depenency_name in dependencies:
            raise ValueError("{0} is a depenency to itself".format(depenency_name))
        self.dependency_name = dependency_name
        self.dependency_obj = dependency_obj
        self.dependencies = dependencies

class DependencyGraph(object):
    def __init__(root_dependency_name, **nodes_keyed_by_name):
        try:
            nodes_keyed_by_name[root_dependency_name]
        except KeyError:
            raise ValueError("{0} is not a valid root to provided graph as it does not appear in graph".format(root_dependency_name))
        if nodes_keyed_by_name.dependencies:
            raise ValueError("root dependency {0} must not have any dependencies".format(root_dependency_name))
