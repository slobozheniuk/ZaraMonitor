import subprocess

import sys
import collections
from datetime import timedelta
import logging

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from timeloop import Timeloop

zara_monitor_bot_token = sys.argv[1]
print('Using token: {}'.format(zara_monitor_bot_token))
updater = Updater(token=zara_monitor_bot_token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
tasks = ['zara-black.spec.ts', 'zara-grey.spec.ts', 'zara-white.spec.ts', 'zara-test.spec.ts']
tl = Timeloop()

def run_playwright_test(test_name):
    # Construct the command to run the Playwright test
    command = f'npx playwright test {test_name} --headed'

    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

        # Check the result and return True if the test passed, False otherwise
        if result.returncode == 0:
            return True
        else:
            return False

    except subprocess.CalledProcessError as e:
        return False            

@tl.job(interval=timedelta(seconds=10))
def run():
    for key in tasks:
        for value in tasks[key]:
            result = value['monitor'].check()
            if result:
                context.bot.send_message(chat_id=value['chat_id'], text='В наличии! Срочно беги проверять!')
                value['context'].bot.send_message(chat_id=value['chat_id'], text=value['monitor'].monitor_url)
                remove_task_for_user(key, value['monitor'])

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
updater.start_polling()
tl.start()




print(run_playwright_test('zara-black.spec.ts'))
print(run_playwright_test('zara-white.spec.ts'))
print(run_playwright_test('zara-grey.spec.ts'))