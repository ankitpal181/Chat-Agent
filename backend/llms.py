import os
from .tools import search_internet, generate_csv_tool, generate_pdf_tool
from pydantic import BaseModel
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI


class Model:
    def __init__(self, output_schema: BaseModel = None) -> None:
        self.tools = [search_internet, generate_csv_tool, generate_pdf_tool]

        if os.environ.get("OPENAI_API_KEY"):
            self.model = self._set_openai_model(output_schema)
        else:
            self.model = self._set_gemini_model(output_schema)
    
    def _set_openai_model(self, output_schema: BaseModel) -> ChatOpenAI:
        model = ChatOpenAI(model = os.environ.get("LLM_MODEL_NAME", ""))
        model = model.bind_tools(self.tools)

        if output_schema: model = model.with_structured_output(output_schema)
        return model
    
    def _set_gemini_model(self, output_schema: BaseModel) -> ChatGoogleGenerativeAI:
        model = ChatGoogleGenerativeAI(model = os.environ.get("LLM_MODEL_NAME", ""))
        model = model.bind_tools(self.tools)

        if output_schema: model = model.with_structured_output(output_schema)
        return model
