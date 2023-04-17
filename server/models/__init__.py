# /app/models/__init__.py

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from server.config import MONGO_DB_NAME, MONGO_DB_URL


class MongoDB:
    def __init__(self):
        self.client = None
        self.client = None

    def connect(self):
        self.client = AsyncIOMotorClient(MONGO_DB_URL)
        self.engine = AIOEngine(client=self.client, database=MONGO_DB_NAME)
        print("DB 와 연결되었습니다.")

    def close(self):
        self.client.close()


mongodb = MongoDB()
