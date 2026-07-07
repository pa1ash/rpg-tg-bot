from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Character


async def get_character(session: AsyncSession, telegram_id: int):
    query = select(Character).where(Character.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def add_character(session: AsyncSession,
                        telegram_id: int, username: str, char_class: int,
                        difficulty: int):
    new_char = Character(
        telegram_id = telegram_id,
        username = username,
        char_class = char_class,
        difficulty = difficulty,
    )

    session.add(new_char)
    await session.commit()
    return new_char


async def update_character_name(session: AsyncSession, telegram_id: int, new_name: str):
    character = await get_character(session, telegram_id)
    if character:
        character.username = new_name
        await session.commit()
        return character
    return None



async def delete_character(session: AsyncSession, telegram_id: int):
    character = await get_character(session, telegram_id)
    if character:
        await session.delete(character)
        await session.commit()
        return True
    return False


