from dotenv import load_dotenv
import os
import asyncpg

load_dotenv("./utils/.env")

class Database:
    def __init__(self):
        self.__version__ = "0.2"
        
    async def get_connection(self) -> asyncpg.connection.Connection:
        return await asyncpg.connect(os.environ["PSQL_URI"])