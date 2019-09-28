from sys import version_info

interoperable_reduce = None

if version_info >= (3, 3):
    from functools import reduce
    interoperable_reduce = reduce
else:
    interoperable_reduce = reduce