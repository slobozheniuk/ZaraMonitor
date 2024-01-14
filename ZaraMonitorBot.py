import sys
import collections
from datetime import timedelta
import logging
import time

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from timeloop import Timeloop
from ZaraMonitor import ZaraMonitor

zara_monitor_bot_token = sys.argv[1]
print('Using token: {}'.format(zara_monitor_bot_token))
updater = Updater(token=zara_monitor_bot_token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
tasks = dict([])

tl = Timeloop()

def start(update: Update, context: CallbackContext):
    hello_text = """
    Как пользоваться ботом?
    3 основные команды:
    /add + URL с сайта - Добавить ссылку для слежения
    /list - Показать все текущие позиции за которыми идет охота
    /remove + число - Перестать следить за позицией (номер берется из list)

    Примеры:
    /add https://zara.com/ru/test.html
    # Добавлено: ИмяШмотки
    /list
    # Список шмоток:
    # 1. ИмяШмотки
    /remove 1
    # Удалено: ИмяШмотки

    Как только статус шмотки поменяется на "В наличии" - бот пришлет уведомление об этом, прикрепит ссылку на шмотку и удалит ее из списка слежения
    
    Надеюсь сработает :)
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=hello_text)

def add(update: Update, context: CallbackContext):
    url = update.message.text.removeprefix('/add ')
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    callback_context = context

    task = (ZaraMonitor(url), callback_context, user_id, chat_id) 
    tasks[url] = task
    task[1].bot.send_message(chat_id=update.effective_chat.id, text="Добавлено: {}".format(task[0].monitor_url))
      
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

start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
updater.start_polling()
tl.start()
