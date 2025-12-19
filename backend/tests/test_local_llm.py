import os
import json
import torch
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from backend.llms import LocalModel
from unittest.mock import MagicMock, patch

# Define a simple schema for structured output testing
class Joke(BaseModel):
    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline of the joke")

# Define a mock tool for tool calling testing
def get_weather(location: str):
    """Get the current weather in a given location"""
    return f"The weather in {location} is sunny."

def test_local_model_features(use_mock=True):
    model_id = os.environ.get("LLM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    
    if use_mock:
        print("🚀 Running in MOCK mode for fast verification of parsing logic.")
        # We need to mock the transformers parts so we can instantiate LocalModel without loading a real model
        with patch("backend.llms.AutoTokenizer.from_pretrained") as mock_auth, \
             patch("backend.llms.AutoModelForCausalLM.from_pretrained") as mock_model:
            
            mock_tokenizer = MagicMock()
            mock_client = MagicMock()
            mock_auth.return_value = mock_tokenizer
            mock_model.return_value.to.return_value = mock_client
            
            llm = LocalModel(model="mock-model")
            
            # Helper to mock the generation result
            def mock_generate_implementation(messages, **kwargs):
                from langchain_core.outputs import ChatResult, ChatGeneration
                from langchain_core.messages import ToolCall
                import uuid
                
                # Simulate a tool call response
                tool_call_content = 'Sure! I can help with that.\n```json\n{"tool": "get_weather", "parameters": {"location": "Paris"}}\n```'
                
                # If we are testing structured output, simulate a JSON response that matches the schema
                # (Note: structured_output in LangChain usually wraps the model and expects tool calls if bound)
                
                tc = ToolCall(name="get_weather", args={"location": "Paris"}, id=str(uuid.uuid4()))
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=tool_call_content, tool_calls=[tc]))])

            # Instead of mocking _generate (which would bypass the parsing logic we want to test),
            # we should mock the client.generate and tokenizer.decode calls.
            
            # 1. Mock tokenizer return for input encoding
            mock_tokenizer.return_value.to.return_value = {"input_ids": torch.tensor([[1, 2, 3]])}
            
            # 2. Mock client.generate to return some dummy token IDs
            mock_client.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
            
            # 3. Mock tokenizer.decode to return our target JSON string
            # This is where we test the parsing logic in _generate!
            mock_tokenizer.decode.return_value = 'Sure! I can help with that.\n```json\n{"tool": "get_weather", "parameters": {"location": "Paris"}}\n```'

            run_test_suite(llm)
    else:
        print(f"🐢 Running in REAL mode with: {model_id} (This may be slow)")
        llm = LocalModel(model=model_id)
        run_test_suite(llm)

def run_test_suite(llm):
    print("\n--- Testing Tool Calling ---")
    tools = [get_weather]
    llm_with_tools = llm.bind_tools(tools)
    
    messages = [
        SystemMessage(content="You are a helpful assistant with access to tools."),
        HumanMessage(content="What is the weather in Paris?")
    ]
    
    print("Executing invoke...")
    response = llm_with_tools.invoke(messages)
    
    print(f"Generated Content: {response.content}")
    if response.tool_calls:
        print("✅ Tool Calls detected and parsed!")
        for tool_call in response.tool_calls:
            print(f"  Tool: {tool_call['name']}")
            print(f"  Args: {tool_call['args']}")
    else:
        print("❌ No Tool Calls detected.")

    print("\n--- Testing Structured Output ---")
    # with_structured_output typically uses the tool calling infrastructure
    try:
        structured_llm = llm.with_structured_output(Joke)
        print("Executing structured invoke...")
        # In mock mode, our mocked decode will return the tool call, 
        # which LangChain's internal parser should then turn into a Pydantic object
        # IF we mock the output to match the expected tool call for 'Joke'
        
        # Adjust mock for Joke schema if in mock mode
        if hasattr(llm.tokenizer, "decode"):
             llm.tokenizer.decode.return_value = '```json\n{"tool": "Joke", "parameters": {"setup": "Why did the robot go to the doctor?", "punchline": "Because it had a virus!"}}\n```'

        joke_response = structured_llm.invoke("Tell me a funny joke about a robot.")
        
        print(f"Result Type: {type(joke_response)}")
        if isinstance(joke_response, Joke):
            print("✅ Structured Output successful!")
            print(f"  Setup: {joke_response.setup}")
            print(f"  Punchline: {joke_response.punchline}")
        elif isinstance(joke_response, AIMessage) and joke_response.tool_calls:
             print("⚠️  Received AIMessage with tool calls instead of Pydantic object.")
             print(f"   Tool Call: {joke_response.tool_calls[0]['name']}")
        else:
            print(f"❌ Structured Output failed. Returned: {joke_response}")
    except Exception as e:
        print(f"❌ Structured Output error: {e}")

if __name__ == "__main__":
    # Toggle this to False to run with a real local model
    USE_MOCK = os.environ.get("USE_MOCK", "True").lower() == "true"
    
    try:
        test_local_model_features(use_mock=USE_MOCK)
    except Exception as e:
        print(f"Error during testing: {e}")
