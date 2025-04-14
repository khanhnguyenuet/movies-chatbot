from ..processors.suggestions import MoviesSuggestions
from ..processors.keywords import KeywordsExtractor
from ..processors.web_search import WebSearch
from ..processors.web_search_agent import AgentSearcher
from ..processors.verify import SuggestionVerifier

from ..models.keywords import MoviesProperties
from ..models.verify_models import VerifyRequest, VerifyResponse, VerifiedMovies

from ..logging import *

logger = init_logger(__name__)

class Pipeline:
    def __init__(self):
        self.keyword_extractor = KeywordsExtractor()
        self.movies_suggestions = MoviesSuggestions()
        self.web_search = AgentSearcher()
        self.suggestion_verifier = SuggestionVerifier()
    
    @time_logger(logger)
    def __call__(self, query: str):
        # Extract keywords from the query
        logger.info(f"Extract keywords from query")
        keywords = self.keyword_extractor.extract_keywords(query)
        
        # Get movie suggestions based on the keywords
        suggestion, suggestions_list = self.movies_suggestions(keywords)
        
        # Verify the suggestions with query
        is_valid = False
        if suggestion is not None and suggestions_list is not None:
            verify_rs = self.suggestion_verifier.verify_suggestions(query, suggestions_list)
            valid_movies = [movie for movie in verify_rs.verified_movies if movie.is_suitable]    
            is_valid = len(valid_movies) > 0
        
        if not is_valid:
            # Perform web search
            suggestion, list_movies = self.web_search(keywords)
            self.movies_suggestions._update_index(list_movies)
            valid_movies = [
                movie for movie in list_movies.movie_list
            ]
        
        return suggestion, self._format_output(valid_movies)
    
    def _format_output(self, valid_movies: list):
        formatted_movies = []
        for movie in valid_movies:
            json_obj = movie.model_dump()
            formatted_movie = {
                "title": json_obj["names"],
                "overview": json_obj["overview"],
                "genre": ", ".join(json_obj["genre"]),
                "actor": ", ".join(json_obj["crew"]),
                "rating": json_obj["score"],
                "release_date": json_obj["date_x"],
                "language": ", ".join(json_obj["orig_lang"]),
                "contry": json_obj["country"],
            }
            formatted_movies.append(formatted_movie)
        return formatted_movies