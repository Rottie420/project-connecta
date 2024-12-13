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
    def log_for_ai_training(control_number, user_input, ai_response):
        """
        Logs user input, AI response, and control number in JSON format for AI training.
        Appends the log entry to the training data file only.
        """
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Convert AI response to string format if it is a dictionary
        if isinstance(ai_response, dict):
            ai_response = json.dumps(ai_response)

        # Create a log entry for this instance
        log_entry = {
            control_number: {
                "timestamp": now,
                "input": user_input,
                "output": ai_response
            }
        }

        # Append the log entry to the training data file
        try:
            with open(TRAINING_DATA_FILE, 'a') as file:
                file.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            Logger.log(f"Error logging AI training data: {e}")
