from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW

from .status_bar import status_bar


# Example. do not inherit this class
class thread_worker(QtCore.QObject):
    result_ready = QtCore.Signal()
    notification = QtCore.Signal(int)
    set_status_bar_text = QtCore.Signal(str)
    set_status_bar_percent = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

    @QtCore.Slot()
    def do_job(self):
        assert(False)
        # Should emit this when notify
        #self.notification.emit()

        # Should emit this when done
        #self.result_ready.emit()

        # Should check isInterruptionRequested and stop

class thread_controller(QtCore.QObject):
    start_thread = QtCore.Signal()
    job_notified = QtCore.Signal(int)
    job_finished = QtCore.Signal()

    def __init__(self, p_worker: thread_worker, p_status_bar: status_bar=None):
        assert(hasattr(p_worker, "result_ready") and type(p_worker.result_ready) == QtCore.SignalInstance)
        assert(hasattr(p_worker, "notification") and type(p_worker.notification) == QtCore.SignalInstance)

        if p_status_bar is not None:
            assert(hasattr(p_worker, "set_status_bar_text") and type(p_worker.notification) == QtCore.SignalInstance)
            assert(hasattr(p_worker, "set_status_bar_percent") and type(p_worker.notification) == QtCore.SignalInstance)
        assert(hasattr(p_worker, "do_job"))

        self.status_bar = p_status_bar

        super().__init__()
        self.q_thread = QtCore.QThread()
        self.worker = p_worker
        self.worker.moveToThread(self.q_thread)

        self.q_thread.finished.connect(self.worker.deleteLater)
        self.q_thread.started.connect(self.worker.do_job)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.notification.connect(self.job_notify)
        if p_status_bar is not None:
            self.worker.set_status_bar_text.connect(self.update_status_bar_text)
            self.worker.set_status_bar_percent.connect(self.update_status_bar_percent)

    def start(self):
        self.q_thread.start()

    def stop(self):
        self.q_thread.requestInterruption()
        self.q_thread.wait()

    @QtCore.Slot()
    def handle_result(self):
        self.job_finished.emit()

    @QtCore.Slot(int)
    def job_notify(self, p_val: int):
        self.job_notified.emit(p_val)

    @QtCore.Slot(str)
    def update_status_bar_text(self, p_val: str):
        if self.status_bar is None:
            return
        if len(p_val) == 0:
            self.status_bar.set_ready()
        else:
            self.status_bar.set_text(p_val)

    @QtCore.Slot(int)
    def update_status_bar_percent(self, p_val: int):
        if self.status_bar is None:
            return
        self.status_bar.set_progress_bar_value(p_val)