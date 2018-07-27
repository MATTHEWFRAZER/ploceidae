from framework_primivites.primitive_marker import MarionettePrimitive


# make primitive
class DependencyWithMutableDependencies(MarionettePrimitive):
    def __init__(self, decorated_obj):
        self.decorated_obj = decorated_obj.dependency_obj
        self.dependencies = decorated_obj.dependencies
        self.mutable_dependencies = decorated_obj.dependencies[:]