import sys
import collections
from datetime import timedelta
import logging

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from timeloop import Timeloop
from ZaraMonitor import ZaraMonitor

zara_monitor_bot_token = sys.argv[1]
print('Using token: {}'.format(zara_monitor_bot_token))
updater = Updater(token=zara_monitor_bot_token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
tasks = collections.defaultdict(list)
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
    try:
        zara_monitor = ZaraMonitor(url)
        add_task_for_user(user_id, chat_id, zara_monitor, callback_context)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Добавлено: {}".format(zara_monitor.get_title()))
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Нужен URL для zara.com')
    

def print_list(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_tasks = get_tasks_titles_for_user(user_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_tasks)

def remove(update: Update, context: CallbackContext):
    index_to_remove = update.message.text.removeprefix('/remove ')
    user_id = update.effective_user.id
    try:
        int_index = int(index_to_remove)
        object_to_remove = list(tasks[user_id])[int_index - 1]
        context.bot.send_message(chat_id=update.effective_chat.id, text='Удалено: {}'.format(object_to_remove['monitor'].get_title()))
        tasks[user_id].remove(object_to_remove)
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Нужна цифра после remove')
      
def add_task_for_user(user_id, chat_id, zara_monitor : ZaraMonitor, callback_context: CallbackContext):
    tasks[user_id].append({'monitor': zara_monitor, 'context': callback_context, 'chat_id': chat_id})

def get_tasks_for_user(user_id):
    return tasks[user_id]

def get_tasks_titles_for_user(user_id):
    i = 1
    reply = 'Список шмоток:\n'
    for task in get_tasks_for_user(user_id):
        reply += '{}. {}\n'.format(i, task['monitor'].get_title())
    return reply

def remove_task_for_user(user_id, zara_monitor):
    for value in tasks[user_id]:
        if value['monitor'] == zara_monitor and value['monitor'].is_found:
            value['context'].bot.send_message(chat_id=value['chat_id'], text='Удаляю {}'.format(value['monitor'].get_title()))
            tasks[user_id].remove(value)

@tl.job(interval=timedelta(seconds=10))
def run():
    for key in tasks:
        for value in tasks[key]:
            result = value['monitor'].check()
            if result:
                value['context'].bot.send_message(chat_id=value['chat_id'], text='В наличии! Срочно беги проверять!')
                value['context'].bot.send_message(chat_id=value['chat_id'], text=value['monitor'].monitor_url)
                remove_task_for_user(key, value['monitor'])

start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
list_handler = CommandHandler('list', print_list)
remove_handler = CommandHandler('remove', remove)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(remove_handler)
updater.start_polling()
tl.start()
