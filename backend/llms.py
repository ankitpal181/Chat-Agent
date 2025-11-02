import os
from .tools import search_internet, generate_csv_tool, generate_pdf_tool
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI


class Model:
    def __init__(self) -> None:
        self.tools = [search_internet, generate_csv_tool, generate_pdf_tool]

        if os.environ.get("OPENAI_API_KEY"):
            self.model = self._set_openai_model()
        else:
            self.model = self._set_gemini_model()
    
    def _set_openai_model(self) -> ChatOpenAI:
        model = ChatOpenAI(model=os.environ.get("LLM_MODEL_NAME", ""))
        return model.bind_tools(self.tools)
    
    def _set_gemini_model(self) -> ChatGoogleGenerativeAI:
        model = ChatGoogleGenerativeAI(model=os.environ.get("LLM_MODEL_NAME", ""))
        return model.bind_tools(self.tools)
