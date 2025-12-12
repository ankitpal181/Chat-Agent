import json
import uuid
from backend.news_server import newsbot
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def run_test():
    print("🚀 Starting Backend Test for News Agent...\n")
    
    # 1. Initialize Thread ID (Simulating a unique user session)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    print(f"🆔 Thread ID: {thread_id}\n")

    # --- Phase 1: Headlines ---
    print("📰 Phase 1: Fetching Headlines...")
    user_input = "Top AI news in US"
    
    # Simulate State: User asks for headlines
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "segment": "headlines",
        "queries": []
    }
    
    # Run Graph
    output = newsbot.invoke(initial_state, config)
    last_message = output["messages"][-1]
    
    print(f"✅ Input: {user_input}")
    if isinstance(last_message, AIMessage):
        try:
            headlines_data = json.loads(last_message.content)
            print(f"✅ Output (Headlines): Found {len(headlines_data.get('headlines', []))} headlines.")
            # print(json.dumps(headlines_data, indent=2))
        except json.JSONDecodeError:
            print("❌ Error: Output is not valid JSON.")
    else:
        print("❌ Error: Unexpected output format.")
    print("-" * 50)


    # --- Phase 2: Stories ---
    print("\n📖 Phase 2: Fetching Stories...")
    # Simulate selecting the first headline (mocking the UI selection)
    selected_headline = "AI breakthrough in healthcare" # Mock headline text
    
    # Update State: Transition to 'stories' segment
    # Note: In the real app, we append to the existing history. 
    # invoke() with a checkpointer handles the history, so we just send the new input.
    stories_input = {
        "messages": [HumanMessage(content=f"Tell me more about: {selected_headline}")],
        "segment": "stories"
    }
    
    output = newsbot.invoke(stories_input, config)
    last_message = output["messages"][-1]
    
    print(f"✅ Input: Selected Headline '{selected_headline}'")
    if isinstance(last_message, AIMessage):
        try:
            stories_data = json.loads(last_message.content)
            print(f"✅ Output (Stories): Found {len(stories_data.get('stories', []))} stories.")
        except json.JSONDecodeError:
            print("❌ Error: Output is not valid JSON.")
    print("-" * 50)


    # --- Phase 3: Summary (Anchor) ---
    print("\n🎙️ Phase 3: Generating Summary...")
    
    summary_input = {
        "messages": [HumanMessage(content="Summarize these stories for me.")],
        "segment": "summary"
    }
    
    output = newsbot.invoke(summary_input, config)
    # The Anchor response might be in 'messages' or 'queries' depending on how the graph routed it.
    # Based on logic: query_function returns to 'messages' if queries list is empty.
    
    # Let's check both
    if output.get("queries"):
        last_response = output["queries"][-1]
        print("✅ Output (Summary - from queries):")
    else:
        last_response = output["messages"][-1]
        print("✅ Output (Summary - from messages):")
        
    print(f"📝 {last_response.content[:200]}...") # Print first 200 chars
    print("-" * 50)


    # --- Phase 4: Follow-up Query ---
    print("\n❓ Phase 4: Follow-up Question...")
    followup_text = "What are the risks mentioned?"
    
    # Update State: Still in 'summary' segment, but now using 'queries' list logic
    followup_input = {
        "queries": [HumanMessage(content=followup_text)],
        "segment": "summary"
    }
    
    output = newsbot.invoke(followup_input, config)
    last_response = output["queries"][-1]
    
    print(f"✅ Input: {followup_text}")
    print(f"✅ Output (Answer): {last_response.content[:200]}...")
    print("-" * 50)


    # --- Phase 5: Tool Execution (PDF Generation) ---
    print("\n⚙️ Phase 5: Tool Execution (Create PDF)...")
    tool_request = "Generate a pdf report of this summary."
    
    # This should trigger the custom_tool_node
    tool_input = {
        "queries": [HumanMessage(content=tool_request)],
        "segment": "summary"
    }
    
    # We need to iterate through the graph steps to see the tool call and result
    print("   ...Running graph steps...")
    
    # Using invoke directly will run until completion (tool call + tool output + final response)
    output = newsbot.invoke(tool_input, config)
    
    # Check the queries list for ToolMessage
    queries_history = output["queries"]
    tool_msg_found = False
    final_response = None
    
    for msg in queries_history:
        if isinstance(msg, ToolMessage):
            tool_msg_found = True
            print(f"✅ Tool Executed: {msg.name if hasattr(msg, 'name') else 'Unknown'}")
            print(f"📂 Tool Output: {msg.content}")
        if isinstance(msg, AIMessage):
            final_response = msg

    if tool_msg_found:
        print("✅ Tool execution confirmed.")
    else:
        print("❌ Warning: No ToolMessage found in history.")

    if final_response:
        print(f"✅ Final Response: {final_response.content}")
    
    print("\n🎉 Test Complete!")

if __name__ == "__main__":
    run_test()
