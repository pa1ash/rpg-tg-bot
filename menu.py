from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from constants import RPGaction
from sqlalchemy.ext.asyncio import AsyncSession
from crud import get_character
from handlers.character_creation import CLASSES
from crud import update_character_name, delete_character
import httpx

router = Router()
enemies = [ ('Гоблин', 1), ('Орк', 2), ('Дракон', 3), ('Скелет', 4), ('Король пауков', 5) , ('Вернуться назад', 0)]


async def get_enemies_keyboard(array):
    builder = InlineKeyboardBuilder()
    for name, target_id in array:
        if target_id != 0:
            builder.add(types.InlineKeyboardButton(
                text=f"Атаковать {name}",
                callback_data=RPGaction(action_type="attack", target_id=target_id).pack()
            ))
        else:
            builder.add(types.InlineKeyboardButton(
                text= name,
                callback_data = RPGaction(action_type='back', target_id=target_id).pack()
            ))

    builder.adjust(2)
    return builder





@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    url = f"http://127.0.0.1:8000/character?telegram_id={message.from_user.id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()


    builder = await get_enemies_keyboard(enemies)
    if "message" in data:
        await message.answer(text="У вас еще нет персонажа! Используйте /create для создания.")
        return

    await message.answer(
        text= f"⚔️Игрок: {data['username']}\nВыбранный класс: {CLASSES.get(data['char_class'])}\n\nВыбери противника для боя:",
        reply_markup= builder.as_markup()
    )

@router.callback_query(RPGaction.filter())
async def handle_rpg_actions(callback: types.CallbackQuery, callback_data: RPGaction ):
    action = callback_data.action_type
    target = callback_data.target_id

    if action == 'attack':
        await callback.answer()
        back_builder = InlineKeyboardBuilder()
        back_builder.add(types.InlineKeyboardButton(
            text = "Вернуться назад",
            callback_data= RPGaction(action_type='back', target_id=0).pack()
        ))
        await callback.message.edit_text(f"Вы выбрали атаку! Тип действия {action}, ID цели: {target}",
                                         reply_markup=back_builder.as_markup())
    if action == 'back':
        await callback.answer()
        builder = await get_enemies_keyboard(enemies)

        await callback.message.edit_text(
            text="Проверка на ***",
            reply_markup= builder.as_markup()
        )

@router.message(Command("rename"))
async def cmd_rename(message: types.Message,
                     command: CommandObject):
    new_name = command.args
    if not new_name:
        await message.answer(text="Введите имя после команды. Например: /rename 67покойо67")
        return
    payload = {
        "telegram_id": message.from_user.id,
        "new_name": new_name
    }
    async with httpx.AsyncClient() as client:
        response = await client.patch("http://127.0.0.1:8000/character/rename", json=payload)
    data = response.json()
    await message.answer(data["message"])
    return

@router.message(Command("reset"))
async def cmd_reset(message: types.Message):
    url = f"http://127.0.0.1:8000/character?telegram_id={message.from_user.id}"
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
    data = response.json()
    await message.answer(data["message"])
    return