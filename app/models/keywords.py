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
        description="The LIST of genre of the movie",
    )
    overview: Optional[str] = Field(
        description="A brief overview of the movie",
    )
    status: Optional[str] = Field(
        description="The status of the movie (Released, Upcoming, etc.)",
    )
    orig_lang: Optional[List[str]] = Field(
        description="The The LIST of language of the movie",
    )
    crew: Optional[List[str]] = Field(
        description="The The LIST of name of actors, directors, and producers in the movie",
    )
    country: Optional[str] = Field(
        description="The country of the movie represent by the country code",
    )
    budget_x: Optional[float] = Field(
        description="The budget of the movie",
    )
    revenue: Optional[float] = Field(
        description="The revenue of the movie",
    )
    score : Optional[float] = Field(
        description="The rating score of the movie",
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