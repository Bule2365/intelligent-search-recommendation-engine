# Intelligent Search & Recommendation Engine for E-Commerce

Sistem pencarian dan rekomendasi e-commerce dengan keyword search (BM25), semantic search
(Sentence Transformers), hybrid ranking, collaborative filtering, dan analytics dashboard —
dirancang untuk berjalan sepenuhnya lokal di laptop tanpa GPU (Intel i3 / RAM 8GB).

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen.svg)

## Fitur

- **Keyword Search** — baseline substring matching untuk perbandingan
- **BM25 Search** — keyword ranking production-grade (algoritma yang sama dengan Elasticsearch)
- **Semantic Search** — pencarian berbasis makna dengan Sentence Transformers + LanceDB
- **Hybrid Search** — gabungan BM25 + semantic dengan weighted fusion
- **Content-Based & Collaborative Filtering** — rekomendasi produk serupa & personalisasi
- **Cold Start Handling** — fallback popularity-based untuk user/produk baru
- **Event Tracking & Analytics Dashboard** — funnel, CTR, query terpopuler
- **A/B Testing** — deterministic variant assignment

## Demo

| Search Page                                        | Product Detail            | Analytics Dashboard    |
| -------------------------------------------------- | ------------------------- | ---------------------- |
| Hybrid/BM25/Semantic search dengan skor transparan | Rekomendasi produk serupa | Funnel & CTR real-time |

## Quick Start

```bash
# 1. Clone & setup environment
git clone https://github.com/<username>/ecommerce-search-engine.git
cd ecommerce-search-engine/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Generate & seed data
python scripts/generate_dataset.py --n-products 5000 --n-users 500
python scripts/seed_database.py
python scripts/embed_products.py   # butuh internet sekali untuk unduh model

# 3. Jalankan backend
uvicorn app.main:app --reload --port 8000

# 4. Jalankan frontend (terminal terpisah)
cd ../frontend
python -m http.server 5500
```

Buka `http://localhost:5500/index.html`, atau dokumentasi API otomatis di `http://localhost:8000/docs`.

## Arsitektur

```
Frontend (Vanilla JS) → FastAPI Backend → Search/Recommendation/Analytics Engine → SQLite + LanceDB
```

Lihat dokumentasi arsitektur lengkap di [`docs/architecture.md`](docs/architecture.md).

## Struktur Proyek

```
backend/    FastAPI app, search & recommendation engine, scripts, tests
frontend/   HTML/CSS/JS vanilla (search, product detail, analytics)
data/       Dataset, SQLite database, LanceDB vector index
docs/       Dokumentasi arsitektur & API reference
```

## Testing

```bash
cd backend
pytest tests/ -v --cov=app
```

34 test (unit + integration), 79% code coverage.

## Mengapa Stack Ini?

Setiap keputusan teknologi di proyek ini didasari pertimbangan hardware-aware engineering
(laptop tanpa GPU, RAM 8GB) — bukan kebetulan. Penjelasan lengkap trade-off (kenapa
all-MiniLM-L6-v2, kenapa LanceDB bukan Pinecone, kenapa modular monolith bukan microservices)
ada di dokumentasi Technical Handbook lengkap proyek ini.

## Contributing

Lihat [`CONTRIBUTING.md`](CONTRIBUTING.md) untuk panduan kontribusi.

## License

MIT — lihat [`LICENSE`](LICENSE).
