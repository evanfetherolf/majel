import sqlite3
import logging
from langchain.memory.entity import (
    BaseEntityStore,
    ConversationEntityMemory,
    SQLiteEntityStore
)
from langchain_openai import OpenAI

conn = None

_entity_store = None

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

class SQLiteDB():
    def __init__(self):
        self.db_path = "entities.db"

    def get_connection(self):
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

class SQLiteConversationEntityMemory(ConversationEntityMemory):
    def __init__(
            self,
            llm,
            chat_history_key: str = "chat_history",
        ):
        self.chat_history_key = chat_history_key
        self.entity_store = None
        self.llm=llm
        self.return_messages = True
        self.__conn = None
        self.__fields_set__ = super.__fields_set__
        super.__init__()

    def open_entity_store(self):
        if self.__conn is None:
            self.__conn == sqlite3.connect(
                "entities.db",
                check_same_thread=False
            )
            logging.info("Database connection established...")
        self.entity_store = SQLiteEntityStore(self.conn)

    def close_entity_store(self):
        if self.__conn is not None:
            self.__conn.close()
            logging.info("Database connection closed...")