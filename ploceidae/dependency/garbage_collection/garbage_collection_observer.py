import gc
from threading import Lock

from six import with_metaclass

from ploceidae.dependency.garbage_collection.singleton_implementer import SingletonImplementer
from ploceidae.constants import PHASE_STOP

class GarbageCollectionObserver(with_metaclass(SingletonImplementer)):

    def __new__(cls, *args, **kwargs):
        instance = super(GarbageCollectionObserver, cls).__new__(cls, *args, **kwargs)
        #gc.callbacks.append(instance)
        return instance

    def __init__(self):
        self.garbage_lock = Lock()
        self.callbacks = []

    def register(self, callback):
        with self.garbage_lock:
            self.callbacks.append(callback)

    def __call__(self, phase, info):
        if phase == PHASE_STOP:
            # we remove filter callbacks that cleanup
            with self.garbage_lock:
                # TODO: probably make async
                self.callbacks = list(callback for callback in self.callbacks if not callback(phase, info))
