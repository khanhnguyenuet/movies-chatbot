import os
from typing import overload
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

from openai import AzureOpenAI
import random
import string

from ..models.keywords import Keywords, MoviesProperties, Movies
from ..logging import *

from langchain_core.output_parsers import PydanticOutputParser

logger = init_logger(__name__)

class EmbeddingModel:
    def __init__(self):
        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_API_KEY")
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
        
        return response.data[0].embedding

class MoviesSuggestions:
    def __init__(self):
        self.index_client = SearchIndexClient(endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
                                              credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.search_client = SearchClient(endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
                                          index_name=self.index_name, 
                                          credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
        self.embedding_service = EmbeddingModel()
    
    @time_logger(logger)   
    def __call__(self, request: MoviesProperties) -> dict:
        logger.info(f"Create search condition")
        filter_queries, search_queries, return_field = self._create_search_query(request)
        logger.info(f"Find total {len(search_queries)} SEARCH QUERIES")
        logger.info(f"Find total {len(filter_queries)} FILTER QUERIES")
        logger.info("=================")
        
        suggestions, suggestions_list = self._create_suggestions(filter_queries, search_queries, return_field)
        return suggestions, suggestions_list
    
    @staticmethod
    def standardize_string(input_str):
        parts = [part.strip().title() for part in input_str.split(',')]
        return ', '.join(parts)
    
    @staticmethod
    def generate_custom_id(length=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def _create_search_query(self, request: MoviesProperties) -> list:
        request_obj = request.model_dump()
        return_field = list(request_obj.keys())
        
        search_queries = []
        filter_queries = []
        
        for k, v in request_obj.items():
            if v is None: continue
            
            if isinstance(v, list) and (k == "genre" or k == "crew" or k == "orig_lang"):
                filter_query = " or ".join([f"{k}/any(x: x eq '{self.standardize_string(item)}')" for item in v])
                filter_queries.append(filter_query)
            elif isinstance(v, str) and k == "overview":
                logger.info(f"Create embedding for overview")
                embed_vector = self.embedding_service.generate_embedding(v)
                vector_query = VectorizedQuery(vector=embed_vector, k_nearest_neighbors=3, fields="overview_embedding")
                search_queries.append(vector_query)
            elif isinstance(v, str) and k == "names":
                pass
        
        return filter_queries, search_queries, return_field
    
    # def _create_suggestions(self, search_quies: list, return_search_list=True) -> str:
    #     suggestions = []
    #     suggestions_list = []
    #     for i, query in enumerate(search_quies):
    #         results = self.search_client.search(search_text="*", filter=query)
    #         results = list(results)
    #         if len(results) == 0:
    #             logger.info(f"Query {i}: {query} // No results found")
    #             continue
            
    #         logger.info(f"Query {i}: {query} // Found {len(results)} results")
    #         suggestions_list += results
    #         for result in results:
    #             movie_name = result["names"]
    #             movie_overview = result["overview"]
    #             movie_genre = ", ".join(result["genre"])
    #             movie_actor = ", ".join(result["crew"])
                
    #             format_output = f"""
    #             Name: {movie_name}, 
    #             Overview: {movie_overview},
    #             Genre: {movie_genre},
    #             Actor: {movie_actor},
    #             """
    #             suggestions.append(format_output)
        
    #     if len(suggestions) > 0:
    #         suggestions = "==========\n".join(suggestions)
    #     else:
    #         logger.info("No suitable movie found")
    #         suggestions = None
            
    #     if return_search_list:
    #         return suggestions, suggestions_list
    #     return suggestions, None

    def _create_suggestions(self, filter_queries, search_queries, return_field, return_search_list=True) -> str:
        filter_query = " and ".join(filter_queries) if len(filter_queries) > 0 else None
        search_query = search_queries if len(search_queries) > 0 else None
            
        search_results = self.search_client.search(search_text="*",
                                                   filter=filter_query,
                                                   vector_queries=search_query,
                                                   top=5)
        search_results = list(search_results)
        if len(search_results) == 0:
            logger.info("No suitable movie found")
            return None, None
        
        logger.info(f"Found {len(search_results)} results")
        suggestions = []
        movie_list = []
        for result in search_results:
            sub_rs = {key: result[key] for key in return_field}
            movie_list.append(sub_rs)
            
            movie_name = result["names"]
            movie_overview = result["overview"]
            movie_genre = ", ".join(result["genre"])
            movie_actor = ", ".join(result["crew"])
            
            format_output = f"""
            Name: {movie_name}, 
            Overview: {movie_overview},
            Genre: {movie_genre},
            Actor: {movie_actor},
            """
            suggestions.append(format_output)
        
        movie_links = ["None"] * len(movie_list)
        search_results = Movies(movie_list=movie_list, movie_links=movie_links)
        suggestions = "==========\n".join(suggestions)

        return suggestions, search_results

    def _update_index(self, movie: Movies):
        list_movies = movie.movie_list
        documents = []
        for idx, m in enumerate(list_movies):
            document = {
                "id": self.generate_custom_id(),
                "names": m.names,
                "date_x": m.date_x,
                "score": 100.0,
                "crew": m.crew,
                "orig_title": m.names,
                "status": m.status,
                "budget_x": m.budget_x,
                "revenue": m.revenue,
                "overview": m.overview,
                "genre": m.genre,
                "orig_lang": m.orig_lang,
                "country": m.country,
            }  
            documents.append(document)
        
        if len(documents) == 0:
            logger.info("No movies to update")
            return
        
        self.search_client.upload_documents(documents)