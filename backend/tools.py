import pandas
from weasyprint import HTML
from .prompts import CSV_PROMPT, PDF_PROMPT
from langchain_core.tools import StructuredTool
from langchain_community.tools import DuckDuckGoSearchRun


def generate_csv_file(data: dict) -> dict:
    pandas.DataFrame(data).to_csv('chatbot.csv', index=False)
    return {
        "label": "Download CSV File",
        "file_path":'chatbot.csv',
        "file_name":"data.csv",
        "mime":"text/csv"
    }

def generate_pdf_file(template: str) -> dict:
    HTML(string = template).write_pdf("chatbot.pdf")
    return {
        "label": "Download PDF File",
        "file_path":'chatbot.pdf',
        "file_name":"data.pdf",
        "mime":"application/pdf"
    }

# Tools
search_internet = DuckDuckGoSearchRun()
generate_csv_tool = StructuredTool.from_function(generate_csv_file, description = CSV_PROMPT)
generate_pdf_tool = StructuredTool.from_function(generate_pdf_file, description = PDF_PROMPT)
