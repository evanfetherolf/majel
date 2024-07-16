import os
import logging
from fastapi import FastAPI
from agents.chatbot_agent import chatbot_agent_executor
from models.chatbot_query import ChatbotInput, ChatbotOutput
from utils.async_utils import async_retry

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title="Majel",
    description="Endpoints for a chatbot",
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(input: str):
    """Retry the agent if a tool fails to run.

    This can help when there are intermittent connection issues
    to external APIs.
    """
    logging.debug("invoke_agent_with_retry() called")

    # Pass chat_history to the agent_executor here
    # return await chatbot_agent_executor.ainvoke({ "input": input })
    return await chatbot_agent_executor.ainvoke({ "input": input })

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/chatbot_agent")
async def query_chatbot_agent(input: ChatbotInput) -> ChatbotOutput:
    # Save the most recent Human message to chat_history
    logging.debug("/chatbot-agent called")
    # chat_history.add_user_message(input.text)
    query_response = await invoke_agent_with_retry(input.text)

    # Save the most recent AI message to chat_history
    # chat_history.add_ai_message(query_response["output"])
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    return query_response