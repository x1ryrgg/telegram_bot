from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_keyboard():
    kb_buttons = [
        [KeyboardButton(text='Доставка')],
        [KeyboardButton(text='История покупок')],
        [KeyboardButton(text='Выйти из акканута')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True,
                                   input_field_placeholder='Выбирите пункт на клавиатуре')
    return keyboard