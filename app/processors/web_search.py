import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool, MessageRole
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage

from ..prompts.web_search import REQUEST, MOVIE_FORMAT_SYSTEM, MOVIE_FORMAT_REQUEST
from ..models.keywords import Movies, MoviesProperties
from ..logging import *
from langchain_core.output_parsers import PydanticOutputParser

logger = init_logger(__name__)

class OutputFormatter:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_OPENAI_API_KEY")),
        )
        
        self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
        self.parser = self._set_up_parser()
        
    def _set_up_prompt(self, query: str):
        message = [
            SystemMessage(content=MOVIE_FORMAT_SYSTEM),
            UserMessage(content=MOVIE_FORMAT_REQUEST.format(query=query, format_instructions=self.parser.get_format_instructions())),
        ]
        
        return message
    
    def _set_up_parser(self):
        parser = PydanticOutputParser(pydantic_object=Movies)
        return parser
    
    @time_logger(logger)
    def format_output(self, query) -> MoviesProperties:
        prompt = self._set_up_prompt(query)
        response = self.client.complete(
            model=self.model_name,
            messages=prompt,
            max_tokens=1000,
            temperature=0.1,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        
        if response:
            output = self.parser.parse(response.choices[0].message.content)
            return output
        else:
            raise ValueError("No response from the model")

class WebSearch:
    def __init__(self):
        self.formatter = OutputFormatter()
    
    @time_logger(logger)
    def __call__(self, keywords: MoviesProperties) -> Movies:
        # Create client
        client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.getenv("PROJECT_CONNECTION_STRING"),
        )
        
        # Create Bing Search Tool
        logger.info(f"Create Bing Search Tool")
        bing_connection = client.connections.get(connection_name=os.getenv("BING_CONNECTION_NAME"))
        conn_id = bing_connection.id
        bing = BingGroundingTool(connection_id=conn_id)
        
        # Create condition
        logger.info(f"Create condition to search")
        condition = self._create_condition(keywords)
        logger.info(f"Condition: {condition}")
        
        output_mess, annotaion = self._run_client(client, bing, condition)
        if not output_mess:
            search_results = self.formatter.format_output(output_mess)
        else:
            search_results = []
        
        # Get suggestions
        suggestions, _ = self._create_output(search_results)
        return suggestions, search_results
        
    def _run_client(self, client, tool, condition):
        with client:
            agent = client.agents.create_agent(
                model=os.getenv("AGENT_MODEL_NAME"),
                name="my-assistant",
                instructions="You are a helpful assistant",
                tools=tool.definitions,
                headers={"x-ms-enable-preview": "true"},
            )
            
            logger.info(f"Created agent, ID: {agent.id}")

            # Create thread for communication
            thread = client.agents.create_thread()
            logger.info(f"Created thread, ID: {thread.id}")

            # Create message to thread
            message = client.agents.create_message(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=REQUEST.format(condition=condition),
            )
            logger.info(f"Created message, ID: {message.id}")

            # Create and process agent run in thread with tools
            run = client.agents.create_and_process_run(thread_id=thread.id, 
                                                    agent_id=agent.id,
                                                    temperature=0.5,
                                                    top_p=0.9,
                                                    max_completion_tokens=1000,
                    )
            logger.info(f"Run finished with status: {run.status}")

            if run.status == "failed":
                logger.info(f"Run failed: {run.last_error}")

            # Delete the assistant when done
            client.agents.delete_agent(agent.id)
            logger.info("Deleted agent")

            # Print the Agent's response message with optional citation
            response_message = client.agents.list_messages(thread_id=thread.id).get_last_message_by_role(
                MessageRole.AGENT
            )
            
            if response_message:
                txt_mess = response_message.text_messages[0].text.value
                annotation = response_message.url_citation_annotations[0].url_citation
            else:
                txt_mess = None
                annotation = None
                
        
        return txt_mess, annotation
                
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
        
        if isinstance(search_results, list):
            return suggestions, suggestions_list
        
        for movie in search_results.movie_list:
            movie_info = f"Name: {movie.name}\n"
            if movie.genre:
                genre = ", ".join(movie.genre)
                movie_info += f"Genre: {genre}\n"
            if movie.overview:
                movie_info += f"Overview: {movie.overview}\n"
            if movie.status:
                movie_info += f"Status: {'yes' if movie.status else 'no'}\n"
            if movie.crews:
                crews = ", ".join(movie.crews)
                movie_info += f"Actors: {crews}\n"
            
            suggestions.append(movie_info)
            suggestions_list.append(movie)
            
        if len(suggestions) > 0:
            suggestions = "==========\n".join(suggestions)
        else:
            logger.info("No suitable movie found")
        
        return suggestions, suggestions_list