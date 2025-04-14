import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool, MessageRole
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage

from ..prompts.web_search import REQUEST, SEARCH_SYSTEM_PROMPT
from ..models.keywords import Movies, MoviesProperties
from ..logging import *
from langchain_core.output_parsers import PydanticOutputParser

logger = init_logger(__name__)

class AgentSearcher:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_OPENAI_API_KEY")),
        )
        
        self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
        self.parser = self._set_up_parser()
    
    @time_logger(logger)
    def __call__(self, keywords: MoviesProperties):
        # Create search condition
        logger.info(f"Create search condition")
        query = self._create_condition(keywords)
        logger.info(f"Condition filter: {query}")
        
        # Set up prompt        
        prompt = self._set_up_prompt(query)
        
        # Search
        logger.info(f"Searching results ...")
        search_results = self.search(prompt)
        
        # Format output
        suggestions, _ = self._create_output(search_results=search_results)
        return suggestions, search_results
        
    def _set_up_prompt(self, query: str):
        message = [
            SystemMessage(content=SEARCH_SYSTEM_PROMPT),
            UserMessage(content=REQUEST.format(condition=query, format_instructions=self.parser.get_format_instructions())),
        ]
        
        return message
    
    def _set_up_parser(self):
        parser = PydanticOutputParser(pydantic_object=Movies)
        return parser
    
    @time_logger(logger)
    def search(self, prompt) -> Movies:
        num_call = 3
        success = False
        while not success and num_call > 0:
            response = self.client.complete(
                model=self.model_name,
                messages=prompt,
                max_tokens=2000,
                temperature=.3,
                top_p=.95,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            
            if response:
                try:
                    output = self.parser.parse(response.choices[0].message.content)
                    success = True
                    return output
                except Exception as e:
                    logger.error(f"Error parsing response: {e}")
                    num_call -= 1
                    if num_call == 0:
                        raise ValueError("Failed to parse response after multiple attempts")
            else:
                raise ValueError("No response from the model")
      
    def _create_condition(self, keywords: MoviesProperties) -> str:
        condition = ""
        for k, v in keywords.model_dump().items():
            if isinstance(v, list):
                term = ", ".join(v)
                condition += f"{k}: {term}\n"
            elif isinstance(v, str):
                condition += f"{k}: {v}\n"
            elif isinstance(v, bool):
                condition += f"{k}: {'yes' if v else 'no'}\n"
                
        return condition
        
    def _create_output(self, search_results: Movies) -> str:
        suggestions = []
        suggestions_list = []
        
        for movie in search_results.movie_list:
            movie_info = f"Name: {movie.names}\n"
            if movie.genre:
                genre = ", ".join(movie.genre)
                movie_info += f"Genre: {genre}\n"
            if movie.overview:
                movie_info += f"Overview: {movie.overview}\n"
            if movie.status:
                movie_info += f"Status: {movie.status}\n"
            if movie.crew:
                crews = ", ".join(movie.crew)
                movie_info += f"Actors: {crews}\n"
            
            suggestions.append(movie_info)
            suggestions_list.append(movie)
            
        if len(suggestions) > 0:
            suggestions = "==========\n".join(suggestions)
        else:
            logger.info("No suitable movie found")
        
        return suggestions, suggestions_list