# Medical Chatbot

A patient-friendly medical information chatbot built with Flask, LangChain, Groq, Pinecone, and Hugging Face embeddings. It uses retrieval-augmented generation (RAG) to answer questions from the indexed medical knowledge base and presents responses in a clear, structured chat interface.

> **Medical notice:** This application is for educational and general-information purposes only. It does not diagnose conditions, replace a qualified healthcare provider, or provide emergency care.

## Features

- Retrieval-augmented answers grounded in the Pinecone medical knowledge base.
- Clear responses with Markdown sections such as **Answer**, **Explanation**, **Key points**, **When to seek care**, and **Disclaimer**.
- Per-user conversation memory using LangChain's `InMemoryChatMessageHistory` and `RunnableWithMessageHistory`.
- A dedicated chat-settings screen where users choose a display name and one of six local avatars.
- User-specific memory keys based on a generated UUID and the selected username, preventing users with the same name from sharing a conversation.
- A warm beige-and-brown responsive chat interface with an About popup and project/profile links.
- Local avatars served from `static/images/avatars`; no external avatar service is required.

## User flow

1. Open the application at `http://127.0.0.1:8080`.
2. On the Chat Settings page, enter a name and choose an avatar.
3. Select **Save settings** to open the chat.
4. Ask health questions and continue with follow-up questions—the current conversation stays in context.
5. Returning users can reopen Chat Settings, change their display details, or close it to return to the existing chat.

## Conversation memory

The application uses the current LangChain message-history pattern rather than the legacy `ConversationBufferMemory` class:

```text
InMemoryChatMessageHistory
        +
RunnableWithMessageHistory
```

For every request, the previous user and assistant messages are injected into the prompt as `chat_history`. The history is isolated by this session key:

```text
<generated UUID>:<normalized username>
```

### Current limitation

Memory is stored in the Flask process only. It is cleared when the application restarts and is not shared across multiple application instances. For a production deployment, replace the in-memory store with Redis or a database-backed history and apply a rolling message window to control prompt size.

## Project structure

```text
app.py                       Flask app, RAG chain, routes, and session memory
src/prompt.py                Medical-assistant system prompt
templates/chatSetting.html   Name and avatar selection screen
templates/chat.html          Main chat interface and About popup
static/chat-settings.css     Settings-page styling
static/chat.css              Chat-page styling
static/images/avatars/       Six selectable local user avatars
store_index.py               Indexes source documents in Pinecone
```

## Prerequisites

- Python 3.12 or later
- A Pinecone account and API key
- A Groq API key
- A configured Pinecone index named `medical-chatbot`

## Setup and run locally

Clone the repository:

```bash
git clone https://github.com/msaid1976/Complete-Medical-Chatbot-with-LLMs-LangChain-Pinecone-Flask-AWS.git
cd Complete-Medical-Chatbot-with-LLMs-LangChain-Pinecone-Flask-AWS
```

Create and activate a virtual environment:

```bash
conda create -n medibot python=3.12 -y
conda activate medibot
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Create a `.env` file in the project root:

```ini
PINECONE_API_KEY="your-pinecone-api-key"
GROQ_API_KEY="your-groq-api-key"
FLASK_SECRET_KEY="replace-with-a-long-random-secret-in-production"
```

Index the medical documents in Pinecone when creating or refreshing the vector index:

```bash
python store_index.py
```

Start the application:

```bash
python app.py
```

Then visit [http://127.0.0.1:8080](http://127.0.0.1:8080).

## Technology stack

- Python and Flask
- LangChain
- Groq LLM
- Pinecone vector database
- Hugging Face sentence-transformer embeddings
- HTML, CSS, and vanilla JavaScript

## Deployment notes

For a container/AWS deployment, provide these environment variables through the deployment platform's secret manager:

- `PINECONE_API_KEY`
- `GROQ_API_KEY`
- `FLASK_SECRET_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `ECR_REPO`

Use a persistent shared store such as Redis for conversation history when running more than one Flask worker or container.

## Author

**Mohamed Mohamed Said Aly**Agentic AI Engineer · Applied AI Engineer · LLM Systems Engineer

- [AI Portfolio](https://mohamedsaid-portfolio.vercel.app)
- [GitHub](https://github.com/msaid1976)
- [Hugging Face](https://huggingface.co/msaid1976)
- [LinkedIn](https://linkedin.com/in/mohamedsaidaly)
