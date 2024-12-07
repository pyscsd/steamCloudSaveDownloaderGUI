from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW

import time
import sys

class thread_worker(QtCore.QObject):
    result_ready = QtCore.Signal()

    def __init__(self):
        print("Thread worker init")
        super().__init__()

    @QtCore.Slot()
    def do_job(self):
        sys.stdout.write("Test")
        sys.stdout.flush()
        try:
            print("DO JOB")
            for i in range(5):
                print(f"Do JOB and sleep {i}")
                time.sleep(1)
            self.result_ready.emit()
        except:
            a, b, c = sys.exc_info()
            sys.excepthook(a, b, c)


class thread_controller(QtCore.QObject):
    start_thread = QtCore.Signal()

    def __init__(self):
        print("CONTROLLER __INIT")
        super().__init__()
        self.q_thread = QtCore.QThread()
        self.worker = thread_worker()
        self.worker.moveToThread(self.q_thread)

        self.q_thread.finished.connect(self.worker.deleteLater)
        self.start_thread.connect(self.worker.do_job)
        self.worker.result_ready.connect(self.handle_result)

        print("Start")
        self.q_thread.start()

        self.start_thread.emit()


    def __del__(self):
        print("_del")
        self.q_thread.quit()
        self.q_thread.wait()

    @QtCore.Slot()
    def handle_result(self):
        print("handle result")