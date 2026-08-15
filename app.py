from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from src.prompt import *
import os
import secrets
import uuid
from threading import Lock


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
AVATAR_FILENAMES = {f"avatar{number}.jpg" for number in range(1, 7)}


load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
GROQ_API_KEY=os.environ.get('GROQ_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


embeddings = download_hugging_face_embeddings()

index_name = "medical-chatbot" 
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)




retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

chatModel = init_chat_model(model="groq:openai/gpt-oss-120b",temperature=0.4)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Each browser receives a separate, in-memory conversation buffer. This is ideal
# for local development; use Redis or a database-backed history before deploying
# multiple application instances.
chat_histories = {}
chat_histories_lock = Lock()


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    with chat_histories_lock:
        if session_id not in chat_histories:
            chat_histories[session_id] = InMemoryChatMessageHistory()
        return chat_histories[session_id]


rag_chain_with_memory = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)



@app.route("/")
def index():
    return render_template(
        "chatSetting.html",
        user_name=session.get("user_name", ""),
        user_avatar=session.get("user_avatar", "avatar1.jpg"),
        avatars=sorted(AVATAR_FILENAMES),
        has_saved_settings=bool(session.get("user_uuid") and session.get("user_name")),
    )


@app.route("/chat")
def chat_page():
    if not session.get("user_uuid") or not session.get("user_name"):
        return redirect(url_for("index"))
    avatar_filename = session.get("user_avatar", "avatar1.jpg")
    return render_template(
        "chat.html",
        user_name=session["user_name"],
        user_avatar=url_for("static", filename=f"images/avatars/{avatar_filename}"),
    )


@app.route("/start-session", methods=["POST"])
def start_session():
    user_name = " ".join(request.form.get("name", "").split())
    avatar_filename = request.form.get("avatar", "")
    if not 2 <= len(user_name) <= 50:
        return render_template(
            "chatSetting.html",
            user_name=user_name,
            user_avatar=avatar_filename or "avatar1.jpg",
            avatars=sorted(AVATAR_FILENAMES),
            has_saved_settings=bool(session.get("user_uuid") and session.get("user_name")),
            error="Please enter a name between 2 and 50 characters.",
        ), 400
    if avatar_filename not in AVATAR_FILENAMES:
        return render_template(
            "chatSetting.html",
            user_name=user_name,
            user_avatar="avatar1.jpg",
            avatars=sorted(AVATAR_FILENAMES),
            has_saved_settings=bool(session.get("user_uuid") and session.get("user_name")),
            error="Please select one of the available avatars.",
        ), 400

    if "user_uuid" not in session:
        session["user_uuid"] = str(uuid.uuid4())
    session["user_name"] = user_name
    session["user_avatar"] = avatar_filename
    return redirect(url_for("chat_page"))



@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form.get("msg", "").strip()
    if not msg:
        return "Please enter a message.", 400

    user_uuid = session.get("user_uuid")
    user_name = session.get("user_name")
    if not user_uuid or not user_name:
        return "Please enter your name to start a chat session.", 400

    # The UUID prevents users with the same display name from sharing memory.
    memory_session_id = f"{user_uuid}:{user_name.casefold()}"

    response = rag_chain_with_memory.invoke(
        {"input": msg},
        config={"configurable": {"session_id": memory_session_id}},
    )
    print("Response : ", response["answer"])
    return str(response["answer"])



if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)
