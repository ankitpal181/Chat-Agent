import sys
import os
import uuid
import json
from langgraph.types import Command

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.interview_server import interviewbot

def run_test():
    print(">>> Starting Comprehensive Backend Test")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    print(f">>> Thread ID: {thread_id}")

    # 1. Start Interview (Short Format)
    print("\n>>> Step 1: Initializing Interview (Short Format)")
    initial_state = {
        "messages": [{"role": "user", "content": "Start Interview"}],
        "phase": "execution",
        "rules": {"format": "short"}
    }
    
    result = interviewbot.invoke(initial_state, config)
    
    # 2. Handle Interrupts (Candidate Info & Q&A)
    question_count = 0
    
    while "__interrupt__" in result:
        interrupt_value = result['__interrupt__'][0].value
        
        response = ""
        
        if isinstance(interrupt_value, str):
            print(f"\n>>> Interrupt (Info): {interrupt_value}")
            # Candidate Info Phase
            if "full name" in interrupt_value.lower():
                response = "Test Candidate"
                print(f">>> Providing Name: {response}")
            elif "job role" in interrupt_value.lower():
                response = "Software Engineer"
                print(f">>> Providing Role: {response}")
            elif "names of companies" in interrupt_value.lower():
                response = "Google, Microsoft"
                print(f">>> Providing Companies: {response}")
            else:
                response = "Generic Answer"
                print(f">>> Providing Generic Info: {response}")
        else:
            # Question Phase
            try:
                question_text = interrupt_value.question
                print(f"\n>>> Interrupt (Question {question_count + 1}): {question_text}")
                response = f"This is a test answer for question {question_count + 1}."
                question_count += 1
            except AttributeError:
                print(f"\n>>> Unknown Interrupt Type: {interrupt_value}")
                response = "Fallback Answer"

        # Resume execution
        result = interviewbot.invoke(Command(resume=response), config)

    # 3. Evaluation
    print("\n>>> Step 3: Evaluation Phase")
    if "messages" in result and result["messages"]:
        last_message = result["messages"][-1]
        print(f">>> Final Message Content (First 200 chars): {last_message.content[:200]}...")
        
        try:
            evaluation = json.loads(last_message.content)
            print(">>> ✅ Evaluation JSON parsed successfully.")
            if "rating" in evaluation:
                 print(f">>> Rating: {evaluation['rating']}")
        except Exception as e:
            print(f">>> ❌ Failed to parse evaluation JSON: {e}")
    else:
        print(">>> ❌ No messages returned in final state.")

    # 4. Report Generation
    print("\n>>> Step 4: Report Generation")
    report_state = {
        "messages": [{
            "role": "user",
            "content": "Generate a PDF report of the conversion and evaluation of the interview."
        }],
        "phase": "reporting"
    }
    
    # We need to invoke with the SAME config to access the memory
    report_result = interviewbot.invoke(report_state, config)
    
    if "messages" in report_result:
        last_msg = report_result["messages"][-1]
        print(f">>> Report Message Type: {type(last_msg)}")
        print(f">>> Report Content (First 200 chars): {last_msg.content[:200]}...")
    
    print("\n>>> Test Complete")

if __name__ == "__main__":
    run_test()
