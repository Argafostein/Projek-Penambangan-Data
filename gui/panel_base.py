"""Kelas dasar panel analisis - KONTRAK GUI untuk Arga dan Lintang.

Panel analisis cukup mewarisi ``AnalysisPanelBase``:
  * ``self.log``                  log aktif (LogData) atau None.
  * ``set_log(log)``              dipanggil otomatis saat file baru diimpor (memanggil reset()).
  * ``reset()``                   override untuk mengosongkan tampilan/hasil.
  * ``result_ready.emit(result)`` kirim hasil (dict kontrak) agar bisa diekspor dan dibuka di Case Explorer.
  * ``show_in_explorer.emit(result, case_id)``  minta Case Explorer menampilkan hasil/case tertentu.
  * ``status_message.emit(text)`` pesan singkat ke status bar.
"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class AnalysisPanelBase(QWidget):
    result_ready = Signal(dict)
    show_in_explorer = Signal(dict, str)
    status_message = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log = None

    def set_log(self, log) -> None:
        self.log = log
        self.reset()

    def reset(self) -> None:
        """Override: kosongkan tampilan dan hasil sebelumnya."""
