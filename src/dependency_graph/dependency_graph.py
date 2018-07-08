class DependencyGraphNode(object):
    def __init__(self, dependency_obj, *dependencies):
        try:
            self.dependency_name = dependency_obj.__name__
        except AttributeError:
            raise ValueError("dependency must have __name__ attribute")
        self.dependency_obj = dependency_obj
        self.dependencies = dependencies


class DependencyGraph(object):
    def __init__(self):
        self.graph = {}

    def add_node(self, dependency_graph_node):
        if dependency_graph_node.dependency_name in self.graph:
            raise ValueError("dependency with name {0} already exists in dependency graph".format(dependency_graph_node.dependency_name))

    def get_node(self, node_name):
        return self.graph[node_name]

    def __contains__(self, node_name):
        return node_name in self.graph


