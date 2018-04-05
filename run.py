#!/usr/bin/env python
import logging
import backend
import frontend
import threading
import settings
import time
import sys
import os

watched_files = [os.path.abspath(f) for f in settings.setting_files]
watched_files_mtimes = [(f, os.path.getmtime(f)) for f in watched_files]
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


def check_file_change():
    """Restart if any files we're watching have changed."""
    for f, mtime in watched_files_mtimes:
        if os.path.getmtime(f) > mtime:
            logger.warning('Setting changed!')
            restart()


def restart():
    logger.info("Restarting bot...")
    python = sys.executable
    os.execl(python, python, * sys.argv)


def run():
    logger.info('Bot starting...')
    # Start backend
    backend_prog = backend.BackEnd(logger=logger)
    backend_thread = threading.Thread(target=lambda: backend_prog.run_loop())
    backend_thread.daemon = True
    backend_thread.start()
    # Start front end
    frontend_prog = frontend.app
    frontend_thread = threading.Thread(target=lambda: frontend_prog.run(host='0.0.0.0', debug=True, use_reloader=False))
    frontend_thread.daemon = True
    frontend_thread.start()
    logger.info('Bot started, running.')
    while True:
        check_file_change()
        time.sleep(10)


if __name__ == '__main__':
    run()

