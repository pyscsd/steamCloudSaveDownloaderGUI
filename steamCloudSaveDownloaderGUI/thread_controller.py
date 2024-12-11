from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW

import sys

# Example do not inherit this class
class thread_worker(QtCore.QObject):
    result_ready = QtCore.Signal()
    notification = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

    @QtCore.Slot()
    def do_job(self):
        assert(False)
        # Should emit this when notify
        #self.notification.emit()

        # Should emit this when done
        #self.result_ready.emit()

class thread_controller(QtCore.QObject):
    start_thread = QtCore.Signal()
    job_notified = QtCore.Signal(int)
    job_finished = QtCore.Signal()

    def __init__(self, p_worker: thread_worker):
        assert(hasattr(p_worker, "result_ready") and type(p_worker.result_ready) == QtCore.SignalInstance)
        assert(hasattr(p_worker, "notification") and type(p_worker.notification) == QtCore.SignalInstance)

        super().__init__()
        self.q_thread = QtCore.QThread()
        self.worker = p_worker
        self.worker.moveToThread(self.q_thread)

        self.q_thread.finished.connect(self.worker.deleteLater)
        self.q_thread.started.connect(self.worker.do_job)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.notification.connect(self.job_notify)

    def start(self):
        self.q_thread.start()

    # TODO Handle on mainwindow exit
    def __del__(self):
        self.q_thread.quit()
        self.q_thread.wait()

    @QtCore.Slot()
    def handle_result(self):
        self.job_finished.emit()

    @QtCore.Slot(int)
    def job_notify(self, p_val: int):
        self.job_notified.emit(p_val)