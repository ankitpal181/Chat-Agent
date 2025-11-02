Chat Agent: The Multi-Functional AI Assistant 🤖📰

🚀 Project Overview
    Chat Agent is a powerful, multi-module AI application built with Streamlit and LangChain (or similar
    LLM framework) that serves as both a versatile personal assistant and a comprehensive news analysis
    platform.
    The project is split into two distinct, runnable modules: a Chatbot for general tasks and a dedicated
    Newsbot for deep-dive news aggregation and summarization. It is designed to be accessible to
    everyone, providing advanced features like live chat streaming, file generation, and dynamic web
    search.

✨ Core Features

    1. Chat Agent Module (chat_screen.py)
        Live Streamed Responses: Chat messages are displayed token-by-token for a real-time, engaging
        experience.

        Internet Access: The agent can use web search tools to provide up-to-date and contextually
        relevant answers.

        Dynamic File Generation: Automatically generates and provides a download button for requested
        files (e.g., reports, data dumps) in formats like PDF and CSV.

        Database Integration: Utilizes a database (for conversation history, data caching, etc., as
        configured).

    2. News Bot Module (news_screen.py)
        Top 10 Headlines Fetcher: Retrieves the top 10 news headlines for today, with optional filtering
        by country, region, or genre. Defaults to world news.

        Comparative Analysis: For a selected headline, the bot searches the internet for the top 5
        related articles and displays them side-by-side in a card-like interface for easy comparison.

        Advanced Summarization: Users can ask the bot to summarize the news story using selected (or all)
        source articles and generate a full article.

        Contextual Follow-up: Supports follow-up questions on the news, answering primarily from the
        gathered source articles and using a secondary internet search if necessary.

📦 Installation and Setup

    Prerequisites
        You must have Python 3.10 or higher installed.

    OS Dependencies (Operating System Package)
        1. System Dependencies (PDF/CSV Generation)
            This project uses a Python library (like WeasyPrint or xhtml2pdf) for PDF/CSV generation,
            which relies on the GTK+ runtime environment. You must install these system packages first.

            🖥️ Windows
                The easiest solution is to install the GTK+ Runtime Environment.

                Download and Install: Go to the GTK for Windows Runtime Environment Installer releases
                page (or a reliable mirror) and download the latest executable file (e.g.,
                gtk3-runtime-x.y.z-****-x64.exe for 64-bit systems).

                Add to PATH: During installation, ensure the option to add the installation path to the
                system's PATH environment variable is selected.

                Restart: Restart your computer or terminal session for the changes to take effect.

                Alternative (Manual Path): If the automatic PATH fails, you may need to manually set the
                WEASYPRINT_DLL_DIRECTORIES environment variable to your GTK bin directory (e.g.,
                C:\Program Files\GTK3-Runtime Win64\bin).

            🐧 Linux (Ubuntu/Debian-based)
                Use apt to install the required GTK-related libraries:

                Bash:
                    sudo apt update
                    sudo apt install libgobject-2.0-0 libpango1.0-0 libcairo2 libgdk-pixbuf2.0-0
                    
                    # If the above doesn't work, try the full set:
                    sudo apt install libgirepository1.0-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info

            🍎 macOS
                Use Homebrew to install the core dependencies:

                Bash:
                    brew install cairo pango gdk-pixbuf libffi

        2. Python Dependencies
            Clone the repository:
                Bash:
                    git clone [Your_Repository_URL]
                    cd [Your_Project_Folder]

            Install Python packages:
                Bash:
                    pip install -r requirements.txt

        3. Environment Variables (.env)
            This project uses a .env file to manage API keys.
            
            - Create the file: Copy the provided example file to create your local environment file:
            Bash:
                cp .example-env .env
            
            - Edit .env: Open the new .env file and fill in your API keys.
                Use the fields in your .env file to select your Large Language Model (LLM) provider and
                specify the model name.
                
                1. Set Your API Key and LLM Choice
                    Fill in the appropriate API key for the provider you wish to use.
                    
                    - Default Provider: The project is configured to prioritize OpenAI (GPT models) if
                    both keys are provided.
                    
                    - To Use GPT Models (OpenAI):Paste your OpenAI API key into the OPENAI_API_KEY field.
                    Leave GOOGLE_API_KEY empty.
                    
                    - To Use Gemini Models (Google):Paste your Google Gemini API key into the
                    GOOGLE_API_KEY field. Leave OPENAI_API_KEY empty.
                
                2. Specify the Model Name
                    The LLM_MODEL_NAME variable is used to specify the exact model you want to run from
                    your chosen provider.
                    
                    - Default Model: If left unchanged, the project will default to using gpt-4o-mini.
                    
                    - Custom Model: Fill in the name of the model you prefer to use (e.g., gpt-4-turbo,
                    gemini-2.5-pro, etc.).
                
                3. Database Configuration Instructions (Optional)
                    By default, your application will likely use simple in-memory storage or a SQLite
                    database, meaning you don't need to change anything in this section.

                    However, if you wish to use a more robust external database like PostgreSQL or
                    MongoDB for persistent, scaled data storage, follow the instructions below.
                        To use an external database, you only need to fill in one of the connection URIs:
                        - POSTGRES_CONNECTION_URI: Replace the example string with the complete
                            connection URI for your running PostgreSQL instance.
                            Format: postgresql://user:password@host:port/database
                        - MONGODB_CONNECTION_URI: Replace the example string with the connection URI
                            for your running MongoDB instance.
                            Format: mongodb://[user:password@]host:port[/database]

                    Important: Before configuring these variables, you must already have a running
                    instance of your chosen database (PostgreSQL or MongoDB) accessible from your machine.
                
                4. LangSmith Tracing Setup (Optional)
                    To enable tracing, debugging, and testing of your LangChain application using
                    LangSmith, you must uncomment all the lines under the LangSmith section and provide
                    your API key.
                    
                    - Instructions for LangSmith
                        Uncomment: Remove the # symbol from the beginning of all five lines in the
                        LangSmith section.
                        
                        Provide Key: Fill in your LangChain API Key.
                        
                        Project Name: You can change the default project name (chatbot) if you prefer.

▶️ How to Run the Application

    The project is launched via Streamlit, running each of the two main modules separately.

    1. Running the Chat Agent
        This module provides the general-purpose chat, file generation, and search capabilities.

        Bash:
            # Ensure you are in the folder containing the 'chat_agent/' directory
            streamlit run frontend/chat_screen.py

    2. Running the News Bot
        This module provides the headline fetching and deep news analysis capabilities.

        Bash:
            # Ensure you are in the folder containing the 'chat_agent/' directory
            streamlit run frontend/news_screen.py

🤝 Contributing
    I welcome contributions! If you have suggestions, bug reports, or want to contribute code, please open
    an issue or a pull request.