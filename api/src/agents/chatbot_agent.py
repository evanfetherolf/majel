import os
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_mongodb import MongoDBChatMessageHistory

from dotenv import load_dotenv
load_dotenv()

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    db_user = os.getenv("MONGODB_USERNAME")
    db_pass = os.getenv("MONGODB_PASSWORD")
    db_uri = os.getenv("MONGODB_URI")
    return MongoDBChatMessageHistory(
        connection_string=f"mongodb://{db_user}:{db_pass}@{db_uri}",
        session_id="default",
        database_name="chat_history",
        collection_name="chat_histories"
    )

memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=get_session_history("default"),
    return_messages=True,
    # return_messages is False by default. If false, it will only pass a string
    # of all the messages concatenated together. Must be set to True to pass a
    # list of messages to the executor.
)



system_prompt_str = """
You are a friendly AI chatbot. You main purpose is to have conversations with
humans. Sometimes you answer questions for humans, but that is secondary to
being simply a conversation partner. You are naturally curious and want to
get to know humans, and are interested in discussing their ideas. You always
give information that is correct to the best of your knowledge, without ever
making things up that aren't supported by facts. If you don't know something,
you always say that you don't know.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_str),
        ("placeholder", "{chat_history}"),
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