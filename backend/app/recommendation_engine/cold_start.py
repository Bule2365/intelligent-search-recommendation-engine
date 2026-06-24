from dataclasses import dataclass


@dataclass
class RecResult:
    product_id: str
    score: float
    title: str
    reason: str


def is_cold_start_product(product_id: str, co_occurrence_index: dict) -> bool:
    return product_id not in co_occurrence_index or not co_occurrence_index[product_id]


def is_cold_start_user(user_id: str, user_interactions: dict) -> bool:
    return user_id not in user_interactions or not user_interactions[user_id]


def popular_products_fallback(
    products: list[dict], category: str | None = None, top_k: int = 10
) -> list[RecResult]:
    """
    Skor popularitas sederhana: gabungan rating dan jumlah review, dengan
    Bayesian-ish smoothing supaya produk dengan 2 review rating 5.0 tidak
    mengalahkan produk dengan 500 review rating 4.6 (masalah klasik
    "small sample size bias").
    """
    pool = [p for p in products if category is None or p["category"] == category]

    # Bayesian average: gabungkan rating produk dengan rating rata-rata
    # keseluruhan (prior), dibobot oleh jumlah review (confidence).
    global_avg = sum(p["rating"] for p in pool) / len(pool) if pool else 0
    C = 50  # confidence constant -- semakin besar, semakin butuh banyak review untuk dipercaya penuh

    scored = []
    for p in pool:
        v = p["num_reviews"]
        r = p["rating"]
        bayesian_score = (v / (v + C)) * r + (C / (v + C)) * global_avg
        scored.append(
            RecResult(
                product_id=p["product_id"],
                score=bayesian_score,
                title=p["title"],
                reason="Produk populer"
                + (f" di kategori {category}" if category else ""),
            )
        )

    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_k]
