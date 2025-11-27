# Agentic Architecture & Design Patterns

This document outlines the **backend architecture** of the **Chat Agent**, focusing strictly on the autonomous agentic components. The system is built on **LangChain** and **LangGraph**, implementing a stateful, multi-agent workflow that operates independently of the frontend interface.

## 1. Perception Systems
*Modules that gather and interpret information from the environment.*

*   **Perception Node**:
    *   The system implements a dedicated **Perception Node** (`perception_function` in `backend/news_server.py`).
    *   **Responsibility**: It acts as the single entry point for state analysis. It "perceives" the current environment—specifically the `segment` variable (Headlines, Stories, Summary) and the conversation history.
    *   **Action**:
        *   Based on this perception, it proactively injects the appropriate **System Message** (Persona) into the state *before* control is passed to the reasoning engines. This ensures that the execution nodes always receive a fully prepared, context-aware state.
        *   It also handles the **Query** (User Input) and **Tool** (File Generation) messages, ensuring they are properly formatted and added to the state.

## 2. Reasoning and Decision-Making
*The "brain" of the agent, analyzing information and choosing actions.*

*   **Reasoning Engines (Execution Nodes)**:
    *   **News Bot**: The "thinking" is performed by specific **Execution Nodes** that utilize LLMs (`backend/llms.py`) to process information:
        *   **Headlines Node**: The **Reporter** persona reasons about raw search data to extract and format valid news.
        *   **Stories Node**: The **Journalist** persona reasons about which deep-dive stories are relevant to a selected headline.
        *   **Query Node**: The **Anchor** persona reasons about how to synthesize gathered information into a narrative or answer user follow-up questions.
    *   **Chat Bot**: The "thinking" is performed by specific **Execution Node** that utilize LLMs (`backend/llms.py`) to process information:
        *   **Chat Node**: The **Engaging** persona reasons about how to deliver replies that match the user's taste and engagement level.

## 3. Memory Systems
*Maintaining context and learning from interactions.*

*   **News Bot Memory (In-Memory)**:
    *   The News Bot utilizes a **Dual-State Working Memory** that persists only for the duration of the graph execution (RAM):
        *   **`messages` (Episodic Memory)**: Records the structural narrative of the main task (Headlines -> Stories -> Summary).
        *   **`queries` (Transient Memory)**: A scratchpad for immediate, low-stakes follow-up interactions. This memory is programmatically cleared (`RemoveMessage`) when a new summary is generated, ensuring the agent's focus remains on the current topic.
*   **Chat Bot Memory (Persistent)**:
    *   The Chat Bot utilizes **Long-Term Database Memory** (`backend/storage.py`), persisting conversation threads to a SQLite database (`chatbot.db`) to allow continuity across sessions.

## 4. Planning Modules
*Breaking down goals into manageable steps.*

*   **Graph-Based Planning**:
    *   The **Plan** is explicitly defined by the **Graph Structure** (`StateGraph`) and its edges.
    *   **High-Level Planner**: The `select_segment_function` determines the *phase* of the operation, dictating the transition between Headlines, Stories, and Summary nodes.
    *   **Reactive Planner**: The `custom_tools_condition` determines the immediate next step, deciding whether to execute an action (Tool) or complete the reasoning step.
*   **ReAct Pattern**:
    *   The Chat Bot employs a flexible **Reasoning + Acting** loop, planning one step at a time based on the immediate needs of the user request.

## 5. Tool Access and Actuation
*Enabling the agent to take action in the real world.*

*   **Actuators**:
    *   **File Generation**: `generate_pdf_tool` and `generate_csv_tool` allow the agent to physically alter the environment by creating persistent files.
*   **Sensors**:
    *   **Internet Search**: `search_internet` acts as a sensor capability, allowing the agent to retrieve external data.
*   **Controllers**:
    *   **`custom_tool_node`**: A specialized controller for the News Bot that intelligently routes tool execution commands, ensuring they operate within the correct memory context (`queries` vs `messages`).

## 6. Learning and Reflection
*Continuous improvement and feedback loops.*

*   **Current Status**: Not Implemented.
*   **Future Vision**: The architecture is designed to support a **Human-in-the-loop Feedback Module**. This module will be inserted at each step of the workflow, allowing the agent to pause and request human validation ("Is this headline list accurate?") before proceeding, thereby "learning" from immediate correction.
