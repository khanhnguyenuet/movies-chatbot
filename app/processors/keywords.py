import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from ..prompts.keywords import KEYWORDS_SYSTEM_PROMPT, KEYWORDS_REQUEST
from ..models.keywords import Keywords, MoviesProperties

from langchain_core.output_parsers import PydanticOutputParser

class KeywordsExtractor:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_OPENAI_API_KEY")),
        )
        
        self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
        self.parser = self._set_up_parser()
        
    
    def _set_up_prompt(self, query: str):
        message = [
            SystemMessage(content=KEYWORDS_SYSTEM_PROMPT),
            UserMessage(content=KEYWORDS_REQUEST.format(query=query, format_instructions=self.parser.get_format_instructions())),
        ]
        
        return message
    
    def _set_up_parser(self):
        parser = PydanticOutputParser(pydantic_object=Keywords)
        return parser
    
    def extract_keywords(self, query) -> MoviesProperties:
        prompt = self._set_up_prompt(query)
        response = self.client.complete(
            model=self.model_name,
            messages=prompt,
            max_tokens=500,
            temperature=0.1,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        
        if response:
            keywords = self.parser.parse(response.choices[0].message.content)
            return keywords.search_term
        else:
            raise ValueError("No response from the model")