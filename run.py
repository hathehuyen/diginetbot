import backend
import threading
import time

backend_thread = threading.Thread(backend.run())
backend_thread.daemon = True
backend_thread.start()

while True:
    time.sleep(10)

