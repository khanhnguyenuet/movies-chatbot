from typing import List, Optional

from pydantic import BaseModel, Field


class Keywords(BaseModel):
    search_term: List[str] = Field(
        description="The keywords to search for",
    )