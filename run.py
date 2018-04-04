import backend
import threading
import logging
import time
import sys
import os

logging.info('Bot starting...')
settings_mtime = os.path.getmtime('settings.py')
backend_thread = threading.Thread(backend.run())
backend_thread.daemon = True
backend_thread.start()

logging.info('Bot started, running.')
while True:
    time.sleep(10)
    new_mtime = os.path.getmtime('settings.py')
    if new_mtime > settings_mtime:
        logging.warning('Config changed, restarting bot')
        program = sys.executable
        os.execl(program, program, *sys.argv)


