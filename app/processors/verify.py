import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from ..prompts.verify import VERIFY_SYSTEM_PROMPT, VERIFY_SUGGESTION_REQUEST
from ..models.verify_models import VerificationResult
from ..logging import *
from langchain_core.output_parsers import PydanticOutputParser

logger = init_logger(__name__)

class SuggestionVerifier:
    def __init__(self):
        self.client = ChatCompletionsClient(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_OPENAI_API_KEY")),
        )
        
        self.model_name = os.getenv("MODEL_NAME")
        self.parser = self._set_up_parser()
    
    def _set_up_parser(self):
        parser = PydanticOutputParser(pydantic_object=VerificationResult)
        return parser
    
    def _set_up_prompt(self, query: str, suggestions: str):
        message = [
            SystemMessage(content=VERIFY_SYSTEM_PROMPT),
            UserMessage(content=VERIFY_SUGGESTION_REQUEST.format(
                query=query, 
                suggestions=suggestions,
                format_instructions=self.parser.get_format_instructions()
            )),
        ]
        
        return message
    
    @time_logger(logger)
    def verify_suggestions(self, query: str, suggestions: str) -> VerificationResult:
        prompt = self._set_up_prompt(query, suggestions)
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
            result = self.parser.parse(response.choices[0].message.content)
            return result
        else:
            raise ValueError("No response from the model")