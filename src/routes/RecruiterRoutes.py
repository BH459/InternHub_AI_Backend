from fastapi import APIRouter, HTTPException
from src.controller.RecruiterController import CandidateRanker
from src.models.recruiter import RecruiterRankRequest
import logging

logger = logging.getLogger("recruiter_api")

router = APIRouter()


@router.post("/rank")
async def recruiter_rank(data: RecruiterRankRequest):
    try:
        payload = data.model_dump()

        custom_weights = (
            payload.get("config", {})
            .get("systemWeights")
        )

        ranker = CandidateRanker(
            config_weights=custom_weights
        )

        ranking = ranker.rank(payload)

        return {
            "success": True,
            "totalInput": len(payload.get("candidates", [])),
            "passedFilters": len(ranking),
            "ranking": ranking
        }

    except Exception as e:
        logger.error(
            f"Recruiter AI Processing Error: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while processing student rankings."
        )