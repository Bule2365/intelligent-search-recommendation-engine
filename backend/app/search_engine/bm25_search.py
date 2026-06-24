import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass
class SearchResult:
    product_id: str
    score: float
    title: str


class BM25Search:
    """
    Index dibangun SEKALI saat startup (lihat build_bm25_index.py untuk versi
    offline), bukan setiap request -- prinsip precompute vs realtime di
    Bagian 3.6.
    """

    def __init__(self, products: list[dict]):
        self.products = products
        self.product_ids = [p["product_id"] for p in products]
        self.titles = [p["title"] for p in products]

        corpus = [
            tokenize(f"{p['title']} {p['description']} {p['brand']} {p['category']}")
            for p in products
        ]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        # Ambil top_k index dengan skor tertinggi tanpa full sort O(n log n)
        # kalau n besar -- untuk skala portfolio (puluhan ribu produk) full
        # sort masih cukup cepat, tapi argpartition lebih scalable.
        ranked_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            :top_k
        ]

        results = []
        for i in ranked_idx:
            if scores[i] <= 0:
                continue
            results.append(
                SearchResult(
                    product_id=self.product_ids[i],
                    score=float(scores[i]),
                    title=self.titles[i],
                )
            )
        return results
