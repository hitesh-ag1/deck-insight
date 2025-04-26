from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional

class ExtractSchema(BaseModel):
    repository: str = Field(default=None, alias="Repository Name", description="Repository Name")
    stars: str = Field(default=None, alias="Number of stars", description="Number of stars")
    forks: str = Field(default=None, alias="Number of forks", description="Number of forks")
    link: str = Field(default=None, alias="Link of repository", description="Link of repository")

class Repositories(BaseModel):
    repo: List[ExtractSchema]

class GraphState(TypedDict):
    link: str
    repo: Optional[List[ExtractSchema]]
    error: Optional[str]