# PEMBAGIAN TUGAS PROYEK TAHAP 1 — BPIC17 & PM4Py

**Proyek:** Aplikasi Desktop untuk Analisis Event Log BPIC17  
**Teknologi wajib:** Python, PM4Py, GUI desktop  
**Anggota:** Ida Bagus, Arga, Lintang  
**Dasar:** *Instruksi Proyek Tahap 1 — Analisis Soal BPIC17 PM4Py*, versi 16 November 2026, 8 halaman.  
**Status dokumen:** Pembagian kerja internal 3 orang — bukan perubahan instruksi dosen.

> **Penting sebelum mulai:** Dokumen dosen menyebut kelompok terdiri dari **4 mahasiswa** (hal. 1–2). Karena kelompok ini berisi **3 orang**, pastikan susunan anggota sudah disetujui dosen. Cakupan fitur dan kualitas hasil **tidak boleh dikurangi**. Urutan nama di bawah adalah **urutan penanggung jawab dan alur integrasi**, bukan berarti semua tugas harus dikerjakan satu per satu.

---

## 1. Prinsip pembagian tugas: setara dan tidak tumpang tindih

Bobot rubrik dosen:

| Komponen penilaian | Bobot | Penanggung jawab utama |
|---|---:|---|
| Import & overview (F01–F02) | 10% | **Ida Bagus** |
| Exercise 11.7 A–E (F03) | 30% | **Lintang** |
| Exercise 11.15 (F04) | 15% | **Arga** |
| Exercise 11.18 (F05) | 15% | **Arga** |
| Exercise 11.22 (F06) | 10% | **Ida Bagus** |
| Case Explorer & ekspor (F07) | 10% | **Ida Bagus** |
| Pengujian & dokumentasi | 10% | **Bersama** |
| **TOTAL** | **100%** | |

**Kesetaraan berdasarkan bobot rubrik:** Ida Bagus **30%**, Arga **30%**, Lintang **30%**, dan **10% dikerjakan bersama**. Bobot rubrik **tidak sama dengan estimasi jam coding**: Ida Bagus punya lebih banyak fitur pendukung dan tugas penggabungan, sehingga **Arga dan Lintang wajib membuat GUI modul sendiri serta menguji dan memperbaiki modul masing-masing**. Ida Bagus **bukan** pemrogram GUI untuk seluruh anggota.

**Aturan kepemilikan:**
1. **Satu modul = satu pemilik utama.** Setiap anggota mengerjakan, menguji, dan mendokumentasikan modul miliknya sampai siap dipakai.
2. **Semua angka dihitung dari file XES aktif melalui PM4Py**, bukan hard-coded, bukan menyalin jawaban dari materi, dan bukan dihitung manual untuk ditampilkan sebagai jawaban aplikasi.
3. **Setiap hasil analisis berbasis case/trace**, bukan jumlah event, kecuali metrik memang meminta jumlah event.
4. **Setiap filter mengembalikan daftar case ID dan bukti event.** Jangan hanya menampilkan satu angka.
5. **GUI utama dibuat Ida Bagus; GUI panel analisis dibuat oleh pemilik analisis.**
6. **Semua orang terlibat dalam validasi dan demo.** Tidak ada pembagian “satu orang coding, satu orang cuma laporan”.

---

## 2. IDA BAGUS — Penanggung jawab 1: fondasi aplikasi, 11.22, dan navigasi (30%)

### A. Scope wajib

**F01 — Impor dan validasi XES (10% bersama F02)**
- Buat tombol **Pilih File .xes** dengan file dialog GUI.
- Baca XES menggunakan **PM4Py** dan simpan sebagai **log aktif** yang dapat dipakai modul lain.
- Validasi atribut penting: identitas case, `concept:name`, `time:timestamp`; deteksi `lifecycle:transition` dan `org:resource` apabila tersedia.
- Tampilkan **nama file, berhasil/gagal impor, jumlah case, jumlah event, serta atribut yang ditemukan**.
- Tangani file tidak ditemukan, file rusak, log kosong, timestamp tidak valid, dan atribut wajib tidak ada dengan pesan yang bisa dipahami.
- Berikan **status/progres** saat file diproses. Operasi berat jangan membekukan UI (gunakan worker/thread jika perlu).

**F02 — Overview statistik dasar (termasuk dalam 10% F01–F02)**
- Tampilkan total **unique case**, total event, frekuensi aktivitas, rentang timestamp, dan rata-rata cycle time dalam **hari**.
- Sediakan daftar case dan durasi per case (minimal tabel, idealnya ada pencarian).
- **Wajib memakai fungsi cycle time milik Lintang**, bukan membuat rumus lain yang berpotensi tidak konsisten.
- Jelaskan satuan dan ketelitian/pembulatan angka yang ditampilkan.

**F06 — Exercise 11.22 (10%)**
- Cari **case** yang mengandung event `O_Cancelled` pada posisi **lebih awal**, dan `O_Accepted` pada posisi **lebih akhir**.
- **Tidak wajib berurutan/bersebelahan.** Aktivitas lain boleh ada di antaranya.
- Jangan salah menganggap setiap case yang mengandung kedua aktivitas pasti lolos: **urutan wajib benar**.
- Hitung **jumlah unique case yang lolos**, kemudian **persentase = jumlah case lolos / seluruh case dalam log aktif × 100%**.
- Tampilkan **angka pembilang, denominator, persentase, case ID, dan pasangan event pembukti**, termasuk posisi/timestamp dalam trace.
- Buat **GUI panel Exercise 11.22** sendiri.

**F07 — Case Explorer dan ekspor CSV (10%)**
- Buat satu **Case Explorer bersama** yang menerima daftar case dari hasil setiap latihan.
- Sediakan pencarian case ID, pemilihan case, dan tampilan kronologi event: minimal **timestamp, activity, lifecycle jika ada, resource jika ada**.
- Buat ekspor **CSV ringkasan jawaban** serta **CSV daftar case terpilih/bukti analisis**.
- Sediakan **reset/re-run** tanpa harus membuka kembali file yang sama.
- Jika analisis memiliki hasil kosong, tetap tampilkan hasil 0 dan berikan ekspor yang valid dengan header kolom.

**GUI shell dan integrasi awal (tanggung jawab teknis, bukan penambahan bobot)**
- Siapkan aplikasi utama dengan navigasi: **Dataset/Status → Overview → 11.7 → 11.15/11.18 → 11.22 → Case Explorer → Export**.
- Siapkan container/panel tempat modul **Lintang dan Arga** dipasang, beserta mekanisme mengirim log aktif dan menerima hasil.
- **Jangan** mengambil alih coding GUI 11.7 atau GUI 11.15/11.18: panel tersebut wajib dibuat masing-masing pemiliknya.
- Saat integrasi, Ida menggabungkan panel; pemilik panel bertanggung jawab membantu sampai panel tersebut bekerja.

### B. Output yang wajib diserahkan
- [ ] Loader/validasi XES menggunakan PM4Py.
- [ ] Model atau struktur data **log aktif** yang disepakati seluruh anggota.
- [ ] Dashboard overview dan tabel case/durasi.
- [ ] Modul perhitungan **11.22** dengan evidence posisi event dan denominator yang benar.
- [ ] GUI utama, panel 11.22, Case Explorer, dan ekspor CSV.
- [ ] Unit test modul import, overview, urutan 11.22, Case Explorer, dan ekspor.
- [ ] Bagian laporan F01/F02/F06/F07 dan bukti screenshot terkait.

**Selesai apabila:** file XES dapat diimpor, metrik overview muncul, 11.22 dihitung dari data aktif, daftar case bisa dibuka, ekspor CSV bisa dibaca, dan UI tetap memberi feedback ketika proses lama/gagal.

---

## 3. ARGA — Penanggung jawab 2: analisis repeated complete & same resource (30%)

### A. Scope wajib

**F04 — Exercise 11.15 (15%)**
- Temukan case yang aktivitas **`W_Assess Potential Fraud` selesai (`complete`) minimal 2 kali**.
- Tentukan cara mengenali aktivitas target dan status **complete** berdasarkan **atribut yang benar-benar ada di XES**. Periksa apakah status tercatat melalui `lifecycle:transition` atau representasi lain pada log yang dipakai; dokumentasikan keputusan, **jangan berasumsi tanpa memeriksa data**.
- Event `scheduled`, `start`, `abort`, dan status non-`complete` **tidak boleh dihitung** sebagai penyelesaian.
- Hitung **jumlah unique case**, bukan jumlah occurrence total.
- Tampilkan **case ID, jumlah complete occurrence tiap case, serta event/timestamp bukti**.
- Buat GUI khusus Exercise **11.15**.

**F05 — Exercise 11.18 (15%)**
- Mulai dari konsep **dua atau lebih `complete` occurrence** pada aktivitas target **dalam case yang sama**.
- Tambahkan syarat: **minimal dua occurrence memiliki `org:resource` yang sama dan teridentifikasi**.
- **Resource kosong/null tidak boleh otomatis dianggap sama**; dua event dengan nilai kosong tidak cukup untuk meloloskan case.
- Dua occurrence complete oleh resource **berbeda** boleh lolos **11.15** tetapi **tidak otomatis lolos 11.18**.
- Tampilkan **case ID, resource ID, jumlah complete oleh resource itu, dan daftar event pembuktinya**.
- Buat GUI khusus Exercise **11.18** (boleh satu tab/halaman bersama 11.15, tetapi hasil dan aturan harus jelas dibedakan).

**Quality assurance khusus dan test runner**
- Siapkan struktur/test runner otomatis untuk menjalankan unit test ketiga modul tanpa membuka GUI (misalnya `pytest`); **bukan berarti Arga harus menulis semua test milik orang lain**.
- Tulis sendiri test untuk 11.15/11.18, terutama interaksi `complete` dan `resource` kosong/berbeda/sama.
- Siapkan **contoh case evidence** untuk menjelaskan kenapa case lolos atau tidak lolos.

### B. Output yang wajib diserahkan
- [ ] Fungsi pemeriksaan status complete berbasis representasi nyata XES.
- [ ] Modul analisis 11.15 dan modul analisis 11.18.
- [ ] GUI panel 11.15 dan 11.18 beserta tabel/filter hasil.
- [ ] Output standar: unique case, daftar case ID, occurrence/resource, evidence event.
- [ ] Unit test edge case 11.15/11.18 dan test runner yang terdokumentasi.
- [ ] Bagian laporan: definisi lifecycle, aturan 11.15/11.18, hasil BPIC17, dan screenshot evidence.

**Selesai apabila:** scheduled/start tidak terhitung sebagai complete; resource berbeda dibedakan dari resource sama; resource kosong ditangani benar; seluruh hasil dapat dilacak hingga event pembukti.

---

## 4. LINTANG — Penanggung jawab 3: seluruh Exercise 11.7 A–E dan cycle time (30%)

### A. Scope wajib

**F03 — Exercise 11.7 A–E (30%)**

| Soal | Pekerjaan persis yang harus dilakukan | Aturan kunci |
|---|---|---|
| **11.7 A** | Hitung jumlah keseluruhan case | **Unique case ID/trace**, bukan total event |
| **11.7 B** | Hitung rata-rata cycle time semua case | Per case: **timestamp akhir − timestamp awal**, dinyatakan dalam **hari** |
| **11.7 C** | Jumlah successful cases + mean cycle time-nya | Case mengandung **≥1 `O_Accepted`** (*contains*) |
| **11.7 D** | Jumlah unsuccessful cases + mean cycle time-nya | Case mengandung **≥1 `O_Refused`** (*contains*) |
| **11.7 E** | Jumlah canceled cases + mean cycle time-nya | **Event TERAKHIR** dalam trace adalah `O_Cancelled` (*endpoint*) |

**Perhatian yang tidak boleh keliru:**
- Satu case dengan **dua `O_Accepted` tetap dihitung sekali** pada 11.7 C.
- Case yang memiliki **`O_Accepted` sekaligus `O_Refused`** boleh masuk **kedua kategori** C dan D; jangan memaksakan kategori eksklusif.
- Case yang pernah memiliki `O_Cancelled` **belum tentu** termasuk 11.7 E; **event paling akhir** yang menentukan.
- **Cycle time dihitung dari keseluruhan trace asli case**, **bukan** dari subset event setelah filter `O_Accepted`/`O_Refused`.
- Pengurangan timestamp harus menangani zona waktu dengan konsisten; dokumentasikan presisi dan cara menampilkan rata-rata dalam hari.
- Buat **satu helper/fungsi cycle time reusable**. Berikan ke Ida agar overview dan 11.7 memakai definisi yang sama.
- Untuk setiap kategori, keluarkan **jumlah unique case, rata-rata cycle time, daftar case ID, serta aturan filter dan bukti yang dapat ditinjau di Case Explorer**.

**GUI khusus Exercise 11.7**
- Buat **lima section/kartu/tabel hasil A–E**, tombol jalankan/re-run, serta daftar case dan durasi.
- Pastikan tombol menuju Case Explorer memakai interface yang disepakati Ida; **Lintang yang menghubungkan hasil panel 11.7 ke interface itu**.
- Buat pesan jika ada kelompok kosong; mean kelompok kosong harus jelas ditampilkan sebagai **N/A/tidak tersedia**, **bukan 0 hari**.

**Pengujian dan dokumentasi**
- Tulis test untuk unique case, durasi, `contains`, `endpoint`, hasil overlap C/D, pembulatan mean, dan tidak memperpendek trace ketika filter diterapkan.
- Tulis bagian laporan 11.7 A–E, perhitungan cycle time, contoh case, serta screenshot GUI 11.7.
- Bantu review README bagian alur pengguna dan demonstrasi keseluruhan agar beban dokumentasi tidak jatuh seluruhnya ke Ida.

### B. Output yang wajib diserahkan
- [ ] Helper cycle time per case dan rata-rata dalam hari.
- [ ] Modul hasil 11.7 A, B, C, D, E lengkap.
- [ ] Panel GUI khusus 11.7 yang terintegrasi dengan Case Explorer.
- [ ] Bukti daftar case ID/aturan contains vs endpoint.
- [ ] Unit test dan screenshot 11.7.
- [ ] Bagian laporan 11.7 serta pemeriksaan README alur pengguna.

**Selesai apabila:** semua lima soal menampilkan hasil dinamis dan konsisten, durasi case tidak berubah karena filter event, C/D boleh overlap, dan E hanya lolos bila event terakhir tepat `O_Cancelled`.

---

## 5. KONTRAK TEKNIS WAJIB sebelum coding paralel

Agar ketiganya dapat kerja paralel tanpa file konflik, sepakati **satu kontrak data dan fungsi** saat awal. Nama fungsi/file di bawah hanyalah **rekomendasi implementasi**, bukan perintah dosen.

### A. Input bersama

- Semua modul menerima objek log aktif yang sama dari **Ida** (mis. `LogData` atau PM4Py EventLog/DataFrame yang dinormalisasi).
- Identitas **case ID** harus konsisten, dan setiap case menyimpan daftar event sesuai **urutan trace yang disepakati**.
- Setiap event memuat field yang tersedia: `case_id`, `activity`, `timestamp`, `lifecycle`, `resource`, dan **posisi event dalam trace** untuk evidence.
- **Tetapkan dan dokumentasikan urutan trace**, terutama bila timestamp sama. Rekomendasi: pertahankan urutan trace yang ada pada data sumber; jika ada normalisasi/sorting, jangan sampai membuat hasil `endpoint` atau `eventually follows` ambigu. Durasi dapat memakai `max(timestamp) − min(timestamp)` agar definisi konsisten.
- Jangan menghapus event dari original full-case trace hanya karena case terpilih oleh filter tertentu.
- Untuk seluruh analisis, **denominator 11.22 = jumlah case pada log aktif**, bukan case yang telah difilter untuk exercise lain.

### B. Output fungsi analisis bersama

Setiap fungsi analisis **minimal** mengembalikan struktur semacam:

```python
{
    "exercise": "11.15",
    "case_count": 0,
    "case_ids": [],
    "filter_rule": "...",
    "evidence": {},          # case_id -> event terkait dan alasan lolos
    "metrics": {},           # mean_days, percentage, denominator, dll jika relevan
}
```

Catatan: contoh ini adalah **kontrak rancangan**, bukan hasil pengolahan BPIC17. Jangan gunakan angka `0` sebagai jawaban statis aplikasi. `evidence` harus memuat **event asli yang relevan beserta atributnya** sehingga bisa dibuka di Case Explorer dan diekspor.

### C. Batas kepemilikan kode

| Folder/komponen usulan | Pemilik utama | Anggota lain boleh melakukan apa? |
|---|---|---|
| `core/log_loader.py`, `core/overview.py` | Ida Bagus | Mengajukan perubahan kontrak/API lewat diskusi, tidak mengubah sepihak |
| `core/exercise_1122.py` | Ida Bagus | Membantu pengujian dan review |
| `gui/main_window.py`, `gui/case_explorer.py`, `utils/csv_export.py` | Ida Bagus | Menyediakan hasil modul agar dapat terintegrasi; review/bug report |
| `core/exercise_1115_1118.py`, `gui/panel_1115_1118.py` | Arga | Review dan pengujian |
| `core/cycle_time.py`, `core/exercise_117.py`, `gui/panel_117.py` | Lintang | Memanggil helper cycle time tanpa menduplikasi rumus |
| `tests/` | **Bersama**, test dipisah berdasarkan modul | Setiap orang menulis dan memperbaiki test miliknya; Arga memelihara konfigurasi runner |
| `README.md`, `requirements.txt`, laporan akhir | **Bersama** | Tulis bagian masing-masing; gabungkan setelah direview |

> **Larangan pekerjaan rangkap yang boros:** Ida tidak perlu menghitung ulang 11.7 untuk overview; Lintang tidak perlu membuat Case Explorer kedua; Arga tidak perlu membuat sistem impor kedua. Gunakan interface bersama yang disepakati.

---

## 6. Urutan pengerjaan yang benar (lintang BUKAN langkah pertama)

**Penting:** Urutan berikut adalah **urutan dependensi**, bukan perintah bahwa satu orang harus selesai semua pekerjaannya sebelum yang lain mulai.

### Tahap 0 — Kesepakatan bersama (sebelum mengubah kode)
- [ ] Baca instruksi proyek dan daftar 8 subsoal wajib: **11.7 A–E, 11.15, 11.18, 11.22**.
- [ ] Tentukan framework GUI (mis. PySide6 atau Tkinter), versi Python/PM4Py, dan format hasil fungsi.
- [ ] Tentukan cara menampilkan event trace, aturan urutan event, dan nama atribut lifecycle/resource yang akan diperiksa dari XES.
- [ ] Tetapkan branch dan aturan commit; pastikan tiga anggota menggunakan satu repo.
- [ ] Konfirmasi ketentuan kelompok 3 vs 4 mahasiswa ke dosen.

### Tahap 1 — Fondasi awal: IDA BAGUS (mulai pertama)
- [ ] Buat project skeleton dan GUI window minimal.
- [ ] Implementasikan impor XES dengan PM4Py dan data model log aktif.
- [ ] Buat data dummy/log sintetis kecil agar anggota lain bisa menguji sebelum BPIC17 selesai dimuat.
- [ ] Kunci kontrak pemanggilan modul (input, output, cara membuka Case Explorer).
- **Milestone:** Arga dan Lintang dapat mengimpor/menyediakan log ke fungsi analisis tanpa mengedit loader sendiri.

### Tahap 2 — Implementasi paralel: ARGA dan LINTANG (+ IDA BAGUS)
- **Arga:** identifikasi lifecycle, implementasikan 11.15/11.18, panel GUI sendiri, dan unit test.
- **Lintang:** implementasikan helper cycle time yang dibutuhkan overview, lalu 11.7 A–E, panel GUI sendiri, dan unit test.
- **Ida Bagus:** lanjutkan overview (memanggil helper Lintang), 11.22, Case Explorer, dan ekspor.
- **Milestone:** setiap modul berjalan dan diuji terpisah; semua fungsi mengembalikan daftar case/evidence.

### Tahap 3 — Integrasi bersama
- [ ] Ida menyiapkan navigasi/komposisi halaman dan memanggil seluruh fungsi.
- [ ] Arga **memasang dan memperbaiki panel 11.15/11.18 miliknya** jika ada kendala integrasi.
- [ ] Lintang **memasang dan memperbaiki panel 11.7 miliknya** jika ada kendala integrasi.
- [ ] Ketiganya memeriksa nama atribut, data output, klik ke Case Explorer, status progres, reset, dan ekspor CSV.
- **Milestone:** seluruh **F01–F07** berfungsi dari aplikasi desktop yang sama.

### Tahap 4 — Validasi, laporan, demo bersama
- [ ] Jalankan unit test seluruh modul.
- [ ] Jalankan BPIC17 XES asli yang disepakati, **tanpa hard-coded answer**.
- [ ] Verifikasi hasil dibanding materi latihan dosen; jika berbeda, jelaskan secara teknis interpretasi lifecycle/filter, bukan memaksa angka.
- [ ] Simpan screenshot setiap menu utama, plus **minimal satu screenshot jejak kasus** untuk **11.15, 11.18, dan 11.22**.
- [ ] Siapkan README, requirements, laporan kontribusi, dan rekaman/demo aplikasi.
- **Milestone:** dapat mendemokan **impor → overview → jalankan soal → buka evidence → ekspor**, dan setiap anggota mampu menjelaskan aplikasi.

---

## 7. Checklist pengujian wajib (sesuai skenario dosen)

| No. | Skenario edge case | Hasil yang benar | PIC penulis unit test |
|---:|---|---|---|
| 1 | Satu case memiliki `O_Accepted` dua kali | 11.7 C menghitung **case sekali** | Lintang |
| 2 | `O_Cancelled` terjadi di tengah lalu diikuti aktivitas lain | **Tidak** dihitung canceled pada 11.7 E | Lintang |
| 3 | Satu case memiliki `O_Refused` dan `O_Accepted` | Boleh masuk **kedua** kategori 11.7 C/D | Lintang |
| 4 | `W_Assess Potential Fraud` dijadwalkan dua kali tetapi complete sekali | **Tidak** lolos 11.15 | Arga |
| 5 | Dua complete oleh resource berbeda | Lolos 11.15; **tidak otomatis** 11.18 | Arga |
| 6 | Dua complete oleh resource sama (teridentifikasi) | Lolos 11.15 **dan** 11.18 | Arga |
| 7 | `O_Cancelled` → aktivitas lain → `O_Accepted` | **Lolos** 11.22 | Ida Bagus |
| 8 | `O_Accepted` lebih dulu daripada `O_Cancelled`, tidak ada accepted sesudahnya | **Tidak** lolos 11.22 | Ida Bagus |

**Tambahan tes integrasi oleh ketiganya:**
- [ ] Impor file XES tidak valid memberi pesan jelas (Ida).
- [ ] Penghitungan case tidak tercampur jumlah event (Lintang; dicek bersama).
- [ ] Cycle time tidak dihitung dari trace yang sudah dipotong oleh filter (Lintang).
- [ ] Resource kosong/null tidak diloloskan sebagai resource identik (Arga).
- [ ] Untuk 11.22, persentase memiliki **denominator jumlah case log aktif** (Ida).
- [ ] Reload dataset yang sama menghasilkan angka yang sama; mengganti log menghitung ulang angka baru (Bersama).
- [ ] Re-run analisis tanpa impor ulang, navigasi Case Explorer, ekspor CSV, dan responsivitas GUI berfungsi (Bersama).
- [ ] Versi Python, PM4Py, dan dependensi tercatat (Bersama).

---

## 8. Standar selesai / definition of done setiap orang

Sebuah tugas **belum boleh dinyatakan selesai** jika hanya fungsi backend berjalan tetapi panel, bukti case, atau test tidak ada. **Selesai** berarti:

1. Logika analisis sesuai soal, **berbasis dataset pilihan pengguna**.
2. Modul bisa dipanggil dari aplikasi utama, bukan hanya dari notebook/terminal.
3. GUI menampilkan hasil, satuan, aturan filter, daftar case ID, dan evidence sesuai kebutuhan.
4. Ada unit test minimal untuk skenario tepi terkait, dan seluruh tesnya lulus.
5. Ada penanganan error/hasil kosong yang jelas.
6. Ada screenshot yang relevan dan uraian modul untuk laporan.
7. Code sudah direview dan digabung; tidak merusak fitur anggota lain.

**Aturan pengerjaan Git (rekomendasi):**
- Branch kerja: `feat/ida-import-overview-explorer`, `feat/arga-repeated-resource`, `feat/lintang-exercise-117`.
- Jangan commit file `.xes` dataset besar atau folder environment/temporary files.
- PR wajib mencantumkan fitur, file yang diubah, langkah tes, screenshot GUI, dan hasil unit test.
- Jangan mengubah modul anggota lain tanpa koordinasi. Konflik atau perubahan kontrak dibicarakan terlebih dahulu.

---

## 9. Berkas akhir yang wajib dikumpulkan

- [ ] **Aplikasi desktop Python + PM4Py** yang bisa dijalankan di komputer lain.
- [ ] Source code modular, file `requirements.txt` dan `README.md` berisi langkah instalasi/pakai.
- [ ] Menu dan alur aplikasi mencakup **F01–F07**.
- [ ] Jawaban dinamis untuk **8 butir:** 11.7 A–E, 11.15, 11.18, 11.22.
- [ ] Bukti case ID dan event pembukti untuk filter; ekspor minimal **CSV**.
- [ ] Laporan ringkas: pemetaan soal → fungsi, definisi filter, hasil BPIC17, contoh case evidence, pengujian, kendala, **kontribusi masing-masing anggota**.
- [ ] Screenshot setiap menu utama dan jejak kasus untuk 11.15, 11.18, 11.22.
- [ ] Demo/replay alur impor XES → analisis → periksa case → ekspor.
- [ ] Semua anggota memahami cara kerja dan mampu menjelaskan modul masing-masing **serta** alur keseluruhan.

**Tidak diwajibkan dalam Tahap 1:** Alpha Miner, Heuristics Miner, Inductive Miner, Petri net discovery. Pengembangan tambahan (DFG/visualisasi lanjutan/laporan PDF) hanya dilakukan **setelah** seluruh fitur wajib berfungsi.

---

## 10. Ringkasan singkat untuk disalin ke grup

**PEMBAGIAN TUGAS BPIC17 (3 ORANG) — BERDASARKAN RUBRIK DOSEN**

**1. IDA BAGUS — 30%**: Import/validasi XES (F01), Overview (F02), Exercise 11.22 (F06), Case Explorer & export CSV (F07), navigasi/integrasi GUI utama. **Ida tidak membuat GUI exercise milik Arga/Lintang.**

**2. ARGA — 30%**: Exercise 11.15 (repeated complete), 11.18 (same-resource complete), identifikasi lifecycle/resource, GUI kedua exercise, evidence, unit test, serta konfigurasi test runner.

**3. LINTANG — 30%**: Exercise 11.7 **A–E**, helper cycle time reusable, GUI 11.7, daftar case dan evidence, unit test, serta review petunjuk penggunaan/README.

**4. BERSAMA — 10%**: Kesepakatan interface data, integrasi, pengujian BPIC17 asli, debugging, laporan final, screenshot, demo, dan verifikasi hasil.

**URUTAN:** Ida menyiapkan **fondasi XES dan kontrak data lebih dulu**. Setelah kontrak siap, **Arga, Lintang, dan Ida mengerjakan modul masing-masing secara paralel**. Setiap orang mengintegrasikan dan memperbaiki panel miliknya. Finalisasi/test/demo dikerjakan **bersama**.

**SYARAT MUTLAK:** Tidak hard-code jawaban; semua hasil harus dari log aktif, dapat ditelusuri ke case/event, dan sesuai aturan lifecycle serta urutan trace. **Catatan:** Instruksi dosen menyebut kelompok 4 mahasiswa; konfirmasi penggunaan kelompok 3 orang.

---

*Sumber utama: Instruksi Proyek Tahap 1 — Aplikasi Desktop untuk Analisis Event Log BPIC17, versi 16 November 2026, khususnya halaman 1–7 (ketentuan dan spesifikasi) serta halaman 8 (checklist demo).*
