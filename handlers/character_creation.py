from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from models import Character
from constants import RPGaction
from crud import get_character, add_character
import httpx

router = Router()

class CharacterCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_class = State()
    waiting_for_difficulty = State()

CLASSES = {
    11: "Рыцарь",
    12: "Маг",
    13: "Кавалерия"
}

DIFFICULTIES = {
    21: "Лёгкая",
    22: "Средняя",
    23: "Хард"
}


@router.message(CharacterCreation.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(CharacterCreation.waiting_for_class)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text= "Рыцарь",
        callback_data = RPGaction(action_type='choice', target_id=11).pack()
    ))
    builder.add(types.InlineKeyboardButton(
        text= 'Маг',
        callback_data= RPGaction(action_type="choice", target_id=12).pack()
    ))
    builder.add(types.InlineKeyboardButton(
        text='Кавалерия',
        callback_data= RPGaction(action_type="choice", target_id=13).pack()
    ))
    builder.adjust(1)

    await message.answer(
        text= 'Выберите класс',
        reply_markup=builder.as_markup()
    )

@router.callback_query(RPGaction.filter(F.action_type == 'choice'), CharacterCreation.waiting_for_class)
async def process_class_selection(callback: types.CallbackQuery, callback_data: RPGaction, state: FSMContext):
    # Логика обработки выбора класса
    await state.update_data(char_class=callback_data.target_id)

    await state.set_state(CharacterCreation.waiting_for_difficulty)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text= "Лёгкая",
        callback_data= RPGaction(action_type='difficulty', target_id=21).pack()
    ))

    builder.add(types.InlineKeyboardButton(
        text= 'Средняя',
        callback_data= RPGaction(action_type='difficulty', target_id=22).pack()
    ))

    builder.add(types.InlineKeyboardButton(
        text= 'Хард',
        callback_data= RPGaction(action_type='difficulty', target_id=23).pack()
    ))

    await callback.message.edit_text(
        text= "Выберите сложность",
        reply_markup= builder.as_markup()
    )


@router.callback_query(RPGaction.filter(F.action_type == 'difficulty'), CharacterCreation.waiting_for_difficulty)
async def process_difficulty_selection(callback: types.CallbackQuery,
                                       callback_data: RPGaction,
                                       state: FSMContext):
    await state.update_data(difficulty=callback_data.target_id)  # 💾 Сохраняем сложность

    data = await state.get_data()
    payload = data.copy()
    payload["telegram_id"] = callback.from_user.id
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/character", json=payload)

    await state.clear()
    await callback.message.edit_text(
        text= f"Ваш персонаж:\nИмя: {data['username']}\nВыбранный класс: {CLASSES[data['char_class']]}\nСложность: {DIFFICULTIES[data['difficulty']]}"
    )


@router.message(Command("create"))
async def cmd_create(message: types.Message, state: FSMContext):
    url = f"http://127.0.0.1:8000/character?telegram_id={message.from_user.id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()

    if "username" in data:
        await message.answer(text="Персонаж уже создан! Используйте /menu чтобы начать/продолжить игру.")
        return

    await message.answer(text="Гоу создавать перса!\nВведи имя:")
    await state.set_state(CharacterCreation.waiting_for_name)