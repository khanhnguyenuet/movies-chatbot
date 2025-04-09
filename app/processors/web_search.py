import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool
from azure.core.credentials import AzureKeyCredential

from ..prompts.web_search import REQUEST
from ..models.keywords import Movies
from langchain_core.output_parsers import PydanticOutputParser

class WebSearch:
    def __init__(self):
        self.client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.getenv("PROJECT_CONNECTION_STRING"),
        )
        self.agent = self.client.agents.get_agent(os.getenv("BING_AGENT_ID"))
        self.parser = self._set_up_parser()
        
    def __call__(self, condition: str) -> Movies:
        # Create thread
        thread = self.client.agents.create_thread()
        
        # Create input query
        message = self.client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=REQUEST.format(condition=condition, instruction=self.parser.get_format_instructions()),
        )
        
        # Run thread
        run = self.client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=self.agent.id
        )
        
        # Get output
        messages = self.client.agents.list_messages(thread_id=thread.id)
        output = messages.text_messages[0].as_dict()["text"]["value"]
        
        # Delete thread
        self.client.agents.delete_thread(thread_id=thread.id)
        return self.parser.parse(output)
        
        
    def _set_up_parser(self,):
        parser = PydanticOutputParser(pydantic_object=Movies)
        return parser
        