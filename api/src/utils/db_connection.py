import sqlite3
import threading
import logging

class DBConnection:
    def __init__(self, db_path="entities.db"):
        self.db_path = db_path
        self.conn = None
        self.thread_local = threading.local()

    def open_connection(self):
        if not hasattr(self.thread_local, "conn"):
            self.thread_local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )
        logging.info("DB connection opened")
        return self.thread_local.conn
  
    def close_connection(self):
        if not hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            del self.thread_local.conn
        logging.info("DB connection closed.")
