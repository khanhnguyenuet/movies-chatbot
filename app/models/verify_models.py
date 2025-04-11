from pydantic import BaseModel, Field
from typing import List

class VerifyRequest(BaseModel):
    query: str = Field(..., description="The original user query asking for movie recommendations")
    suggestions: str = Field(..., description="The list of suggested movies to verify")

class VerifyResponse(BaseModel):
    is_suitable: bool = Field(..., description="Whether the suggestions are suitable for the user's query")
    reason: str = Field(..., description="Brief explanation of why the suggestions are suitable or not")
    
class VerificationResult(BaseModel):
    is_suitable: bool = Field(
        description="Whether the suggestions are suitable for the user's query (True/False)"
    )
    reason: str = Field(
        description="Brief explanation of why the suggestions are suitable or not"
    )