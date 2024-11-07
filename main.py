import json
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import pandas as pd

app = Flask(__name__, template_folder='templates', static_folder='static')

# Paths and configurations
JSON_FILE_PATH = 'pets.json'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
LOG_FILE_PATH = 'log.txt'
DATA_FILE = 'consultations.json'

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to log errors to log.txt
def printlog(*args, **kwargs):
    now = datetime.now()
    formatted_date = now.strftime("%d-%m-%Y %H:%M:%S")
    message = f"{formatted_date} : {' '.join(map(str, args))}"
    print(message, **kwargs)
    
    with open(LOG_FILE_PATH, 'a') as file:
        file.write(message + "\n")

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to load pets from JSON file
def load_pets():
    try:
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, 'r') as f:
                return json.load(f)
    except Exception as e:
        printlog(f"Error loading pets data: {e}")
    return {}

# Function to save pets to JSON file
def save_pets(pets):
    try:
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump(pets, f, indent=4)
    except Exception as e:
        printlog(f"Error saving pets data: {e}")

# Initialize pets data
pets = load_pets()

# Function to validate control number
def is_valid_control_number(control_number):
    return control_number.isdigit() and control_number not in pets

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

@app.route('/pet/<control_number>')
def pet_profile(control_number):
    try:
        pet = pets.get(control_number)
        if pet:
            timestamp = datetime.now().timestamp()
            return render_template('pet-profile.html', pet=pet, timestamp=timestamp)
        else:
            return "Pet not found", 404
    except Exception as e:
        printlog(f"Pet profile error for control number {control_number}: {e}")
        return "An error occurred while loading the pet profile.", 500

@app.route('/add-pet', methods=['GET', 'POST'])
def add_pet():
    try:
        if request.method == 'POST':
            control_number = request.form['control_number']
            petname = request.form['petname']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            social = {
                'facebook': request.form['facebook'],
                'twitter': request.form['twitter'],
                'instagram': request.form['instagram']
            }

            if not is_valid_control_number(control_number):
                return render_template('add-pet.html', error="Invalid or duplicate control number")

            if 'photo' not in request.files:
                return render_template('add-pet.html', error="No file part")
            
            file = request.files['photo']
            
            if file.filename == '':
                return render_template('add-pet.html', error="No selected file")
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{control_number}_{filename}"

                original_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(original_path)

                # Convert image to WEBP format
                webp_filename = f"{control_number}.webp"
                webp_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)

                try:
                    img = Image.open(original_path)
                    img.save(webp_path, 'webp')
                except Exception as e:
                    printlog(f"Image conversion error for {filename}: {e}")
                    return render_template('add-pet.html', error="Failed to convert image.")
                finally:
                    os.remove(original_path)  # Delete original image

                # Save pet data
                pets[control_number] = {
                    'control_number': control_number,
                    'name': petname,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'social': social,
                    'photo': f'uploads/{webp_filename}'
                }

                save_pets(pets)
                return redirect(url_for('pet_profile', control_number=control_number))
        
        return render_template('add-pet.html')

    except Exception as e:
        printlog(f"Add pet error: {e}")
        return render_template('add-pet.html', error="An error occurred while processing your request.")

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
    # Load the subscriber data from the JSON file
    df = pd.read_json(DATA_FILE)

    # Convert 'datetime' column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Logs sorted by 'datetime' in descending order
    logs = sorted(df.to_dict(orient='records'), key=lambda x: x['datetime'], reverse=True)

    # Prepare the logs (subscribers with all their info)
    formatted_logs = []
    for index, row in df.iterrows():
        formatted_logs.append({
            "name": row['name'],
            "email": row['email'],
            "phone": row['phone'],
            "date": row['datetime'].strftime('%Y-%m-%d'),
            "time": row['datetime'].strftime('%H:%M'),
            "message": row['message']
        })

    # Render the template with the necessary data
    return render_template('admin-dashboard.html', logs=formatted_logs)


# Initialize application
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
