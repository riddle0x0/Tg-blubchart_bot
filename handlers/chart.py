
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from PIL import Image

import io
import time
from datetime import datetime
import os
import glob


def get_chart_image(token_symbol):
    # Configure WebDriver options
    options = Options()
    options.headless = True  # Run in headless mode
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    try:
        # Construct the TradingView URL
        trading_view_chart_url = "https://www.mexc.com/exchange/BLUB_USDT"
        # Navigate to the page
        driver.get(trading_view_chart_url)
        
        # time.sleep(1) 
        notification_selector = ".ant-popover[class*='symbol-price_priceTipOverlay_'] .mx-icon[class*='symbol-price_closeBtn_']"
        notification_click = driver.find_element(By.CSS_SELECTOR, notification_selector)

        
        timeStamp_selector =  "[class*='klineInterval_klineActions_'] > :nth-child(6)"
        timeStamp_click = driver.find_element(By.CSS_SELECTOR, timeStamp_selector)

        actions = ActionChains(driver)
        actions.click(timeStamp_click)
        actions.click(notification_click)
        actions.perform()
        # Wait for the page to load completely
        time.sleep(1)  # Adjust timing according to your network speed and page complexity
        
        # Take a full screenshot
        full_screenshot = driver.get_screenshot_as_png()

        # Open the screenshot as an Image object
        image = Image.open(io.BytesIO(full_screenshot))

        # Define the rectangle area to crop (left, upper, right, lower)
        area = (395, 192, 1490, 630)
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
    directory = "chart"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{directory}/chart_{timestamp}.png"
    with open(filename, "wb") as image_file:
        image_file.write(image_data)
    return filename

def get_latest_image():
    list_of_files = glob.glob('chart/chart_*.png')  # * means all if need specific format then *.csv
    if not list_of_files:  # No files found
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


