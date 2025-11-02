import sqlite3, os
from typing import Literal
from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.checkpoint.mongodb import MongoDBSaver
# from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import InMemorySaver


class Storage:
    def __init__(
        self,
        mode: Literal["memory", "database"],
        database: Literal["sqlite", "mongo", "postgres"] = "sqlite"
    ) -> None:
        if mode == "memory":
            self.storage = InMemorySaver()
        else:
            # if database == "mongo": self.storage = self._set_mongo_storage()
            # if database == "postgres": self.storage = self._set_postgres_storage()
            # else: self.storage = self._set_sqlite_storage()
            self.storage = self._set_sqlite_storage()
    
    def _set_sqlite_storage(self) -> SqliteSaver:
        connection = sqlite3.connect("chatbot.db", check_same_thread=False)
        return SqliteSaver(connection)
    
    # def _set_mongo_storage(self) -> MongoDBSaver:
    #     return MongoDBSaver(uri=os.environ.get("MONGODB_CONNECTION_URI", ""), db_name="chatbot.db")
    
    # def _set_postgres_storage(self) -> PostgresSaver:
    #     return PostgresSaver(conn_string=os.environ.get("POSTGRES_CONNECTION_URI", ""))
