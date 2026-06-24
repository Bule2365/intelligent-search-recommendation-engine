from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.product_schema import ProductOut

SearchMode = Literal["keyword", "bm25", "semantic", "hybrid"]


class SearchResultItem(BaseModel):
    product_id: str
    score: float
    product: Optional[ProductOut] = None
    # Komponen skor individual -- berguna untuk debugging & transparansi,
    # ditampilkan opsional di UI mode "developer" (Bagian 10).
    bm25_score: Optional[float] = None
    semantic_score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    mode: SearchMode
    total_results: int
    results: list[SearchResultItem]
    took_ms: float
