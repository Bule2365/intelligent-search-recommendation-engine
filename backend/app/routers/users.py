from fastapi import APIRouter, HTTPException

from app.db.sqlite_client import db_session

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}")
def get_user(user_id: str):
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} tidak ditemukan")
    return dict(row)


@router.get("/{user_id}/history")
def get_user_history(user_id: str, limit: int = 50):
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT e.event_type, e.product_id, e.search_query, e.timestamp, p.title
            FROM events e
            LEFT JOIN products p ON e.product_id = p.product_id
            WHERE e.user_id = ?
            ORDER BY e.timestamp DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return {"user_id": user_id, "history": [dict(r) for r in rows]}
