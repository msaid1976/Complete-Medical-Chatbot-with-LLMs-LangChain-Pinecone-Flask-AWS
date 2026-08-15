# Medical Chatbot

A patient-friendly medical information chatbot built with Flask, LangChain, Groq, Pinecone, and Hugging Face embeddings. It uses retrieval-augmented generation (RAG) to answer questions from the indexed medical knowledge base and presents responses in a clear, structured chat interface.

## Live demo

Try the application: [Medical Chatbot on Render](https://complete-medical-chatbot-with-llms-o0uy.onrender.com)

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

Install Python 3.12 with `uv` if it is not already available, then create the project virtual environment from `pyproject.toml`:

```bash
uv python install 3.12
uv sync --python 3.12
```

The `.python-version` file and `pyproject.toml` both pin the project to Python 3.12. `uv sync` creates and manages a local `.venv` directory using that version. Then install the project requirements into that environment:

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

## Deployment flow

When you manually start the workflow from the **Actions** tab, GitHub Actions performs these steps:

1. Builds the Docker image from the source code.
2. Authenticates with Amazon ECR.
3. Pushes the tagged image to the ECR repository.
4. Runs the deployment job on the EC2 self-hosted runner.
5. Pulls and starts the application container on port `8080`.

For a multi-container or multi-instance deployment, use a persistent shared store such as Redis for conversation history instead of the current in-memory store.

> The workflow is manual-only (`workflow_dispatch`) so ordinary code and documentation pushes do not create failed deployment checks while the EC2 self-hosted runner is offline.

## AWS CI/CD deployment with GitHub Actions

The repository includes a GitHub Actions workflow at `.github/workflows/cicd.yaml`. It builds a Docker image, pushes it to Amazon ECR, and deploys it to an EC2 machine configured as a self-hosted GitHub Actions runner.

### 1. Sign in to AWS

Sign in to the [AWS Console](https://aws.amazon.com/console/).

### 2. Create an IAM user for deployment

Create an IAM user with programmatic access for the GitHub Actions workflow. The deployment needs access to:

- **Amazon EC2** — runs the self-hosted GitHub Actions runner and Docker container.
- **Amazon ECR** — stores the Docker image.

For this project’s initial setup, attach the following policies:

- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEC2FullAccess`

For production, replace broad managed policies with a least-privilege IAM policy scoped to the required ECR repository and EC2 resources.

### 3. Create an Amazon ECR repository

Create an ECR repository to store the Docker image. Save its repository URI; for example:

```text
- Save the URL : 533016149171.dkr.ecr.us-east-1.amazonaws.com/medicalbot
```

Use the repository name portion (for example, `medicalbot`) as the value for the `ECR_REPO` GitHub secret.

### 4. Create an Ubuntu EC2 instance

Launch an Ubuntu EC2 instance. This machine will host the self-hosted GitHub Actions runner and run the Docker image after deployment.

Ensure the instance security group allows inbound traffic on port `8080` if you want to access the Flask application directly.

### 5. Install Docker on the EC2 instance

Connect to the EC2 instance and run:

```bash
sudo apt-get update -y
sudo apt-get upgrade -y

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

### 6. Configure the EC2 instance as a self-hosted runner

In your GitHub repository, go to:

```text
Settings → Actions → Runners → New self-hosted runner
```

Choose Linux and follow the generated commands on the EC2 instance. Once the runner is online, the deployment job can run Docker commands on that server.

### 7. Add GitHub Actions secrets

In the repository, go to **Settings → Secrets and variables → Actions** and add:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `ECR_REPO`
- `PINECONE_API_KEY`
- `GROQ_API_KEY`
- `FLASK_SECRET_KEY`

> The current chatbot uses Groq, so configure `GROQ_API_KEY` rather than `OPENAI_API_KEY` for the application container.

## Author

**Mohamed Mohamed Said Aly** Agentic AI Engineer · Applied AI Engineer · LLM Systems Engineer

- [AI Portfolio](https://mohamedsaid-portfolio.vercel.app)
- [GitHub](https://github.com/msaid1976)
- [Hugging Face](https://huggingface.co/msaid1976)
- [LinkedIn](https://linkedin.com/in/mohamedsaidaly)
