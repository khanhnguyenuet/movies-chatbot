from pydantic import BaseModel, Field
from typing import Optional, List

class MoviesProperties(BaseModel):
    names: Optional[str] = Field(
        description="The name of the movie",
    )
    date_x: Optional[str] = Field(
        description="The release date of the movie",
    )
    genre: Optional[List[str]] = Field(
        description="The genre of the movie",
    )
    overview: Optional[str] = Field(
        description="A brief overview of the movie",
    )
    status: Optional[bool] = Field(
        description="The status of the movie",
    )
    orig_lang: Optional[List[str]] = Field(
        description="The language of the movie",
    )
    crew: Optional[List[str]] = Field(
        description="The name of actors, directors, and producers in the movie",
    )
    country: Optional[str] = Field(
        description="The country of the movie",
    )
    budget_x: Optional[str] = Field(
        description="The budget of the movie",
    )
    revenue: Optional[str] = Field(
        description="The revenue of the movie",
    )
    
class Keywords(BaseModel):
    search_term: MoviesProperties = Field(
        description="The keywords to search for",
    )
    
class Movies(BaseModel):
    movie_list: Optional[List[MoviesProperties]] = Field(
        description="List of movies",
    )
    
    movie_links: Optional[List[str]] = Field(
        description="The links to the movies"
    )