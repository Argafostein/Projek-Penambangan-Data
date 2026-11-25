"""Menjalankan komputasi berat di thread latar belakang agar GUI tidak membeku."""
from __future__ import annotations

import traceback

from PySide6.QtCore import QThread, Signal

from core.log_loader import LogLoadError

_ACTIVE: list = []  # menjaga referensi thread agar tidak dibersihkan GC saat masih berjalan


class TaskThread(QThread):
    status = Signal(str)
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, fn, args=(), with_progress=False):
        super().__init__()
        self._fn, self._args, self._with_progress = fn, args, with_progress

    def run(self):
        try:
            if self._with_progress:
                result = self._fn(*self._args, progress=self.status.emit)
            else:
                result = self._fn(*self._args)
        except LogLoadError as exc:
            self.failed.emit(str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - semua error dilaporkan ke pengguna
            traceback.print_exc()
            self.failed.emit(f"Terjadi kesalahan tak terduga ({type(exc).__name__}): {exc}")
            return
        self.succeeded.emit(result)


def run_task(fn, *args, on_success, on_error=None, on_status=None, with_progress=False) -> TaskThread:
    """Jalankan ``fn(*args)`` di thread lain. Callback harus berupa method milik widget."""
    _ACTIVE[:] = [t for t in _ACTIVE if t.isRunning()]
    thread = TaskThread(fn, args, with_progress)
    thread.succeeded.connect(on_success)
    if on_error:
        thread.failed.connect(on_error)
    if on_status:
        thread.status.connect(on_status)
    _ACTIVE.append(thread)
    thread.start()
    return thread


def shutdown_tasks(timeout_ms: int = 1500) -> None:
    for t in list(_ACTIVE):
        if t.isRunning() and not t.wait(timeout_ms):
            t.terminate()
            t.wait()
    _ACTIVE.clear()
