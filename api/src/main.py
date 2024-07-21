import os
import logging
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.agents import AgentExecutor
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from agents.chatbot_agent import agent, chatbot_agent_executor
from models.chatbot_query import ChatbotInput, ChatbotOutput
from utils.async_utils import async_retry

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title="Majel",
    description="Endpoints for a chatbot",
)

# Subclass AsyncIteratorCallbackHandler to be more explicit in code, and
# to make future scalability easier. The subclass is already here in case we
# want to make changes to it later.
class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
    def __init__(self):
        super().__init__()

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        await super().on_llm_new_token(token, **kwargs)

callback_handler = AsyncCallbackHandler()

chatbot_agent_executor.callbacks = [callback_handler]

async def run_agent_executor(input: str):
    logging.debug("run_agent_executor() called")
    callbacks = [callback_handler]
    logging.debug(f"callbacks: {callbacks}")
    async for token in chatbot_agent_executor.astream(input):
        yield token

# async def stream_response(input: str, callback_handler: AsyncCallbackHandler):
#     # logging.debug("stream_response() called")
#     task = asyncio.create_task(run_agent_executor(input))
#     async for token in callback_handler.aiter():
#         yield token
#     await task

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/chatbot_agent")
async def query_agent(input: ChatbotInput):
    logging.debug("POST: /chatbot_agent called")
    return StreamingResponse(
        # logging.debug("return StreamingResponse() called"),
        run_agent_executor({ "input": input.text}),
        media_type="text/event-stream"
    )
 