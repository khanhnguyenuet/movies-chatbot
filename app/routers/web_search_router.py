from fastapi import APIRouter, HTTPException
from ..processors.web_search import WebSearch
from ..processors.web_search_agent import AgentSearcher
from ..models.keywords import MoviesProperties

router = APIRouter(prefix="/web_search", tags=["web_search"])

@router.post("/")
def film_search(keywords: MoviesProperties):
    try:
        web_search = AgentSearcher()
        suggestions, search_rs = web_search(keywords)
        return search_rs.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))