from sys import version_info

pygmy_reduce = None

if version_info >= (3, 3):
    from functools import reduce
    pygmy_reduce = reduce
else:
    pygmy_reduce = reduce