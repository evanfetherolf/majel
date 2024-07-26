import os
import sqlite3
from typing import Any, Dict, List
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.memory.entity import ConversationEntityMemory, SQLiteEntityStore
from langchain.prompts import ChatPromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import OpenAI, ChatOpenAI
from utils.memory import SQLiteConversationEntityMemory


from dotenv import load_dotenv
load_dotenv()

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

# conn = get_connection()

# entity_store = SQLiteEntityStore(
#     conn=conn,
#     session_id="default",
# )


memory = SQLiteConversationEntityMemory(
    llm=OpenAI(model="gpt-3.5-turbo-instruct", temperature=0),
)


system_prompt_str = """
You are a helpful assistant.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_str),
        ("placeholder", "{history}"),
        # {chat_history} corresponds with ConversationBufferMemory.memory_key
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [
    # Dummy tool because the model didn't like being passed an empty list
    Tool(
        name="Default",
        func=lambda: None,
        description="This tool does nothing."
    )
]

llm = ChatOpenAI(
    model=CHATBOT_AGENT_MODEL,
    temperature=1,
)

agent = create_tool_calling_agent(llm, tools, prompt)
# create_openai_functions_agent deprecated

chatbot_agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
    handle_parsing_errors=True,
    memory=memory,
)