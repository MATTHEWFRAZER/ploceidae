Ploceidae (https://en.wikipedia.org/wiki/Ploceidae) is the family name of birds that weave intricate nests not unlike how this framework wires together intricate dependency graphs. Ploceidae is heavily influenced by pytest fixtures and follows the same decoration declares a dependency paradigm.

example 1 (how to declare a dependency):
```python
from ploceidae.dependency import dependency
@dependency
def dep():
    return 3
``` 

example 2 (how to request a dependency):
```python
def use_dep(dep):
    print(dep)
```

example 3 (how to wire up dependencies):
```python
from ploceidae.container import Container
container_instance = Container.get_basic_container()
wired_return_value = container_instance.wire_dependencies(use_dep)
```

example 4 (how to partially wire up dependencies)
```python
from ploceidae.container import Container
container_instance = Container.get_basic_container()
partially_wired_return_value = container_instance.partial_wire_dependencies(use_dep, "dep")
wired_return_value = partially_wired_return_value()
```

example 5 (how to declare a dependency that belongs to a group):
```python
from ploceidae.dependency import dependency
@dependency(group="group")
def group():
    return 3
```

example 6 (how to request dependencies that belong to a group):
```python
def use_group(*group):
    print(group)
```

example 7 (how to wire up dependencies):
```python
from ploceidae.container import Container
container_instance = Container.get_basic_container()
wired_return_value = container_instance.wire_dependencies(use_group)
```