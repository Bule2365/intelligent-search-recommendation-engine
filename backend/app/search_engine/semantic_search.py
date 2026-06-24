from dataclasses import dataclass

import lancedb
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIM = 384


@dataclass
class SearchResult:
    product_id: str
    score: float  # semakin tinggi semakin relevan (sudah dikonversi dari distance)
    title: str


class SemanticSearch:
    def __init__(
        self, db_path: str = "../../data/lancedb", table_name: str = "products"
    ):
        # Model di-load SEKALI saat startup aplikasi (lihat config.py / main.py
        # di Bagian 9), bukan setiap request -- ini operasi paling mahal
        # (sekitar 90MB RAM, lihat anggaran memori Bagian 3.2).
        self.model = SentenceTransformer(MODEL_NAME)
        self.db = lancedb.connect(db_path)
        self.table = self.db.open_table(table_name)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        # Encode 1 kalimat pendek -- operasi realtime yang murah (Bagian 3.6).
        query_vector = self.model.encode(query, normalize_embeddings=True)

        raw_results = (
            self.table.search(query_vector.tolist())
            .metric("cosine")
            .limit(top_k)
            .to_list()
        )

        results = []
        for r in raw_results:
            # LanceDB mengembalikan _distance (cosine distance, 0 = identik).
            # Kita konversi ke similarity score (1 = identik) supaya konsisten
            # arahnya dengan skor BM25 (semakin besar semakin relevan).
            similarity = 1.0 - r["_distance"]
            results.append(
                SearchResult(
                    product_id=r["product_id"],
                    score=float(similarity),
                    title=r["title"],
                )
            )
        return results


def build_product_table(
    products: list[dict],
    model: SentenceTransformer,
    db_path: str = "../../data/lancedb",
    table_name: str = "products",
    batch_size: int = 32,
):
    """
    Dipanggil dari embed_products.py (script offline, Bagian 7.3.2), BUKAN
    saat request masuk. Encode seluruh katalog dalam batch -- jauh lebih
    cepat di CPU dibanding encode satu per satu (Bagian 3.5).
    """
    texts = [f"{p['title']}. {p['description']}" for p in products]

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True,
    ).astype(
        np.float32
    )  # float32, bukan float64 -- hemat storage (Bagian 3.7)

    data = [
        {
            "product_id": p["product_id"],
            "title": p["title"],
            "vector": embeddings[i].tolist(),
        }
        for i, p in enumerate(products)
    ]

    db = lancedb.connect(db_path)
    db.create_table(table_name, data=data, mode="overwrite")
    return len(data)
