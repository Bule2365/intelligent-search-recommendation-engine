from fastapi import APIRouter, Query

from app.analytics_engine.aggregator import (
    category_popularity,
    click_through_rate,
    daily_event_counts,
    funnel_summary,
    top_search_queries,
)
from app.db.sqlite_client import db_session

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary():
    with db_session() as conn:
        return {
            "funnel": funnel_summary(conn),
            "click_through_rate": click_through_rate(conn),
            "top_queries": top_search_queries(conn, limit=10),
            "top_categories": category_popularity(conn, limit=10),
        }


@router.get("/queries/top")
def top_queries(limit: int = Query(10, ge=1, le=50)):
    with db_session() as conn:
        return {"queries": top_search_queries(conn, limit=limit)}


@router.get("/timeline")
def event_timeline(days: int = Query(14, ge=1, le=90)):
    with db_session() as conn:
        return {"timeline": daily_event_counts(conn, days=days)}
