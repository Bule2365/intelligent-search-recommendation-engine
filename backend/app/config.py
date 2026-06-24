import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR.parent / "data"))
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", DATA_DIR / "ecommerce.db"))
LANCEDB_PATH = Path(os.getenv("LANCEDB_PATH", DATA_DIR / "lancedb"))

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# Parameter default search & recommendation -- bisa dioverride lewat query
# parameter API, tapi nilai default tersimpan terpusat di sini.
DEFAULT_TOP_K = 10
DEFAULT_HYBRID_ALPHA = 0.5  # bobot BM25 vs semantic (Bagian 7.4)
DEFAULT_CONTENT_COLLAB_ALPHA = 0.5  # bobot content-based vs collaborative (Bagian 8.4)
CANDIDATE_POOL_SIZE = 50

# Feature flag: nonaktifkan semantic search jika model belum ter-download /
# untuk mempercepat testing tanpa memuat model besar ke memori.
ENABLE_SEMANTIC_SEARCH = os.getenv("ENABLE_SEMANTIC_SEARCH", "true").lower() == "true"
