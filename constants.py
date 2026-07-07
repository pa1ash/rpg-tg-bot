from aiogram.filters.callback_data import CallbackData

class RPGaction(CallbackData, prefix='rpg'):
    action_type: str
    target_id: int
