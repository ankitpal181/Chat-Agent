# Chat Agent: The Multi-Functional AI Assistant 🤖📰

## 🚀 Project Overview

**Chat Agent** is a powerful, multi-module AI application built with **Streamlit** and **LangChain**. It serves as a versatile personal assistant, a comprehensive news analysis platform, and an evolving interview simulator.

The project is designed to be modular and extensible, featuring a unified interface to switch between different "agents":
*   **Chatbot**: A general-purpose assistant with web search and file generation capabilities.
*   **Newsbot**: A specialized agent for fetching headlines, analyzing news stories, and generating reports.
*   **Interview Bot**: (Coming Soon) A module for simulated interview experiences.

## ✨ Core Features

### 1. Chat Agent Module
*   **Live Streamed Responses**: Real-time token-by-token responses for an engaging experience.
*   **Internet Access**: The agent can search the web to provide up-to-date information.
*   **Dynamic File Generation**: Automatically generates downloadable **PDF** and **CSV** reports upon request.
*   **Database Integration**: Supports SQLite (default), PostgreSQL, and MongoDB for conversation history.

### 2. News Bot Module
*   **Top Headlines**: Fetches top news headlines (defaults to world news).
*   **Deep Dive Analysis**: Select a headline to find related articles and see a side-by-side comparison.
*   **Summarization**: Generates comprehensive summaries from multiple sources.
*   **Report Generation**: Create PDF or CSV reports of the news data directly from the UI.

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
    *   **Model Name**: Set `LLM_MODEL_NAME` (e.g., `gpt-4o-mini`, `gemini-1.5-pro`).
    *   **Database** (Optional): Set `POSTGRES_CONNECTION_URI` or `MONGODB_CONNECTION_URI` if you want to use an external database instead of the default SQLite.
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
*   **Interview**: (Under Development).

## 📂 Project Structure

*   `frontend/`: Contains the Streamlit UI code.
    *   `agents_screen.py`: Main entry point handling navigation.
    *   `chat_screen.py`: UI logic for the Chatbot.
    *   `news_screen.py`: UI logic for the Newsbot.
*   `backend/`: Contains the core logic.
    *   `chat_server.py`: Logic for the Chatbot.
    *   `news_server.py`: Graph definition and assembly for the Newsbot.
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