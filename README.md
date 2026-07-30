# Sistem Pakar Diagnosis Kerusakan iPhone
### Hibridisasi Dempster-Shafer & Particle Swarm Optimization (DS-PSO)

> **Skripsi** — Muh. Renaldi  
> NST Phone Repair · Sistem Pakar Kerusakan iPhone

---

## 🚀 Cara Menjalankan di Komputer Lain

### Prasyarat
- **Python 3.10+** (diuji pada Python 3.13)
- **pip** (biasanya sudah termasuk bersama Python)
- **Git** (untuk clone repositori)
- **Browser** (Chrome, Firefox, Edge, dsb.)

### Langkah-langkah

#### 1. Clone Repositori
```bash
git clone https://github.com/nowarlove/Sistem-pakar-kerusakan-iphone.git
cd Sistem-pakar-kerusakan-iphone
```

#### 2. Install Dependensi
```bash
pip install -r app/requirements.txt
```
> Hanya membutuhkan **Flask** — tidak ada dependensi berat seperti TensorFlow, dsb.

#### 3. Jalankan Aplikasi Web
```bash
cd app
python app.py
```

#### 4. Buka di Browser
Akses alamat berikut:
```
http://localhost:5000
```

**Selesai!** Aplikasi siap digunakan untuk mendiagnosis kerusakan iPhone.

---

## 📁 Struktur Proyek

```
.
├── preprocessing.ipynb           ← [MODEL] Prapemrosesan data & normalisasi slang
├── pso.ipynb                     ← [MODEL] Optimasi bobot belief dengan DS-PSO
├── data/
│   ├── belief.json               ← Aturan pakar awal (16 aturan)
│   ├── optimal_knowledge_base.json ← OUTPUT PSO (basis pengetahuan optimal)
│   ├── data toko 2.xlsx          ← Data mentah toko 2
│   ├── data utama.xlsx           ← Data mentah utama
│   ├── dataLatih/                ← CSV latih (diabaikan git)
│   └── dataUji/                  ← CSV uji (diabaikan git)
├── app/                          ← Antarmuka Web (Flask)
│   ├── app.py                    ← Backend Flask (endpoint /diagnosa, /model-info, /feedback)
│   ├── requirements.txt          ← Dependensi Python (flask>=3.0.0)
│   ├── core/                     ← Modul inti inferensi
│   │   ├── normalizer.py         ← Normalisasi teks (slang → baku)
│   │   ├── feature_extractor.py  ← Ekstraksi 12 fitur gejala dari teks bebas
│   │   └── ds_engine.py          ← Mesin inferensi Dempster-Shafer + Pignistik
│   ├── templates/
│   │   └── index.html            ← Halaman utama (diagnosa & analisis)
│   └── static/
│       ├── css/style.css         ← Stylesheet profesional
│       └── js/main.js            ← Logika frontend (form, visualisasi, cetak PDF)
└── referensi/
    └── usulanPenelitianMuh_Renaldi.pdf
```

---

## ⚠️ Catatan Penting

> **`preprocessing.ipynb` dan `pso.ipynb` adalah berkas model inti yang TIDAK BOLEH dimodifikasi setelah tag `v1.0-model`.**
> Untuk memulihkan versi model yang telah diuji penguji, gunakan:
> ```bash
> git checkout v1.0-model
> ```

---

## 🔬 Cara Melatih Ulang Model (Opsional)

> **Catatan:** Langkah ini **tidak diperlukan** untuk menjalankan aplikasi web.
> Model sudah dilatih dan hasilnya tersimpan di `data/optimal_knowledge_base.json`.

### Langkah 1: Preprocessing
Jalankan semua sel di `preprocessing.ipynb` menggunakan Jupyter Notebook.
- **Input:** `data/data toko 2.xlsx`, `data/data utama.xlsx`
- **Output:** `data/dataLatih/dataLatih-YYYY-MM-DD-HH-MM.csv`, `data/dataUji/dataUji-YYYY-MM-DD-HH-MM.csv`
- **Dependensi tambahan:** `pip install pandas openpyxl scikit-learn`

### Langkah 2: Optimasi DS-PSO
Jalankan semua sel di `pso.ipynb`
- **Input:** CSV latih/uji terbaru + `data/belief.json`
- **Output:** `data/optimal_knowledge_base.json`
- **Durasi:** ~40 detik (100 iterasi, 30 partikel)
- **Dependensi tambahan:** `pip install pandas numpy scikit-learn matplotlib seaborn`

---

## 📊 Hasil Model (v1.0)
| Metrik | Nilai |
|---|---|
| Akurasi Data Uji | **~87.57%** |
| Fungsi Fitness | Brier Score (kontinu) |
| Algoritma | Dempster-Shafer + PSO |
| Aturan Pakar | 16 aturan |
| Dimensi Partikel | 32 parameter belief |
| Kelas Diagnosis | 13 kategori kerusakan hardware iPhone |
| Kolom Fitur | 12 gejala terstruktur |

---

## 🌐 Fitur Aplikasi Web
- **Diagnosis Kerusakan:** Ketik keluhan bebas → hasil diagnosis dengan probabilitas Pignistik
- **Deteksi Konteks Cerdas:** Memahami frasa seperti "layar normal, speaker pecah" dan "bergetar saat dicas"
- **Analisis Inferensi DS:** Log detail langkah kombinasi Dempster-Shafer untuk dokumentasi skripsi
- **Cetak Laporan PDF:** Hasil diagnosis dalam format laporan siap cetak
- **Pembelajaran Dinamis:** Koreksi diagnosis melalui umpan balik yang memperbarui prior empiris model secara real-time
- **Deteksi Software Gate:** Keluhan software (flash, iCloud, bypass) ditangani secara terpisah
