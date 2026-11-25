BPIC17 Event Log Analyzer
Aplikasi desktop untuk analisis event log BPI Challenge 2017 menggunakan Python, PM4Py, dan PySide6.

Proyek Tahap 1 · Mata Kuliah Penambangan Data · Universitas Diponegoro

Aplikasi ini membaca berkas XES dan menjawab delapan butir latihan Bab 11 Fundamentals of Business Process Management secara dinamis. Setiap hasil analisis dilengkapi jumlah kasus, aturan filter, dan bukti event yang dapat ditelusuri melalui Case Explorer serta diekspor ke CSV.
Catatan pengujian: Pengujian otomatis terakhir dilaporkan berhasil pada log sintetis sample_data/sample_log.xes. Pengujian akhir menggunakan dataset BPIC17 asli masih diperlukan. Hasil log sampel tidak boleh dianggap sebagai hasil BPIC17 asli.

Fitur utama
Fitur	Kemampuan
F01 · Import XES	Memuat event log melalui PM4Py, memvalidasi atribut, dan menampilkan status pemrosesan.
F02 · Overview	Menampilkan jumlah case dan event, frekuensi aktivitas, rentang waktu, serta rata-rata cycle time.
F03 · Exercise 11.7 A–E	Menghitung total case, rata-rata cycle time, serta kelompok successful, unsuccessful, dan canceled.
F04 · Exercise 11.15	Menemukan case dengan aktivitas W_Assess Potential Fraud berstatus complete minimal dua kali.
F05 · Exercise 11.18	Menemukan case dengan minimal dua penyelesaian aktivitas tersebut oleh resource yang sama.
F06 · Exercise 11.22	Menghitung case saat O_Cancelled diikuti O_Accepted pada posisi event berikutnya, beserta persentasenya.
F07 · Case Explorer & Export	Menelusuri detail trace, menyorot event pembukti, dan mengekspor ringkasan serta daftar case ke CSV.


Seluruh hasil dihitung dari log yang sedang aktif, bukan dari angka yang ditanam langsung di kode (hard-coded).
Instalasi dan menjalankan aplikasi
Persyaratan
- Python 3.11 direkomendasikan.
- pip dan akses instalasi dependensi dari requirements.txt.
- Windows, macOS, atau Linux dengan dukungan GUI Qt.
1. Ambil kode proyek
Gunakan branch finalisasi:
git clone --branch finishing/bpic17-final --single-branch https://github.com/Argafostein/Projek-Penambangan-Data.git
cd Projek-Penambangan-Data
Jika repositori sudah ada, cukup buka folder proyek dan pastikan branch yang dipakai sesuai.
2. Siapkan virtual environment
Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
3. Jalankan
python main.py
Setelah jendela aplikasi terbuka, pilih file .xes melalui menu Dataset & Status.
Cara menggunakan
1. Import log. Pilih sample_data/sample_log.xes untuk mencoba aplikasi atau pilih dataset BPIC17 asli.
2. Lihat Overview. Periksa total case, total event, statistik aktivitas, dan cycle time.
3. Jalankan Exercise. Buka 11.7, 11.15/11.18, atau 11.22 dan jalankan analisis yang diperlukan.
4. Periksa Case Explorer. Pilih case dari hasil analisis untuk melihat urutan event dan bukti filter.
5. Ekspor CSV. Simpan ringkasan hasil serta daftar case terpilih untuk dokumentasi atau pemeriksaan lanjutan.
Dataset
- Untuk uji cepat: sample_data/sample_log.xes (log sintetis bawaan proyek).
- Untuk pengujian akhir: BPI Challenge 2017 di 4TU.ResearchData.
Dataset BPIC17 asli tidak disertakan dalam repositori karena ukuran berkasnya besar. Hasil analisis akan bergantung pada XES yang dipilih saat aplikasi berjalan.
Pengujian
Jalankan dari direktori utama proyek:
# Unit test tanpa pengujian GUI
python run_tests.py --unit

# Semua test, termasuk integrasi GUI
python run_tests.py

# Alternatif langsung menggunakan pytest
python -m pytest -q
Pada laporan pengujian finalisasi sebelumnya, 39 pengujian dilaporkan lulus, tanpa kegagalan atau pengujian yang dilewati. Angka ini adalah hasil yang dilaporkan pada lingkungan pengembangan dan perlu diperiksa kembali saat dijalankan pada komputer lain.

Kasus tepi yang diuji antara lain kategori 11.7 yang dapat tumpang tindih, perbedaan contains dan endpoint, pembatasan complete, resource kosong, serta urutan event yang tidak harus bersebelahan.
Struktur proyek
Projek-Penambangan-Data/
├── core/                       # Pembacaan log, cycle time, dan logika Exercise
│   ├── log_loader.py
│   ├── overview.py
│   ├── cycle_time.py
│   ├── lifecycle.py
│   ├── exercise_117.py
│   ├── exercise_1115.py
│   ├── exercise_1118.py
│   └── exercise_1122.py
├── gui/                        # Jendela utama, panel Exercise, dan Case Explorer
│   ├── main_window.py
│   ├── panel_117.py
│   ├── panel_1115_1118.py
│   ├── panel_1122.py
│   └── case_explorer.py
├── utils/                      # Ekspor CSV dan utilitas pendukung
├── tests/                      # Pengujian unit dan integrasi
├── tools/                      # Skrip bantu
├── sample_data/                # Log sintetis untuk demonstrasi
├── docs/                       # Audit, laporan, hasil pengujian, dan panduan demo
├── main.py                     # Titik masuk aplikasi
├── run_tests.py                # Test runner
├── requirements.txt            # Dependensi Python
└── README.md
Aturan analisis penting
Exercise	Aturan
11.7 C / D	Case dipilih jika mengandung O_Accepted / O_Refused. Kedua kelompok tidak harus saling eksklusif.
11.7 E	Case lolos hanya jika event terakhir pada trace adalah O_Cancelled.
11.15	Hanya kejadian W_Assess Potential Fraud berstatus complete yang dihitung.
11.18	Minimal dua complete dalam case yang sama harus berasal dari resource identik yang teridentifikasi.
11.22	Harus ada O_Cancelled pada posisi lebih awal daripada O_Accepted. Keduanya tidak harus bersebelahan.


Cycle time dihitung dari selisih timestamp terbesar dan terkecil pada seluruh event dalam satu case. Penyaringan case tidak boleh memangkas trace untuk perhitungan durasi.
Tim pengembang
Anggota	Tanggung jawab utama
Ida Bagus	Import XES, Overview, Exercise 11.22, Case Explorer, ekspor CSV, dan navigasi utama.
Arga	Exercise 11.15 dan 11.18, pemeriksaan lifecycle/resource, serta pengujian terkait.
Lintang	Exercise 11.7 A–E, perhitungan cycle time, panel analisis, dan pengujian terkait.
Bersama	Integrasi, validasi, dokumentasi, dan demonstrasi aplikasi.


Pembagian di atas menunjukkan area tanggung jawab, bukan klaim bahwa satu anggota mengerjakan seluruh perubahan dalam area tersebut secara mandiri.
Dokumentasi
Dokumen pendukung proyek tersedia dalam folder docs/, antara lain:
- [`AUDIT_FINAL_BPIC17.md`](docs/AUDIT_FINAL_BPIC17.md): hasil audit fitur dan kebutuhan.
- [`LAPORAN_FINAL_TAHAP1.md`](docs/LAPORAN_FINAL_TAHAP1.md): laporan teknis proyek.
- [`TEST_REPORT.md`](docs/TEST_REPORT.md): ringkasan pengujian.
- [`DEMO_CHECKLIST.md`](docs/DEMO_CHECKLIST.md): alur demonstrasi aplikasi.
Dokumen di atas merujuk pada struktur yang dilaporkan untuk branch finalisasi. Pastikan berkas tersebut tersedia pada branch yang dibuka.
Batasan proyek
Proyek Tahap 1 berfokus pada pembacaan event log, filtering, metrik berbasis case, dan penelusuran bukti. Alpha Miner, Heuristics Miner, Inductive Miner, dan penemuan Petri net tidak termasuk cakupan tugas ini.
