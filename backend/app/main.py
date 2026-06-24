from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.db.sqlite_client import db_session, fetch_all_products
from app.recommendation_engine.collaborative import (
    CollaborativeFilteringRecommender,
    build_interaction_matrix,
)
from app.recommendation_engine.content_based import ContentBasedRecommender
from app.recommendation_engine.hybrid_recommender import HybridRecommender
from app.search_engine.bm25_search import BM25Search
from app.search_engine.hybrid_search import HybridSearch
from app.search_engine.keyword_search import KeywordSearch


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] Memuat data produk dari SQLite...")
    with db_session() as conn:
        products = fetch_all_products(conn)
        user_interactions = build_interaction_matrix(conn)

    app.state.products_cache = products
    app.state.products_by_id_cache = {p["product_id"]: p for p in products}
    app.state.user_interactions = user_interactions

    print(f"[startup] Membangun index keyword & BM25 untuk {len(products)} produk...")
    app.state.keyword_search = KeywordSearch(products)
    app.state.bm25_search = BM25Search(products)

    if config.ENABLE_SEMANTIC_SEARCH:
        print(
            f"[startup] Memuat model embedding {config.EMBEDDING_MODEL_NAME} & index LanceDB..."
        )
        from app.search_engine.semantic_search import SemanticSearch

        semantic_search = SemanticSearch(db_path=str(config.LANCEDB_PATH))
        app.state.semantic_search = semantic_search
        app.state.hybrid_search = HybridSearch(
            app.state.bm25_search, semantic_search, alpha=config.DEFAULT_HYBRID_ALPHA
        )
        content_recommender = ContentBasedRecommender(
            products, semantic_search=semantic_search
        )
    else:
        print("[startup] ENABLE_SEMANTIC_SEARCH=false -- berjalan dengan BM25 saja.")
        app.state.semantic_search = None
        app.state.hybrid_search = None
        content_recommender = ContentBasedRecommender(products, semantic_search=None)

    print("[startup] Melatih collaborative filtering dari histori interaksi...")
    collaborative_recommender = CollaborativeFilteringRecommender(products)
    collaborative_recommender.fit(user_interactions)

    app.state.content_recommender = content_recommender
    app.state.collaborative_recommender = collaborative_recommender
    app.state.hybrid_recommender = HybridRecommender(
        content_recommender, collaborative_recommender, products
    )

    print("[startup] Semua engine siap. Aplikasi berjalan.")
    yield
    print("[shutdown] Selesai.")


app = FastAPI(
    title="Intelligent Search & Recommendation Engine for E-Commerce",
    description="Backend API: keyword/BM25/semantic/hybrid search, recommendation, analytics, A/B testing.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # portfolio/local dev -- persempit di production sungguhan
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import (
    analytics,
    events,
    experiments,
    products,
    recommendations,
    search,
    users,
)  # noqa: E402

app.include_router(search.router)
app.include_router(products.router)
app.include_router(recommendations.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(analytics.router)
app.include_router(experiments.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
