# LAPORAN FINAL PROYEK PENAMBANGAN DATA — TAHAP 1
**Analisis Event Log BPIC17 Menggunakan Python, PM4Py, dan GUI Desktop PySide6**

**Kelompok:** 3 Orang (Ida Bagus, Arga, Lintang)  
*Catatan Administratif:* Instruksi dosen hal. 1–2 menyebutkan kelompok 4 orang. Karena kelompok ini berjumlah 3 orang, izin dosen perlu dikonfirmasi saat pengumpulan tanpa mengurangi cakupan pekerjaan (seluruh F01–F07 dan seluruh subsoal 11.7, 11.15, 11.18, 11.22 diselesaikan 100%).

---

## 1. Latar Belakang & Deskripsi Proyek

Proyek ini bertujuan membangun aplikasi desktop berbasis GUI yang terintegrasi untuk mengeksplorasi dan menganalisis event log proses bisnis BPI Challenge 2017 (BPIC17) menggunakan pustaka Process Mining **PM4Py** dan framework antarmuka desktop **PySide6**.

Aplikasi dirancang agar seluruh analisis berjalan dinamis dari file event log `.xes` yang diimpor pengguna tanpa hard-coding angka, dengan kemampuan:
1. Validasi dan pemuatan dataset secara asinkron (background thread worker) agar antarmuka tidak membeku (*non-blocking UI*).
2. Penyajian ringkasan statistik proses (Overview).
3. Eksekusi 8 butir soal analisis proses bisnis:
   - **Exercise 11.7 A–E:** Analisis jumlah kasus unik dan *cycle time* (keseluruhan, sukses/`O_Accepted`, gagal/`O_Refused`, dibatalkan/`O_Cancelled` di akhir trace).
   - **Exercise 11.15:** Deteksi kasus dengan aktivitas *fraud assessment* (`W_Assess Potential Fraud`) yang selesai (*complete*) berulang (minimal 2 kali).
   - **Exercise 11.18:** Deteksi kasus fraud assessment yang diselesaikan minimal 2 kali oleh sumber daya (*resource*) yang identik dan teridentifikasi.
   - **Exercise 11.22:** Verifikasi aturan urutan waktu (*eventually follows*) di mana `O_Cancelled` mendahului `O_Accepted`.
4. Pelacakan bukti kasus hingga baris event spesifik (*Case Explorer*) dengan penyorotan baris pembukti (*highlighting*).
5. Ekspor data terstruktur ke format CSV (ringkasan metrik dan detail kasus).

---

## 2. Pemetaan Soal, Fungsi, Formula, dan Definisi Operasional Filter

| Soal | Fungsi Backend | Definisi Operasional & Aturan Filter | Formula / Metode |
|---|---|---|---|
| **F01** | `core.log_loader.load_log` | Validasi atribut wajib XES (`case:concept:name`, `concept:name`, `time:timestamp`). Normalisasi atribut opsional (`lifecycle:transition`, `org:resource`). Nilai string kosong/spasi dikonversi menjadi `NaN`. | PM4Py `read_xes()`, mapping kolom standar, penetapan urutan asli trace (`position`, 1-based). |
| **F02** | `core.overview.compute_overview` | Ringkasan metrik log aktif: total unique case, total event, distribusi aktivitas, rentang timestamp, dan rata-rata cycle time seluruh log dalam hari. | Durasi per case = $\max(t) - \min(t)$ pada trace lengkap; $\text{Mean} = \frac{\sum \text{durasi}}{N}$. |
| **11.7 A** | `core.exercise_117.exercise_117_a` | Menghitung seluruh case unik yang terdapat pada event log aktif. | $N_{\text{cases}} = |\text{unique}(\text{case\_id})|$. |
| **11.7 B** | `core.exercise_117.exercise_117_b` | Menghitung rata-rata cycle time seluruh kasus pada log aktif. Denominator ditampilkan eksplisit. | $\text{Mean} = \frac{\sum_{i=1}^{N} (\max(t_i) - \min(t_i))}{N}$ (dalam hari). Kasus 1 event = 0.0 hari. |
| **11.7 C** | `core.exercise_117.exercise_117_c` | Kasus sukses: mengandung minimal satu event `O_Accepted`. Tidak saling eksklusif dengan 11.7 D. | Kemunculan berulang dalam 1 case dihitung 1 case unik. Cycle time dihitung dari **trace lengkap** kasus tersebut, bukan subset event. |
| **11.7 D** | `core.exercise_117.exercise_117_d` | Kasus gagal: mengandung minimal satu event `O_Refused`. Tidak saling eksklusif dengan 11.7 C. | Kemunculan berulang dalam 1 case dihitung 1 case unik. Cycle time dihitung dari **trace lengkap** kasus tersebut. |
| **11.7 E** | `core.exercise_117.exercise_117_e` | Kasus dibatalkan: event **paling akhir** dalam trace asli adalah `O_Cancelled`. Kemunculan di tengah tidak dihitung. | Identifikasi event dengan `position` terbesar per case. Filter $\text{activity}_{\text{last}} = \text{"O\_Cancelled"}$. Full case cycle time. |
| **11.15** | `core.exercise_1115.exercise_1115` | Kasus dengan aktivitas `W_Assess Potential Fraud` berstatus `complete` minimal 2 kali. Status non-complete (`schedule`, `start`, `abort`, kosong) tidak dihitung. | Filter mask: `(activity == "W_Assess Potential Fraud") & (lifecycle == "complete")`. Hitung unique case dengan count $\ge 2$. |
| **11.18** | `core.exercise_1118.exercise_1118` | Kasus dengan `W_Assess Potential Fraud` berstatus `complete` minimal 2 kali oleh `org:resource` yang sama dan teridentifikasi. | Filter resource teridentifikasi: bukan None, bukan NaN, bukan string kosong/spasi. Groupby `(case_id, resource)`. Lolos jika ada resource dengan count $\ge 2$. |
| **11.22** | `core.exercise_1122.exercise_1122` | Adanya pasangan urutan `O_Cancelled` (posisi $i$) diikuti kemudian oleh `O_Accepted` (posisi $j$) dengan $i < j$. | Cari $\min(i)$ untuk `O_Cancelled`, cari $\min(j > \min(i))$ untuk `O_Accepted`. Persentase = $\frac{\text{case lolos}}{\text{seluruh unique case log aktif}} \times 100\%$. |

---

## 3. Representasi Lifecycle & Resource pada XES

Berdasarkan analisis arsitektur data event log BPIC17:
1. **Lifecycle Transition:** Status pelaksanaan aktivitas dicatat pada tag `<string key="lifecycle:transition" value="..."/>`.
   - Modul `core/lifecycle.py` melakukan inspeksi ketat: hanya nilai `"complete"` (case-insensitive setelah `strip()`) yang diakui sebagai event selesai.
   - Status non-complete seperti `schedule`, `scheduled`, `start`, `suspend`, `resume`, `ate_abort`, `pi_abort`, `withdraw`, maupun tag yang tidak memuat lifecycle diperlakukan sebagai **non-complete** dan **tidak dihitung** pada Exercise 11.15 maupun 11.18.
2. **Resource Identification:** Dicatat pada tag `<string key="org:resource" value="..."/>`.
   - Resource kosong (`""`), spasi (`"   "`), atau `None`/`NaN` disaring melalui fungsi `is_identified_resource()`.
   - **Prinsip Utama:** Dua event dengan resource kosong **tidak pernah dianggap sama**. Resource harus teridentifikasi secara eksplisit (contoh: `User_4`).

---

## 4. Hasil Aktual pada Dataset Uji (`sample_data/sample_log.xes`)

Pengujian dilakukan menggunakan event log `sample_data/sample_log.xes` yang memuat 10 kasus sintetis representatif edge cases:

| Butir Soal | Kasus Lolos / Pembilang | Denominator / Basis | Nilai / Rata-rata / Persentase | Kasus Bukti (*Witness Evidence*) |
|---|:---:|:---:|:---:|---|
| **11.7 A** | 10 case | 10 case | 10 unique cases | `Application_01` s.d. `Application_10` |
| **11.7 B** | 10 case | 10 case | **0.054167 hari** (13/240 hari) | Seluruh 10 case (durasi total 13 jam) |
| **11.7 C** | 4 case | 10 case | **0.072917 hari** (7/96 hari) (40.0%) | `Application_01`, `02`, `03`, `04` |
| **11.7 D** | 1 case | 10 case | **0.041667 hari** (1/24 hari) (10.0%) | `Application_06` |
| **11.7 E** | 3 case | 10 case | **0.041667 hari** (1/24 hari) (30.0%) | `Application_02`, `03`, `05` |
| **11.15** | 3 case | 10 case | 3 unique cases (30.0%) | `Application_08` (2x), `Application_09` (2x), `Application_10` (2x) |
| **11.18** | 1 case | 10 case | 1 unique case (10.0%) | `Application_09` (2x oleh `User_4`) |
| **11.22** | 3 case | 10 case | **30.00%** (3/10 case) | `Application_01` (pos 1 -> 3), `Application_03` (pos 1 -> 2), `Application_04` (pos 2 -> 3) |

### Analisis Kasus Spesifik (*Edge Cases Evidence*):
- **`Application_01`:** Memiliki `O_Cancelled` di urutan ke-1 dan `O_Accepted` di urutan ke-3 (diselingi `W_Call after offers` di urutan ke-2). Lolos 11.22 (tidak harus bertetangga) dan lolos 11.7 C.
- **`Application_02`:** Memiliki `O_Accepted` di urutan ke-1 dan `O_Cancelled` di urutan ke-2. Gagal 11.22 (karena accepted mendahului cancelled), tetapi lolos 11.7 C dan lolos 11.7 E (karena event terakhir tepat `O_Cancelled`).
- **`Application_05`:** Hanya memiliki 1 event (`O_Cancelled` di urutan ke-1). Durasinya tepat 0.0 hari. Lolos 11.7 E karena event tunggal tersebut sekaligus merupakan event terakhir.
- **`Application_07`:** Memiliki 2 event `schedule` dan 1 event `complete` untuk `W_Assess Potential Fraud`. Gagal 11.15 dan gagal 11.18 karena status `schedule` tidak dihitung.
- **`Application_08`:** Memiliki 2 event `complete` oleh `User_4` dan `User_5`. Lolos 11.15, namun **gagal 11.18** karena resource berbeda.
- **`Application_09`:** Memiliki 2 event `complete` oleh `User_4` dan `User_4`. **Lolos 11.15 dan lolos 11.18** (same identified resource).
- **`Application_10`:** Memiliki 2 event `complete` dengan `org:resource` kosong (`None`). Lolos 11.15, namun **gagal 11.18** karena nilai null/kosong tidak dianggap resource identik.

---

## 5. Status Pengujian Dataset BPIC17 Asli

> **Laporan Transparan:**  
> File arsip ZIP yang diaudit hanya memuat `sample_data/sample_log.xes` (file log penuh `BPI Challenge 2017.xes` berukuran ~550 MB tidak disertakan dalam bundle pengiriman).  
> Oleh karena itu, pengujian pada dataset asli BPIC17 berstatus: **Belum Diuji Langsung pada Lingkungan Ini**.  
> Aplikasi siap digunakan untuk membuka file BPIC17 asli kapan saja melalui tombol **Buka file XES...**, di mana seluruh modul menggunakan pemrosesan vektor Pandas dan background thread untuk menangani data besar.

---

## 6. Verifikasi Pengujian Otomatis (*Test Suite*)

Seluruh pengujian dijalankan dan diverifikasi melalui dua runner resmi:
1. `python run_tests.py --unit`: Menjalankan 36 unit test core logika bisnis. **Status: 36 Passed (100%)**.
2. `python run_tests.py`: Menjalankan seluruh 39 test (36 unit test + 3 test GUI offscreen). **Status: 39 Passed (100%)**.

Semua pengujian deterministik, memverifikasi struktur output, penanganan error, ketepatan formula, dan invariansi trace.

---

## 7. Bukti Tangkapan Layar GUI (*Screenshots*)

Screenshot asli dari antarmuka aplikasi desktop PySide6 telah diambil secara otomatis menggunakan Qt engine dan disimpan di direktori `docs/screenshots/`:
1. `01_dataset_status.png` — Tampilan panel Dataset & Status setelah log berhasil dimuat (menampilkan nama berkas, 10 case, 23 event, status atribut XES).
2. `02_overview.png` — Tampilan dashboard Overview (kartu metrik total case, total event, mean cycle time 0.0542 hari, tabel frekuensi aktivitas, tabel durasi kasus).
3. `03_exercise_117_c.png` — Tampilan panel Exercise 11.7 pada Tab C (Successful cases dengan filter `O_Accepted`, kartu metrik, dan tabel trace duration).
4. `03_exercise_117_e.png` — Tampilan panel Exercise 11.7 pada Tab E (Canceled cases dengan endpoint `O_Cancelled`, kartu metrik, dan tabel trace duration).
5. `04_exercise_1115.png` — Tampilan panel Exercise 11.15 (banner deteksi lifecycle XES, kartu 3 case lolos, filter spinbox minimal complete).
6. `05_exercise_1118.png` — Tampilan panel Exercise 11.18 (kartu 1 case lolos `User_4`, kartu 2 case gugur karena resource beda/kosong, filter pencarian resource ID).
7. `06_exercise_1122.png` — Tampilan panel Exercise 11.22 (kartu pembilang 3 case, denominator 10 case, persentase 30.00%, formula penjelasan, tabel witness pair).
8. `07_case_explorer_1115.png` — Tampilan Case Explorer menelusuri `Application_08` untuk Exercise 11.15.
9. `08_case_explorer_1118.png` — Tampilan Case Explorer menelusuri `Application_09` untuk Exercise 11.18 dengan event `complete` oleh `User_4` disorot kuning.
10. `09_case_explorer_1122.png` — Tampilan Case Explorer menelusuri `Application_01` untuk Exercise 11.22 dengan event `O_Cancelled` dan `O_Accepted` disorot kuning.
11. `10_export_panel.png` — Tampilan panel Export CSV ringkasan seluruh jawaban dan export detail kasus.

---

## 8. Pembagian Kontribusi Anggota Tim

| Anggota Tim | Fitur & Tanggung Jawab Utama | Kontribusi Riil Kode / Modul |
|---|---|---|
| **Ida Bagus** | F01 (Import/Validasi XES), F02 (Overview), F06 (Exercise 11.22), F07 (Case Explorer & CSV Export), Integrasi GUI Utama | `core/log_loader.py`, `core/overview.py`, `core/exercise_1122.py`, `gui/main_window.py`, `gui/panel_dataset.py`, `gui/panel_overview.py`, `gui/panel_1122.py`, `gui/case_explorer.py`, `gui/panel_export.py`, `utils/csv_export.py` |
| **Arga** | F04 (Exercise 11.15), F05 (Exercise 11.18), Audit Lifecycle & Resource Identification, Test Runner Otomatis | `core/lifecycle.py`, `core/exercise_1115.py`, `core/exercise_1118.py`, `gui/panel_1115_1118.py`, `tests/test_exercise_1115_1118.py`, `tests/test_gui_1115_1118.py`, `docs/LAPORAN_ARGA_1115_1118.md` |
| **Lintang** | F03 (Exercise 11.7 A–E), Standardisasi & Finalisasi Perhitungan Cycle Time Kasus | `core/cycle_time.py`, `core/exercise_117.py`, `gui/panel_117.py`, `tests/test_exercise_117.py`, `tests/test_gui_117.py` |
| **Bersama** | QA & Validasi E2E, Cross-module Testing, Dokumentasi Pengumpulan Final | `run_tests.py`, `tools/capture_screenshots.py`, `docs/AUDIT_FINAL_BPIC17.md`, `docs/LAPORAN_FINAL_TAHAP1.md`, `docs/TEST_REPORT.md`, `docs/DEMO_CHECKLIST.md` |
