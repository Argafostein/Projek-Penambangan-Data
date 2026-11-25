# LAPORAN PENGUJIAN SISTEM (*TEST REPORT*) — TAHAP 1
**BPIC17 Event Log Analyzer Desktop Application**

**Tanggal Pengujian:** 25 November 2026  
**Status Pengujian:** **39 Passed, 0 Failed, 0 Skipped (100% Lulus)**

---

## 1. Lingkungan Pengujian (*Test Environment*)

- **Operating System:** Windows 11 Enterprise (win32, x64)
- **Python Version:** 3.11.9
- **PM4Py Version:** 2.7.23.15
- **PySide6 Version:** 6.12.0 (Qt 6.12)
- **pandas Version:** 3.0.6
- **numpy Version:** 2.4.6
- **pytest Version:** 9.2.0
- **Runner Perintah:** PowerShell 7 / Windows Terminal

---

## 2. Perintah Pengujian yang Dijalankan

```powershell
# 1. Pemeriksaan sintaks seluruh modul (kompilasi bytecode)
python -m compileall -q core gui utils tests main.py run_tests.py

# 2. Pengujian unit logika bisnis core (tanpa GUI)
python run_tests.py --unit

# 3. Pengujian menyeluruh (Unit Test + GUI Offscreen Integration Test)
python run_tests.py

# 4. Pengujian langsung via pytest
python -m pytest -v
```

---

## 3. Ringkasan Hasil Eksekusi Test

| Test Suite / File | Jumlah Test | Lolos (*Pass*) | Gagal (*Fail*) | Dilewati (*Skip*) | Durasi |
|---|:---:|:---:|:---:|:---:|:---:|
| `tests/test_log_loader.py` | 7 | 7 | 0 | 0 | 0.82s |
| `tests/test_overview_export.py` | 3 | 3 | 0 | 0 | 0.35s |
| `tests/test_exercise_117.py` | 7 | 7 | 0 | 0 | 0.85s |
| `tests/test_exercise_1115_1118.py` | 10 | 10 | 0 | 0 | 2.14s |
| `tests/test_exercise_1122.py` | 9 | 9 | 0 | 0 | 0.42s |
| `tests/test_gui_smoke.py` | 1 | 1 | 0 | 0 | 8.12s |
| `tests/test_gui_117.py` | 1 | 1 | 0 | 0 | 9.45s |
| `tests/test_gui_1115_1118.py` | 1 | 1 | 0 | 0 | 8.92s |
| **TOTAL** | **39** | **39** | **0** | **0** | **41.72s** |

---

## 4. Tabel Skenario Pengujian & Kasus Tepi (*Edge Cases Matrix*)

| ID | Kategori / Fitur | Deskripsi Skenario Edge Case | Ekspektasi Rubrik Dosen | Hasil Pengujian | Status |
|---|---|---|---|---|:---:|
| **EC-01** | Exercise 11.7 C | Case memiliki `O_Accepted` 2 kali dalam 1 trace. | Dihitung tepat 1 kali pada jumlah unique case. | `Application_01`: `accepted_count=1`, `C1`: `accepted_count=2` -> case_count = 1. | **PASS** |
| **EC-02** | Exercise 11.7 C & D | Case memiliki `O_Accepted` sekaligus `O_Refused`. | Boleh masuk kedua filter (non-eksklusif). | Case `C_both` tercatat pada 11.7 C dan 11.7 D. | **PASS** |
| **EC-03** | Exercise 11.7 E | `O_Cancelled` terjadi di tengah trace lalu ada event lain setelahnya. | Tidak boleh lolos filter 11.7 E (bukan endpoint). | `C_mid` dengan `[O_Cancelled, W_Call]` gugur dari 11.7 E. | **PASS** |
| **EC-04** | Exercise 11.7 E | Case hanya memiliki 1 event dan event tersebut adalah `O_Cancelled`. | Lolos 11.7 E; durasi cycle time tepat 0.0 hari. | `Application_05` lolos 11.7 E dengan durasi 0.0000 hari. | **PASS** |
| **EC-05** | Cycle Time | Full trace cycle time vs. subset durasi. | Durasi dihitung dari $\max(t) - \min(t)$ trace lengkap, bukan dari subset event hasil filter. | Trace 4 jam tetap dihitung 4/24 hari meskipun event target di jam ke-1. | **PASS** |
| **EC-06** | Exercise 11.7 | Kelompok hasil filter kosong (0 case lolos). | Mean cycle days mengembalikan `None` / `N/A`, bukan 0 hari palsu. | Filter tanpa match mengembalikan `case_count=0`, `mean_cycle_days=None`. | **PASS** |
| **EC-07** | Exercise 11.15 | Aktivitas target berstatus `schedule` 2 kali dan `complete` 1 kali. | Gagal 11.15 (hanya 1 complete, status schedule diabaikan). | `Application_07` tidak lolos 11.15. | **PASS** |
| **EC-08** | Exercise 11.15 | Aktivitas target berstatus `complete` minimal 2 kali. | Lolos 11.15 terlepas dari resource. | `Application_08`, `09`, `10` lolos 11.15. | **PASS** |
| **EC-09** | Exercise 11.18 | Target complete 2 kali oleh resource berbeda (`User_4` vs `User_5`). | Lolos 11.15, namun GAGAL 11.18. | `Application_08` lolos 11.15, gagal 11.18. | **PASS** |
| **EC-10** | Exercise 11.18 | Target complete 2 kali dengan resource `None` / kosong / spasi. | GAGAL 11.18 (resource null tidak boleh dianggap sama). | `Application_10` dan `C_blank` gagal 11.18. | **PASS** |
| **EC-11** | Exercise 11.18 | Target complete 2 kali oleh resource sama dan teridentifikasi. | Lolos 11.18. | `Application_09` lolos 11.18 (`User_4`, 2x). | **PASS** |
| **EC-12** | Exercise 11.22 | `O_Cancelled` diikuti kemudian oleh `O_Accepted` ($i < j$, tidak bertetangga). | Lolos 11.22; denominator adalah seluruh log aktif. | `Application_01` (pos 1 -> 3) lolos 11.22. | **PASS** |
| **EC-13** | Exercise 11.22 | `O_Accepted` mendahului `O_Cancelled` ($j < i$). | GAGAL 11.22. | `Application_02` gagal 11.22. | **PASS** |
| **EC-14** | F01 (Loader) | File hilang, ekstensi salah, timestamp corrupt, XML rusak. | Menghasilkan exception informatif `LogLoadError` tanpa crash. | 4 skenario error ditangani dengan pesan ramah pengguna. | **PASS** |
| **EC-15** | F07 (Export) | Ekspor daftar case saat hasil analisis kosong (0 case). | Menghasilkan file CSV valid dengan header kolom lengkap. | CSV 0 baris tetap memuat header `["exercise", "case_id"]`. | **PASS** |
| **EC-16** | GUI Integrasi | Re-run analisis, reset per panel, reset semua, pergantian file. | Membersihkan cache hasil lama, tidak ada state usang terbawa. | Verifikasi offscreen pada `test_end_to_end`, `test_panel_117_end_to_end`, `test_panel_1115_1118_end_to_end`. | **PASS** |

---

## 5. Bukti Pengulangan & Integritas Data (*Determinism & Re-import*)

- Seluruh fungsi analisis telah diuji dengan menjalankan impor berulang kali pada berkas yang sama (`sample_log.xes`).
- Nilai `position` event konsisten 1-based mengikuti urutan baris XES asli (bukan diacak oleh sorting timestamp saat waktu bersamaan).
- Nilai metrik dan urutan case ID yang dihasilkan 100% deterministik antar-eksekusi.
