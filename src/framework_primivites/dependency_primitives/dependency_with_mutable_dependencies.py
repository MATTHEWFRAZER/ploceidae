from framework_primivites.primitive_marker import MarionettePrimitive


# make primitive
class DependencyWithMutableDependencies(MarionettePrimitive):
    def __init__(self, dependency):
        self.dependency_obj = dependency.dependency_obj
        self.dependency_name = dependency.dependency_name
        self.dependencies = dependency.dependencies
        self.mutable_dependencies = dependency.dependencies[:]