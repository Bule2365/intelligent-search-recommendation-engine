# Contributing Guide

Terima kasih sudah tertarik berkontribusi! Proyek ini awalnya dibangun sebagai portfolio,
tapi disusun supaya bisa dikembangkan lebih lanjut secara kolaboratif.

## Setup Development

```bash
git clone https://github.com/Bule2365/intelligent-search-recommendation-engine.git
cd ecommerce-search-engine/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/generate_dataset.py --n-products 2000 --n-users 300  # dataset kecil untuk dev cepat
python scripts/seed_database.py
pytest tests/ -v   # pastikan semua test lulus sebelum mulai
```

## Alur Kontribusi

1. Fork repository ini.
2. Buat branch baru dari `main`: `git checkout -b fitur/nama-fitur-anda`.
3. Tulis kode beserta test-nya (lihat panduan testing di bawah).
4. Pastikan `pytest tests/ -v` lulus penuh dan tidak menurunkan coverage secara signifikan.
5. Commit dengan pesan yang jelas (lihat konvensi di bawah).
6. Push ke fork Anda dan buka Pull Request ke `main`, isi template PR yang tersedia.

## Konvensi Kode

- **Python**: ikuti PEP 8. Setiap modul baru di `search_engine/` atau `recommendation_engine/`
  harus mengekspos interface yang konsisten dengan modul sejenis (lihat konvensi di Bagian 5.4
  Technical Handbook — method `.search(query, top_k)` atau `.recommend(id, top_k)`).
- **Docstring**: setiap modul baru wajib punya docstring di awal file yang menjelaskan APA
  fungsinya dan KENAPA didesain seperti itu (lihat contoh di seluruh kode `app/`).
- **Commit message**: gunakan awalan `feat:`, `fix:`, `docs:`, `test:`, `refactor:`,
  `perf:` sesuai jenis perubahan (mengikuti konvensi Conventional Commits).
- **Tidak ada magic number**: parameter tuning (top_k, alpha, dsb) masuk ke `config.py`,
  bukan hardcoded di tengah logika.

## Panduan Testing

- Unit test baru untuk logika murni masuk ke `tests/test_search.py` atau
  `tests/test_recommendations.py`, memakai dataset kecil buatan tangan (lihat fixture
  `sample_products` sebagai contoh).
- Test endpoint baru masuk ke `tests/test_api.py`, memakai `TestClient`.
- Jika menambah dependency baru (library Python), tambahkan ke `requirements.txt` dengan
  versi minimum yang jelas, dan jelaskan alasannya di Pull Request (terutama soal dampak
  resource — proyek ini punya komitmen kuat terhadap hardware-aware engineering).

## Melaporkan Bug

Gunakan template Bug Report di Issues. Sertakan: langkah reproduksi, perilaku yang diharapkan
vs aktual, dan environment (OS, versi Python, RAM).

## Mengusulkan Fitur

Gunakan template Feature Request. Jelaskan masalah yang ingin diselesaikan, bukan hanya solusi
yang diinginkan — ini membantu diskusi menemukan pendekatan terbaik untuk skala proyek ini
(ingat: proyek ini punya batasan sengaja untuk tetap ringan di hardware terbatas).

## Kode Etik

Bersikap hormat dan konstruktif. Proyek ini terbuka untuk kontributor dari semua level
pengalaman.
