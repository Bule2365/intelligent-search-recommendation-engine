import pytest

from app.recommendation_engine.cold_start import (
    is_cold_start_product,
    is_cold_start_user,
    popular_products_fallback,
)
from app.recommendation_engine.collaborative import CollaborativeFilteringRecommender
from app.recommendation_engine.content_based import ContentBasedRecommender
from app.recommendation_engine.hybrid_recommender import HybridRecommender


@pytest.fixture
def sample_products():
    return [
        {
            "product_id": "P1",
            "title": "Sepatu Lari A",
            "category": "Sepatu",
            "brand": "Stridon",
            "price": 200000,
            "rating": 4.5,
            "num_reviews": 500,
        },
        {
            "product_id": "P2",
            "title": "Sepatu Lari B",
            "category": "Sepatu",
            "brand": "Stridon",
            "price": 220000,
            "rating": 4.2,
            "num_reviews": 300,
        },
        {
            "product_id": "P3",
            "title": "Kemeja Pria",
            "category": "Fashion Pria",
            "brand": "Urbano",
            "price": 150000,
            "rating": 4.8,
            "num_reviews": 10,
        },
        {
            "product_id": "P4",
            "title": "Smartphone X",
            "category": "Elektronik",
            "brand": "Zentra",
            "price": 2000000,
            "rating": 4.0,
            "num_reviews": 1000,
        },
    ]


class TestContentBased:
    def test_recommends_same_category_and_brand_higher(self, sample_products):
        rec = ContentBasedRecommender(
            sample_products
        )  # tanpa semantic_search -> fallback atribut
        results = rec.recommend("P1", top_k=5)
        assert results[0].product_id == "P2"  # kategori & brand sama persis

    def test_unknown_product_returns_empty(self, sample_products):
        rec = ContentBasedRecommender(sample_products)
        assert rec.recommend("P999", top_k=5) == []


class TestCollaborativeFiltering:
    def test_co_occurrence_learns_pattern(self, sample_products):
        rec = CollaborativeFilteringRecommender(sample_products)
        # User U1 dan U2 sama-sama berinteraksi dengan P1 & P2 --
        # collaborative filtering harus belajar bahwa P1-P2 sering bersama.
        interactions = {
            "U1": {"P1", "P2"},
            "U2": {"P1", "P2"},
            "U3": {"P3"},
        }
        rec.fit(interactions)
        results = rec.recommend("P1", top_k=5)
        assert results[0].product_id == "P2"

    def test_no_interaction_returns_empty(self, sample_products):
        rec = CollaborativeFilteringRecommender(sample_products)
        rec.fit({})
        assert rec.recommend("P1", top_k=5) == []


class TestColdStart:
    def test_is_cold_start_product_true_when_absent(self):
        assert is_cold_start_product("P999", {}) is True

    def test_is_cold_start_product_false_when_present(self):
        assert is_cold_start_product("P1", {"P1": {"P2": 3}}) is False

    def test_is_cold_start_user(self):
        assert is_cold_start_user("U999", {"U1": {"P1"}}) is True
        assert is_cold_start_user("U1", {"U1": {"P1"}}) is False

    def test_popularity_fallback_uses_bayesian_smoothing(self, sample_products):
        """P3 punya rating tertinggi (4.8) tapi review sangat sedikit (10) --
        Bayesian smoothing (Bagian 8.3) harus mencegahnya otomatis menang
        melawan P4 yang punya 1000 review dengan rating lebih rendah (4.0)."""
        results = popular_products_fallback(sample_products, top_k=4)
        ranked_ids = [r.product_id for r in results]
        # P3 tidak boleh berada di posisi pertama meskipun rating-nya tertinggi
        assert ranked_ids[0] != "P3"

    def test_popularity_fallback_filters_by_category(self, sample_products):
        results = popular_products_fallback(sample_products, category="Sepatu", top_k=5)
        assert all(r.product_id in {"P1", "P2"} for r in results)


class TestHybridRecommender:
    def test_cold_start_product_falls_back_to_content_based(self, sample_products):
        content_rec = ContentBasedRecommender(sample_products)
        collab_rec = CollaborativeFilteringRecommender(sample_products)
        collab_rec.fit({})  # tidak ada interaksi sama sekali -- semua produk cold start

        hybrid = HybridRecommender(content_rec, collab_rec, sample_products)
        results = hybrid.recommend_similar_products("P1", top_k=5)

        # Karena collaborative filtering kosong, hasil harus murni dari content-based
        assert results[0].product_id == "P2"

    def test_cold_start_user_falls_back_to_popularity(self, sample_products):
        content_rec = ContentBasedRecommender(sample_products)
        collab_rec = CollaborativeFilteringRecommender(sample_products)
        collab_rec.fit({})

        hybrid = HybridRecommender(content_rec, collab_rec, sample_products)
        results = hybrid.recommend_for_user("U_NEW", user_interactions={}, top_k=3)

        assert len(results) > 0
        assert all(r.reason.startswith("Produk populer") for r in results)
