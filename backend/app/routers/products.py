from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.sqlite_client import db_session
from app.schemas.product_schema import (
    ProductDetailResponse,
    ProductListResponse,
    ProductOut,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    category: str | None = Query(None),
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    where_clauses = []
    params: list = []

    if category:
        where_clauses.append("category = ?")
        params.append(category)
    if min_price is not None:
        where_clauses.append("price >= ?")
        params.append(min_price)
    if max_price is not None:
        where_clauses.append("price <= ?")
        params.append(max_price)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    offset = (page - 1) * page_size

    with db_session() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM products {where_sql}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM products {where_sql} ORDER BY num_reviews DESC LIMIT ? OFFSET ?",
            [*params, page_size, offset],
        ).fetchall()

    items = [ProductOut(**dict(r)) for r in rows]
    return ProductListResponse(total=total, items=items)


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: str):
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"Produk {product_id} tidak ditemukan"
        )
    return ProductDetailResponse(product=ProductOut(**dict(row)))
