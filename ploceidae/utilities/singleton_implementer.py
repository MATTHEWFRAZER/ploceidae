from weakref import ref

class SingletonImplementer(type):
    _INSTANCE_CACHE = {}

    def __call__(cls, *args):
        instance = super(SingletonImplementer, cls).__call__(*args)
        cls._INSTANCE_CACHE[cls] = ref(instance)
        return instance

    def get_instance(cls, *args):
        try:
            return_value = cls._INSTANCE_CACHE[cls]()
            if return_value is None:
                return cls(*args)
            return return_value
        except KeyError:
            return cls(*args)
