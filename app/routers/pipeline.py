from fastapi import APIRouter, HTTPException
from ..processors.pipeline import Pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])
    
pipeline = Pipeline()

@router.post("/")
def film_suggestion(query: str):
    try:
        suggestions, outputs = pipeline(query)
        return {
            "response": outputs,
            "query": query,
            "suggestion": suggestions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))