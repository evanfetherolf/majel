from fastapi import FastAPI
from agents.chatbot_agent import chatbot_agent_executor
from models.chatbot_query import ChatbotInput, ChatbotOutput
from utils.async_utils import async_retry

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

    return await chatbot_agent_executor.ainvoke({"input": input})

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/chatbot_agent")
async def query_chatbot_agent(input: ChatbotInput) -> ChatbotOutput:
    query_response = await invoke_agent_with_retry(input.text)
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    return query_response