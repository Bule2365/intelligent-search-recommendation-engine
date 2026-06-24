from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.product_schema import ProductOut


class RecommendationItem(BaseModel):
    product_id: str
    score: float
    reason: str
    product: Optional[ProductOut] = None


class RecommendationResponse(BaseModel):
    source: str  # "similar_products" | "for_user" | "cold_start_fallback"
    total_results: int
    results: list[RecommendationItem]


EventType = Literal[
    "search_performed", "product_view", "product_click", "add_to_cart", "purchase"
]


class EventCreate(BaseModel):
    user_id: str
    event_type: EventType
    product_id: Optional[str] = None
    search_query: Optional[str] = None


class EventAck(BaseModel):
    status: Literal["logged"]
    event_id: int


class ExperimentAssignRequest(BaseModel):
    experiment_id: str
    user_id: str


class ExperimentAssignResponse(BaseModel):
    experiment_id: str
    user_id: str
    variant: str
