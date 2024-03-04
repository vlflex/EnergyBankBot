from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# клавиатура с "да" и "нет"
def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text = 'Да')
    builder.button(text = 'Нет')
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup