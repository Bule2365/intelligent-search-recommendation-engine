from fastapi import APIRouter

from app.analytics_engine.event_logger import log_event
from app.db.sqlite_client import db_session
from app.schemas.recommendation_schema import EventAck, EventCreate

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=EventAck)
def create_event(event: EventCreate):
    with db_session() as conn:
        event_id = log_event(
            conn,
            user_id=event.user_id,
            event_type=event.event_type,
            product_id=event.product_id,
            search_query=event.search_query,
        )
    return EventAck(status="logged", event_id=event_id)
