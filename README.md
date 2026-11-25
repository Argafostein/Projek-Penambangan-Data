# BPIC17 Event Log Analyzer - Tahap 1 (bagian Ida Bagus)

Aplikasi desktop (Python + PM4Py + PySide6) untuk menjawab latihan Bab 11 FBPM dari event log BPIC17.
Repositori ini berisi bagian **Ida Bagus**: impor XES (F01), overview (F02), Exercise 11.22 (F06),
Case Explorer & ekspor CSV (F07), serta kerangka GUI utama. Panel Lintang (11.7) dan Arga (11.15/11.18)
dipasang otomatis jika file-nya ditambahkan (lihat "Menyambungkan panel").

## Instalasi
Python 3.10 - 3.12 disarankan.

    python -m venv venv
    venv\Scripts\activate            # Windows   (macOS/Linux: source venv/bin/activate)
    pip install -r requirements.txt
    pip install r4pm                 # opsional: mempercepat pembacaan XES besar

## Menjalankan
    python main.py                   # lalu: File > Buka file XES (atau tombol "Pilih file .xes")

Untuk mencoba tanpa dataset BPIC17:

    python tools/generate_sample_xes.py     # membuat sample_data/sample_log.xes (sudah disertakan)

Dataset BPIC17 (tidak disertakan): https://data.4tu.nl/articles/dataset/BPI_Challenge_2017/12696884

## Pengujian
    python -m pytest -q

## Struktur
    main.py                  titik masuk aplikasi
    core/log_loader.py       F01  impor XES (PM4Py), validasi, LogData (log aktif)
    core/overview.py         F02  metrik dasar, frekuensi aktivitas, tabel case & durasi
    core/cycle_time.py       SEMENTARA - milik Lintang (durasi case)
    core/exercise_1122.py    F06  O_Cancelled -> O_Accepted (eventually follows)
    utils/csv_export.py      F07  ekspor CSV
    utils/versions.py        versi library untuk menu Bantuan
    gui/main_window.py       jendela utama, navigasi, status, perekat antar panel
    gui/panel_base.py        kontrak panel analisis (untuk Arga & Lintang)
    gui/panel_dataset.py     tampilan Dataset & Status
    gui/panel_overview.py    tampilan Overview
    gui/panel_1122.py        tampilan Exercise 11.22
    gui/case_explorer.py     Case Explorer
    gui/panel_export.py      tampilan Export
    gui/widgets.py           tabel berfitur cari, kartu metrik
    gui/workers.py           thread latar belakang (GUI tidak membeku)
    tests/                   unit test + uji GUI offscreen
    tools/generate_sample_xes.py   pembuat log sintetis

## Kontrak data (untuk Arga & Lintang)
Log aktif = `LogData` (`core/log_loader.py`). DataFrame `log.df` berkolom:
`case_id`, `activity`, `timestamp` (UTC), `lifecycle`, `resource` (NaN jika kosong), `position` (mulai 1).

Fungsi analisis menerima `df` dan mengembalikan dict `result`:

    {"exercise": "11.15", "title": "...", "case_count": int, "case_ids": [...],
     "filter_rule": "...", "evidence": {case_id: dict | list[dict]},
     "metrics": {"numerator": .., "denominator": .., "percentage": .., ...}}

Di `evidence`, kunci `reason` (teks) dan `highlight_positions` (list nomor `position`) dipakai Case Explorer
untuk menyorot event bukti. Kunci `exercise` harus unik per hasil (mis. "11.7 A", "11.15", "11.18").

## Menyambungkan panel
Buat `gui/panel_117.py` (kelas `Panel117`) dan `gui/panel_1115_1118.py` (kelas `Panel1115_1118`) yang mewarisi
`AnalysisPanelBase`. Setelah analisis selesai: `self.result_ready.emit(result)`. Untuk membuka rincian:
`self.show_in_explorer.emit(result, case_id)`. Contoh lengkap: `gui/panel_1122.py`.
`core/cycle_time.py` boleh diganti Lintang selama fungsi `case_durations_days(df)` dan `mean_cycle_days(df)` tetap ada.
