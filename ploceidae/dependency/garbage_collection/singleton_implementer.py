from weakref import ref

class SingletonImplementer(type):
    _INSTANCE_CACHE = {}

    def __call__(cls, *args):
        instance = super(SingletonImplementer, cls).__call__(*args)
        cls._INSTANCE_CACHE[(cls,) + args] = ref(instance)
        return instance

    def get_instance(cls, *args):
        try:
            return cls._INSTANCE_CACHE[args]
        except KeyError:
            return cls(*args)