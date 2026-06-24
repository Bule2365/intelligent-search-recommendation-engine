import pytest

from app.search_engine.bm25_search import BM25Search
from app.search_engine.hybrid_search import HybridSearch, min_max_normalize
from app.search_engine.keyword_search import KeywordSearch


@pytest.fixture
def sample_products():
    return [
        {
            "product_id": "P1",
            "title": "Sepatu Lari Ringan",
            "description": "Sepatu untuk lari jarak jauh, ringan dan nyaman.",
            "brand": "Stridon",
            "category": "Sepatu",
        },
        {
            "product_id": "P2",
            "title": "Sepatu Formal Kulit",
            "description": "Sepatu formal untuk kantor, bahan kulit asli.",
            "brand": "Klassio",
            "category": "Sepatu",
        },
        {
            "product_id": "P3",
            "title": "Kemeja Lengan Panjang",
            "description": "Kemeja katun untuk acara formal maupun santai.",
            "brand": "Urbano",
            "category": "Fashion Pria",
        },
        {
            "product_id": "P4",
            "title": "Smartphone Hemat Daya",
            "description": "Smartphone dengan baterai tahan lama dan harga terjangkau.",
            "brand": "Zentra",
            "category": "Elektronik",
        },
    ]


class TestKeywordSearch:
    def test_finds_exact_match(self, sample_products):
        engine = KeywordSearch(sample_products)
        results = engine.search("sepatu lari", top_k=5)
        assert len(results) >= 1
        assert results[0].product_id == "P1"

    def test_no_match_returns_empty(self, sample_products):
        engine = KeywordSearch(sample_products)
        results = engine.search("xyznotfound", top_k=5)
        assert results == []

    def test_equal_match_count_gives_equal_score(self, sample_products):
        """Mendemonstrasikan keterbatasan keyword search (Bagian 7.1):
        dua hasil dengan jumlah kata cocok yang sama mendapat skor identik."""
        engine = KeywordSearch(sample_products)
        results = engine.search("sepatu", top_k=5)
        scores = {r.score for r in results}
        assert len(scores) == 1  # semua skor identik -- inilah masalahnya


class TestBM25Search:
    def test_finds_relevant_product(self, sample_products):
        engine = BM25Search(sample_products)
        results = engine.search("sepatu lari ringan", top_k=5)
        assert results[0].product_id == "P1"

    def test_scores_are_differentiated(self, sample_products):
        """Berbeda dari keyword search, BM25 harus memberi skor granular
        yang membedakan tingkat relevansi (Bagian 7.2.2)."""
        engine = BM25Search(sample_products)
        results = engine.search("sepatu", top_k=5)
        scores = [r.score for r in results]
        assert len(set(scores)) > 1 or len(scores) <= 1

    def test_rare_term_boosts_idf(self, sample_products):
        """Term yang jarang muncul di katalog (mis. 'kulit') harus
        memberi kontribusi skor IDF yang signifikan untuk dokumen yang
        memuatnya."""
        engine = BM25Search(sample_products)
        results = engine.search("kulit", top_k=5)
        assert results[0].product_id == "P2"


class TestHybridSearch:
    def test_min_max_normalize_basic(self):
        scores = {"a": 10.0, "b": 5.0, "c": 0.0}
        normalized = min_max_normalize(scores)
        assert normalized["a"] == 1.0
        assert normalized["c"] == 0.0
        assert normalized["b"] == 0.5

    def test_min_max_normalize_single_value(self):
        """Edge case: hanya 1 hasil -- tidak boleh divide by zero (Bagian 7.4.2)."""
        scores = {"a": 7.0}
        normalized = min_max_normalize(scores)
        assert normalized["a"] == 1.0

    def test_min_max_normalize_empty(self):
        assert min_max_normalize({}) == {}

    def test_hybrid_combines_both_sources(self, sample_products):
        bm25 = BM25Search(sample_products)

        class StubSemantic:
            def search(self, query, top_k=10):
                from app.search_engine.hybrid_search import SearchResult

                return [
                    SearchResult(
                        product_id="P4", score=0.9, title="Smartphone Hemat Daya"
                    )
                ]

        hybrid = HybridSearch(bm25, StubSemantic(), alpha=0.5)
        results = hybrid.search("hp murah", top_k=5)

        # BM25 tidak akan menemukan apapun untuk "hp murah" (vocabulary
        # mismatch, lihat Bagian 7.4.3), tapi semantic stub menemukannya --
        # hasil akhir harus tetap memuat P4 berkat komponen semantic.
        assert any(r.product_id == "P4" for r in results)

    def test_hybrid_alpha_extremes(self, sample_products):
        """alpha=1.0 berarti BM25 murni -- komponen semantic harus diabaikan."""
        bm25 = BM25Search(sample_products)

        class StubSemantic:
            def search(self, query, top_k=10):
                from app.search_engine.hybrid_search import SearchResult

                return [SearchResult(product_id="P3", score=1.0, title="Kemeja")]

        hybrid = HybridSearch(bm25, StubSemantic(), alpha=1.0)
        results = hybrid.search("sepatu lari", top_k=5)
        top_result = results[0]
        assert top_result.product_id == "P1"  # BM25 yang menang, bukan stub semantic
