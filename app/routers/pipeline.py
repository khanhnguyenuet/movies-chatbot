from fastapi import APIRouter, HTTPException
from ..processors.suggestions import MoviesSuggestions
from ..models.keywords import MoviesProperties
from ..processors.keywords import KeywordsExtractor
from ..processors.web_search import WebSearch
from ..processors.web_search_agent import AgentSearcher
from ..processors.verify import SuggestionVerifier
from ..models.keywords import MoviesProperties

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

keyword_extractor = KeywordsExtractor()
movies_suggestions = MoviesSuggestions()
web_search = AgentSearcher()
suggestion_verifier = SuggestionVerifier()

def pipeline(query: str):
    # Extract keywords from the query
    keywords = keyword_extractor.extract_keywords(query)
    
    # Get movie suggestions based on the keywords
    suggestion, suggestions_list = movies_suggestions(keywords)
    
    # Verify the suggestions with query
    is_valid = True
    if not suggestion or len(suggestions_list) == 0:
        is_valid = False
    
    verify_rs = suggestion_verifier.verify_suggestions(suggestion, query)
    is_valid = verify_rs.is_suitable
    
    if not is_valid:
        # Perform web search
        suggestion, list_movies = web_search(keywords)
        movies_suggestions._update_index(list_movies)
    
    return suggestion
    
@router.post("/")
def film_suggestion(query: str):
    try:
        result = pipeline(query)
        return {
            "response": result,
            "query": query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))