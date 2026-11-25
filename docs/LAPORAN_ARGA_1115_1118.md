# Laporan Modul F04 & F05 — Exercise 11.15 & 11.18 (Arga)

## 1. Definisi Lifecycle & Representasi Nyata XES

Pada modul `core/lifecycle.py`, pemeriksaan status penyelesaian aktivitas tidak diasumsikan begitu saja, melainkan memeriksa atribut aktual yang tersedia di dalam `LogData.df`:

- **Atribut target aktivitas:** `concept:name` (dipetakan ke kolom `activity`), dengan nilai target `W_Assess Potential Fraud`.
- **Atribut status lifecycle:** `lifecycle:transition` (dipetakan ke kolom `lifecycle`, bernilai `NaN` jika kosong/tidak ada).
- **Aturan pengenalan status `complete` (`is_complete_series`):**
  - Hanya event dengan nilai `lifecycle:transition == "complete"` (case-insensitive, di-strip) yang dihitung sebagai penyelesaian aktivitas.
  - Status non-`complete` seperti `schedule`, `scheduled`, `start`, `suspend`, `resume`, `withdraw`, `ate_abort`, `pi_abort`, maupun nilai kosong/`NaN` **tidak dihitung**.
  - Jika suatu log tidak memiliki `lifecycle:transition` sama sekali (`has_lifecycle == False`), fungsi `inspect_lifecycle()` melaporkannya secara eksplisit dan tidak mengasumsikan event sebagai `complete`.

---

## 2. Aturan Analisis Exercise 11.15 & 11.18

### Exercise 11.15 (`core/exercise_1115.py`)
- **Tujuan:** Menemukan unique case di mana aktivitas `W_Assess Potential Fraud` berstatus `complete` **minimal 2 kali**.
- **Aturan kunci:**
  - Status non-`complete` diabaikan.
  - Satu case dengan >= 2 `complete` tetap dihitung **1 unique case** (bukan jumlah occurrence).
  - Output mencakup `case_count`, `case_ids`, `complete_count` per case, timestamp, posisi event (`highlight_positions`), serta `resource`.

### Exercise 11.18 (`core/exercise_1118.py`)
- **Tujuan:** Menemukan unique case di mana aktivitas `W_Assess Potential Fraud` berstatus `complete` **minimal 2 kali oleh `org:resource` yang sama dan teridentifikasi**.
- **Aturan kunci:**
  - Event `complete` dengan `org:resource` kosong, spasi, atau `NaN`/`None` disaring terlebih dahulu (`is_identified_resource`) sehingga dua event tanpa resource **tidak pernah dianggap sama**.
  - Dua event `complete` oleh resource berbeda lolos 11.15 tetapi **tidak lolos** 11.18.
  - Jika dalam satu case ada lebih dari satu resource yang masing-masing menyelesaikan >= 2 kali, case tetap dihitung **1 unique case**.

---

## 3. Contoh Case Evidence (dari `sample_data/sample_log.xes`)

| Case ID | Jejak Event `W_Assess Potential Fraud` | Lolos 11.15? | Lolos 11.18? | Penjelasan Evidence |
|---|---|---:|---:|---|
| `Application_07` | `schedule` (pos 1), `schedule` (pos 2), `complete` oleh `User_4` (pos 3) | Tidak | Tidak | Hanya 1 event berstatus `complete`; dua event `schedule` tidak dihitung. |
| `Application_08` | `complete` oleh `User_4` (pos 1), `complete` oleh `User_5` (pos 2) | **Ya** (2x) | Tidak | Ada 2 `complete`, tetapi resource berbeda (`User_4` vs `User_5`). |
| `Application_09` | `complete` oleh `User_4` (pos 1), `complete` oleh `User_4` (pos 2) | **Ya** (2x) | **Ya** (`User_4`, 2x) | Ada 2 `complete` oleh resource sama dan teridentifikasi (`User_4`). |
| `Application_10` | `complete` resource kosong (pos 1), `complete` resource kosong (pos 2) | **Ya** (2x) | Tidak | Ada 2 `complete`, tetapi kedua resource kosong/null sehingga tidak dianggap sama. |

---

## 4. Hasil Dataset BPIC17 Asli

> **Catatan:** File dataset BPIC17 penuh (`BPI Challenge 2017.xes`) tidak disertakan di repositori karena ukurannya besar. Jalankan aplikasi (`python main.py`), pilih file `.xes` BPIC17, lalu catat hasil aktual dari panel **Exercise 11.15 & 11.18** dan ekspor CSV ke tabel di bawah ini:

- **Jumlah seluruh case BPIC17:** *(isi setelah menjalankan pada BPIC17.xes)*
- **Hasil Exercise 11.15 (unique case):** *(isi dari kartu metrik / CSV summary)*
- **Hasil Exercise 11.18 (unique case):** *(isi dari kartu metrik / CSV summary)*
- **Screenshot Evidence:**
  - *(Lampirkan screenshot tab Exercise 11.15, tab Exercise 11.18, dan Case Explorer untuk minimal 1 case bukti)*

---

## 5. Dokumentasi Test Runner Otomatis

Pengujian otomatis menggunakan `pytest` dan dapat dijalankan tanpa membuka GUI:

```bash
# Menjalankan seluruh unit test dan uji GUI offscreen
python run_tests.py

# Menjalankan hanya unit test logika core (tanpa GUI)
python run_tests.py --unit

# Alternatif langsung via pytest
python -m pytest -v
```

