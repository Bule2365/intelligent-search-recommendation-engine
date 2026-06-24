from fastapi import APIRouter

from app.analytics_engine.ab_testing import experiment_summary, get_or_assign
from app.db.sqlite_client import db_session
from app.schemas.recommendation_schema import (
    ExperimentAssignRequest,
    ExperimentAssignResponse,
)

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.post("/assign", response_model=ExperimentAssignResponse)
def assign_experiment(req: ExperimentAssignRequest):
    with db_session() as conn:
        variant = get_or_assign(conn, req.experiment_id, req.user_id)
    return ExperimentAssignResponse(
        experiment_id=req.experiment_id, user_id=req.user_id, variant=variant
    )


@router.get("/{experiment_id}/summary")
def get_experiment_summary(experiment_id: str):
    with db_session() as conn:
        return {
            "experiment_id": experiment_id,
            "distribution": experiment_summary(conn, experiment_id),
        }
