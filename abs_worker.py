from abc import ABC, abstractmethod
from threading import Thread
from time import sleep


class AbstractWorker(ABC):
    """
    Abstract class that provides functionality to perform periodic operations in separate thread.
    """

    def __init__(self, name, loop_delay=0, on_start_cb=None, on_stop_cb=None):
        """
        Initialize class' instance.

        :param name:
        :param loop_delay:
        :param on_start_cb:
        :param on_stop_cb:
        """
        self.loop_delay = loop_delay
        self.name = name
        self.on_start_cb = on_start_cb
        self.on_stop_cb = on_stop_cb
        self.is_run_int = False
        self.thread = None
        super().__init__()
        print("Init %s" % self.name)

    def start(self):
        """
        Start to perform operations.

        :return:
        """
        if self.is_run_int:
            return

        print("Start %s" % self.name)
        self.is_run_int = True
        if self.on_start_cb is not None:
            self.on_start_cb()
        # Run worker in separate thread
        if self.thread is None:
            self.thread = Thread(target=self.runnable_int, name=self.name + "-Thread")
        self.thread.start()

    def stop(self):
        """
        Stop to perform operations.

        :return:
        """
        if not self.is_run_int:
            return
        print("Stop %s" % self.name)
        self.is_run_int = False
        self.thread = None
        if self.on_stop_cb is not None:
            self.on_stop_cb()

    def is_run(self):
        """
        Helper method to inform whether operations loop is running.

        :return: True or False
        """
        return self.is_run_int

    def runnable_int(self):
        """
        Internal logic to perform operations in a loop.

        :return:
        """
        while self.is_run_int:
            self.runnable()
            if not self.is_run_int:
                return
            sleep(self.loop_delay)
            if not self.is_run_int:
                return

    @abstractmethod
    def runnable(self):
        """
        Abstract method to provide to client to implement custom functionality accosiated with operation.

        :return:
        """
        pass

    def join(self):
        if not self.is_run_int:
            return
        self.thread.join()
