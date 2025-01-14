from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional

router = Router()

class MenuFactory(CallbackData, prefix="trade"):
    action: str
    process: Optional[str] = None
    subject: Optional[str] = None

def generate_menu():
    markup = InlineKeyboardBuilder()
    markup.button(text="----- Wallet -----", callback_data='filler')
    markup.button(text="💼 Create", callback_data="wallet_create")
    markup.button(text="📤 Import", callback_data="wallet_import")
    markup.button(text="🗑️ Delete", callback_data="wallet_delete")

    markup.adjust(1, 3)
    return markup.as_markup()

def arrows(single:bool=False):
    markup = InlineKeyboardBuilder()
    if not single:
        markup.button(text="Previous", callback_data="arrow:previous")
    markup.button(text="Next", callback_data="arrow:next")
    arrow_count = 1 if single else 2
    markup.adjust(arrow_count)
    return markup.as_markup()
