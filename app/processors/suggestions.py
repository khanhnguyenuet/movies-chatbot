import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType
)

from openai import AzureOpenAI
from uuid import uuid4

from ..models.keywords import Keywords, MoviesProperties, Movies

from langchain_core.output_parsers import PydanticOutputParser

class EmbeddingModel:
    def __init__(self):
        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",
            endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_API_KEY"))
        )
        
        self.deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME")
        self.model_version = os.getenv("EMBEDDING_MODEL_VERSION")
        
    def generate_embedding(self, input_txts):
        if isinstance(input_txts, str):
            input_txts = [input_txts]
            
        response = self.client.embeddings.create(
            input=input_txts,
            model=self.deployment_name
        )
        
        return response

class MoviesSuggestions:
    def __init__(self):
        self.index_client = SearchIndexClient(endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
                                              credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.search_client = SearchClient(endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
                                          index_name=self.index_name, 
                                          credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
        self.embedding_service = EmbeddingModel()
        
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
    
    def _update_index(self, movie: Movies):
        list_movies = movie.movie_list
        documents = []
        for m in list_movies:
            document = {
                "id": uuid4(),
                "names": m.name,
                "date_x": m.date,
                "score": m.score,
                "crew": m.crews,
                "orig_title": m.name,
                "status": m.status,
                "budget_x": m.budget,
                "revenue": m.revenue,
                "overview": m.overview,
                "genre": m.genre,
                "orig_lang": m.lang,
                "country": m.country,
            }  
            documents.append(document)
            
        self.search_client.upload_documents(documents)