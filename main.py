import asyncio
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import TOKEN, DATABASE_URL
from middlewares.db import DbSessionMiddleware
from handlers.character_creation import router as character_router
from menu import router as menu_router

async def main():
    print("Бот успешно запустился!")

    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.update.outer_middleware(DbSessionMiddleware(session_maker=async_session))

    dp.include_router(character_router)
    dp.include_router(menu_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())