from fastapi import APIRouter, HTTPException
from ..processors.suggestions import MoviesSuggestions
from ..models.keywords import MoviesProperties
from ..processors.keywords import KeywordsExtractor
from ..processors.web_search import WebSearch
from ..models.keywords import MoviesProperties

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

keyword_extractor = KeywordsExtractor()
movies_suggestions = MoviesSuggestions()
web_search = WebSearch()
    
def create_web_search_condition(keywords: MoviesProperties) -> str:
    pass

def create_output(suggestions_list: list) -> str:
    pass

def pipeline(query: str):
    # Extract keywords from the query
    keywords = keyword_extractor.extract_keywords(query)
    
    # Get movie suggestions based on the keywords
    suggestion, suggestions_list = movies_suggestions(keywords)
    
    # Verify the suggestions with query
    is_valid = True
    
    if not is_valid:
        film_condition = create_web_search_condition(keywords)
        # Perform web search
        web_search_result = web_search(film_condition)
        movies_suggestions._update_index(web_search_result)
        
        return create_output(web_search_result)
    
    return create_output(suggestions_list)
    
@router.post("/")
def film_suggestion(query: str):
    try:
        result = pipeline(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))