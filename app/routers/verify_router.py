from fastapi import APIRouter, HTTPException
from app.processors.verify import SuggestionVerifier
from app.models.verify_models import VerifyRequest, VerifyResponse, VerifiedMovies

router = APIRouter(prefix="/verify", tags=["verify"])

@router.post("/", response_model=VerifiedMovies)
def verify_suggestions(request: VerifyRequest):
    try:
        verifier = SuggestionVerifier()
        result = verifier.verify_suggestions(request.query, request.suggestions)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))