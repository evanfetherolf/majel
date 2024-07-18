import os
from langchain.memory import ConversationSummaryMemory
from langchain_community.memory.kg import ConversationKGMemory
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from langchain_mongodb import MongoDBChatMessageHistory
from pymongo import MongoClient
from neo4j import GraphDatabase

from dotenv import load_dotenv
load_dotenv()

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")


class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        def close(self):
            self.driver.close()

        def run_query(self, query, parameters=None):
            with self.driver.session() as session:
                return session.run(query, parameters)
            
uri = "neo4j+s://b605a4be.databases.neo4j.io"
user = "neo4j"
password="roYlQym0xD29VBEwFUpc3-d8-4fgmuwHPuRwBYTAj-Q"

neo4j_client = Neo4jClient(uri, user, password)

class Neo4jChatMessageHistory:
    def __init__(self, client):
        self.client = client

    def add_message(self, message):
        query = """
        MERGE (m:Message {content: $content, role: $role, timestamp: $timestamp})
        """
        self.client.run_query(query, {
            "content": message["content"],
            "role": message["role"],
            "timestamp": message["timestamp"]
        })
    
    def get_messages(self):
        query = "MATCH (m:Message) RETURN m ORDER BY m.timestamp"
        result = self.client.run_query(query)
        messages = []
        for record in result:
            message = {
                "content": record["m"]["content"],
                "role": record["m"]["role"],
                "timestamp": record["m"]["timestamp"]
            }
            messages.append(message)
        return messages


neo4j_message_history = Neo4jChatMessageHistory(neo4j_client)
conversation_kg_memory = ConversationKGMemory(chat_memory=neo4j_message_history)


# class MongoDBConversationSummaryMemory(ConversationSummaryMemory):
#     def __init__()


# def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
#     db_user = os.getenv("MONGODB_USERNAME")
#     db_pass = os.getenv("MONGODB_PASSWORD")
#     db_uri = os.getenv("MONGODB_URI")
#     return MongoDBChatMessageHistory(
#         connection_string=f"mongodb://{db_user}:{db_pass}@{db_uri}",
#         session_id=session_id,
#         database_name="test_db",
#         collection_name="test_summary"
#     )

# memory = ConversationSummaryMemory(
#     llm=OpenAI(model="gpt-3.5-turbo-instruct", temperature=0),
#     memory_key="chat_history",
#     chat_memory=get_session_history("default"),
#     return_messages=True,
#     # return_messages is False by default. If false, it will only pass a string
#     # of all the messages concatenated together. Must be set to True to pass a
#     # list of messages to the executor.
# )


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