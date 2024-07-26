import os
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_mongodb import MongoDBChatMessageHistory

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
You are a helpful assistant.
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
tavily_search_results = TavilySearchResults()
tools = [tavily_search_results]

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