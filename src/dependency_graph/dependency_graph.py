class DependencyGraphNodeLocator(object):
    def __init__(self, dependency_obj, scope_key_string):
        self.name = dependency_obj.__name__
        self.dependency_obj = dependency_obj
        self.scope_key_string = scope_key_string


class DependencyGraph(object):
    def __init__(self):
        self.graph = {}

    def add_node(self, dependency_obj, scope_key_string):
        #if self.graph.get(dependency_obj.dependency_name) is dependency_obj.dependency_obj:
        #    raise ValueError("dependency_primitives with name {0} already exists in dependency_primitives graph".format(dependency_obj.dependency_name))
        #self.graph[dependency_obj.dependency_name] = dependency_obj
        if dependency_obj.dependency_name not in self.graph:
            self.graph[dependency_obj.dependency_name] = {}
            self.graph[dependency_obj.dependency_name][scope_key_string] = dependency_obj

    def get_node(self, dependency_graph_node_locator):
        return self.graph[dependency_graph_node_locator.name][dependency_graph_node_locator.scope_key_string]

    def clear(self):
        for services in self.graph.values(): services.clear()
        self.graph.clear()

    def copy(self):
        return {k:v.copy()for k, v in self.graph.items()}

    def __contains__(self, dependency_graph_node_locator):
        return dependency_graph_node_locator.name in self.graph and dependency_graph_node_locator.scope_key_string in self.graph[dependency_graph_node_locator.name]

    def __len__(self):
        return len(self.graph)

    def __getitem__(self, dependency_graph_node_locator):
        return self.graph[dependency_graph_node_locator.name]

    def pop(self, dependency_graph_node_locator):
        return self.graph[dependency_graph_node_locator.name].pop(dependency_graph_node_locator.scope_key_string)

    def items(self, scope_key_string):
        return {k: v[scope_key_string] for k, v in self.graph.items()}.items()