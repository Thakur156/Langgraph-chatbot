# LangGraph Chatbot with Tools

A conversational AI chatbot built with LangGraph, Streamlit, and Groq LLM that supports multiple tools including web search, stock price lookup, and calculator functionality. Features persistent conversation history with SQLite checkpointing.

## Screenshots

### Tool Usage in Progress
![Tool Usage](Screenshot%202026-03-15%20at%201.21.36%E2%80%AFPM.png)
*The chatbot shows real-time status when using tools like `get_stock_price`*

### Complete Response
![Response Ready](Screenshot%202026-03-15%20at%201.21.48%E2%80%AFPM.png)
*Final response displaying Tesla stock information with current price, high, low, and volume*

## Features

- **Multi-turn Conversations**: Maintains conversation context across messages
- **Persistent History**: All conversations are saved to SQLite database
- **Multiple Conversation Threads**: Create and switch between different chat sessions
- **Real-time Tool Status**: Visual feedback when tools are being used
- **Streaming Responses**: AI responses stream in real-time for better UX

## Built-in Tools

| Tool | Description |
|------|-------------|
| **DuckDuckGo Search** | Search the web for real-time information |
| **Stock Price** | Get latest stock prices using Alpha Vantage API |
| **Calculator** | Perform arithmetic operations (add, sub, mul, div) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  (streamlit_frontend_tool.py)                               │
│  - Chat UI with message history                             │
│  - Sidebar for conversation management                       │
│  - Real-time streaming display                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Backend                          │
│  (langgraph_tool_backend.py)                                │
│                                                             │
│  ┌─────────┐    ┌───────────┐    ┌─────────┐              │
│  │  START  │───▶│ chat_node │───▶│   END   │              │
│  └─────────┘    └─────┬─────┘    └─────────┘              │
│                       │                                     │
│                       │ tools_condition                     │
│                       ▼                                     │
│                 ┌───────────┐                               │
│                 │   tools   │                               │
│                 │  (ToolNode)│                               │
│                 └───────────┘                               │
│                                                             │
│  Checkpointer: SqliteSaver (Chatbot.db)                     │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Langgraph-chatbot/
├── streamlit_frontend_tool.py   # Streamlit UI application
├── langgraph_tool_backend.py    # LangGraph agent with tools
├── Chatbot.db                   # SQLite database for persistence
├── .env                         # Environment variables
└── README.md                    # This file
```

## File Descriptions

### `langgraph_tool_backend.py`

The backend module containing the LangGraph agent implementation:

- **ChatState**: TypedDict defining the conversation state with message history
- **Model**: Uses Groq's `qwen/qwen3-32b` model with hidden reasoning
- **Tools**:
  - `search_tool`: DuckDuckGo web search for real-time information
  - `get_stock_price`: Fetches stock data from Alpha Vantage API
  - `calculator`: Basic arithmetic operations
- **Graph Structure**:
  - `chat_node`: Processes messages through the LLM with tools
  - `tools`: ToolNode that executes tool calls
  - Conditional edge routing based on `tools_condition`
- **Persistence**: SQLite-based checkpointer for conversation history
- **Helper Functions**:
  - `retreive_all_threads()`: Returns all saved conversation thread IDs

### `streamlit_frontend_tool.py`

The frontend Streamlit application:

- **Session State Management**:
  - `message_History`: Current conversation messages
  - `thread_id`: Active conversation thread UUID
  - `chat_list`: All available conversation threads
- **UI Components**:
  - Sidebar with "New Chat" button and conversation list
  - Main chat area with message display
  - Chat input field
- **Core Functions**:
  - `generate_thread_id()`: Creates new UUID for conversations
  - `reset_chat()`: Starts a new conversation
  - `add_thread()`: Adds thread to sidebar list
  - `load_conversation()`: Retrieves messages from checkpointer
- **Streaming**: Real-time message streaming with tool status indicators

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Langgraph-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit langgraph langchain-groq langchain-community python-dotenv requests
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_frontend_tool.py
   ```

5. **Access the chatbot**

   Open your browser and navigate to `http://localhost:8501`

## Usage

1. **Start a conversation**: Type your message in the input field and press Enter
2. **Ask about stocks**: Try "What is the stock price of AAPL?"
3. **Search the web**: Ask questions requiring real-time information
4. **Use calculator**: Ask "What is 245 * 18?"
5. **Switch conversations**: Click on any thread ID in the sidebar
6. **Start new chat**: Click "New Chat" button in the sidebar

## API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| Groq | LLM inference | [console.groq.com](https://console.groq.com) |
| Alpha Vantage | Stock price data | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |

## Technologies Used

- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Agent orchestration framework
- **[Streamlit](https://streamlit.io)**: Web UI framework
- **[LangChain](https://langchain.com)**: LLM tooling and integrations
- **[Groq](https://groq.com)**: Fast LLM inference
- **SQLite**: Local database for conversation persistence

## License

MIT License
