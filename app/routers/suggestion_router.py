from fastapi import APIRouter, HTTPException
from processors.suggestions import MoviesSuggestions
from models.keywords import MoviesProperties

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

@router.post("/")
def film_filter(request: MoviesProperties):
    try:
        movies_suggestions = MoviesSuggestions()
        suggestion, suggestions_list = movies_suggestions(request)
        return {
            "suggestion": suggestion,
            "suggestions_list": suggestions_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))