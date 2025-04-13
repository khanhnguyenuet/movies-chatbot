from pydantic import BaseModel, Field
from typing import List
from ..models.keywords import MoviesProperties, Movies

class VerifyRequest(BaseModel):
    query: str = Field(..., description="The original user query asking for movie recommendations")
    suggestions: Movies = Field(..., description="The list of suggested movies to verify")

class VerifyResponse(BaseModel):
    is_suitable: bool = Field(..., description="Whether the suggestions are suitable for the user's query")
    reason: str = Field(..., description="Brief explanation of why the suggestions are suitable or not")
    
class Verification(MoviesProperties):
    is_suitable: bool = Field(
        description="Whether the suggestions are suitable for the user's query (True/False)"
    )
    reason: str = Field(
        description="Brief explanation of why the suggestions are suitable or not"
    )
    
class VerifiedMovies(BaseModel):
    verified_movies: List[Verification] = Field(
        description="List of verified movies with their suitability and reasoning"
    )