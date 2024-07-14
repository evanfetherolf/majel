from fastapi import FastAPI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)
from agents.chatbot_agent import chatbot_agent_executor
from models.chatbot_query import ChatbotInput, ChatbotOutput
from utils.async_utils import async_retry

app = FastAPI(
    title="Majel",
    description="Endpoints for a chatbot",
)

# Instantiate an empty list of messages for chat_history.
chat_history = []

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(input: str):
    """Retry the agent if a tool fails to run.

    This can help when there are intermittent connection issues
    to external APIs.
    """

    # Pass chat_history to the agent_executor here
    return await chatbot_agent_executor.ainvoke({
        "input": input,
        "chat_history": chat_history,
    })

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/chatbot_agent")
async def query_chatbot_agent(input: ChatbotInput) -> ChatbotOutput:
    # Save the most recent Human message to chat_history
    chat_history.append(HumanMessage(content=input.text))
    query_response = await invoke_agent_with_retry(input.text)

    # Save the most recent AI message to chat_history
    chat_history.append(AIMessage(content=query_response["output"]))
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    print(chat_history)
    return query_response