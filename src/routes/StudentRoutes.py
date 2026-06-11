from fastapi import APIRouter, HTTPException
from src.controller.StudentController import InternshipRecommender
from src.models.student import InternshipRecommendationRequest
import logging

logger = logging.getLogger("student_api")

router = APIRouter()
recommender = InternshipRecommender()


@router.post("/recommendations")
async def get_internship_recommendations(
    data: InternshipRecommendationRequest
):
    try:

        payload = data.model_dump()

        top_matches = recommender.recommend(
            payload
        )

        return {
            "success": True,
            "studentName": data.student.name,
            "resultsCount": len(top_matches),
            "recommendations": top_matches
        }

    except Exception as e:
        logger.error(
            f"Recommendation Engine Error: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate recommendations. Please try again."
        )