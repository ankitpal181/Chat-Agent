from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


# Graph state and output schemas
class QueryState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    segment: str
    queries: Annotated[list[BaseMessage], add_messages]

class HeadlinesItemSchema(BaseModel):
    location: str = Field(
        description = "Location of where the incident/event of a single news headline took place"
    )
    text: str = Field(
        description = "Text of a single news headline"
    )
    date: str = Field(
        description = "Date & time, in human readble format, of when the incident/event of a single news headline took place"
    )

class StoriesItemSchema(BaseModel):
    source: str = Field(
        description = "Name of source of the article"
    )
    text: str = Field(
        description = "Text/Content of the article"
    )
    link: str = Field(
        description = "http/hhtps link of the article's full story"
    )

class HeadlinesSchema(BaseModel):
    headlines: List[HeadlinesItemSchema] = Field(description = "List of news headlines")

class StoriesSchema(BaseModel):
    stories: List[StoriesItemSchema] = Field(description = "List of selected headline related articles")
