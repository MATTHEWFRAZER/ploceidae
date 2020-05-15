from threading import Thread, Event
import time

class Scheduler(object):
    SCHEDULING_INTERVAL_IN_SECONDS = 20

    def __init__(self, garbage_collector_observer):
        self.event = Event()
        self.thread = Thread(target=self.target, name="ploceidae_scheduler")
        self.thread.daemon = True
        self.garbage_collector_observer = garbage_collector_observer

    def start(self):
        self.thread.start()

    def stop(self):
        self.event.set()
        self.thread.join(self.SCHEDULING_INTERVAL_IN_SECONDS)
        if self.thread.is_alive():
            raise EnvironmentError("scheduler thread could not be stopped in a timely manner")

    def target(self):
        while not self.event.is_set():
            self.garbage_collector_observer()
            time.sleep(self.SCHEDULING_INTERVAL_IN_SECONDS)