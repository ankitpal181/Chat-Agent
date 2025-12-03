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
        description = "Date & time, in human readble format, of when the incident/event of a single news headline took\
             place"
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

class InterviewState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    questions: list
    answers: list
    rules: dict

class QuestionsItemSchema(BaseModel):
    question: str = Field(
        description = "The question for which the candidate have to give answer"
    )
    type: str = Field(
        description = "Practical(a coding question or a maths/calculation problem) or Theory(a concept or process\
             explaination)"
    )
    companies: str = Field(
        description = "String of comma seperated names of companies which usually asks this type of questions"
    )

class PerformanceMetricsItemsSchema(BaseModel):
    Confidence: str = Field(
        description = "Assess the level of certainty and clarity in the presentation"
    )
    answering_patterns: str = Field(
        description = "Note any recurring positive or negative habits (e.g., rambling, jumping to conclusions,\
             excellent structuring)"
    )
    clarity_and_completeness_within_time: str = Field(
        description = "Judge whether the candidate was able to clearly and completely explain the solution/concept\
             within the strict 10-minute timeframe"
    )

class EvaluationSchema(BaseModel):
    rating: str = Field(
        description = "Assign a rating to each individual answer: Good, Average, or Bad"
    )
    feedback: str = Field(
        description = "For every answer, provide detailed, actionable feedback. Explain in detail what went wrong\
             (technical inaccuracy, lack of depth, poor structure) and how the answer could have been improved\
                 (specific concepts to mention, better approach, clearer explanation)"
    )
    performance_metrics: List[PerformanceMetricsItemsSchema] = Field(description = "Judge the candidate's performance\
         across the entire interview")
    final_verdict: str = Field(
        description = "Conclude the entire interaction with a clear, unambiguous verdict on the candidate's capability\
             for the desired role. If the verdict is negative ('Not Capable'), you must provide a concise, prioritized\
                 list of key reasons why (e.g., 'Lacks deep knowledge in Distributed Transactions', 'System design\
                     lacked metrics and failure analysis')"
    )

class QuestionsSchema(BaseModel):
    questions: List[QuestionsItemSchema] = Field(description = "List of questions")
