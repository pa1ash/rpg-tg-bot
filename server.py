from crud import delete_character, get_character, add_character, update_character_name
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import DATABASE_URL
app = FastAPI()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session

class CharacterCreate(BaseModel):
    telegram_id: int
    username: str
    char_class: int
    difficulty: int

class CharacterRename(BaseModel):
    telegram_id: int
    new_name: str

# @app.get("/")
# async def read_root():
#     return {"message": "Привет! API работает."}

@app.delete("/character")
async def delete_char(telegram_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_character(db, telegram_id)
    if success:
        return {"message" : "Персонаж успешно удален"}
    return {"message": "Персонаж не найден или его не существует"}

@app.get("/character")
async def get_char(telegram_id: int, db: AsyncSession = Depends(get_db)):
    character = await get_character(db, telegram_id)
    if character is not None:
        return {"username" : character.username,
                "char_class": character.char_class,
                "hp": character.hp,
                "max_hp": character.max_hp,
                "level": character.level,
                "xp": character.xp}
    return {"message": "Персонаж не найден"}

@app.post("/character")
async def create_char(payload: CharacterCreate,
                      db: AsyncSession = Depends(get_db),
                      ):
    new_hero = await add_character(
        session=db,
        telegram_id=payload.telegram_id,
        username=payload.username,
        char_class=payload.char_class,
        difficulty=payload.difficulty,
    )
    return {"message" : "Персонаж создан!",
            "id": new_hero.id}

@app.patch("/character/rename")
async def rename_char(payload: CharacterRename,
                      db: AsyncSession = Depends(get_db)):
    updated_char = await update_character_name(db, payload.telegram_id, payload.new_name)
    if updated_char is not None:
        return {"message": f"Имя изменено на: {payload.new_name}"}
    return {"message": "Ошибка! Возможно, персонажа не существует."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)