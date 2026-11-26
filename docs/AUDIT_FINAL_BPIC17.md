# MATRIKS AUDIT FINAL & VALIDASI MENYELURUH PROYEK BPIC17 TAHAP 1

**Proyek:** Aplikasi Desktop Analisis Event Log BPIC17 Menggunakan PM4Py & PySide6  
**Tanggal Audit:** 25 November 2026  
**Auditor/Implementor:** Antigravity (Senior Software Engineer & QA Lead)  
**Lingkungan Validasi:** Windows 11, Python 3.11.9, PM4Py 2.7.23.15, PySide6 6.12.0, pandas 3.0.6, pytest 9.2.0  
**Dataset Uji:** `sample_data/sample_log.xes` (sintetis standar BPIC17 edge cases, 10 case, 23 event).  
*Catatan Dataset Asli:* Dataset BPIC17 penuh (~550 MB) tidak disertakan dalam bundle repositori ZIP; ditandai secara jujur dan transparan belum diuji langsung pada dataset asli.

---

## 1. Matriks Kepatuhan Fitur (F01 – F07 & Seluruh Subsoal)

| Kode Fitur / Subsoal | Ketentuan Rubrik Dosen | File Relevan | Status Awal (Audit Baseline) | Tindakan & Perbaikan yang Dikerjakan | Status Akhir | Bukti Kode & Hasil Pengujian |
|---|---|---|:---:|---|:---:|---|
| **F01**<br>Import & Validasi XES | Membaca file `.xes` menggunakan PM4Py; validasi case ID (`case:concept:name`), aktivitas (`concept:name`), timestamp (`time:timestamp`); deteksi opsional lifecycle & resource; penanganan error format/rusak/hilang; background worker non-blocking UI. | `core/log_loader.py`<br>`gui/workers.py`<br>`gui/panel_dataset.py` | **PASS** | Memverifikasi penanganan string kosong/spasi pada resource & lifecycle (`_blank_to_nan`), urutan `position` 1-based per case, pembersihan hasil saat pergantian file log. | **PASS** | `tests/test_log_loader.py` (7 skenario lulus): valid XES, missing file, wrong extension, missing timestamp, corrupt XML, optional attributes. |
| **F02**<br>Overview Log | Menampilkan total unique case, total event, frekuensi aktivitas, rentang waktu (min/max timestamp), mean cycle time dalam hari; daftar case dan durasi; pencarian case; memakai fungsi cycle time bersama. | `core/overview.py`<br>`core/cycle_time.py`<br>`gui/panel_overview.py` | **PARTIAL** | Mengganti implementasi sementara `cycle_time.py` dengan fungsi presisi tinggi dan teruji; menghubungkan tabel durasi ke Overview. | **PASS** | `tests/test_overview_export.py`::`test_overview_counts_and_mean_cycle` PASSED. Nilai sample: 10 case, 23 event, mean 0.05417 hari. |
| **F03 — 11.7 A**<br>Total Unique Cases | Menghitung jumlah unique case ID pada seluruh log aktif (bukan total event); daftar case ID dan bukti event. | `core/exercise_117.py`<br>`gui/panel_117.py` | **MISSING** | Mengimplementasikan `exercise_117_a()`, mengekstrak seluruh unique case tanpa duplikasi, menyusun evidence event per case. | **PASS** | `tests/test_exercise_117.py`::`test_sample_log_xes_117_exact_numbers` PASSED (10 case). |
| **F03 — 11.7 B**<br>Rata-rata Cycle Time All | Rata-rata cycle time seluruh case (max timestamp - min timestamp) dalam hari; denominator total case; kelompok kosong -> N/A. | `core/cycle_time.py`<br>`core/exercise_117.py`<br>`gui/panel_117.py` | **MISSING** | Menghitung durasi full trace setiap case dalam hari via detik/86400; menghitung mean across cases; denominator 10. | **PASS** | `tests/test_exercise_117.py` PASSED (mean = 13/240 = 0.0541667 hari). |
| **F03 — 11.7 C**<br>Successful Cases (O_Accepted) | Jumlah case mengandung >= 1 `O_Accepted` + mean full cycle time-nya; kemunculan berulang tetap dihitung 1 case; tidak eksklusif dengan D. | `core/exercise_117.py`<br>`gui/panel_117.py` | **MISSING** | Filter contains `O_Accepted`; durasi dihitung dari full trace kasus (bukan dipotong); overlap dengan 11.7 D didukung. | **PASS** | `test_repeated_accepted_counted_once_117_c`, `test_sample_log_xes_117_exact_numbers` (4 case: App 01, 02, 03, 04; mean = 7/96 = 0.0729167 hari). |
| **F03 — 11.7 D**<br>Unsuccessful Cases (O_Refused) | Jumlah case mengandung >= 1 `O_Refused` + mean full cycle time-nya; kemunculan berulang tetap dihitung 1 case; tidak eksklusif dengan C. | `core/exercise_117.py`<br>`gui/panel_117.py` | **MISSING** | Filter contains `O_Refused`; durasi dihitung dari full trace kasus; overlap dengan 11.7 C didukung. | **PASS** | `test_accepted_and_refused_overlap_c_and_d`, `test_sample_log_xes_117_exact_numbers` (1 case: App 06; mean = 1/24 = 0.0416667 hari). |
| **F03 — 11.7 E**<br>Canceled Cases (Endpoint O_Cancelled) | Jumlah case dengan event TERAKHIR pada trace-nya adalah `O_Cancelled` + mean full cycle time-nya; kemunculan di tengah tidak lolos. | `core/exercise_117.py`<br>`gui/panel_117.py` | **MISSING** | Menggunakan posisi tertinggi trace (`idxmax("position")`) per case; memverifikasi event terakhir == `O_Cancelled`. | **PASS** | `test_cancelled_in_middle_not_endpoint_117_e`, `test_sample_log_xes_117_exact_numbers` (3 case: App 02, 03, 05; mean = 1/24 = 0.0416667 hari). |
| **F04 — 11.15**<br>Repeated Complete Target | Aktivitas `W_Assess Potential Fraud` berstatus `complete` minimal 2 kali; non-complete (`schedule`, `start`, `abort`, kosong) tidak dihitung. | `core/lifecycle.py`<br>`core/exercise_1115.py`<br>`gui/panel_1115_1118.py` | **PASS** | Audit representasi lifecycle:transition == "complete" (case-insensitive & trimmed); verifikasi multi-complete dihitung per unique case. | **PASS** | `tests/test_exercise_1115_1118.py` (10 skenario lulus): scheduled 2x complete 1x gagal, non-complete diabaikan, sample log lolos 3 case (App 08, 09, 10). |
| **F05 — 11.18**<br>Same-Resource Complete Target | Aktivitas `W_Assess Potential Fraud` complete minimal 2 kali oleh `org:resource` yang sama & teridentifikasi; resource kosong/spasi/None tidak dianggap sama; subset dari 11.15. | `core/lifecycle.py`<br>`core/exercise_1118.py`<br>`gui/panel_1115_1118.py` | **PASS** | Audit penanganan `is_identified_resource`; validasi resource kosong dibuang sebelum pencarian resource sama; per case dihitung sekali. | **PASS** | `test_different_resources_pass_1115_but_fail_1118`, `test_empty_or_null_resources_never_considered_same`, `test_same_identified_resource_passes_both_and_ignores_extra_null` (1 case: App 09 oleh User_4). |
| **F06 — 11.22**<br>Eventually Follows (Cancelled -> Accepted) | Pasangan `O_Cancelled` (posisi $i$) mendahului `O_Accepted` (posisi $j$) dengan $i < j$; tidak harus bertetangga; hitung unique case & persentase terhadap seluruh log. | `core/exercise_1122.py`<br>`gui/panel_1122.py` | **PASS** | Verifikasi formula persentase denominator seluruh case log aktif ($n/\text{total}\times 100\%$); witness position pertama valid. | **PASS** | `tests/test_exercise_1122.py` (8 skenario lulus): non-adjacent lolos, accepted-before-cancelled gagal, multiple pairs dihitung 1x, sample log lolos 3 case (App 01, 03, 04 = 30.0%). |
| **F07**<br>Case Explorer & CSV Export | Penelusuran trace per case, highlighting baris event pembukti, pencarian case ID, export CSV ringkasan seluruh jawaban dan daftar case detail. | `gui/case_explorer.py`<br>`utils/csv_export.py`<br>`gui/panel_export.py` | **PASS** | Integrasi 5 subhasil 11.7 ke selector dropdown Case Explorer dan Export; memastikan header CSV tetap tercipta saat hasil 0 case. | **PASS** | `test_export_summary_and_cases`, `test_export_empty_result_has_header`, `test_gui_smoke.py`, `test_gui_117.py`, `test_gui_1115_1118.py`. |

---

## 2. Status Modul Awal vs. Akhir

1. **`core/cycle_time.py`**
   - *Awal:* Berlabel SEMENTARA, hanya 2 fungsi sederhana tanpa penanganan edge cases atau timezone-safe difference.
   - *Perbaikan:* Difinalkan dengan penanganan empty cases (mengembalikan `None`), 1 event / same timestamp = `0.0` hari, fungsi pendukung `mean_cycle_days_for_cases`. Mempertahankan kompatibilitas 100% dengan API lama.
2. **`core/exercise_117.py`**
   - *Awal:* **Belum ada sama sekali**.
   - *Perbaikan:* Dibuat lengkap mencakup `exercise_117_a`, `exercise_117_b`, `exercise_117_c`, `exercise_117_d`, `exercise_117_e`, dan `exercise_117_all`. Mengembalikan dict kontrak lengkap dengan evidence, highlight positions, duration days, dan denominator.
3. **`gui/panel_117.py`**
   - *Awal:* **Belum ada**, `main_window.py` menggunakan `PlaceholderPanel`.
   - *Perbaikan:* Dibuat lengkap mewarisi `AnalysisPanelBase`, menyediakan 5 kartu ringkasan di atas, 5 tab rincian (A, B, C, D, E) dengan tabel yang bisa dicari, tombol Buka di Case Explorer, tombol Run/Reset, dan memancarkan 5 signal `result_ready` terpisah.
4. **`run_tests.py`**
   - *Awal:* Parameter `--unit` hanya mengabaikan 2 test GUI lama (`test_gui_smoke.py` dan `test_gui_1115_1118.py`).
   - *Perbaikan:* Menambahkan pengabaian `test_gui_117.py` dan pola `test_gui_*.py` agar pengujian unit murni tetap berjalan bersih tanpa ketergantungan GUI.
5. **`tests/test_exercise_117.py` & `tests/test_gui_117.py`**
   - *Awal:* Belum ada pengujian untuk 11.7.
   - *Perbaikan:* Dibuat unit test mendalam dan uji integrasi GUI offscreen. Seluruh 39 test lulus 100%.
6. **`tools/capture_screenshots.py` & `docs/screenshots/`**
   - *Awal:* Tidak ada screenshot bukti GUI.
   - *Perbaikan:* Dibuat script penangkap screenshot otomatis offscreen dan dihasilkan 11 file screenshot PNG asli dari seluruh menu dan trace kasus bukti.
