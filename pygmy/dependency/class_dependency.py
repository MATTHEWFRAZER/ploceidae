from pygmy.dependency import Dependency

class ClassDependency(Dependency):
    def __call__(self, dependency_obj):
        if type(dependency_obj) is not DependencyClassHook:
            raise ValueError("in order to use the dependency class decorator, the class needs to inherit from DependencyClassHook as a metaclass")
        dependency_func = super(ClassDependency, self).__call__(dependency_obj)
        if dependency_obj