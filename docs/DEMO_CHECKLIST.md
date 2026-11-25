# PANDUAN & CHECKLIST DEMONSTRASI DOSEN — TAHAP 1
**BPIC17 Event Log Analyzer Desktop Application**

Panduan langkah-demi-langkah bagi tim saat melakukan demonstrasi langsung di hadapan dosen penguji, dilengkapi referensi bukti tangkapan layar asli yang tersimpan di `docs/screenshots/`.

---

## Urutan Demonstrasi Terstruktur (Alur 10 Langkah)

### Langkah 1: Peluncuran Aplikasi (*Launch*)
1. Buka terminal (PowerShell atau Command Prompt) pada direktori proyek.
2. Jalankan perintah:
   ```powershell
   python main.py
   ```
3. **Hasil yang terlihat:** Jendela aplikasi desktop terbuka dengan judul *"BPIC17 Event Log Analyzer - Tahap 1"* ukuran 1200x780. Navigasi sisi kiri menampilkan 7 menu:
   - *Dataset & Status*
   - *Overview*
   - *Exercise 11.7*
   - *Exercise 11.15 & 11.18*
   - *Exercise 11.22*
   - *Case Explorer*
   - *Export*
4. Status bar bawah menampilkan pesan: *"Siap. Impor file XES untuk memulai."*

---

### Langkah 2: Impor File Event Log XES (*Import Dataset*)
1. Pada menu **Dataset & Status**, klik tombol **"Pilih file .xes..."** (atau gunakan menu `File -> Buka file XES...` / shortcut `Ctrl+O`).
2. Pilih file `sample_data/sample_log.xes` (atau file dataset BPIC17 jika tersedia).
3. **Hasil yang terlihat:**
   - Progress bar bergerak (proses background non-blocking).
   - Log viewer menampilkan log tahapan validasi.
   - Status bar menampilkan: *"Impor selesai: 10 case, 23 event."*
   - Kotak informasi menampilkan nama berkas, status atribut, serta ketersediaan `lifecycle:transition` dan `org:resource`.
4. **Bukti Screenshot:** `docs/screenshots/01_dataset_status.png`

---

### Langkah 3: Tinjauan Statistik Log (*Overview Dashboard*)
1. Klik menu **Overview** pada navigasi sisi kiri (otomatis terbuka setelah impor selesai).
2. **Hasil yang terlihat:**
   - 4 Kartu Metrik: Total Case (10), Total Event (23), Rata-rata Cycle Time (0.0542 hari), Rentang Waktu (1 Jan 2016 s.d. 10 Jan 2016).
   - Tabel Kiri: Frekuensi Aktivitas (diurutkan dari aktivitas terbanyak beserta jumlah kasusnya).
   - Tabel Kanan: Daftar Kasus Lengkap dengan waktu mulai, waktu selesai, jumlah event, dan durasi per kasus (hari).
   - Kotak pencarian case ID untuk menyaring kasus secara interaktif.
3. **Bukti Screenshot:** `docs/screenshots/02_overview.png`

---

### Langkah 4: Analisis Exercise 11.7 (A, B, C, D, E) — Milik Lintang
1. Klik menu **Exercise 11.7**.
2. Klik tombol **"Jalankan analisis 11.7 A-E"**.
3. **Hasil yang terlihat pada Kartu Ringkasan Atas:**
   - `11.7 A (Total Cases):` **10**
   - `11.7 B (Mean Cycle Time):` **0.0542 hari**
   - `11.7 C (Accepted Cases):` **4 (0.0729 hari)**
   - `11.7 D (Refused Cases):` **1 (0.0417 hari)**
   - `11.7 E (Canceled Cases):` **3 (0.0417 hari)**
4. Buka **Tab 11.7 C (O_Accepted)**:
   - Terlihat 4 case lolos: `Application_01`, `02`, `03`, `04` (persentase 40.00%, mean 0.0729 hari).
   - Tabel menampilkan jumlah `O_Accepted`, posisi event dalam trace, dan durasi trace lengkap.
   - **Bukti Screenshot:** `docs/screenshots/03_exercise_117_c.png`
5. Buka **Tab 11.7 E (O_Cancelled Endpoint)**:
   - Terlihat 3 case lolos: `Application_02`, `03`, `05` (mean 0.0417 hari).
   - Kasus `Application_01` (yang memuat `O_Cancelled` di urutan ke-1 namun event akhirnya `O_Accepted`) terbukti **tidak lolos** di 11.7 E.
   - **Bukti Screenshot:** `docs/screenshots/03_exercise_117_e.png`

---

### Langkah 5: Analisis Exercise 11.15 (Repeated Complete) — Milik Arga
1. Klik menu **Exercise 11.15 & 11.18**.
2. Klik tombol **"Jalankan analisis 11.15 & 11.18"**.
3. **Hasil yang terlihat pada Banner Lifecycle:**
   - Sistem mendeteksi atribut XES `lifecycle:transition == 'complete'`.
   - Melaporkan bahwa status non-complete (`schedule`, `start`, dll.) diabaikan.
4. Buka **Tab Exercise 11.15**:
   - Kartu Metrik: Case lolos = **3**, Seluruh case = **10**, Persentase = **30.00%**, Event complete = **6**.
   - Tabel menampilkan `Application_08` (2x complete), `Application_09` (2x complete), dan `Application_10` (2x complete).
   - Kasus `Application_07` (yang memuat 2x `schedule` dan 1x `complete`) terbukti **tidak lolos**.
   - Coba ubah spinbox *"Filter minimal complete"* menjadi 3 -> tabel kosong; kembalikan ke 2 -> tabel memuat 3 case.
5. **Bukti Screenshot:** `docs/screenshots/04_exercise_1115.png`

---

### Langkah 6: Analisis Exercise 11.18 (Same Resource Complete) — Milik Arga
1. Beralih ke **Tab Exercise 11.18**.
2. **Hasil yang terlihat:**
   - Kartu Metrik: Case lolos = **1**, Persentase = **10.00%**, Gugur resource beda/kosong = **2**, Complete resource kosong = **2**.
   - Tabel menampilkan hanya `Application_09` dengan Resource Utama `User_4` (diselesaikan 2 kali oleh orang yang sama).
   - Kasus `Application_08` (dikerjakan `User_4` dan `User_5`) dan `Application_10` (resource `None`) terbukti **gugur** karena resource berbeda / tidak teridentifikasi.
   - Kotak filter resource ID dapat dicoba dengan mengetik `User_4`.
3. **Bukti Screenshot:** `docs/screenshots/05_exercise_1118.png`

---

### Langkah 7: Analisis Exercise 11.22 (Cancelled Then Accepted) — Milik Ida Bagus
1. Klik menu **Exercise 11.22**.
2. Klik tombol **"Jalankan analisis"**.
3. **Hasil yang terlihat:**
   - Kartu Metrik: Case lolos = **3**, Seluruh case = **10**, Persentase = **30.00%**, Case memuat keduanya = **4**.
   - Penjelasan Formula: *"3 / 10 x 100% = 30.0000%. Dihitung per case (satu case dihitung sekali)."*
   - Tabel menampilkan 3 case pembukti: `Application_01` (posisi 1 -> 3), `Application_03` (posisi 1 -> 2), `Application_04` (posisi 2 -> 3).
   - Kasus `Application_02` (memiliki accepted di pos 1 dan cancelled di pos 2) terbukti **gagal**.
4. **Bukti Screenshot:** `docs/screenshots/06_exercise_1122.png`

---

### Langkah 8: Pelacakan Bukti pada Case Explorer (*Case Evidence Trace*)
1. Klik tombol **"Buka di Case Explorer"** dari panel manapun, atau klik menu **Case Explorer**.
2. Pilih sumber daftar case pada dropdown (misalnya *11.18 - 1 case* atau *11.22 - 3 case*).
3. **Pengujian Jejak Kasus 11.18 (`Application_09`):**
   - Pilih `Application_09` pada tabel kiri.
   - Tabel trace kanan menampilkan seluruh kronologi event `Application_09`.
   - Baris event `complete` oleh `User_4` **disorot dengan warna kuning**.
   - **Bukti Screenshot:** `docs/screenshots/08_case_explorer_1118.png`
4. **Pengujian Jejak Kasus 11.22 (`Application_01`):**
   - Pilih sumber *11.22*, klik `Application_01`.
   - Event urutan ke-1 (`O_Cancelled`) dan ke-3 (`O_Accepted`) **disorot warna kuning**. Event urutan ke-2 (`W_Call after offers`) berwarna putih.
   - **Bukti Screenshot:** `docs/screenshots/09_case_explorer_1122.png`
5. **Pengujian Jejak Kasus 11.15 (`Application_08`):**
   - **Bukti Screenshot:** `docs/screenshots/07_case_explorer_1115.png`

---

### Langkah 9: Ekspor Hasil ke CSV (*Export*)
1. Klik menu **Export**.
2. Klik tombol **"Ekspor ringkasan jawaban (CSV)"** -> simpan file `ringkasan_jawaban.csv`.
   - Buka file CSV: memuat seluruh baris metrik 11.7 A–E, 11.15, 11.18, dan 11.22 dengan encoding `utf-8-sig` (langsung terbaca rapi di Microsoft Excel).
3. Pilih salah satu latihan pada dropdown (misalnya *11.18*), klik **"Ekspor daftar case (CSV)"** -> simpan file `daftar_case_11.18.csv`.
   - Buka file CSV: memuat header, case ID, resource utama, ringkasan bukti, dan timestamp lengkap.
4. **Bukti Screenshot:** `docs/screenshots/10_export_panel.png`

---

### Langkah 10: Reset & Re-run Tanpa Impor Ulang
1. Pilih menu `File -> Reset semua hasil analisis`.
2. Verifikasi: seluruh kartu kembali ke tanda `"-"`, tabel kosong, status bar mengonfirmasi hasil direset, namun **log aktif tetap tersimpan di memori**.
3. Pengguna dapat langsung menekan tombol *"Jalankan analisis"* pada panel manapun untuk menghitung ulang secara instan tanpa perlu membaca ulang file dari hard disk.
