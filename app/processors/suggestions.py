import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType
)

from models.keywords import Keywords, MoviesProperties

from langchain_core.output_parsers import PydanticOutputParser

class MoviesSuggestions:
    def __init__(self):
        self.index_client = SearchIndexClient(endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
                                              credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.search_client = SearchClient(endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
                                          index_name=self.index_name, 
                                          credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
        
    def __call__(self, request: MoviesProperties) -> dict:
        search_queries = []
        for k, v in request:
            if v is None: continue
            
            if isinstance(v, list):
                query = " and ".join([f"{k}/any(x: x eq '{item}')" for item in v])
                search_queries.append(query)
        
        suggestions, suggestions_list = self._create_suggestions(search_queries)
        return suggestions, suggestions_list
    
    def _create_suggestions(self, search_quies: list, return_search_list=True) -> str:
        suggestions = []
        suggestions_list = []
        for i, query in enumerate(search_quies):
            results = self.search_client.search(search_text="*", filter=query)
            results = list(results)
            if len(results) == 0:
                continue
            suggestions_list += results
            for result in results:
                movie_name = result["names"]
                movie_overview = result["overview"]
                movie_genre = " ".join(result["genre"])
                
                
                format_output = f"""
                Name: {movie_name}, 
                Overview: {movie_overview},
                Genre: {movie_genre},
                """
                suggestions.append(format_output)
        suggestions = "==========\n".join(suggestions)
        if return_search_list:
            return suggestions, suggestions_list
        return suggestions, None