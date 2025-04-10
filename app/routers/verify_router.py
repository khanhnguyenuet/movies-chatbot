from fastapi import APIRouter, HTTPException
from app.processors.verify import SuggestionVerifier
from app.models.verify_models import VerifyRequest, VerifyResponse

router = APIRouter(prefix="/verify", tags=["verify"])

@router.post("/", response_model=VerifyResponse)
def verify_suggestions(request: VerifyRequest):
    try:
        verifier = SuggestionVerifier()
        result = verifier.verify_suggestions(request.query, request.suggestions)
        return {
            "is_suitable": result.is_suitable,
            "reason": result.reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))