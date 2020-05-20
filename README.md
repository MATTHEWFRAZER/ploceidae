Ploceidae (https://en.wikipedia.org/wiki/Ploceidae) is the family name of birds that weave intricate nests not unlike how this framework wires together intricate dependency graphs. Ploceidae is heavily influenced by pytest fixtures and follows the same decoration-declares-a-dependency paradigm.

**Terminology:**

**container:** a class that is used to resolve and wire up dependencies to a dependent object (see example 3)

**dependency:** the name of a decorator that is used to register ploceidae dependencies (see example 1)

**partial injection:** a situation in which only a partial list of dependencies are requested and resolved to a dependent object (see example 4) 

**dependency lifetime:** defines how long a dependency is cached. A dependency lifetime is bound to either the process lifetime (Session), a module lifetime is bound to the lifetime of a module and will only be resolved to objects contained in the same module (Module), a class lifetime is bound to the lifetime of a class and will only be resolved to members of said class (Class), an instance lifetime is bound to the lifetime of an instance of an object and will only be resolved to members of said instance (Instance), a function lifetime is the default value and means no caching occurs and a new dependency is resolved each time it is requested (Function) (see ploceidae.dependency_lifetime.dependency_lifetime_enum.py)

**globally visible dependency:** a dependency that is visible to all objects in process. As such, any object can request the resolution of a global dependency

**module visibility dependency:** a dependency that is not declared as a global dependency. Such a dependency will only be visible to objects in the same module. Module visibility has higher precedence than global visibility and is the default value

**builtin dependency:** A dependency that is offered by ploceidae. Such a dependency is globally visible. Currently, there are no builtin dependencies 

**group:** a list of dependencies that have been resolved under the same tag (see examples 5, 6, 7)

**Examples**

**example 1 (how to declare a dependency):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
dependency = configurator.get_dependency_wrapper()

@dependency
def dep():
    return 3
``` 

**example 2 (how to request a dependency):**
```python
def use_dep(dep):
    print(dep)
```

**example 3 (how to wire up dependencies):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
container = configurator.get_container()
wired_return_value = container.wire_dependencies(use_dep)
```

**example 4 (how to partially wire up dependencies):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
container = configurator.get_container()
partially_wired_return_value = container.partially_wire_dependencies(use_dep, "dep")
wired_return_value = partially_wired_return_value()
```

**example 5 (how to declare a dependency that belongs to a group):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
dependency = configurator.get_dependency_wrapper()

@dependency(group="group")
def group():
    return 3
```

**example 6 (how to request dependencies that belong to a group):**
```python
def use_group(*group):
    print(group)
```

**example 7 (how to wire up dependencies that belong to a group):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
container = configurator.get_container()
wired_return_value = container.wire_dependencies(use_group)
```

**example 8 (how to change the name a dependency gets resolved as; this pattern is useful for declaring class objects as dependencies):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
container = configurator.get_container()
dependency = configurator.get_dependency_wrapper()

@dependency(resolvable_name="class_name")
class ClassName(object): pass

def depend_on_class(class_name):
    return class_name
wired_return_value = container.wire_dependencies(depend_on_class)
```

**example 9 (the relation between dependency and dependent is transitive. E.g. if a depends on b and b depends on c, then c is computed as an implicit dependency on a):**
```python
from ploceidae.core.configurators import BasicConfigurator

configurator = BasicConfigurator()
container = configurator.get_container()
dependency = configurator.get_dependency_wrapper()

@dependency
def a():
    return "a"
    
@dependency
def b(a):
    return a + "b"

def c(b):
    return b + "c"

wired_return_value = container.wire_dependencies()
wired_return_value == "abc"
```