import os

from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

chat_history=[]

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
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [
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
)