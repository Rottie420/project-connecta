import json
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from config import UPLOAD_FOLDER
import pandas as pd
from PetHandler import PetHandler

app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pet_handler = PetHandler()

# Function to log errors to log.txt
def printlog(*args, **kwargs):
    now = datetime.now()
    formatted_date = now.strftime("%d-%m-%Y %H:%M:%S")
    message = f"{formatted_date} : {' '.join(map(str, args))}"
    print(message, **kwargs)
    
    with open(LOG_FILE_PATH, 'a') as file:
        file.write(message + "\n")


# Define routes with error handling
@app.route('/')
def index():
    try:
        return render_template('home.html')
    except Exception as e:
        printlog(f"Index page error: {e}")
        return "An error occurred loading the homepage.", 500

@app.route('/smart-nfc-tag')
def smart_nfc_tag():
    try:
        return render_template('smart-nfc-tag.html')
    except Exception as e:
        printlog(f"Smart NFC Tag page error: {e}")
        return "An error occurred loading the Smart NFC Tag page.", 500

@app.route('/smart-nfc-card')
def smart_nfc_card():
    try:
        return render_template('smart-nfc-card.html')
    except Exception as e:
        printlog(f"Smart NFC Card page error: {e}")
        return "An error occurred loading the Smart NFC Card page.", 500

@app.route('/smart-nfc-sticker')
def smart_nfc_sticker():
    try:
        return render_template('smart-nfc-sticker.html')
    except Exception as e:
        printlog(f"Smart NFC Sticker page error: {e}")
        return "An error occurred loading the Smart NFC Sticker page.", 500

@app.route('/smart-nfc-wearables')
def smart_nfc_wearables():
    try:
        return render_template('smart-nfc-wearables.html')
    except Exception as e:
        printlog(f"Smart NFC Wearables page error: {e}")
        return "An error occurred loading the Smart NFC Wearables page.", 500


@app.route('/pet-profile-edit/<control_number>', methods=['GET', 'POST'])
def pet_profile_edit(control_number=None):
    return pet_handler.pet_profile_edit(control_number)


@app.route('/pet-profile-view/<control_number>', methods=['GET', 'POST'])
def pet_profile_view(control_number=None):
    return pet_handler.pet_profile_view(control_number)
  

# Function to read JSON data from the file
def read_data():
    try:
        if not os.path.exists(DATA_FILE):
            # Create the file if it doesn't exist
            with open(DATA_FILE, 'w') as f:
                json.dump([], f, indent=4)
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        printlog(f"Error reading bookings data: {e}")
        return []

# Function to write JSON data to the file
def write_data(data):
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        printlog(f"Error writing bookings data: {e}")

# Consult Now Route with Error Logging
@app.route('/consult-now', methods=['GET', 'POST'])
def book_demo():
    try:
        if request.method == 'POST':
            # Check if the request contains JSON
            if request.is_json:
                booking_info = {
                    'name': request.json.get('name'),
                    'email': request.json.get('email'),
                    'phone': request.json.get('phone'),
                    'date': request.json.get('date'),
                    'time': request.json.get('time'),
                    'message': request.json.get('message')
                }
            else:
                # Fallback for form data if JSON isn't provided
                booking_info = {
                    'name': request.form.get('name'),
                    'email': request.form.get('email'),
                    'phone': request.form.get('phone'),
                    'date': request.form.get('date'),
                    'time': request.form.get('time'),
                    'message': request.form.get('message')
                }

            # Validate required fields
            if not booking_info['name'] or not booking_info['email']:
                return jsonify({'error': 'Name and email are required.'}), 400
            
            bookings = read_data()
            bookings.append(booking_info)
            write_data(bookings)
            
            return jsonify({'message': 'Booked successfully!', 'booking_info': booking_info}), 200

        return render_template('consult-now.html')

    except Exception as e:
        printlog(f"Book demo error: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 5000


@app.route('/admin-dashboard')
def admin_dashboard_page():
    try:
        # Load the subscriber data from the JSON file
        df = pd.read_json(DATA_FILE)

        # Check if 'date' column exists
        if 'date' not in df.columns:
            raise KeyError("'date' column is missing from the data")

        # Convert 'date' column to datetime type, handling errors in case of invalid data
        try:
            df['date'] = pd.to_datetime(df['date'])
        except Exception as e:
            raise ValueError(f"Error converting 'date' column to datetime: {str(e)}")

        # Logs sorted by 'date' in descending order
        logs = sorted(df.to_dict(orient='records'), key=lambda x: x['date'], reverse=True)

        # Prepare the logs (subscribers with all their info)
        formatted_logs = []
        for index, row in df.iterrows():
            formatted_logs.append({
                "name": row['name'],
                "email": row['email'],
                "phone": row['phone'],
                # Format 'date' as 'YYYY-MM-DD' and 'HH:MM'
                "date": row['date'].strftime('%Y-%m-%d'),
                "time": row['date'].strftime('%H:%M'),
                "message": row['message']
            })

        # Render the template with the necessary data
        return render_template('admin-dashboard.html', logs=formatted_logs)
    
    except Exception as e:
        # Catch any other unforeseen errors
        printlog(f"admin-dashboard error: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 5000



# Initialize application
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
