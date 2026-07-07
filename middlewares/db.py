
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram import BaseMiddleware

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker):
        self.session_maker = session_maker
    async def __call__(self, handler, event, data):
        async with self.session_maker() as session:
            data["session"] = session
            return await handler(event, data)