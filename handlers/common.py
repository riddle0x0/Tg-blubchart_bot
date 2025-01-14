from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from typing import Union

from aiogram.types import FSInputFile
import os
from datetime import datetime, timedelta
from .price import get_token_price
from .chart import get_chart_image, save_chart_image, get_latest_image

router = Router()
router.message.filter(F.chat.type == "private")

class CommonState(StatesGroup):
    setting_input = State() # Will be represented in storage as 'CommonState:setting_input'


async def set_bot_commands(bot: Bot):
    return True
    
DELIMITER = "____"
KEY_VALAUE_DELIMITER = "__"
async def process_start_cmd(_text: str, _user_id: int) -> Union[str, None]:
    _jwt_token_present = False
   
            

@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    print(message.text)
    preload_message = await message.answer("Loading bot...")
    await state.clear()

    user_id = message.from_user.id
    try:
        command_message = message.text.split(" ")[1]
        start_process = await process_start_cmd(command_message, user_id)
        if start_process is not None:
            await preload_message.edit_text(start_process)
            return
    except IndexError:
        await preload_message.edit_text("There are no parameters to your start command")
        return
    
    await message.answer("Hello")
    await state.set_state(CommonState.setting_input)
    

@router.message(Command(commands=["chart"]))
async def cmd_chart(message: Message, state: FSMContext):
    processing_message = await message.answer("Processing your request...")
    token_symbol = "BLUB_USDT"
    price = get_token_price(token_symbol)
    latest_image = get_latest_image()
    if latest_image and (datetime.now() - datetime.fromtimestamp(os.path.getmtime(latest_image))) < timedelta(minutes=5):
        # Image is recent, use this one
        photo_file = latest_image
    else:
        # Image is old or not present, generate a new one
        chart_image = get_chart_image(token_symbol)
        if chart_image:
            photo_file = save_chart_image(chart_image)
        else:
            await message.answer("Failed to retrieve chart image.")
            return
   
    photo_file = FSInputFile(path=photo_file)
    # Directly pass the BytesIO object to answer_photo
    await processing_message.answer_photo(photo=photo_file, caption=f"The current price of BLUB is: {price} USD")
    await processing_message.delete()

@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer("This Bot is designed to help you with your trading on the BLUB platform. It provides you with the latest price of BLUB, as well as a chart of the price over time. It also allows you to set up alerts for when the price of BLUB reaches a certain level.") 

@router.message(Command(commands=["price"]))
async def cmd_price(message: Message, state: FSMContext):
    token_symbol = "BLUB_USDT"  # Change this to the token pair you are interested in
    price = get_token_price(token_symbol)
    print(f"The current price of {token_symbol} is: {price}")
    await message.answer(f"The current price of BLUB is: {price} usd")
