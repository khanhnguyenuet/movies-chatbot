from fastapi import APIRouter, HTTPException
from processors.keywords import KeywordsExtractor

router = APIRouter(prefix="/keywords", tags=["keywords"])

@router.post("/")
def keyword_extractor(request: str):
    try:
        keyword_extractor = KeywordsExtractor()
        result = keyword_extractor.extract_keywords(request)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))