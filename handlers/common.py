from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ContentType

from utils.config import BOT_TOKEN
from typing import Union
from keyboards.menu import arrows

from io import BytesIO
from aiogram.types import InputFile, FSInputFile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from PIL import Image

import io
import time
import requests
from datetime import datetime, timedelta
import os
import glob


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
    

def get_chart_image(token_symbol):
    # Configure WebDriver options
    options = Options()
    options.headless = True  # Run in headless mode
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    try:
        # Construct the TradingView URL
        trading_view_chart_url = f"https://www.mexc.com/exchange/BLUB_USDT"
        # Navigate to the page
        driver.get(trading_view_chart_url)
        
        time.sleep(1) 
        css_selector = ".ant-popover[class*='symbol-price_priceTipOverlay_'] .mx-icon[class*='symbol-price_closeBtn_']"
        notification_click = driver.find_element(By.CSS_SELECTOR, css_selector)
        actions = ActionChains(driver)
        actions.click(notification_click)
        actions.perform()
        # Wait for the page to load completely
        time.sleep(3)  # Adjust timing according to your network speed and page complexity
        
        # Take a full screenshot
        full_screenshot = driver.get_screenshot_as_png()

        # Open the screenshot as an Image object
        image = Image.open(io.BytesIO(full_screenshot))

        # Define the rectangle area to crop (left, upper, right, lower)
        area = (384, 192, 1450, 610)
        cropped_image = image.crop(area)

        # Save or process the cropped image
        cropped_image_bytes = io.BytesIO()
        cropped_image.save(cropped_image_bytes, format='PNG')
        return cropped_image_bytes.getvalue()
    finally:
        driver.quit()  # Make sure to quit the driver to free resources

    return None

def save_chart_image(image_data):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"chart_{timestamp}.png"
    with open(filename, "wb") as image_file:
        image_file.write(image_data)
    return filename

def get_latest_image():
    list_of_files = glob.glob('chart_*.png')  # * means all if need specific format then *.csv
    if not list_of_files:  # No files found
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

@router.message(Command(commands=["chart"]))
async def cmd_chart(message: Message, state: FSMContext):
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
    await message.answer_photo(photo=photo_file, caption=f"The current price of BLUB is: {price} USD")

@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer("This Bot is designed to help you with your trading on the BLUB platform. It provides you with the latest price of BLUB, as well as a chart of the price over time. It also allows you to set up alerts for when the price of BLUB reaches a certain level.") 

@router.message(Command(commands=["price"]))
async def cmd_price(message: Message, state: FSMContext):
    token_symbol = "BLUB_USDT"  # Change this to the token pair you are interested in
    price = get_token_price(token_symbol)
    print(f"The current price of {token_symbol} is: {price}")
    await message.answer(f"The current price of BLUB is: {price} usd")


@router.callback_query(F.data.startswith("arrow:"))
async def handle_arrow_callback(callback: CallbackQuery, _state: FSMContext):
    request = callback.data.split(':')[1]
    _user_id = callback.from_user.id
    next_page = 1 if request == "next" else 0
    if next_page < 1:
        next_page = 1
    keyboard = arrows(True if next_page == 1 else False)
    await callback.message.answer(
        text = "Hello, This is the arrow response",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
@router.message(CommonState.setting_input)
async def handle_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer("Hello" + user_id)
    await state.set_state(CommonState.setting_input)


async def cmd_invoke(message: Message):
    # user_id = message.from_user.id
    await message.answer("Please wait as the model is invoked...")
    

async def process_msg(message: Message, instruction: ContentType):
    bot = Bot(token=BOT_TOKEN)
    if instruction != message.content_type:
        return None
    elif message.content_type == ContentType.PHOTO:
        photo_id = message.photo[-1].file_id
        photo_info = await bot.get_file(photo_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo_info.file_path}"
        print(message.photo, message.photo[-1], photo_id, photo_info, file_url)
        return file_url
    elif message.content_type == ContentType.AUDIO:
        audio_file_id = message.audio.file_id
        audio_info = await bot.get_file(audio_file_id)
        audio_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{audio_info.file_path}"
        return audio_url
    elif message.content_type == ContentType.VIDEO:
        video_file_id = message.video.file_id
        video_info = await bot.get_file(video_file_id)
        video_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{video_info.file_path}"
        return video_url
    else:
        return None
    

def get_token_price(symbol):
    url = f"https://www.mexc.com/open/api/v2/market/ticker?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    if data and 'data' in data and len(data['data']) > 0:
        price = data['data'][0]['last']
        return price
    else:
        return "Price data not available"