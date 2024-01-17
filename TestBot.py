import asyncio
import sys
import collections
from datetime import timedelta
import logging
import time
from playwright.async_api import async_playwright

from telegram import Update
from telegram.ext import Application, Updater, CallbackContext, CommandHandler
from telegram.error import NetworkError
from timeloop import Timeloop
from ZaraMonitor import ZaraMonitor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

zara_monitor_bot_token = sys.argv[1]
print('Using token: {}'.format(zara_monitor_bot_token))
application = Application.builder().token(zara_monitor_bot_token).build()
chat_urls = []
tl = Timeloop()

# Function to add a chat_id and URL
def add_chat_url(chat_id, url):
    logging.info(f"Added {(chat_id, url)} to chat_urls.")
    chat_urls.append((chat_id, url))

def remove_chat_url(chat_id, url):
    try:
        chat_urls.remove((chat_id, url))
        logging.info(f"Removed {(chat_id, url)} from chat_urls.")
    except ValueError:
        logging.warn(f"Tuple {(chat_id, url)} not found in chat_urls.")
# Function to get URLs by chat_id
def get_urls_by_chat_id(chat_id):
    return [url for cid, url in chat_urls if cid == chat_id]

async def ping(update: Update, context: CallbackContext):
    chatid = update.effective_chat.id
    await send_message(chat_id = chatid, text="I am alive and have {} requests for your chat".format(len(get_urls_by_chat_id(chatid))))

async def check(update: Update, context: CallbackContext):
    url = update.message.text.removeprefix('/check ')
    try:
        out_of_stock = await is_out_of_stock(url)
    except:
        logging.error("Something is wrong")    
    await send_message(chat_id = update.effective_chat.id, text='Out of stock' if out_of_stock else 'In stock')

async def add(update: Update, context: CallbackContext):
    url = update.message.text.removeprefix('/add ')
    chat_id = update.effective_chat.id
    add_chat_url(chat_id, url)
    logging.info('Added {} for {}'.format(url, chat_id))
    try:
        await send_message(chat_id=chat_id, text='Added ' + await get_title(url))
    except:
        await update.message.reply_text(text='Something is wrong, try again later')

async def is_out_of_stock(url):
    async with async_playwright() as p:
        # Create a browser instance
        browser = await p.chromium.launch()
        # Create a context and a page inside it
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        # Navigate to the URL
        await page.goto(url)
        # Get the title of the page
        # Select the element with the specified class name
        element = await page.query_selector('.product-detail-info__buttons')

        if element:
            # Get the inner text of the element
            text_content = await element.inner_text()
            # Check if the text contains "OUT OF STOCK"
            is_out_of_stock = "OUT OF STOCK" in text_content.upper()
        else:
            # Element not found
            is_out_of_stock = False
        # Close the browser
        await browser.close()
        return is_out_of_stock
    
async def get_title(url):
    async with async_playwright() as p:
        # Create a browser instance
        browser = await p.chromium.launch()
        # Create a context and a page inside it
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        # Navigate to the URL
        await page.goto(url)
        # Get the title of the page
        # Select the element with the specified class name
        title = await page.title()
        await browser.close()
        return title    
    
@tl.job(interval=timedelta(seconds=15))
def run():
    asyncio.run(check_async())

async def check_async():
    logging.info('Running the {} checks'.format(len(chat_urls)))
    toDelete = []
    for chat_id, url in chat_urls:
        logging.info('Checking {} for {}'.format(url, chat_id))
        out_of_stock = await is_out_of_stock(url)
        logging.info('{} is {}'.format(url, 'out of stock...' if out_of_stock else 'IN STOCK!!'))
        if not out_of_stock:
            try:
                await send_message(chat_id = chat_id, text=url)
                await asyncio.sleep(3)
                await send_message(chat_id = chat_id, text='In Stock!!')
                await asyncio.sleep(3)
                await send_message(chat_id = chat_id, text='ALERT!!!')
                toDelete.append((chat_id, url))
            except:
                logging.error('Could not notify')
                return  
    for chat_id, url in toDelete:
        remove_chat_url(chat_id, url)        

async def send_message(chat_id, text, max_retries=3):
    for attempt in range(max_retries):
        try:
            await application.bot.send_message(chat_id=chat_id, text=text)
            logging.info(f"Message sent to {chat_id}")
            break  # Break the loop if message is sent successfully
        except NetworkError:
            logging.warning(f"NetworkError encountered. Attempt {attempt + 1} of {max_retries}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break  # Break on other unexpected errors


tl.start()
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("check", check))
application.add_handler(CommandHandler("add", add))

application.run_polling(allowed_updates=Update.ALL_TYPES)