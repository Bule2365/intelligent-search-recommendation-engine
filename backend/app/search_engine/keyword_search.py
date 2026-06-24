from dataclasses import dataclass


@dataclass
class SearchResult:
    product_id: str
    score: float
    title: str


class KeywordSearch:
    def __init__(self, products: list[dict]):
        """products: list of dict dengan key product_id, title, description."""
        self.products = products

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        query_lower = query.lower()
        query_terms = query_lower.split()
        results = []

        for p in self.products:
            haystack = f"{p['title']} {p['description']}".lower()
            # Skor naif: jumlah query term yang muncul di haystack.
            matches = sum(1 for term in query_terms if term in haystack)
            if matches > 0:
                results.append(
                    SearchResult(
                        product_id=p["product_id"],
                        score=float(matches),
                        title=p["title"],
                    )
                )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
