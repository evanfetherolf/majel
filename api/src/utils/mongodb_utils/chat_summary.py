import json
import logging
from typing import Dict, List, Optional

from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    message_from_dict
)
from pymongo import MongoClient, errors

logger = logging.getLogger(__name__)

DEFAULT_DBNAME = "chat_history"
DEFAULT_COLLECTION_NAME = "message_store"
DEFAULT_SESSION_ID_KEY = "SessionId"
DEFAULT_HISTORY_KEY = "History"


class MongoDBSummaryChatMemory(BaseChatMemory):
    """Chat summary that stores summary in MongoDB.

    Args:
        connection_string: connection string to connect to MongoDB
        session_id: arbitrary key that is used to store the summary
            of a single chat session.
        database_name: name of the database to use
        collection_name: name of the collection to use
        session_id_key: name of the field that stores the session id
        history_key: name of the field that stores the chat history
        create_index: whether to create an index on the session id field
        index_kwargs: additional keyword arguments to pass to the index creation
    """

    def __init__(
            self,
            connection_string: str,
            session_id: str,
            database_name: str = DEFAULT_DBNAME,
            collection_name: str = DEFAULT_COLLECTION_NAME,
            *,
            session_id_key: str = DEFAULT_SESSION_ID_KEY,
            history_key: str = DEFAULT_HISTORY_KEY,
            create_index: bool = True,
            index_kxargs: Optional[Dict] = None,
        ):
        self.connection_string = connection_string
        self.session_id = session_id
        self.database_name = database_name
        self.collection_name = collection_name
        self.session_id_key = session_id_key
        self.history_key = history_key
    
    try:
        self.client = 