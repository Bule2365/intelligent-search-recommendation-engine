from fastapi import APIRouter, Depends, Query

from app.db.sqlite_client import db_session, fetch_products_by_ids
from app.dependencies import get_hybrid_recommender, get_user_interactions
from app.schemas.product_schema import ProductOut
from app.schemas.recommendation_schema import RecommendationItem, RecommendationResponse

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _attach_products(raw_results) -> list[RecommendationItem]:
    product_ids = [r.product_id for r in raw_results]
    with db_session() as conn:
        products = fetch_products_by_ids(conn, product_ids)
    items = []
    for r in raw_results:
        row = products.get(r.product_id)
        items.append(
            RecommendationItem(
                product_id=r.product_id,
                score=r.score,
                reason=r.reason,
                product=ProductOut(**row) if row else None,
            )
        )
    return items


@router.get("/similar/{product_id}", response_model=RecommendationResponse)
def similar_products(
    product_id: str,
    top_k: int = Query(10, ge=1, le=50),
    hybrid_recommender=Depends(get_hybrid_recommender),
):
    raw_results = hybrid_recommender.recommend_similar_products(product_id, top_k=top_k)
    items = _attach_products(raw_results)
    return RecommendationResponse(
        source="similar_products", total_results=len(items), results=items
    )


@router.get("/user/{user_id}", response_model=RecommendationResponse)
def recommendations_for_user(
    user_id: str,
    top_k: int = Query(10, ge=1, le=50),
    recent_category: str | None = Query(None),
    hybrid_recommender=Depends(get_hybrid_recommender),
    user_interactions=Depends(get_user_interactions),
):
    raw_results = hybrid_recommender.recommend_for_user(
        user_id, user_interactions, top_k=top_k, recent_category=recent_category
    )
    items = _attach_products(raw_results)
    source = "cold_start_fallback" if user_id not in user_interactions else "for_user"
    return RecommendationResponse(
        source=source, total_results=len(items), results=items
    )
