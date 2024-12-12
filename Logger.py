from datetime import datetime
from config import LOG_FILE_PATH, TRAINING_DATA_FILE
import json

class Logger:
    @staticmethod
    def log(*args, **kwargs):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        message = f"{now} : {' '.join(map(str, args))}"
        print(message, **kwargs)
        
        with open(LOG_FILE_PATH, 'a') as file:
            file.write(message + "\n")

    @staticmethod
    def log_for_ai_training(user_input, ai_response):
        """
        Logs user input and AI response in JSON format for AI training.
        """
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        log_entry = {
            "timestamp": now,
            "input": user_input,
            "output": ai_response
        }
        
        # Append the log entry to the training data file
        try:
            with open(TRAINING_DATA_FILE, 'a') as file:
                file.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            Logger.log(f"Error logging AI training data: {e}")