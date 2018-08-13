class DependencyGraph(object):
    def __init__(self):
        self.graph = {}

    def add_node(self, dependency_graph_node):
        if dependency_graph_node.dependency_name in self.graph:
            raise ValueError("dependency_primitives with name {0} already exists in dependency_primitives graph".format(dependency_graph_node.dependency_name))
        self.graph[dependency_graph_node.dependency_name] = dependency_graph_node

    def get_node(self, node_name):
        return self.graph[node_name]

    def clear(self):
        self.graph.clear()

    def get(self, node):
        return self.graph.get(node)

    def copy(self):
        return self.graph.copy()

    def values(self):
        return self.graph.values()

    def __contains__(self, item):
        return item in self.graph

    def __len__(self):
        return len(self.graph)

    def __getitem__(self, item):
        return self.graph[item]

    def pop(self, item):
        return self.graph.pop(item)

    def items(self):
        return self.graph.items()