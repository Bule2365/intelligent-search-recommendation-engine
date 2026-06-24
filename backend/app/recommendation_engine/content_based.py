from dataclasses import dataclass


@dataclass
class RecResult:
    product_id: str
    score: float
    title: str
    reason: str


class ContentBasedRecommender:
    def __init__(self, products: list[dict], semantic_search=None):
        """
        products        : list of dict produk
        semantic_search : instance SemanticSearch (opsional). Jika ada,
                           dipakai untuk kemiripan berbasis embedding yang
                           SUDAH dihitung sebelumnya (reuse index LanceDB
                           yang sama dengan search engine -- tidak perlu
                           index terpisah).
        """
        self.products = {p["product_id"]: p for p in products}
        self.semantic_search = semantic_search

    def recommend(self, product_id: str, top_k: int = 10) -> list[RecResult]:
        target = self.products.get(product_id)
        if target is None:
            return []

        if self.semantic_search is not None:
            return self._recommend_by_embedding(target, top_k)
        return self._recommend_by_attributes(target, top_k)

    def _recommend_by_embedding(self, target: dict, top_k: int) -> list[RecResult]:
        # Memakai judul+deskripsi produk sebagai "query" ke index embedding
        # yang sama dipakai semantic search -- elegan karena tidak perlu
        # infrastruktur tambahan.
        query_text = f"{target['title']}. {target['description']}"
        raw = self.semantic_search.search(query_text, top_k=top_k + 1)
        results = [
            RecResult(
                product_id=r.product_id,
                score=r.score,
                title=r.title,
                reason="Mirip secara konten dengan produk yang kamu lihat",
            )
            for r in raw
            if r.product_id != target["product_id"]
        ]
        return results[:top_k]

    def _recommend_by_attributes(self, target: dict, top_k: int) -> list[RecResult]:
        # Fallback tanpa embedding: skor kemiripan berbasis atribut terstruktur.
        candidates = []
        for pid, p in self.products.items():
            if pid == target["product_id"]:
                continue
            score = 0.0
            if p["category"] == target["category"]:
                score += 0.5
            if p["brand"] == target["brand"]:
                score += 0.3
            price_diff_ratio = abs(p["price"] - target["price"]) / max(
                target["price"], 1
            )
            if price_diff_ratio < 0.3:
                score += 0.2 * (1 - price_diff_ratio / 0.3)
            if score > 0:
                candidates.append(
                    RecResult(
                        product_id=pid,
                        score=score,
                        title=p["title"],
                        reason="Kategori/brand/rentang harga serupa",
                    )
                )
        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:top_k]
