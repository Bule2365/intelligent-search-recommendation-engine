from collections import defaultdict
from dataclasses import dataclass

from .cold_start import (
    RecResult,
    is_cold_start_product,
    is_cold_start_user,
    popular_products_fallback,
)


class HybridRecommender:
    def __init__(
        self, content_recommender, collaborative_recommender, products: list[dict]
    ):
        self.content_recommender = content_recommender
        self.collaborative_recommender = collaborative_recommender
        self.products = products

    def recommend_similar_products(
        self, product_id: str, top_k: int = 10
    ) -> list[RecResult]:
        """'Produk yang mirip dengan ini' -- dipakai di halaman detail produk."""
        if is_cold_start_product(
            product_id, self.collaborative_recommender.co_occurrence
        ):
            return self.content_recommender.recommend(product_id, top_k=top_k)

        content_results = self.content_recommender.recommend(product_id, top_k=top_k)
        collab_results = self.collaborative_recommender.recommend(
            product_id, top_k=top_k
        )
        return self._merge(content_results, collab_results, alpha=0.5, top_k=top_k)

    def recommend_for_user(
        self,
        user_id: str,
        user_interactions: dict[str, set[str]],
        top_k: int = 10,
        recent_category: str | None = None,
    ) -> list[RecResult]:
        """'Rekomendasi untuk kamu' -- dipakai di homepage / dashboard user."""
        if is_cold_start_user(user_id, user_interactions):
            return popular_products_fallback(
                self.products, category=recent_category, top_k=top_k
            )

        # Gabungkan rekomendasi dari semua produk yang pernah diinteraksi
        # user, lalu agregasi dan ambil yang paling sering direkomendasikan.
        aggregated: dict[str, RecResult] = {}
        for pid in user_interactions[user_id]:
            for r in self.collaborative_recommender.recommend(pid, top_k=top_k):
                if r.product_id in user_interactions[user_id]:
                    continue  # jangan rekomendasikan produk yang sudah dia interaksi
                if (
                    r.product_id not in aggregated
                    or r.score > aggregated[r.product_id].score
                ):
                    aggregated[r.product_id] = r

        results = sorted(aggregated.values(), key=lambda r: r.score, reverse=True)[
            :top_k
        ]

        if len(results) < top_k:
            # Sinyal collaborative tidak cukup -- lengkapi dengan popularity fallback.
            existing_ids = {r.product_id for r in results} | user_interactions[user_id]
            fallback = popular_products_fallback(self.products, top_k=top_k * 2)
            for r in fallback:
                if r.product_id not in existing_ids:
                    results.append(r)
                if len(results) >= top_k:
                    break

        return results[:top_k]

    @staticmethod
    def _merge(
        content_results: list[RecResult],
        collab_results: list[RecResult],
        alpha: float,
        top_k: int,
    ) -> list[RecResult]:
        scores: dict[str, float] = defaultdict(float)
        titles: dict[str, str] = {}
        reasons: dict[str, str] = {}

        def norm(results):
            if not results:
                return {}
            values = [r.score for r in results]
            lo, hi = min(values), max(values)
            if hi == lo:
                return {r.product_id: 1.0 for r in results}
            return {r.product_id: (r.score - lo) / (hi - lo) for r in results}

        content_norm = norm(content_results)
        collab_norm = norm(collab_results)

        for r in content_results:
            scores[r.product_id] += alpha * content_norm[r.product_id]
            titles[r.product_id] = r.title
            reasons[r.product_id] = r.reason
        for r in collab_results:
            scores[r.product_id] += (1 - alpha) * collab_norm[r.product_id]
            titles[r.product_id] = r.title
            reasons.setdefault(r.product_id, r.reason)

        merged = [
            RecResult(
                product_id=pid, score=score, title=titles[pid], reason=reasons[pid]
            )
            for pid, score in scores.items()
        ]
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged[:top_k]
