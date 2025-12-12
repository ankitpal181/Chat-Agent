# Chat Agent: The Multi-Functional AI Assistant 🤖📰

## 🚀 Project Overview

**Chat Agent** is a powerful, multi-module AI application built with **Streamlit** and **LangChain**. It serves as a versatile personal assistant, a comprehensive news analysis platform, and an evolving interview simulator.

The project is designed to be modular and extensible, featuring a unified interface to switch between different "agents":
*   **Chatbot**: A general-purpose assistant with web search and file generation capabilities.
*   **Newsbot**: A specialized agent for fetching headlines, analyzing news stories, and generating reports.
*   **Interview Bot**: A specialized module for simulated job interviews with real-time feedback and evaluation.

## ✨ Core Features

### 1. Chat Agent Module
*   **Live Streamed Responses**: Real-time token-by-token responses for an engaging experience.
*   **Internet Access**: The agent can search the web to provide up-to-date information.
*   **Dynamic File Generation**: Automatically generates downloadable **PDF** and **CSV** reports upon request.
*   **Database Integration**: Supports SQLite (default), PostgreSQL, and MongoDB for conversation history.
*   **Local SLM Support**: Run Small Language Models (SLMs) locally using Hugging Face Transformers for privacy and offline capability.

### 2. News Bot Module
*   **Top Headlines**: Fetches top news headlines (defaults to world news).
*   **Deep Dive Analysis**: Select a headline to find related articles and see a side-by-side comparison.
*   **Summarization**: Generates comprehensive summaries from multiple sources.
*   **Report Generation**: Create PDF or CSV reports of the news data directly from the UI.

### 3. Interview Bot Module
*   **Role-Based Simulation**: Conducts tailored interviews based on user role, company preferences, and selected format (Short/Long).
*   **Audio Integration**: Features built-in audio recording for answers, allowing users to speak naturally.
*   **Real-Time Timer**: Enforces time limits for each question to simulate real interview pressure.
*   **Comprehensive Evaluation**: Provides detailed feedback, ratings, and performance metrics (Confidence, Clarity) for every answer.
*   **Session Restoration**: automatically restores previous sessions on refresh using URL parameters.
*   **PDF Reports**: Generates detailed interview performance reports.
*   **Customizable Formats (RAG)**: Easily define or modify interview structures via a simple JSON configuration file.

## 📦 Installation and Setup

### Prerequisites
*   **Python 3.10** or higher.
*   **GTK+ Runtime**: Required for PDF generation (WeasyPrint).

### Step 1: Install System Dependencies (GTK+)

**Windows:**
1.  Download the **GTK+ Runtime Environment** installer (latest x64 version).
2.  Install it and ensure "Add to PATH" is selected.
3.  Restart your terminal/computer.

**macOS (Homebrew):**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info
```

### Step 2: Clone and Install Python Dependencies

1.  Clone the repository:
    ```bash
    git clone https://github.com/ankitpal181/Chat-Agent.git
    cd chat_agent
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Configure Environment Variables

1.  Create a `.env` file by copying the example:
    ```bash
    cp .example-env .env
    ```

2.  Open `.env` and configure your API keys:

    *   **LLM Provider**:
        *   **OpenAI**: Set `OPENAI_API_KEY`. (Prioritized if both are present).
        *   **Google Gemini**: Set `GOOGLE_API_KEY`.
        *   **Local Model** (New!): Leave **BOTH** `OPENAI_API_KEY` and `GOOGLE_API_KEY` blank. The system will automatically fallback to loading a local model via Hugging Face.
    *   **Model Name**: Set `LLM_MODEL_NAME` (e.g., `gpt-4o-mini`, `gemini-1.5-pro` for cloud, or a Hugging Face model ID like `TinyLlama/TinyLlama-1.1B-Chat-v1.0` for local).
    *   **Database** (Optional): Set `POSTGRES_CONNECTION_URI` or `MONGODB_CONNECTION_URI` if you want to use an external database instead of the default SQLite.

### ⚠️ Local Model Limitations
While local models offer privacy and offline capabilities, they come with trade-offs compared to large cloud providers (OpenAI/Google):
*   **Hardware Requirements**: Running models locally requires significant RAM and CPU/GPU resources. Performance depends heavily on your hardware.
*   **Speed**: Generation speed is generally slower than cloud APIs.
*   **Feature Support**: Currently, advanced features like **Function Calling (Tool Usage)** and **Structured Output** are **NOT** supported for local models. The agent will behave as a standard chatbot without web search or file generation capabilities when running locally.
*   **Model Size**: We recommend using "Small Language Models" (SLMs) like TinyLlama or Phi-3 unless you have high-end hardware.
*   **LangSmith Tracing** (Optional):
To enable tracing and debugging with LangSmith, uncomment and fill in the following lines in your `.env` file:
```bash
LANGCHAIN_API_KEY="<your-langsmith-api-key>"
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_PROJECT="chatbot" # You can name this whatever you like
```

## ▶️ How to Run the Application

The application uses a unified entry point. Run the following command from the project root:

```bash
streamlit run frontend/agents_screen.py
```

Once the application starts, your browser will open the Streamlit interface. Use the **Sidebar** to navigate between:
*   **Chat**: The general assistant.
*   **News**: The news aggregator and analyzer.
*   **Interview**: Simulated interview mode.

## � Customization

### Adding New Interview Formats (RAG)
The Interview Bot uses a RAG-based approach to retrieve interview rules from a JSON knowledge base. You can add new formats without modifying the codebase:

1.  Open `backend/data/interview_rules.json`.
2.  Add a new format entry:
    ```json
    "executive": {
        "format": "executive",
        "time_frame": 15, # time limit for each question in minutes
        "no_of_questions": 3 # number of questions to ask
    }
    ```
3.  **Note**: You will also need to add a corresponding button in the UI (`frontend/interview_layout.py`) to trigger this new format.

## 📂 Project Structure

*   `frontend/`: Contains the Streamlit UI code.
    *   `agents_screen.py`: Main entry point handling navigation.
    *   `chat_screen.py`: UI logic for the Chatbot.
    *   `news_screen.py`: UI logic for the Newsbot.
    *   `interview_screen.py`: Orchestrator for the Interview Bot.
    *   `interview_layout.py`: Rendering and audio logic for the Interview Bot.
*   `backend/`: Contains the core logic.
    *   `chat_server.py`: Logic for the Chatbot.
    *   `news_server.py`: Graph definition and assembly for the Newsbot.
    *   `interview_server.py`: Graph definition for the Interview Bot.
    *   `operators.py`: Core logic functions (Nodes) for the Newsbot.
    *   `utilities.py`: Planning and routing logic (Edges) for the Newsbot.
    *   `schemas.py`: Data models and state definitions.
    *   `llms.py`: LLM configuration (OpenAI/Gemini).
    *   `tools.py`: Implementation of tools (Search, PDF/CSV generation).
    *   `storage.py`: Database configuration and management.
    *   `prompts.py`: Prompt templates for the Newsbot.
*   `chatbot.db`: Default SQLite database for storing conversation history.

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request for any bug fixes or feature enhancements.