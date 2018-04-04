from backend import BackEnd
import threading
import logging
import time
import sys
import os

# set logging time to GMT
logging.Formatter.converter = time.gmtime
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh = logging.FileHandler('diginetbot.log')
fh.setLevel(logging.WARN)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)

logger.info('Bot starting...')
settings_mtime = os.path.getmtime('settings.py')
backend_prog = BackEnd(logger=logger)
backend_thread = threading.Thread(backend_prog.run())
backend_thread.daemon = True
backend_thread.start()

logger.info('Bot started, running.')
while True:
    time.sleep(10)
    new_mtime = os.path.getmtime('settings.py')
    if new_mtime > settings_mtime:
        logger.warning('Config changed, restarting bot')
        program = sys.executable
        os.execl(program, program, *sys.argv)


