"""F01 - Impor dan validasi event log XES menggunakan PM4Py.

Hasil impor disimpan dalam objek ``LogData`` (disebut "log aktif"). Seluruh modul
analisis (Arga, Lintang, Ida) membaca DataFrame ``LogData.df`` dengan kolom standar:

    case_id    str                 <- case:concept:name
    activity   str                 <- concept:name
    timestamp  datetime64 (UTC)    <- time:timestamp
    lifecycle  object (NaN jika kosong)  <- lifecycle:transition
    resource   object (NaN jika kosong)  <- org:resource
    position   int, mulai dari 1   <- urutan event di dalam case (urutan file XES)
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, Optional

import numpy as np
import pandas as pd

COLUMN_MAP = {
    "case:concept:name": "case_id",
    "concept:name": "activity",
    "time:timestamp": "timestamp",
    "lifecycle:transition": "lifecycle",
    "org:resource": "resource",
}
XES_NAME = {v: k for k, v in COLUMN_MAP.items()}
REQUIRED = ("case_id", "activity", "timestamp")
OPTIONAL = ("lifecycle", "resource")
STANDARD_COLUMNS = ["case_id", "activity", "timestamp", "lifecycle", "resource"]
TRACE_COLUMNS = ["position", "timestamp", "activity", "lifecycle", "resource"]

Progress = Optional[Callable[[str], None]]


class LogLoadError(Exception):
    """Kesalahan impor/validasi; pesannya aman ditampilkan langsung ke pengguna."""


@dataclass(eq=False)
class LogData:
    path: str
    df: pd.DataFrame
    attributes: list
    has_lifecycle: bool
    has_resource: bool

    @property
    def file_name(self) -> str:
        return os.path.basename(self.path)

    @cached_property
    def n_cases(self) -> int:
        return int(self.df["case_id"].nunique())

    @property
    def n_events(self) -> int:
        return int(len(self.df))

    @cached_property
    def case_index(self) -> pd.DataFrame:
        """Daftar seluruh case beserta jumlah event-nya (urutan kemunculan di log)."""
        return (
            self.df.groupby("case_id", sort=False).size().rename("events").reset_index()
        )

    def case_trace(self, case_id: str) -> pd.DataFrame:
        """Urutan event satu case (urut berdasarkan position)."""
        t = self.df[self.df["case_id"] == str(case_id)]
        return t.sort_values("position")[TRACE_COLUMNS].reset_index(drop=True)


def _blank_to_nan(series: pd.Series) -> pd.Series:
    """String kosong/spasi dianggap tidak ada nilai (NaN)."""
    s = series.astype("object")
    blank = s.map(lambda v: isinstance(v, str) and v.strip() == "")
    return s.mask(blank, np.nan)


def build_log_data(raw: pd.DataFrame, path: str = "(memori)", progress: Progress = None) -> LogData:
    """Validasi DataFrame hasil PM4Py lalu ubah menjadi LogData berkolom standar."""
    say = progress or (lambda _msg: None)
    if raw is None or len(raw) == 0:
        raise LogLoadError("Log kosong: tidak ada event yang dapat dianalisis.")

    attributes = [str(c) for c in raw.columns]
    df = raw.rename(columns=COLUMN_MAP)

    missing = [XES_NAME[c] for c in REQUIRED if c not in df.columns]
    if missing:
        raise LogLoadError(
            "Atribut wajib tidak ditemukan pada log: " + ", ".join(missing) + "."
        )

    say("Memvalidasi atribut dan timestamp...")
    # Hanya kolom standar yang disimpan agar hemat memori (BPIC17 sangat besar).
    df = df[[c for c in STANDARD_COLUMNS if c in df.columns]].copy()
    for col in OPTIONAL:
        if col not in df.columns:
            df[col] = pd.Series([None] * len(df), index=df.index, dtype="object")

    n_bad = int(df["case_id"].isna().sum())
    if n_bad:
        raise LogLoadError(f"{n_bad} event tidak memiliki case ID (case:concept:name).")
    n_bad = int(df["activity"].isna().sum())
    if n_bad:
        raise LogLoadError(f"{n_bad} event tidak memiliki nama aktivitas (concept:name).")

    ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    n_bad = int(ts.isna().sum())
    if n_bad:
        raise LogLoadError(f"{n_bad} event memiliki time:timestamp kosong atau tidak valid.")

    df["case_id"] = df["case_id"].astype(str)
    df["activity"] = df["activity"].astype(str)
    df["timestamp"] = ts
    df["lifecycle"] = _blank_to_nan(df["lifecycle"])
    df["resource"] = _blank_to_nan(df["resource"])

    say("Menyusun urutan event pada setiap case...")
    df = df.reset_index(drop=True)
    # Urutan trace = urutan event pada file XES (tidak disortir ulang berdasarkan timestamp).
    df["position"] = df.groupby("case_id", sort=False).cumcount() + 1

    return LogData(
        path=path,
        df=df,
        attributes=attributes,
        has_lifecycle=bool(df["lifecycle"].notna().any()),
        has_resource=bool(df["resource"].notna().any()),
    )


def load_log(path: str, progress: Progress = None) -> LogData:
    """Membaca file XES dengan PM4Py dan mengembalikan log aktif."""
    say = progress or (lambda _msg: None)
    if not path or not os.path.isfile(path):
        raise LogLoadError(f"File tidak ditemukan: {path}")
    if not path.lower().endswith((".xes", ".xes.gz")):
        raise LogLoadError("Format file tidak didukung. Pilih file berekstensi .xes.")

    try:
        import pm4py
    except ImportError as exc:
        raise LogLoadError("PM4Py belum terpasang. Jalankan: pip install pm4py") from exc

    say("Membaca file XES dengan PM4Py (file BPIC17 besar, mohon tunggu)...")
    try:
        raw = pm4py.read_xes(path)
        if not isinstance(raw, pd.DataFrame):
            raw = pm4py.convert_to_dataframe(raw)
    except Exception as exc:  # parser bisa melempar berbagai jenis error
        raise LogLoadError(
            f"File XES tidak dapat dibaca (mungkin rusak atau bukan XES yang valid): {exc}"
        ) from exc

    say(f"File terbaca: {len(raw):,} baris event.")
    return build_log_data(raw, path, progress)
