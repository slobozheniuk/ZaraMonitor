import sys
import collections
from datetime import timedelta
import logging
import time

from telegram import Update
from telegram.ext import Application, Updater, CallbackContext, CommandHandler
from timeloop import Timeloop
from ZaraMonitor import ZaraMonitor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

zara_monitor_bot_token = sys.argv[1]
print('Using token: {}'.format(zara_monitor_bot_token))
application = Application.builder().token(zara_monitor_bot_token).build() 
tasks = dict([])
tl = Timeloop()

async def start(update: Update, context: CallbackContext):
    hello_text = """
    Надеюсь сработает :)
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=hello_text)

def add(update: Update, context: CallbackContext):
    url = update.message.text.removeprefix('/add ')
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    callback_context = context

    task = (ZaraMonitor(url), callback_context, user_id, chat_id) 
    tasks[url] = task
    task[1].bot.send_message(chat_id=update.effective_chat.id, text="Добавлено: {}".format(task[0].monitor_url))
      
async def ping(update: Update, context: CallbackContext):
    chatid = update.effective_chat.id
    await application.bot.send_message(chat_id = chatid, text="Chat ID: {}".format(chatid))

def remove_task(url):
    task = tasks[url]
    task[1].bot.send_message(chat_id=task[3], text="Удаляю: {}".format(task[0].monitor_url))
    del tasks[url]

@tl.job(interval=timedelta(seconds=15))
def run():
    toDelete = []
    for taskKey in tasks.keys():
        result = tasks[taskKey][0].check()
        if not result:
            tasks[taskKey][1].bot.send_message(chat_id=tasks[taskKey][3], text='В наличии! Срочно беги проверять!')
            time.sleep(3)
            tasks[taskKey][1].bot.send_message(chat_id=tasks[taskKey][3], text=tasks[taskKey][0].monitor_url)
            time.sleep(3)
            tasks[taskKey][1].bot.send_message(chat_id=tasks[taskKey][3], text='Быстро!!!')
            time.sleep(3)
            tasks[taskKey][1].bot.send_message(chat_id=tasks[taskKey][3], text='Разберут ведь!!!')
            toDelete.append(taskKey)
    for key in toDelete:
        remove_task(key)


    # Create the Application and pass it your bot's token.
    
    # on different commands - answer in Telegram
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("ping", ping))

tl.start()
    # Run the bot until the user presses Ctrl-C
application.run_polling(allowed_updates=Update.ALL_TYPES)