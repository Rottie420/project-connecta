from datetime import datetime
from config import LOG_FILE_PATH

class Logger:
    @staticmethod
    def log(*args, **kwargs):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        message = f"{now} : {' '.join(map(str, args))}"
        print(message, **kwargs)
        
        with open(LOG_FILE_PATH, 'a') as file:
            file.write(message + "\n")