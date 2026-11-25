# BPIC17 Event Log Analyzer — Proyek Penambangan Data Tahap 1

**Aplikasi Desktop Analisis Event Log BPIC17 Menggunakan Python, PM4Py, dan PySide6**<br>
**Status Integrasi:** **100% Selesai & Teruji** (Seluruh Fitur F01–F07 dan 8 Butir Latihan 11.7 A–E, 11.15, 11.18, 11.22)<br>
**Anggota Tim:** Ida Bagus, Arga, Lintang<br>
*Dasar Acuan:* Instruksi Proyek Tahap 1 — Analisis Soal BPIC17 PM4Py, versi 16 November 2026.

---

## 1. Ringkasan & Arsitektur Aplikasi

Aplikasi ini adalah sistem analisis proses bisnis desktop yang memproses event log standar XES menggunakan pustaka Process Mining **PM4Py** dan framework GUI **PySide6**. Seluruh perhitungan dihitung secara dinamis dari file event log aktif tanpa hard-coding, mencakup validasi data, ringkasan statistik proses, pemfilteran kasus dengan bukti baris event (*witness evidence*), penelusuran trace dengan penyorotan warna (*highlighting*), serta ekspor hasil ke format CSV standar.

### Fitur Utama (F01–F07)
- **F01 — Impor & Validasi XES (Ida Bagus):** Memilih file `.xes` / `.xes.gz` lewat dialog GUI, memvalidasi atribut wajib (`case:concept:name`, `concept:name`, `time:timestamp`), mendeteksi atribut opsional (`lifecycle:transition`, `org:resource`), serta memproses data secara asinkron di background thread agar GUI tidak membeku.
- **F02 — Overview Statistik Proses (Ida Bagus & Lintang):** Menampilkan total kasus unik, total event, frekuensi aktivitas, rentang waktu, dan rata-rata *cycle time* (hari), dilengkapi tabel daftar kasus dan pencarian instan.
- **F03 — Exercise 11.7 A–E (Lintang):**
  - **11.7 A:** Jumlah keseluruhan kasus unik.
  - **11.7 B:** Rata-rata cycle time seluruh kasus (hari) dengan denominator total kasus.
  - **11.7 C:** Jumlah kasus sukses (mengandung $\ge 1$ `O_Accepted`) dan rata-rata cycle time trace lengkapnya.
  - **11.7 D:** Jumlah kasus gagal (mengandung $\ge 1$ `O_Refused`) dan rata-rata cycle time trace lengkapnya.
  - **11.7 E:** Jumlah kasus dibatalkan (event paling akhir pada trace adalah `O_Cancelled`) dan rata-rata cycle time trace lengkapnya.
- **F04 — Exercise 11.15 (Arga):** Deteksi kasus di mana aktivitas `W_Assess Potential Fraud` berstatus `complete` minimal 2 kali (status non-complete seperti `schedule`, `start`, `abort` diabaikan).
- **F05 — Exercise 11.18 (Arga):** Deteksi kasus di mana aktivitas `W_Assess Potential Fraud` diselesaikan minimal 2 kali oleh `org:resource` yang sama dan teridentifikasi (nilai kosong/null tidak dianggap sama).
- **F06 — Exercise 11.22 (Ida Bagus):** Deteksi kasus dengan pola urutan *eventually follows* di mana `O_Cancelled` mendahului `O_Accepted`, menghitung jumlah kasus lolos dan persentase terhadap seluruh log aktif.
- **F07 — Case Explorer & Ekspor CSV (Ida Bagus):** Penelusuran trace kronologis event per kasus dengan penyorotan baris bukti (kuning), pencarian kasus, serta ekspor CSV ringkasan seluruh metrik dan detail kasus terpilih.

---

## 2. Struktur Direktori Proyek

```
Projek-Penambangan-Data/
├── main.py                     # Titik masuk utama aplikasi (GUI Launcher)
├── run_tests.py                # Test runner otomatis (--unit atau full test)
├── pytest.ini                  # Konfigurasi pengujian pytest
├── requirements.txt            # Dependensi pustaka Python
├── README.md                   # Dokumentasi utama proyek
├── core/                       # Logika bisnis & pemrosesan data
│   ├── log_loader.py           # F01: Impor & validasi XES dengan PM4Py, kelas LogData
│   ├── overview.py             # F02: Statistika deskriptif proses log
│   ├── cycle_time.py           # F02/F03: Helper cycle time case (hari) & mean
│   ├── exercise_117.py         # F03: Perhitungan lengkap 11.7 A, B, C, D, E
│   ├── lifecycle.py            # F04/F05: Inspeksi lifecycle transition & resource
│   ├── exercise_1115.py        # F04: Analisis W_Assess Potential Fraud complete >= 2x
│   ├── exercise_1118.py        # F05: Analisis complete >= 2x oleh resource sama
│   └── exercise_1122.py        # F06: Analisis O_Cancelled mendahului O_Accepted
├── gui/                        # Antarmuka desktop PySide6
│   ├── main_window.py          # Jendela utama, navigasi stack, dan perekat modul
│   ├── panel_base.py           # Kontrak dasar panel analisis (AnalysisPanelBase)
│   ├── panel_dataset.py        # Panel Dataset & Status impor
│   ├── panel_overview.py       # Panel Overview statistik proses
│   ├── panel_117.py            # Panel Exercise 11.7 A-E (kartu metrik & 5 tab rincian)
│   ├── panel_1115_1118.py      # Panel Exercise 11.15 & 11.18 (tab terpisah & filter)
│   ├── panel_1122.py           # Panel Exercise 11.22 (metrik, persentase & witness table)
│   ├── case_explorer.py        # Panel Case Explorer penelusur jejak event & highlight
│   ├── panel_export.py         # Panel Ekspor hasil ke CSV
│   ├── widgets.py              # Komponen tabel pencarian dan kartu metrik
│   └── workers.py              # Thread worker latar belakang (non-blocking UI)
├── utils/                      # Utilitas pendukung
│   ├── csv_export.py           # Generator CSV ringkasan metrik & daftar kasus
│   └── versions.py             # Pemeriksa versi pustaka terpasang (dialog About)
├── sample_data/                # Dataset pengujian
│   └── sample_log.xes          # Log sintetis representatif edge cases (10 case, 23 event)
├── tests/                      # Rangkaian pengujian otomatis (39 test cases)
│   ├── helpers.py              # Pembuat log sintetis in-memory untuk unit test
│   ├── test_log_loader.py      # Uji loader, validasi atribut, penanganan error file
│   ├── test_overview_export.py # Uji overview dan generator file CSV
│   ├── test_exercise_117.py    # Uji 11.7 A-E, endpoint, overlap, cycle time full trace
│   ├── test_exercise_1115_1118.py # Uji lifecycle, repeat complete, resource handling
│   ├── test_exercise_1122.py   # Uji urutan eventually follows, percentage denominator
│   ├── test_gui_smoke.py       # Uji asap integrasi GUI offscreen (impor -> 11.22 -> explorer)
│   ├── test_gui_117.py         # Uji GUI offscreen panel 11.7 A-E
│   └── test_gui_1115_1118.py   # Uji GUI offscreen panel 11.15 & 11.18
├── tools/                      # Skrip utilitas pengembangan
│   ├── generate_sample_xes.py  # Skrip pembuat sample_log.xes
│   └── capture_screenshots.py  # Skrip otomatisasi pengambilan screenshot GUI asli
└── docs/                       # Dokumentasi laporan pengumpulan
    ├── AUDIT_FINAL_BPIC17.md   # Matriks audit komprehensif F01-F07
    ├── LAPORAN_FINAL_TAHAP1.md # Laporan teknis lengkap proyek Tahap 1
    ├── TEST_REPORT.md          # Laporan eksekusi pengujian & tabel edge cases
    ├── DEMO_CHECKLIST.md       # Panduan demonstrasi 10 langkah dosen
    └── screenshots/            # 11 tangkapan layar nyata antarmuka GUI desktop
```

---

## 3. Persyaratan Sistem & Instalasi

### Kebutuhan Lingkungan:
- **Sistem Operasi:** Windows 10/11, macOS, atau Linux
- **Python:** Versi 3.10 s.d. 3.12 (Diuji pada Python 3.11.9)
- **Pustaka Utama:**
  - `pm4py >= 2.7` (Diuji pada 2.7.23.15)
  - `PySide6 >= 6.6` (Diuji pada 6.12.0)
  - `pandas >= 2.0` (Diuji pada 3.0.6)
  - `numpy >= 1.26` (Diuji pada 2.4.6)
  - `pytest >= 7.4` (Diuji pada 9.2.0)

### Langkah Instalasi:
1. Buka terminal pada folder proyek.
2. Buat virtual environment (opsional namun disarankan):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate          # Windows PowerShell
   # source venv/bin/activate       # Linux / macOS
   ```
3. Pasang seluruh dependensi:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. *(Opsional)* Pasang `r4pm` untuk mempercepat pembacaan file XES besar:
   ```powershell
   python -m pip install r4pm
   ```

---

## 4. Cara Menjalankan Aplikasi & Pengujian

### Menjalankan Aplikasi Desktop:
```powershell
python main.py
```
*Alur Pengoperasian:*
1. Klik **Pilih file .xes...** pada menu *Dataset & Status* dan pilih file XES (mis. `sample_data/sample_log.xes`).
2. Masuk ke menu **Overview** untuk melihat metrik deskriptif dan tabel kasus.
3. Jalankan analisis pada menu **Exercise 11.7**, **Exercise 11.15 & 11.18**, atau **Exercise 11.22**.
4. Klik tombol **Buka di Case Explorer** pada baris kasus manapun untuk meninjau jejak kronologis dan event pembukti ber-highlight kuning.
5. Masuk ke menu **Export** untuk menyimpan ringkasan metrik atau daftar kasus ke file CSV.

### Menjalankan Pengujian Otomatis (*Automated Tests*):
```powershell
# 1. Jalankan seluruh pengujian unit (tanpa membuka GUI)
python run_tests.py --unit

# 2. Jalankan seluruh pengujian (Unit Test + GUI Offscreen Test)
python run_tests.py

# 3. Jalankan via pytest langsung
python -m pytest -v
```

---

## 5. Ringkasan Hasil Analisis pada Dataset Sampel (`sample_log.xes`)

| Latihan / Soal | Hasil Kasus Lolos | Denominator | Rata-rata / Persentase | Bukti Kasus Representatif |
|---|:---:|:---:|:---:|---|
| **11.7 A** | 10 case | 10 case | 10 unique cases | Seluruh 10 case |
| **11.7 B** | 10 case | 10 case | **0.054167 hari** (1.3 jam) | Seluruh 10 case |
| **11.7 C** | 4 case | 10 case | **0.072917 hari** (1.75 jam) (40.0%) | `Application_01`, `02`, `03`, `04` |
| **11.7 D** | 1 case | 10 case | **0.041667 hari** (1.0 jam) (10.0%) | `Application_06` |
| **11.7 E** | 3 case | 10 case | **0.041667 hari** (1.0 jam) (30.0%) | `Application_02`, `03`, `05` |
| **11.15** | 3 case | 10 case | 3 unique cases (30.0%) | `Application_08`, `09`, `10` |
| **11.18** | 1 case | 10 case | 1 unique case (10.0%) | `Application_09` (User_4, 2x) |
| **11.22** | 3 case | 10 case | **30.00%** (3/10 case) | `Application_01`, `03`, `04` |

---

## 6. Pembagian Kontribusi & Tanggung Jawab Tim

- **Ida Bagus (30%):** Penanggung jawab F01 (Import/Validasi XES), F02 (Overview), F06 (Exercise 11.22), F07 (Case Explorer & CSV Export), serta arsitektur dan navigasi GUI utama.
- **Arga (30%):** Penanggung jawab F04 (Exercise 11.15 repeated complete), F05 (Exercise 11.18 same-resource complete), inspeksi aturan status lifecycle XES dan filter resource teridentifikasi, GUI 11.15/11.18, serta konfigurasi test runner.
- **Lintang (30%):** Penanggung jawab F03 (seluruh Exercise 11.7 A, B, C, D, E), standarisasi helper *cycle time* trace lengkap dalam satuan hari, GUI panel 11.7 (kartu ringkasan dan 5 tab rincian), serta pengujian unit terkait.
- **Bersama (10%):** Desain kontrak data terpadu, integrasi antarmuka lintas-modul, pengujian regresi menyeluruh, penyusunan dokumentasi laporan, tangkapan layar GUI, dan persiapan materi demonstrasi dosen.

*Catatan Administratif:* Format kelompok berjumlah 3 mahasiswa ini dikonfirmasi ke dosen penguji saat sesi pengumpulan, dengan pemenuhan 100% seluruh kriteria rubrik teknis Tahap 1.
