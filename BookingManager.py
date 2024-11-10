import os
import json
import pandas as pd
from Logger import Logger
from config import DATA_FILE

class BookingManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self._initialize_data_file()

    def _initialize_data_file(self):
        """Initialize the data file if it does not exist."""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f, indent=4)

    def read_data(self):
        """Read JSON data from the file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            Logger.log(f"Error reading bookings data: {e}")
            return []

    def write_data(self, data):
        """Write JSON data to the file."""
        try:
            with open(self.data_file, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            Logger.log(f"Error writing bookings data: {e}")

    def book_demo(self, booking_info):
        """Handle booking requests."""
        try:
            if not booking_info.get('name') or not booking_info.get('email'):
                return {'error': 'Name and email are required.'}, 400

            bookings = self.read_data()
            bookings.append(booking_info)
            self.write_data(bookings)
            
            return {'message': 'Booked successfully!', 'booking_info': booking_info}, 200

        except Exception as e:
            Logger.log(f"Book demo error: {e}")
            return {'error': 'An error occurred while processing your request.'}, 500

    def get_admin_dashboard_data(self):
        """Retrieve and format data for the admin dashboard."""
        try:
            df = pd.read_json(self.data_file)

            if 'date' not in df.columns:
                raise KeyError("'date' column is missing from the data")

            try:
                df['date'] = pd.to_datetime(df['date'])
            except Exception as e:
                raise ValueError(f"Error converting 'date' column to datetime: {str(e)}")

            logs = sorted(df.to_dict(orient='records'), key=lambda x: x['date'], reverse=True)

            formatted_logs = [
                {
                    "name": row['name'],
                    "email": row['email'],
                    "phone": row['phone'],
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "time": row['date'].strftime('%H:%M'),
                    "message": row['message']
                }
                for _, row in df.iterrows()
            ]

            return formatted_logs

        except Exception as e:
            Logger.log(f"admin-dashboard error: {e}")
            return {'error': 'An error occurred while processing your request.'}, 500
