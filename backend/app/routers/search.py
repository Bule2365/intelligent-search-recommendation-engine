import time

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.sqlite_client import db_session, fetch_products_by_ids
from app.dependencies import (
    get_bm25_search,
    get_hybrid_search,
    get_keyword_search,
    get_semantic_search,
)
from app.schemas.product_schema import ProductOut
from app.schemas.search_schema import SearchMode, SearchResponse, SearchResultItem

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Query pencarian"),
    mode: SearchMode = Query(
        "hybrid", description="keyword | bm25 | semantic | hybrid"
    ),
    top_k: int = Query(10, ge=1, le=50),
    keyword_search=Depends(get_keyword_search),
    bm25_search=Depends(get_bm25_search),
    semantic_search=Depends(get_semantic_search),
    hybrid_search=Depends(get_hybrid_search),
):
    t0 = time.perf_counter()

    if mode == "keyword":
        # Baseline naif, lihat Bagian 7.1 -- disediakan di API supaya
        # frontend "developer mode" (Bagian 10) bisa menampilkan
        # perbandingan langsung antar metode untuk query yang sama.
        raw_results = keyword_search.search(q, top_k=top_k)
    elif mode == "bm25":
        raw_results = bm25_search.search(q, top_k=top_k)
    elif mode == "semantic":
        if semantic_search is None:
            raise HTTPException(
                status_code=503,
                detail="Semantic search tidak aktif (ENABLE_SEMANTIC_SEARCH=false atau model belum di-load).",
            )
        raw_results = semantic_search.search(q, top_k=top_k)
    else:  # hybrid
        if hybrid_search is None:
            raise HTTPException(
                status_code=503, detail="Hybrid search butuh semantic search aktif."
            )
        raw_results = hybrid_search.search(q, top_k=top_k)

    product_ids = [r.product_id for r in raw_results]
    with db_session() as conn:
        products = fetch_products_by_ids(conn, product_ids)

    results = []
    for r in raw_results:
        product_row = products.get(r.product_id)
        results.append(
            SearchResultItem(
                product_id=r.product_id,
                score=r.score,
                product=ProductOut(**product_row) if product_row else None,
                bm25_score=getattr(r, "bm25_score", None),
                semantic_score=getattr(r, "semantic_score", None),
            )
        )

    took_ms = (time.perf_counter() - t0) * 1000
    return SearchResponse(
        query=q,
        mode=mode,
        total_results=len(results),
        results=results,
        took_ms=round(took_ms, 2),
    )
