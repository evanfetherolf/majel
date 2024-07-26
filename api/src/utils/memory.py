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
        global conn
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

class SQLiteConversationEntityMemory(ConversationEntityMemory):
    def __init__(self, llm,):
        super().__init__(llm=llm)
        self.entity_store = SQLiteEntityStore()
        self.llm=llm
        self.return_messages = True
        # self.conn = None
        # self.__post_init__()

    # def __post_init__(self):
    #     self._conn = None
        

    # def open_entity_store(self):
    #     if self.conn is None:
    #         self.conn = sqlite3.connect(
    #             "entities.db",
    #             check_same_thread=False
    #         )
    #         logging.info("Database connection established...")
    #     self.entity_store = SQLiteEntityStore(self.conn)

    # def close_entity_store(self):
    #     if self.conn is not None:
    #         self.conn.close()
    #         self.conn = None
    #         logging.info("Database connection closed...")