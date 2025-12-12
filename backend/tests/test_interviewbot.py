import sys
import os

# add the parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Testing
from langgraph.types import Command
import uuid
from .interview_server import interviewbot

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
print(config)
result = interviewbot.invoke({
    "messages": [{"role": "user", "content": "Start Interview"}],
    "phase": "execution"
}, config)

while "__interrupt__" in result:
    data = input(f"{result['__interrupt__'][0].value}: \n")
    result = interviewbot.invoke(Command(resume=data), config)

print(result)

report = interviewbot.invoke({"messages": [{
    "role": "user",
    "content": "Generate a PDF report of the conversion and evaluation of the interview. Keep the evaluation intact and don't try to summarise it."
}], "phase": "reporting"}, config)

while "__interrupt__" in report:
    data = input(f"{report['__interrupt__'][0].value}: \n")
    report = interviewbot.invoke(Command(resume=data), config)