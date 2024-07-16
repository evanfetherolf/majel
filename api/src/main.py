import os
from fastapi import FastAPI
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from agents.chatbot_agent import chatbot_agent_executor
from models.chatbot_query import ChatbotInput, ChatbotOutput
from utils.async_utils import async_retry

app = FastAPI(
    title="Majel",
    description="Endpoints for a chatbot",
)

# Instantiate an empty list of messages for chat_history.
db_user = os.getenv("MONGODB_USERNAME")
db_pass = os.getenv("MONGODB_PASSWORD")
db_uri = os.getenv("MONGODB_URI")
chat_history = MongoDBChatMessageHistory(
    session_id="default",
    connection_string=f"mongodb://{db_user}:{db_pass}@{db_uri}",
    database_name="chat_history",
    collection_name="chat_histories"
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(input: str):
    """Retry the agent if a tool fails to run.

    This can help when there are intermittent connection issues
    to external APIs.
    """

    # Pass chat_history to the agent_executor here
    return await chatbot_agent_executor.ainvoke({
        "input": input,
        "chat_history": chat_history.messages,
    })

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/chatbot_agent")
async def query_chatbot_agent(input: ChatbotInput) -> ChatbotOutput:
    # Save the most recent Human message to chat_history
    print("DEBUG: /chatbot-agent called")
    chat_history.add_user_message(input.text)
    query_response = await invoke_agent_with_retry(input.text)

    # Save the most recent AI message to chat_history
    chat_history.add_ai_message(query_response["output"])
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    return query_response