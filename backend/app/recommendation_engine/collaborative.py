from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RecResult:
    product_id: str
    score: float
    title: str
    reason: str


class CollaborativeFilteringRecommender:
    def __init__(self, products: list[dict]):
        self.titles = {p["product_id"]: p["title"] for p in products}
        self.co_occurrence: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.item_popularity: dict[str, int] = defaultdict(int)

    def fit(self, user_product_interactions: dict[str, set[str]]):
        """
        user_product_interactions: { user_id: {product_id, product_id, ...} }
        Biasanya dibangun dari tabel events (event_type IN ('product_view',
        'purchase')) atau tabel orders -- lihat build_interaction_matrix()
        di bawah.

        Dipanggil sebagai batch job berkala (harian/jam-an), BUKAN saat
        request (Bagian 3.6) -- co-occurrence antar produk berubah perlahan.
        """
        for user_id, product_ids in user_product_interactions.items():
            product_list = list(product_ids)
            for pid in product_list:
                self.item_popularity[pid] += 1
            # Untuk setiap pasangan produk yang sama-sama berinteraksi dengan
            # user ini, naikkan skor co-occurrence keduanya.
            for i, pid_a in enumerate(product_list):
                for pid_b in product_list[i + 1 :]:
                    self.co_occurrence[pid_a][pid_b] += 1
                    self.co_occurrence[pid_b][pid_a] += 1

    def recommend(self, product_id: str, top_k: int = 10) -> list[RecResult]:
        related = self.co_occurrence.get(product_id, {})
        if not related:
            return []

        max_count = max(related.values())
        results = [
            RecResult(
                product_id=pid,
                score=count / max_count,
                title=self.titles.get(pid, pid),
                reason="Sering dilihat/dibeli bersama produk ini",
            )
            for pid, count in related.items()
        ]
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


def build_interaction_matrix(conn) -> dict[str, set[str]]:
    """
    conn: sqlite3.Connection
    Membangun { user_id: {product_id, ...} } dari event product_view,
    add_to_cart, dan purchase (purchase diberi bobot implisit lebih kuat
    dengan dimasukkan dua kali di pemanggil jika perlu).
    """
    rows = conn.execute("""
        SELECT user_id, product_id FROM events
        WHERE event_type IN ('product_view', 'add_to_cart', 'purchase')
          AND product_id IS NOT NULL
        """).fetchall()

    interactions: dict[str, set[str]] = defaultdict(set)
    for user_id, product_id in rows:
        interactions[user_id].add(product_id)
    return interactions
