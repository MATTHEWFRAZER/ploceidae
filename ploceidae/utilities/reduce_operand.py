import functools

from pymonad import Applicative


class ReduceOperand(Applicative):

    def amap(self, functor):
        return self.__class__(functools.partial(self.value, functor.value))

    def invoke(self):
        return self.value()