from dataclasses import dataclass


@dataclass
class SearchResult:
    product_id: str
    score: float
    title: str
    bm25_score: float = 0.0
    semantic_score: float = 0.0


def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    values = list(scores.values())
    lo, hi = min(values), max(values)
    if hi == lo:
        # Semua skor sama (mis. hanya 1 hasil) -- anggap semua maksimal relevan.
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


class HybridSearch:
    def __init__(self, bm25_search, semantic_search, alpha: float = 0.5):
        """
        bm25_search     : instance BM25Search (punya method .search())
        semantic_search : instance SemanticSearch (punya method .search())
        alpha            : bobot BM25 (0..1). (1 - alpha) adalah bobot semantic.
        """
        self.bm25_search = bm25_search
        self.semantic_search = semantic_search
        self.alpha = alpha

    def search(
        self, query: str, top_k: int = 10, candidate_pool: int = 50
    ) -> list[SearchResult]:
        # Ambil kandidat lebih banyak dari masing-masing metode (candidate_pool)
        # sebelum digabung dan dipotong ke top_k -- supaya produk yang kuat di
        # salah satu metode saja tetap punya kesempatan muncul di hasil akhir.
        bm25_results = self.bm25_search.search(query, top_k=candidate_pool)
        semantic_results = self.semantic_search.search(query, top_k=candidate_pool)

        bm25_scores = {r.product_id: r.score for r in bm25_results}
        semantic_scores = {r.product_id: r.score for r in semantic_results}

        bm25_norm = min_max_normalize(bm25_scores)
        semantic_norm = min_max_normalize(semantic_scores)

        titles = {r.product_id: r.title for r in bm25_results}
        titles.update({r.product_id: r.title for r in semantic_results})

        all_ids = set(bm25_norm) | set(semantic_norm)
        combined = []
        for pid in all_ids:
            b = bm25_norm.get(pid, 0.0)
            s = semantic_norm.get(pid, 0.0)
            final = self.alpha * b + (1 - self.alpha) * s
            combined.append(
                SearchResult(
                    product_id=pid,
                    score=final,
                    title=titles[pid],
                    bm25_score=bm25_scores.get(pid, 0.0),
                    semantic_score=semantic_scores.get(pid, 0.0),
                )
            )

        combined.sort(key=lambda r: r.score, reverse=True)
        return combined[:top_k]
